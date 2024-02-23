from flask import Blueprint, render_template

api = Blueprint("backend", __name__)

@api.route("/")
def home():
    return

@api.route("/queue", methods=['GET'])
def q_read_all():
    return

@api.route("/queue/<int:q_id>", methods=['GET'])
def read_q_id(q_id):
    return

@api.route("/queue/<int:q_id>", methods=['POST'])
def add_job(q_id):
    return

@api.route("/queue/<int:q_id>", methods=['DELETE'])
def del_job(q_id):
    return

@api.route("/queue/<int:q_id>/<int:step_id>", methods=['DELETE'])
def del_step(q_id, step_id):
    return

@api.route("/queue/<int:q_id>/<int:step_id>>", methods=['UPDATE'])
def update_step(q_id, step_id):
    return