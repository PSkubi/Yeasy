from flask import Blueprint, request,send_file
from PIL import Image
import io
import numpy as np
import os
from datetime import datetime
# if debug is True, microscope will not exist 
# and calls to the api will throw errors.
# only set debug to True when testing api outside the lab
debug = True
if debug == False:
    from .microscope import Microscope
    microscope = Microscope()
else:
    i = 0

microscope_api = Blueprint("backend", __name__)

@microscope_api.route("/status", methods=['GET'])
def get_status():
    status = microscope.Status()
    return status

@microscope_api.route("/image", methods=['GET'])
def get_image():
    if debug:
        print(f'The server was asked for an image. The time is {datetime.now().time()}')
        global i
        i = (i + 1) % 3
        image_path = os.path.join(os.path.dirname(__file__), f'cells_RGB_{i+1}.tiff')
        with open(image_path, 'rb') as f:
            image_bytes= f.read()
        print(f'The server sent the image. The time is {datetime.now().time()}')
        return send_file(io.BytesIO(image_bytes), mimetype='image/tiff')
    else:
        image = microscope.get_image()
        return image

@microscope_api.route("/movestage", methods=['POST'])
def move_stage():
    dx = request.form.get("dx", type=float)
    dy = request.form.get("dy", type=float)
    status = microscope.move_stage(dx, dy)
    return status

@microscope_api.route("/zoom", methods=['POST'])
def zoom():
    mag = request.form.get("magnification", type=float)
    status = microscope.zoom(mag)
    return status