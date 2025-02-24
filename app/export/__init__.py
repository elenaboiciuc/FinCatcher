from flask import Blueprint

# create blueprint
export = Blueprint('export', __name__, template_folder='templates')

# import routes at the end to avoid circular imports
from app.export import routes

