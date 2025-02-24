from flask import Blueprint

goals = Blueprint('goals', __name__, template_folder='templates')

# import routes at the end to avoid circular imports
from app.goals import routes


