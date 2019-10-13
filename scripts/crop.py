"""
crop sign images
"""

from PIL import Image

# Function copied from http://www.blog.pythonlibrary.org/2017/10/03/how-to-crop-a-photo-with-python/
def crop(image_path, coords, saved_location):
    """
    @param image_path: The path to the image to edit
    @param coords: A tuple of x/y coordinates (x1, y1, x2, y2)
    @param saved_location: Path to save the cropped image
    """
    image_obj = Image.open(image_path)
    cropped_image = image_obj.crop(coords)
    cropped_image.save(saved_location)


if __name__ == "__main__":
    import argparse
    import os

    from tqdm import tqdm

    parser = argparse.ArgumentParser(
        description="crop images"
    )

    parser.add_argument(
        "--from-directory",
        dest="from_directory",
        type=str,
    )

    parser.add_argument(
        "--to-directory",
        dest="to_directory",
        type=str,
    )

    args = parser.parse_args()

    os.makedirs(args.to_directory, exist_ok=True)
    for filename in tqdm(os.listdir(args.from_directory)):
        filepath = os.path.join(args.from_directory, filename)
        to_filepath = os.path.join(args.to_directory, filename)
        crop(filepath, (125, 39, 525, 375), to_filepath)
