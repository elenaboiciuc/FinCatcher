from flask import Blueprint

# create the blueprint instance
transactions = Blueprint('transactions', __name__, template_folder='templates')

# import routes at the end to avoid circular imports
from app.transactions import routes

