from flask import Blueprint

help_sign_out = Blueprint('help_sign_out', __name__, template_folder='templates')

from app.help_sign_out import routes





