from flask import Blueprint

goals = Blueprint('goals', __name__, template_folder='templates')

from app.goals import routes


