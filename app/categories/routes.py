
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from app.categories import categories
from app.extensions import category_icons, db, category_gifs
from app.main.models import Categories


@categories.route('/categories', methods=['GET', 'POST'])
@login_required
def categories_page():
    if request.method == 'POST':
        # Create a new category from form data
        new_category = Categories(
            name=request.form['name'],
            description=request.form['description'],
            user_id = current_user.user_id
        )
        try:
            # Attempt to add and commit the new category to the database
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
        except IntegrityError:
            # Rollback the session in case of error
            db.session.rollback()
            flash('Category name already exists. Please choose a different name.', 'error')

        return redirect(url_for('categories.categories_page'))

    # fetch all categories from the database
    categories_list = Categories.query.filter(
        or_(Categories.id <= 16, Categories.user_id == current_user.user_id)
    ).all()

    return render_template('show_categories.html',
                           categories=categories_list,
                           page_title='Categories', icon='fas fa-folder',
                           category_icons=category_icons)


@categories.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    try:
        # Attempt to add and commit the new category to the database
        db.session.delete(Categories.query.get_or_404(id))
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except IntegrityError:
        # Rollback the session in case of error
        db.session.rollback()
        flash('This category is associated with existing transactions. Please edit or delete those transactions before removing the category.', 'error')
    return redirect(url_for('categories.categories_page'))

@categories.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Categories.query.get_or_404(id)
    if request.method == 'POST':
        try:
            category.name = request.form['name']
            category.description = request.form['description']
            db.session.commit()
            return redirect(url_for('categories.categories_page'))
        except IntegrityError:
            # Rollback the session in case of error
            db.session.rollback()
            flash('Category name already exists. Please choose another name.', 'warning')

    return render_template('edit_category.html', category=category, categories=Categories.query.all(),
                           category_icons=category_icons, category_gifs=category_gifs)


