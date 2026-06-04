from flask import Blueprint
bp = Blueprint("credits", __name__)
from app.credits import routes
