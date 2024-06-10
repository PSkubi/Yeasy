from time import sleep
import os
from pathlib import Path
import shutil

def get_image_paths(directory):
    paths = sorted(Path(directory).glob("*.tiff"), key=os.path.getmtime)
    return paths

def clear_files(directory):
    for path in Path(directory).glob("timelapse_output_*.tiff"):
        path.unlink()
    return

FPS = 2
delay = 1./float(FPS)
directory = "microscope_timelapse"
base_directory = os.path.dirname(__file__)
absolute_path = os.path.join(base_directory, directory)

clear_files(absolute_path)
image_paths = get_image_paths(absolute_path)

try:
    counter = 1
    while True:
        for path in image_paths:
            # copy the file
            shutil.copyfile(path, f"{absolute_path}/timelapse_output_{path.name}")
            sleep(delay)
            counter += 1
finally:
    clear_files(absolute_path)