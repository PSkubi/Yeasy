from flask import Blueprint, render_template

api = Blueprint("backend", __name__)

@api.route("/")
def home():
    return

@api.route("/queue", methods=['GET'])
def q_read_all():
    """Gets all queues"""
    return

@api.route("/queue/<int:q_id>", methods=['GET'])
def read_q_id(q_id):
    """Gets the queue corresponding to the q id"""
    return

@api.route("/queue/<int:q_id>", methods=['POST'])
def add_step(q_id):
    """Adds a new step to the corresponding q id"""
    return

@api.route("/queue/<int:q_id>", methods=['DELETE'])
def del_job(q_id):
    """Deletes the queue corresponding to the q id"""
    return

@api.route("/queue/<int:q_id>/<int:step_id>", methods=['DELETE'])
def del_step(q_id, step_id):
    """Deletes a step corresponding with step id from the queue corresponding with q id"""
    return

@api.route("/queue/<int:q_id>/<int:step_id>>", methods=['UPDATE'])
def update_step(q_id, step_id):
    """Edits a step within a specific queue corresponding to q id. The step must not be in progress."""
    return