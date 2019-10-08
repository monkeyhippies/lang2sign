"""
Copies files from and to s3
"""

from lang2sign.utils.secrets import manager as secrets_manager

import boto3

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="copy file to and from s3"
    )

    parser.add_argument(
        "--s3-bucket",
        dest="s3_bucket",
        type=str,
        help="s3_bucket of this project"
    )

    parser.add_argument(
        "--aws-region",
        dest="aws_region",
        type=str,
        default="us-west-2",
        help="aws_region of S3 bucket for this project"
    )

    parser.add_argument(
        "--repo-directory",
        dest="repo_directory",
        type=str,
        default="/home/ubuntu/lang2sign/",
        help="local path to repo of this project"
    )

    parser.add_argument(
        "--from-filepath",
        dest="from_filepath",
        type=str,
    )

    parser.add_argument(
        "--to-filepath",
        dest="to_filepath",
        type=str,
    )

    parser.add_argument(
        "--download",
        action="store_true",
        dest="download",
        help="Flag to download. Else default is upload"
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

    if args.download:
        bucket.download_file(args.from_filepath, args.to_filepath)
    else:
        bucket.upload_file(args.from_filepath, args.to_filepath)

