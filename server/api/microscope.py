"""Microscope class."""
import os
from pathlib import Path

class Microscope:
    def __init__(self, image_directory):
        base_directory = os.path.dirname(__file__)
        self.image_directory = os.path.join(base_directory, image_directory)
        return
    
    def get_image(self):
        """Return most recent image from image_directory"""
        paths = sorted(Path(self.image_directory).iterdir(), key=os.path.getmtime)
        with open(paths[-1], 'rb') as f:
            image = f.read()
        return image