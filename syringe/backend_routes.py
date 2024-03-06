from flask import Blueprint, render_template, request
from .syringe_controller import SyringeController

api = Blueprint("backend", __name__)

syringe_controller = SyringeController()

@api.route("/")
def home():
    return

@api.route("/syringe", methods=['GET'])
def q_read_all():
    """Gets all syringes"""
    syringes = syringe_controller.GetAll()
    return syringes

@api.route("/syringe/<int:sid>", methods=['GET'])
def read_sid(sid):
    """Gets the syringe corresponding to the sid"""
    syringe = syringe_controller.Get(sid)
    return syringe

@api.route("/syringe/<int:sid>", methods=['POST'])
def add_phase(sid):
    """Adds a new step to the corresponding sid"""
    phase = request.json.get("phase_data")
    status = syringe_controller.AddPhase(sid, phase)
    return status

@api.route("/syringe/<int:sid>", methods=['DELETE'])
def del_job(sid):
    """Deletes the syringe corresponding to the sid"""
    return

@api.route("/syringe/<int:sid>/<int:phase_number>", methods=['DELETE'])
def del_step(sid, phase_number):
    """Deletes a step corresponding with step id from the syringe corresponding with sid"""
    return

@api.route("/syringe/<int:sid>/<int:phase_number>", methods=['UPDATE'])
def update_step(sid, phase_number):
    """Edits a step within a specific syringe corresponding to sid. The step must not be in progress."""
    return