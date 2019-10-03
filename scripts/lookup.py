from collections import namedtuple
import os
import boto3

from lang2sign.utils.secrets import manager as secrets_manager

DOWNLOAD_DIR = "data/raw/gloss2sign/"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Download and process ASLLVD videos'
    )

    parser.add_argument(
        '--repo-directory',
        dest="repo_directory",
        type=str,
        default="/opt",
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
    for pose_id in args.pose_ids:
            pose_filename = "pose-{}.mov".format(pose_id)
            bucket.download_file(
                os.path.join(
                    args.s3_lookup_folder,
                    pose_filename
                ),
                os.path.join(
                    download_directory,
                    pose_filename
                )
            )
