from flask import Blueprint, request,send_file
from PIL import Image
import io
# if debug is True, microscope will not exist 
# and calls to the api will throw errors.
# only set debug to True when testing api outside the lab
debug = False
if debug == False:
    from .microscope import Microscope
    microscope = Microscope()

microscope_api = Blueprint("backend", __name__)

@microscope_api.route("/status", methods=['GET'])
def get_status():
    status = microscope.Status()
    return status

@microscope_api.route("/image", methods=['GET'])
def get_image():
    if debug:
        array = np.random.rand(500,500)
        image = (array * 255).astype(np.uint8)
        image = Image.fromarray(image)
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='TIFF')
        byte_arr = byte_arr.getvalue()
        return send_file(io.BytesIO(byte_arr), mimetype='image/tiff')
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