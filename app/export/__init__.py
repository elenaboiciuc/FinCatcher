from flask import Blueprint

export = Blueprint('export', __name__, template_folder='templates')

from app.export import routes

