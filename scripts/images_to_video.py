"""
converts images into video
"""

from lang2sign.utils.video import images_to_video

if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="convert images to video"
    )

    parser.add_argument(
        "--image-glob",
        dest="image_glob",
        type=str,
    )

    parser.add_argument(
        "--video-filepath",
        dest="video_filepath",
        type=str,
    )

    args = parser.parse_args()

    images_to_video(args.image_glob, args.video_filepath)
