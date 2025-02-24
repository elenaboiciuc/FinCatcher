from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.extensions import db, category_gifs, category_icons
from app.budgets import budgets
from flask import render_template, request, flash, redirect, url_for
from app.main.helpers import get_categories, update_budget_progress_and_notify
from app.main.models import Budgets


@budgets.route('/budgets', methods=['GET', 'POST'])
@login_required # requires the user to be logged in
def budgets_page():
    # if the form is submitted (POST request)
    if request.method == 'POST':
        # create a new budget object with data from the form
        new_budget = Budgets(
            name=request.form['name'],
            monthly_limit=request.form['monthly_limit'],
            category_id=request.form['category_id'],
            user_id=current_user.user_id
        )

        try:
            # add the new budget to the database
            db.session.add(new_budget)
            db.session.commit() # commit the session to save the new budget
            new_budget.calculate_spent_percentage() # calculate and update the spent percentage
            db.session.commit()
            flash('New budget created successfully!', 'success')
        except IntegrityError:
            db.session.rollback() # rollback the session in case of an error
            flash('Budget name already exists. Please choose a different name.', 'error')

        return redirect(url_for('budgets.budgets_page')) # redirect to the budgets page

    # get the list of categories for the dropdown
    categories_list = get_categories()
    # update budget progress and notify the user
    update_budget_progress_and_notify(current_user.user_id, category_icons)  # Update budgets and notify

    # query for all budgets that belong to the current user
    budgets_list = Budgets.query.filter_by(user_id=current_user.user_id).all()

    return render_template('show_budgets.html', page_title='Budgets', icon='fa-solid fa-coins',
                           budgets=budgets_list, categories=categories_list, category_gifs=category_gifs,
                           category_icons=category_icons)

# route to edit a specific budget, identified by its ID
@budgets.route('/budgets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_budget(id):
    # fetch the budget to edit, or return a 404 error if not found
    budget = Budgets.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()

    # if the form is submitted (POST request)
    if request.method == 'POST':
        try:
            # update the budget's attributes with the new values from the form
            budget.name = request.form['name']
            budget.monthly_limit = request.form['monthly_limit']
            budget.category_id = request.form['category_id']
            db.session.commit()  # commit the changes to the budget

            budget.calculate_spent_percentage()  # recalculate percentage after update
            db.session.commit()  # commit after updating the spent percentage

            flash('Budget updated successfully!', 'success')
            return redirect(url_for('budgets.budgets_page'))
        except IntegrityError:
            db.session.rollback()  # rollback the session in case of an error
            flash('Budget name already exists. Please choose another name.', 'error')

    # get the list of categories for the dropdown
    categories_list = get_categories()

    # render the edit budget template
    return render_template('edit_budget.html', budget=budget,
                           budgets=Budgets.query.filter_by(user_id=current_user.user_id).all(),
                           category_gifs=category_gifs, categories=categories_list)

# route to delete a specific budget
@budgets.route('/budgets/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    # fetch the budget to delete, ore return a 404 error if not found
    budget = Budgets.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    db.session.delete(budget) # delete the budget
    db.session.commit() # commit to save changes
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budgets.budgets_page'))