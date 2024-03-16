from flask import Flask
from . import syringe_routes
from . import microscope_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(syringe_routes.syringe_api, name="syringe", url_prefix="/api/syringe")
    app.register_blueprint(microscope_routes.microscope_api, name="microscope", url_prefix="/api/microscope")
    return app