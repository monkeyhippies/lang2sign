import os

import boto3
import pandas as pd

from lang2sign.utils.secrets import manager as secrets_manager
from lang2sign.utils.bash import run_bash_cmd
from lang2sign.utils.video import *

def get_pose_ids(gloss_filepath, gloss):

    videos = pd.read_csv(gloss_filepath)
    pose_ids = list()
    videos["Gloss Variant"] = videos["Gloss Variant"].apply(
        lambda x: x.rstrip("+")
    )
    for term in gloss:
        ids = videos[videos["Gloss Variant"] == term]["id"].values
        if len(ids) > 0:
            pose_ids.append(ids[0])
    return pose_ids

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Download and process ASLLVD videos'
    )

    parser.add_argument(
        '--repo-directory',
        dest="repo_directory",
        type=str,
        help="local path to repo of this project"
    )

    parser.add_argument(
        '--output-directory',
        dest="output_directory",
        type=str,
        help="directory to write output"
    )

    parser.add_argument(
        '--aws-region',
        dest="aws_region",
        type=str,
        help="aws_region of S3 bucket for this project"
    )

    parser.add_argument(
        '--s3-bucket',
        dest="s3_bucket",
        type=str,
        help="s3_bucket of this project"
    )

    parser.add_argument(
        '--gloss-filepath',
        dest="gloss_filepath",
        type=str,
        help="gloss filepath"
    )

    parser.add_argument(
        '--s3-lookup-folder',
        dest="s3_lookup_folder",
        type=str,
        help="where lookup pose videos are stored"
    )

    parser.add_argument(
        '--video-metadata-filepath',
        dest="video_metadata_filepath",
        type=str,
        help="filepath of video metadata"
    )

    args = parser.parse_args()
    secrets_manager.set_base_directory(args.repo_directory)
    access_id = secrets_manager.get("aws_access_key_id").get_or_prompt()
    secret = secrets_manager.get("aws_secret_access_key").get_or_prompt()

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

    with open(args.gloss_filepath, "r") as file_obj:
        gloss = file_obj.read().strip().split()
    pose_ids = get_pose_ids(args.video_metadata_filepath, gloss)

    pose_filepaths = download_pose_files(bucket, args.s3_lookup_folder, args.output_directory, pose_ids)
    combined_video_filepath = os.path.join(os.path.dirname(pose_filepaths[0]), "combined-pose.mov")
    concat_videos(pose_filepaths, combined_video_filepath)
    jpg_directory = os.path.join(
        os.path.dirname(combined_video_filepath),
        "jpg/"
    )

    os.makedirs(jpg_directory, exist_ok=True)

    video_to_jpg(combined_video_filepath, jpg_directory)
