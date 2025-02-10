from flask import Blueprint

categories = Blueprint('categories', __name__, template_folder='templates')

from app.categories import routes