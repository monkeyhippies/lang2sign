from collections import namedtuple
import os
import zipfile
import shutil
from getpass import getpass
import datetime

import boto3
import requests
import pandas as pd

from lang2sign.utils.secrets import manager as secrets_manager
from lang2sign.utils.bash import run_bash_cmd

CHECKPOINTS_DIR = "checkpoints/"
POSE_DIR = "data/raw/gloss2pose/poses/"
VIDEO_DOWNLOAD_DIR = "data/raw/gloss2pose/signs/"
VIDEO_METADATA_FILE = "data/raw/gloss2pose/video_metadata.csv"
UNFORMATTED_URL = "http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime/{session}/scene{scene}-camera1.mov"

class VideoSegmentMetadata(object):

    def __init__(self, segment_id, start_frame, end_frame):

        self.segment_id = segment_id
        self.start_frame = start_frame
        self.end_frame = end_frame

class VideoMetadata(object):

    def __init__(self, video_id, url, session, scene, segments_metadata):

        self.video_id = video_id
        self.url = url
        self.session = session
        self.scene = scene
        self.segments_metadata = segments_metadata

def time_print(string):

    now = datetime.datetime.now()
    return print("{}: {}".format(now, string))

# taken from https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python
def zip_dir(directory, zipped_filepath):
    # ziph is zipfile handle
    ziph = zipfile.ZipFile(zipped_filepath, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(directory):
        for filename in files:
            ziph.write(os.path.join(root, filename))

    return zipped_filepath

def get_video_metadata(bucket, s3_filepath, download_filepath, partition, num_partitions):
    os.makedirs(os.path.dirname(download_filepath), exist_ok=True)
    bucket.download_file(s3_filepath, download_filepath)
    metadata = pd.read_csv(download_filepath)
    metadata = metadata[metadata["session_scene_id"] % num_partitions == partition]
    # Remove corrupt segments
    metadata = metadata[metadata["is_corrupt"] == 0]
    collapsed_metadata = metadata[["session_scene_id", "Session", "Scene"]].drop_duplicates().sort_values(by=["session_scene_id"])
    collapsed_metadata.index = collapsed_metadata["session_scene_id"]
    metadata["id-start-end"] = metadata["id"].apply(str) + "-" + metadata["Start"].apply(str) + "-" + metadata["End"].apply(str)
    frames_info = metadata.groupby(["session_scene_id"])["id-start-end"].apply(list)
    collapsed_metadata = pd.concat([collapsed_metadata, frames_info], axis=1)

    return [
        VideoMetadata(
            value[0],
            UNFORMATTED_URL.format(
                session=value[1],
                scene=value[2]
            ),
            value[1],
            value[2],
            sorted([
                VideoSegmentMetadata(
                    segment_id=int(segment.split("-")[0]),
                    start_frame=int(segment.split("-")[1]),
                    end_frame=int(segment.split("-")[2])
                ) for segment in value[3]
            ], key=lambda x: x.start_frame)
        ) for value in collapsed_metadata.values
    ]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Download and process ASLLVD videos'
    )

    parser.add_argument(
        '--partition-id',
        dest="partition_id",
        type=int,
        help="Id of what partition you want to process (zero-indexes)"
    )

    parser.add_argument(
        '--s3-bucket',
        dest="s3_bucket",
        type=str,
        help="s3_bucket of this project"
    )

    parser.add_argument(
        '--aws-region',
        dest="aws_region",
        type=str,
        help="aws_region of S3 bucket for this project"
    )

    parser.add_argument(
        '--s3-lookup-folder',
        dest="s3_lookup_folder",
        type=str,
        help="where to write lookup files in s3"
    )

    parser.add_argument(
        '--repo-directory',
        dest="repo_directory",
        type=str,
        default="/opt",
        help="local path to repo of this project"
    )

    parser.add_argument(
        '--s3-video-metadata-filepath',
        dest="s3_metadata_filepath",
        type=str,
        help="filepath of video metadata in s3"
    )

    parser.add_argument(
        '--openpose-home',
        dest="openpose_home",
        type=str,
        default="/opt",
        help="directory where openpose is install"
    )
    parser.add_argument(
        '--frame-rate',
        dest="frame_rate",
        type=int,
        default=30,
        help="frame rate of output pose videos"
    )

    parser.add_argument(
        '--number-partitions',
        dest="number_partitions",
        type=int,
        default=1,
        help="Number of parts video data will be processed in"
    )

    args = parser.parse_args()
    secrets_manager.set_base_directory(args.repo_directory)
    access_id = secrets_manager.get("aws_access_key_id").get_or_prompt()
    secret = secrets_manager.get("aws_secret_access_key").get_or_prompt()

    if args.number_partitions == 1:
        partition_id = 0
    else:
        partition_id = args.partition_id

    s3 = boto3.resource(
        's3', aws_access_key_id=access_id,
        aws_secret_access_key=secret
    )

    bucket = s3.Bucket(args.s3_bucket)

    # If the bucket doesn't exist, create it
    if not bucket.creation_date:
        bucket = s3.create_bucket(
            Bucket=args.s3_bucket,
            CreateBucketConfiguration={'LocationConstraint': args.aws_region}
        )

    checkpoint_filename = "partition-{}-of-{}.txt".format(
        partition_id,
        args.number_partitions
    )

    checkpoint_filepath = os.path.join(
        args.s3_lookup_folder,
        CHECKPOINTS_DIR,
        checkpoint_filename
    )

    try:
        checkpoint_video_id = s3.Object(
            args.s3_bucket, checkpoint_filepath
        ).get()['Body'].read().decode('utf-8')
        checkpoint_video_id = int(checkpoint_video_id)
    except s3.meta.client.exceptions.NoSuchKey:
        checkpoint_video_id = None

    video_metadata_filepath = os.path.join(
        args.repo_directory,
        VIDEO_METADATA_FILE
    )

    videos = get_video_metadata(
        bucket, args.s3_metadata_filepath,
        video_metadata_filepath,
        partition_id, args.number_partitions
    )
    for video in videos:
        # Skip all videos with id <= checkpoint_video_id
        # If checkpoint_video_id isn't found, raise an Exception
        if checkpoint_video_id is None:
            pass
        elif checkpoint_video_id > video.video_id:
            continue
        elif checkpoint_video_id == video.video_id:
            checkpoint_video_id = None
            continue
        else:
            raise Exception(
                "Checkpoint video_id {} not valid".format(checkpoint_video_id)
            )
        time_print("Downloading {} with video_id {}".format(video.url, video.video_id))
        download_dir = os.path.join(args.repo_directory, VIDEO_DOWNLOAD_DIR)
        video_filepath = download_large_file(
            video.url,
            download_dir,
            "{}-{}.{}".format(
                video.session,
                video.scene,
                video.url.split(".")[-1]
            )
        )
        for segment in video.segments_metadata:
            time_print("Processing video segment {}".format(
                segment.segment_id
            ))
            temp_segment_filepath = clip_video(
                video_filepath,
                os.path.join(
                    download_dir,
                    "temp-segment-{}.mov".format(segment.segment_id)
                ),
                segment.start_frame,
                segment.end_frame,
            )

            segment_filepath = resample_video(
                temp_segment_filepath,
                os.path.join(
                    download_dir,
                    "segment-{}.mov".format(segment.segment_id)
                ),
                args.frame_rate
            )

            pose_dir = os.path.join(args.repo_directory, POSE_DIR)
            pose_filepath, keypoints_dir = create_pose(
                segment_filepath,
                "pose-{}.mov".format(segment.segment_id),
                pose_dir,
                args.openpose_home,
                os.path.join(
                    pose_dir,
                    "keypoints-{}/".format(segment.segment_id)
                )
            )

            keypoints_filepath = keypoints_dir.rstrip("/") + ".zip"
            keypoints_filepath = zip_dir(keypoints_dir, keypoints_filepath)

            bucket.upload_file(
                keypoints_filepath,
                os.path.join(
                    args.s3_lookup_folder,
                    os.path.basename(keypoints_filepath)
                )
            )
            bucket.upload_file(
                pose_filepath,
                os.path.join(
                    args.s3_lookup_folder,
                    os.path.basename(pose_filepath)
                )
            )

            # Clean up            
            os.remove(temp_segment_filepath)
            os.remove(segment_filepath)
            os.remove(keypoints_filepath)
            os.remove(pose_filepath)
            shutil.rmtree(keypoints_dir)
        # Update checkpoint after processing entire video
        checkpoint = s3.Object(args.s3_bucket, checkpoint_filepath)
        checkpoint.put(Body=r'{}'.format(video.video_id))
        os.remove(video_filepath)
