"""
The flask application package.
"""

from flask import Flask


app = Flask(__name__, static_url_path="")


# load configuration
from . import config

app.logger.info(">>> {}".format(app.config["MODE"]))


# Import blueprints
from app.render import render_bp
from app.api import api_bp


# Register blueprints
app.register_blueprint(render_bp)
app.register_blueprint(api_bp)
