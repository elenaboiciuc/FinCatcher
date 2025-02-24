
from flask import Blueprint

# creates the Blueprint
auth = Blueprint('auth', __name__, template_folder='templates')

# import routes at the end to avoid circular imports
from app.register_login import routes





