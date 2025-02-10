from flask import render_template, request
from app.categories import categories
from app.extensions import db
from app.main.models import Categories


@categories.route('/categories', methods=['GET'])
def categories_page():
    # Fetch all categories from the database
    categories_list = Categories.query.all()

    return render_template('show_categories.html', categories=categories_list)
