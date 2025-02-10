from flask import Blueprint

# Create the blueprint instance
transactions = Blueprint('transactions', __name__, template_folder='templates')

# Import routes at the end to avoid circular imports
from app.transactions import routes

