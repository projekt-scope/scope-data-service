""" Blueprint Application """

from flask import Blueprint


render_bp = Blueprint(
    "render_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/",
)

from app.render import views
