from collections import namedtuple
import os
import boto3

from pix2pix.tools.process import process
from lang2sign.utils.secrets import manager as secrets_manager
from lang2sign.utils.bash import run_bash_cmd
from lang2sign.utils.video import *

DOWNLOAD_DIR = "data/preprocessed/gloss2sign/"

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
        '--pose-ids',
        dest="pose_ids",
        nargs='+',
        type=int,
        help="Id of pose video to download"
    )

    parser.add_argument(
        '--s3-lookup-folder',
        dest="s3_lookup_folder",
        type=str,
        help="where lookup pose videos are stored"
    )

    parser.add_argument(
        '--s3-video-metadata-filepath',
        dest="s3_metadata_filepath",
        type=str,
        help="filepath of video metadata in s3"
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
    download_directory = os.path.join(args.repo_directory, DOWNLOAD_DIR)
    os.makedirs(download_directory, exist_ok=True)

    pose_filepaths = download_pose_files(download_directory, args.pose_ids)
    combined_video_filepath = os.path.join(os.path.dirname(pose_filepaths[0]), "combined-pose.mov")
    concat_videos(pose_filepaths, combined_video_filepath)
    jpg_directory = os.path.join(
        os.path.dirname(combined_video_filepath),
        "jpg/"
    )
    png_directory = os.path.join(
        os.path.dirname(combined_video_filepath),
        "png/"
    )
    combined_directory = os.path.join(
        os.path.dirname(combined_video_filepath),
        "combined/",
    )
    os.makedirs(jpg_directory, exist_ok=True)
    os.makedirs(png_directory, exist_ok=True)
    os.makedirs(combined_directory, exist_ok=True)

    video_to_jpg(combined_video_filepath, jpg_directory)

    jpg_to_png(jpg_directory, png_directory)
    print("png output is in {}".format(png_directory))
    process(png_directory, combined_directory)
