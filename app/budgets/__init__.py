from flask import Blueprint

# create the blueprint
budgets = Blueprint('budgets', __name__, template_folder='templates')

# import routes at the end to avoid circular imports
from app.budgets import routes

