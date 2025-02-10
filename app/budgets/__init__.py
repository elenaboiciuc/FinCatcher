from flask import Blueprint

# Create the blueprint instance
budgets = Blueprint('budgets', __name__, template_folder='templates')

# Import routes at the end to avoid circular imports
from app.budgets import routes

