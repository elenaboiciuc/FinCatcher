from flask import Blueprint

help = Blueprint('help', __name__, template_folder='templates')

from app.help import routes





