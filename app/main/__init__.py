from flask import Blueprint

# create the Blueprint
main = Blueprint('main', __name__, template_folder='templates')

# import routes at the end to avoid circular imports
from app.main import routes