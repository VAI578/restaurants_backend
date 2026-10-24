from flask import Blueprint

api = Blueprint("api", __name__)

from . import resto_controller
