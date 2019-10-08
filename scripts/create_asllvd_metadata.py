"""
Creates the asllvd metadata csv and uploads to s3
"""
import requests
import os
import datetime

import boto3
import pandas as pd
import numpy as np

from lang2sign.utils.secrets import manager as secrets_manager

DOWNLOAD_FILE = "dai-asllvd-BU_glossing_with_variations_HS_information-extended-urls-RU.xlsx"
DOWNLOAD_DIR = "data/raw/gloss2pose/"
URL = "http://www.bu.edu/asllrp/" + DOWNLOAD_FILE

def download_file(download_dir, download_filename, url):
    os.makedirs(download_dir, exist_ok=True)

    download_path = os.path.join(download_dir, download_filename)

    response = requests.get(url)

    with open(download_path, "wb") as file_obj:
        file_obj.write(response.content)

    return download_path

def clean_asllvd_metadata(from_filepath, to_filepath):
    """
    Writes asllvd excel file to a cleaned csv
    """
    video_set = pd.read_excel(from_filepath)
    video_set = video_set.replace("============", np.nan)
    video_set = video_set.replace("------------", np.nan)
    video_set = video_set.replace("-------------------------", np.nan)
    video_set = video_set.dropna(axis=0, subset=["Gloss Variant", "Session", "Scene", "Start", "End"], how="all")
    new_video_set = video_set[["Gloss Variant", "Consultant", "Session", "Scene", "Start", "End"]]
    new_video_set = new_video_set.sort_values(by=["Gloss Variant", "Consultant", "Session", "Scene", "Start", "End"])
    new_video_set = new_video_set.reset_index().drop(["index"], axis=1)
    new_video_set["id"] = new_video_set.index
    new_video_set["Scene"] = new_video_set["Scene"].astype(int)
    new_video_set["Start"] = new_video_set["Start"].astype(int)
    new_video_set["End"] = new_video_set["End"].astype(int)
    new_video_set["session_scene"] = new_video_set["Session"] + "-" + new_video_set["Scene"]\
    new_video_set["Scene"].apply(lambda x: str(x))
    new_video_set["session_scene_id"] = (
        new_video_set["session_scene"]
    ).astype("category").cat.codes
    new_video_set["is_corrupt"] = 0
    new_video_set.to_csv(to_filepath, index=False)

    return to_filepath

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create video metadata",
    )

    parser.add_argument(
        "--s3-video-metadata-filepath",
        dest="s3_filepath",
        type=str,
        help="filepath in S3 that video metadata will be written to"
    )

    parser.add_argument(
        "--s3-bucket",
        dest="s3_bucket",
        type=str,
        help="s3_bucket of this project"
    )

    parser.add_argument(
        "--repo-directory",
        dest="repo_directory",
        type=str,
        default="/opt",
        help="local path to repo of this project"
    )

    args = parser.parse_args()

    csv_filepath = os.path.join(DOWNLOAD_DIR, "video_metadata.csv")
    filepath = download_file(DOWNLOAD_DIR, DOWNLOAD_FILE, URL)
    csv_filepath = clean_asllvd_metadata(filepath, csv_filepath)
    print("Uploading video_metadata to {}".format(args.s3_filepath))

    secrets_manager.set_base_directory(args.repo_directory)
    access_id = secrets_manager.get("aws_access_key_id").get_or_prompt()
    secret = secrets_manager.get("aws_secret_access_key").get_or_prompt()

    s3 = boto3.resource(
        "s3", aws_access_key_id=access_id,
        aws_secret_access_key=secret
    )
    bucket = s3.Bucket(args.s3_bucket)

    # Upload video metadata and timestamp
    bucket.upload_file(csv_filepath, args.s3_filepath)
    timestamp = s3.Object(args.s3_bucket, args.s3_filepath + ".timestamp")
    timestamp.put(Body=r"{}".format(datetime.datetime.now()))

