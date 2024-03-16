from flask import Blueprint, request
from .microscope import Microscope

microscope_api = Blueprint("backend", __name__)

microscope = Microscope()

@microscope_api.route("/microscope/status", methods=['GET'])
def get_status():
    status = microscope.Status()
    return status

@microscope_api.route("/microscope/image", methods=['GET'])
def get_image():
    image = microscope.get_image()
    return image

@microscope_api.route("/microscope/movestage", methods=['POST'])
def move_stage():
    dx = request.form.get("dx", type=float)
    dy = request.form.get("dy", type=float)
    status = microscope.move_stage(dx, dy)
    return status

@microscope_api.route("/microscope/zoom", methods=['POST'])
def zoom():
    mag = request.form.get("magnification", type=float)
    status = microscope.zoom(mag)
    return status