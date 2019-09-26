from collections import namedtuple
import os

import requests
import shutil
import pandas as pd

VIDEO_DOWNLOAD_DIR = "data/raw/gloss2pose/"
VIDEO_METADATA_FILE = "video-metadata/video_metadata.csv"
UNFORMATTED_URL = "http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime/{session}/scene{scene}-camera1.mov"
Video = namedtuple('video', 'id url')

# taken from https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_large_file(url, download_dir):
	os.makedirs(download_dir, exist_ok=True)
	local_filename = os.path.join(download_dir, url.split('/')[-1])
	with requests.get(url, stream=True) as response:
		with open(local_filename, 'wb') as file_obj:
			shutil.copyfileobj(response.raw, file_obj)

	return local_filename
  

def get_video_urls(partition, num_partitions):
	metadata = pd.read_csv(VIDEO_METADATA_FILE)
	metadata = metadata[metadata["session_scene_id"] % num_partitions == partition]
	metadata["Scene"] = metadata["Scene"].astype(int)
	metadata = metadata[["session_scene_id", "Session", "Scene"]].drop_duplicates().sort_values(by=["session_scene_id"])
	return [
		Video(value[0], UNFORMATTED_URL.format(
			session=value[1],
			scene=value[2]
		)) for value in metadata.values
	]

if __name__ == "__main__":
	import argparse
	import time

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
  
	urls = get_video_urls(partition_id, number_partitions)
	for url in urls:
		download_large_file(url.url, VIDEO_DOWNLOAD_DIR)
		time.sleep(10)
