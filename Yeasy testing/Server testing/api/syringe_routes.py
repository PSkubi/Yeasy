from flask import Blueprint, request

# if debug is True, syringe_controller will not exist 
# and calls to the api will throw errors.
# only set debug to True when testing api outside the lab
debug = True
if debug == False:
    from .syringe_controller import SyringeController
    import serial
    from serial.tools import list_ports

    # connect with syringe hardware port
    ports = list(list_ports.comports())
    s_name = ports[0].device
    port = serial.Serial(s_name)
    syringe_controller = SyringeController(port)

syringe_api = Blueprint("backend", __name__)

@syringe_api.route("/<int:sid>/status", methods=['GET'])
def get_status(sid):
    """Gets the syringe corresponding to the sid"""
    # TODO
    syringe = syringe_controller.Get(sid)
    return syringe

@syringe_api.route("/<int:sid>/stop", methods=['POST'])
def stop(sid):
    """Adds a stop step to the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    status = syringe.stop()
    return status

@syringe_api.route("/<int:sid>/run", methods=['POST'])
def run(sid):
    """Adds a stop step to the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    phase_number = request.form.get("value", default=1, type=int)
    status = syringe.run(phase_number)
    return status

@syringe_api.route("/<int:sid>/pump_phase", methods=['POST'])
def set_pump_phase(sid):
    """Sets up a whole pumping phase for the syringe with the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    rate = request.form.get("rate", type=float)
    units = request.form.get("units", type=str)
    volume = request.form.get("volume", type=float)
    direction = request.form.get("direction", type=str, default="INF")
    phase_number = request.form.get("phase", type=int, default=-1)
    status = syringe.create_pumping_phase(rate, units, volume, direction, phase_number=phase_number)
    return status

@syringe_api.route("/<int:sid>/diameter", methods=['POST'])
def set_diameter(sid):
    """Sets diameter of syringe for the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    diameter = request.form.get("value", type=float)
    status = syringe.set_diameter(diameter)
    return status

@syringe_api.route("/<int:sid>/clear", methods=['POST'])
def clear_phases(sid):
    """Clears the Pumping Program on the syringe corresponding with sid"""
    syringe = syringe_controller.Get(sid)
    status = syringe.clear()
    return status

'''
@syringe_api.route("/<int:sid>/rate", methods=['POST'])
def set_rate(sid):
    """Sets rate of syringe for the corresponding sid"""
    syringe = syringe_controller.Get(sid)
    rate = request.form.get("value", type=float)
    unit = request.form.get("unit", type=str)
    status = syringe.set_rate(rate, unit)
    return status
'''