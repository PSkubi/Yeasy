from flask import Flask
from microscope import backend_routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(backend_routes.api, url_prefix="/api")
    return app