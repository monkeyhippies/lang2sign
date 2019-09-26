from collections import namedtuple
import os

import requests
import shutil
import pandas as pd
from subprocess import Popen, PIPE

POSE_DIR = "data/raw/gloss2pose/poses/"
VIDEO_DOWNLOAD_DIR = "data/raw/gloss2pose/signs/"
VIDEO_METADATA_FILE = "video-metadata/video_metadata.csv"
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

def create_pose(video_filepath, pose_filename, pose_dir, openpose_home):
	"""
	creates pose video and json data from
	video found at video_filepath
	"""

	openpose_exe = os.path.join(
		openpose_home,
		"openpose/build/examples/openpose/openpose.bin"
	)

	unformatted_cmd = "{openpose_exe} -disable-blending=True --face --hand --video {video_filepath} --display 0  --write_video {pose_filepath} --write_json {pose_dir}"

	os.makedirs(pose_dir, exist_ok=True)

	pose_filepath = os.path.join(pose_dir, pose_filename)
	cmd = unformatted_cmd.format(
		openpose_exe=openpose_exe,
		video_filepath=video_filepath,
		pose_filepath=pose_filepath,
		pose_dir=pose_dir,
	)
	p = Popen(['bash', '-c', cmd], stdout=PIPE, stderr=PIPE)
	output, error = p.communicate()
	if p.returncode != 0: 
		print("openpose failed %d %s %s" % (p.returncode, output, error))

	return pose_filepath

# taken from https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_large_file(url, download_dir, filename):
	os.makedirs(download_dir, exist_ok=True)
	local_filename = os.path.join(download_dir, filename)
	with requests.get(url, stream=True) as response:
		with open(local_filename, 'wb') as file_obj:
			shutil.copyfileobj(response.raw, file_obj)

	return local_filename


def get_video_metadata(partition, num_partitions):
	metadata = pd.read_csv(VIDEO_METADATA_FILE)
	metadata = metadata[metadata["session_scene_id"] % num_partitions == partition]

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
		'--openpose-home',
		dest="openpose_home",
		type=str,
		default="/opt",
		help="directory where openpose is install"
	)

	parser.add_argument(
		'--number-partitions',
		dest="number_partitions",
		type=int,
		default=1,
		help="Number of parts video data will be processed in"
	)

	args = parser.parse_args()
	number_partitions = args.number_partitions
	if number_partitions == 1:
		partition_id = 0
	else:
		partition_id = args.partition_id
  
	videos = get_video_metadata(partition_id, number_partitions)
	for video in videos:
		print("Processing {}".format(video.url.split("/")[-1]))
		video_filepath = download_large_file(
			video.url,
			VIDEO_DOWNLOAD_DIR,
			"{}-{}.{}".format(
				video.session,
				video.scene,
				video.url.split(".")[-1]
			)
		)
		pose_filename = os.path.basename(video_filepath)
		create_pose(
			video_filepath,
			pose_filename,
			POSE_DIR,
			args.openpose_home
		)

		print("done")
		break
