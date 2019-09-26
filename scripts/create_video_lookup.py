import requests
import shutil
import pandas as pd

VIDEO_METADATA_FILE = "video-metadata/video_metadata.csv"
UNFORMATTED_URL = "http://csr.bu.edu/ftp/asl/asllvd/asl-data2/quicktime/{session}/scene{scene}-camera1.mov"

# taken from https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_large_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as response:
        with open(local_filename, 'wb') as file_obj:
            shutil.copyfileobj(response.raw, file_obj)

    return local_filename
  
url = UNFORMATTED_URL.format(
  session="ASL_2011_07_22_Brady",
  scene=37
)

def get_video_data(partition, num_partitions):
  metadata = pd.read_csv(VIDEO_METADATA_FILE)
  metadata = metadata[metadata["session_scene_id"] % num_partitions == partition]
  return metadata[["session_scene_id", "Session", "Scene"]].values

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
  
  get_video_urls(partition_id, number_partitions)
