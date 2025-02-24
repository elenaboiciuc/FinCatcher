
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.categories import categories
from app.extensions import category_icons, db, category_gifs
from app.main.helpers import get_categories
from app.main.models import Categories

# route for the categories page, allows both GET and POST methods
@categories.route('/categories', methods=['GET', 'POST'])
@login_required # requires the user to be logged in
def categories_page():
    # ff the form is submitted (POST request)
    if request.method == 'POST':
        # Create a new category from form data
        new_category = Categories(
            name=request.form['name'],
            description=request.form['description'],
            user_id = current_user.user_id # associate the category with the logged-in user
        )
        try:
            # attempt to add and commit the new category to the database
            db.session.add(new_category)
            db.session.commit() # commit to save the changes
            flash('Category added successfully!', 'success')
        except IntegrityError:
            # rollback the session in case of error
            db.session.rollback()
            flash('Category name already exists. Please choose a different name.', 'error')

        return redirect(url_for('categories.categories_page')) # redirect to the categories page

    # fetch all categories from the database
    categories_list = get_categories()

    return render_template('show_categories.html',
                           categories=categories_list,
                           page_title='Categories', icon='fas fa-folder',
                           category_icons=category_icons)

# route to delete a specific category by its ID
@categories.route('/categories/delete/<int:id>', methods=['POST'])
@login_required # requires the user to be logged in
def delete_category(id):
    try:
        # attempt to add and commit the new category to the database
        db.session.delete(Categories.query.get_or_404(id))
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except IntegrityError:
        # rollback the session in case of error
        db.session.rollback()
        flash('This category is associated with existing transactions. Please edit or delete those transactions before removing the category.', 'error')
    return redirect(url_for('categories.categories_page'))

# route to edit a specific category identified by its ID
@categories.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Categories.query.get_or_404(id) # fetch the category to edit or return 404 if not found
    if request.method == 'POST': # if the form is submitted (POST request)
        try:
            # update the category's attributes with new values from the form
            category.name = request.form['name']
            category.description = request.form['description']
            db.session.commit() # commit the changes to the database
            return redirect(url_for('categories.categories_page')) # redirect to the categories page
        except IntegrityError:
            # rollback the session in case of error
            db.session.rollback()
            flash('Category name already exists. Please choose another name.', 'warning')

    return render_template('edit_category.html', category=category, categories=Categories.query.all(),
                           category_icons=category_icons, category_gifs=category_gifs)


