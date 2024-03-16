"""Microscope class."""
from pycromanager import Bridge

class Microscope:
    def __init__(self):
        # create the Micro-Managert to Pycro-Manager transfer layer
        bridge = Bridge()
        # get object representing micro-manager core
        self.core = bridge.get_core()
        return
    
    def get_image(self):
        self.core.snap_image()
        tagged_image = self.core.get_tagged_image()
        image_height = tagged_image.tags['Height']
        image_width = tagged_image.tags['Width']
        image = tagged_image.pix.reshape((image_height, image_width))
        return image
    
    def move_stage(self, dx, dy):
        return
    
    def zoom(self, mag):
        return