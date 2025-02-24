from flask import Blueprint

# create the blueprint
help = Blueprint('help', __name__, template_folder='templates')

# import routes at the end to avoid circular imports
from app.help import routes





