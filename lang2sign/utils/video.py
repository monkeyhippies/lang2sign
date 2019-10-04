from lang2sign.utils.secrets import manager as secrets_manager
from lang2sign.utils.bash import run_bash_cmd

from collections import namedtuple
import os
import zipfile
import shutil
from getpass import getpass
import datetime

import boto3
import requests
import pandas as pd

def zip_dir(directory, zipped_filepath):
    # ziph is zipfile handle
    ziph = zipfile.ZipFile(zipped_filepath, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(directory):
        for filename in files:
            ziph.write(os.path.join(root, filename))

    return zipped_filepath

def clip_video(from_video_filepath, to_video_filepath, start_frame, end_frame):

    """
    create video clip starting at @start_frame and ending at @end_frame inclusive
    """

    unformatted_cmd = "ffmpeg -i {from_path} -vf trim=start_frame={start_frame}:end_frame={end_frame} -y -an {to_path}"

    cmd = unformatted_cmd.format(
        from_path=from_video_filepath,
        to_path=to_video_filepath,
        start_frame=start_frame,
        end_frame=end_frame + 1,
    )

    run_bash_cmd(cmd)

    return to_video_filepath

def resample_video(from_video_filepath, to_video_filepath, frame_rate):
    """
    resamples video with @frame_rate and outputs new video
    """

    unformatted_cmd = "ffmpeg -i {from_path} -filter:v fps=fps={frame_rate} -y {to_path}"

    cmd = unformatted_cmd.format(
        from_path=from_video_filepath,
        to_path=to_video_filepath,
        frame_rate=frame_rate,
    )


    run_bash_cmd(cmd)

    return to_video_filepath

def create_pose(
    video_filepath, pose_filename, pose_dir,
    openpose_home, keypoints_dir
):
    """
    creates pose video and json data from
    video found at video_filepath
    """

    openpose_dir = os.path.join(
        openpose_home,
        "openpose/"
    )

    unformatted_cmd = "cd {openpose_dir} && ./build/examples/openpose/openpose.bin -disable_blending=True --face --hand --video {video_filepath} --display 0  --write_video {pose_filepath} --write_json {json_dir}"

    
    os.makedirs(pose_dir, exist_ok=True)
    os.makedirs(keypoints_dir, exist_ok=True)
    pose_filepath = os.path.join(pose_dir, pose_filename)
    cmd = unformatted_cmd.format(
        openpose_dir=openpose_dir,
        video_filepath=video_filepath,
        pose_filepath=pose_filepath,
        pose_dir=pose_dir,
        json_dir=keypoints_dir
    )

    run_bash_cmd(cmd)

    return pose_filepath, keypoints_dir

# taken from https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_large_file(url, download_dir, filename):
    os.makedirs(download_dir, exist_ok=True)
    local_filename = os.path.join(download_dir, filename)
    with requests.get(url, stream=True) as response:
        with open(local_filename, 'wb') as file_obj:
            shutil.copyfileobj(response.raw, file_obj)

    return local_filename

def write_concat_input_file(video_filepaths, input_filepath):

    with open(input_filepath, "w") as file_obj:
        for filepath in video_filepaths:
            file_obj.write("file '{}'\n".format(filepath))

    return input_filepath

def download_pose_files(download_directory, pose_ids):
    pose_filepaths = []
    for pose_id in pose_ids:
        pose_filename = "pose-{}.mov".format(pose_id)
        pose_filepath = os.path.join(download_directory, pose_filename)
        bucket.download_file(
            os.path.join(
                args.s3_lookup_folder,
                pose_filename
            ),
            pose_filepath
        )
        pose_filepaths.append(pose_filepath)

    return pose_filepaths

def video_to_jpg(video_filepath, jpg_directory):
    """
    create video clip starting at @start_frame and ending at @end_frame inclusive
    """


    unformatted_cmd = "ffmpeg -i {} {} -hide_banner"

    cmd = unformatted_cmd.format(
        video_filepath,
        os.path.join(jpg_directory, "video-%06d.jpg")
    )

    run_bash_cmd(cmd)

    return jpg_directory

def jpg_to_png(jpg_directory, png_directory):

    unformatted_cmd = "mogrify -format png -path {} {}"

    cmd = unformatted_cmd.format(
        png_directory,
        os.path.join(jpg_directory, "*.jpg")
    )

    run_bash_cmd(cmd)

    return png_directory

def concat_videos(video_filepaths, output_filepath):

    """
    create video clip starting at @start_frame and ending at @end_frame inclusive
    """

    input_filepath = os.path.join(
        os.path.dirname(video_filepaths[0]),
        "input.txt"
    )

    write_concat_input_file(video_filepaths, input_filepath)

    unformatted_cmd = "ffmpeg -f concat -safe 0 -i {} -codec copy -y {}"

    cmd = unformatted_cmd.format(
        input_filepath,
        output_filepath
    )

    run_bash_cmd(cmd)

    return output_filepath

