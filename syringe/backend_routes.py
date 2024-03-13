from flask import Blueprint, render_template, request
from .syringe_controller import SyringeController

api = Blueprint("backend", __name__)

syringe_controller = SyringeController()

@api.route("/syringe/<int:sid>/status", methods=['GET'])
def get_status(sid):
    """Gets the syringe corresponding to the sid"""
    # TODO
    syringe = syringe_controller.Get(sid)
    return syringe

@api.route("/syringe/<int:sid>/stop", methods=['POST'])
def stop(sid):
    """Adds a stop step to the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    status = syringe.stop()
    return status

@api.route("/syringe/<int:sid>/run", methods=['POST'])
def run(sid):
    """Adds a stop step to the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    phase_number = request.form.get("value", default=1, type=int)
    status = syringe.run(phase_number)
    return status

@api.route("/syringe/<int:sid>/pump_phase", methods=['POST'])
def set_pump_phase(sid):
    """Sets up a whole pumping phase for the syringe with the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    rate = request.form.get("rate", type=float)
    units = request.form.get("units", type=str)
    volume = request.form.get("volume", type=float)
    direction = request.form.get("direction", type=str, default="INF")
    status = syringe.create_pumping_phase(rate, units, volume, direction)
    return status

@api.route("/syringe/<int:sid>/diameter", methods=['POST'])
def set_diameter(sid):
    """Sets diameter of syringe for the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    diameter = request.form.get("value", type=float)
    status = syringe.set_diameter(diameter)
    return status

@api.route("/syringe/<int:sid>/clear", methods=['POST'])
def clear_phases(sid):
    """Clears the Pumping Program on the syringe corresponding with sid"""
    syringe = syringe_controller.Get(sid)
    status = syringe.clear()
    return status

'''
@api.route("/syringe/<int:sid>/rate", methods=['POST'])
def set_rate(sid):
    """Sets rate of syringe for the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    rate = request.form.get("value", type=float)
    unit = request.form.get("unit", type=str)
    status = syringe.set_rate(rate, unit)
    return status
'''