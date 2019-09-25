import requests
import os

import pandas as pd
import numpy as np

DOWNLOAD_FILE = 'dai-asllvd-BU_glossing_with_variations_HS_information-extended-urls-RU.xlsx'
DOWNLOAD_DIR = 'data/raw/gloss2pose/'
URL = 'http://www.bu.edu/asllrp/' + DOWNLOAD_FILE

def download_file(download_dir, download_filename, url):
  os.makedirs(download_dir, exist_ok=True)

  download_path = os.path.join(download_dir, download_filename)

  response = requests.get(url)

  with open(download_path, 'wb') as file_obj:
      file_obj.write(response.content)

  return download_path

def clean_asllvd_metadata(from_filepath, to_filepath):
  """
  Writes asllvd excel file to a cleaned csv
  """

  video_set = pd.read_excel(from_filepath)
  video_set = video_set.replace("============", np.nan)
  video_set = video_set.fillna(method="ffill")
  video_set = video_set.dropna(axis=0, subset=["Gloss Variant", "Session", "Scene", "Start", "End"], how="all")
  new_video_set = video_set[["Gloss Variant", "Consultant", "Session", "Scene", "Start", "End"]]
  new_video_set = new_video_set.sort_values(by=["Gloss Variant", "Consultant", "Session", "Scene", "Start", "End"])
  new_video_set = new_video_set.reset_index().drop(["index"], axis=1)
  new_video_set["id"] = new_video_set.index
  new_video_set["session_scene"] = new_video_set['Session'] + '-' + \
    new_video_set['Scene'].apply(lambda x: str(x))
  new_video_set["session_scene_id"] = (
      new_video_set["session_scene"]
  ).astype('category').cat.codes
  new_video_set.to_csv(to_filepath, index=False)

if __name__ == "__main__":
  csv_filepath = os.path.join(DOWNLOAD_DIR, "video_metadata.csv")
  print("Creating {}".format(csv_filepath))
  filepath = download_file(DOWNLOAD_DIR, DOWNLOAD_FILE, URL)
  clean_asllvd_metadata(filepath, csv_filepath)
