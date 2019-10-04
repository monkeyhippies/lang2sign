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
        '--download-sub-directory',
        dest="sub_directory",
        type=str,
        help="download video"
    )

    parser.add_argument(
        '--repo-directory',
        dest="repo_directory",
        type=str,
        help="local path to repo of this project"
    )

    parser.add_argument(
        '--video-url',
        dest="video_url",
        type=str,
        help="download video"
    )

    parser.add_argument(
        '--openpose-home',
        dest="openpose_home",
        default="/opt",
        type=str,
        help="download video"
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

    # Download file
    download_directory = os.path.join(
        repo_directory,
        DOWNLOAD_DIR,
        args.sub_directory
    )

    download_directory = os.path.join(args.repo_directory, DOWNLOAD_DIR)
    os.makedirs(download_directory, exist_ok=True)
    video_filepath = download_big_file(args.video_url, download_directory)
    video_filename = os.path.basename(video_filepath)
    pose_filename = "pose-" + video_filename
    pose_filepath = create_pose(video_filepath, pose_filename, download_directory, openpose_home, download_directory)
    pose_jpg_directory = os.path.join(
        download_directory,
        "pose/jpg/"
    )
    pose_png_directory = os.path.join(
        download_directory,
        "pose/png/"
    )

    sign_jpg_directory = os.path.join(
        download_directory,
        "sign/jpg/"
    )
    sign_png_directory = os.path.join(
        download_directory,
        "sign/png/"
    )
    combined_directory = os.path.join(
        download_directory,
        "combined/",
    )
    os.makedirs(sign_jpg_directory, exist_ok=True)
    os.makedirs(sign_png_directory, exist_ok=True)
    os.makedirs(pose_jpg_directory, exist_ok=True)
    os.makedirs(pose_png_directory, exist_ok=True)
    os.makedirs(combined_directory, exist_ok=True)


    video_to_jpg(video_filepath, sign_jpg_directory)
    jpg_to_png(sign_jpg_directory, sign_png_directory)

    video_to_jpg(pose_filepath, pose_jpg_directory)
    jpg_to_png(pose_jpg_directory, pose_png_directory)
