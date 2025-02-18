from flask import render_template, redirect, url_for, request
from app.categories import categories
from app.extensions import category_icons, db
from app.main.models import Categories


@categories.route('/categories', methods=['GET'])
def categories_page():
    # Fetch all categories from the database
    categories_list = Categories.query.all()

    return render_template('show_categories.html', categories=categories_list, page_title='Categories', icon='fas fa-folder', category_icons=category_icons)

@categories.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_category(id):
    db.session.delete(Categories.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('categories.categories_page'))

@categories.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Categories.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form['description']
        db.session.commit()
        return redirect(url_for('categories.categories_page'))
    return render_template('edit_category.html', category=category, categories=Categories.query.all(), category_icons=category_icons)
