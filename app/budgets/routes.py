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
    if request.method == 'POST':
        new_budget = Budgets(
            name=request.form['name'],
            monthly_limit=request.form['monthly_limit'],
            category_id=request.form['category_id'],
            user_id=current_user.user_id
        )

        try:
            db.session.add(new_budget)
            db.session.commit()
            new_budget.calculate_spent_percentage()
            db.session.commit()
            flash('New budget created successfully!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Budget name already exists. Please choose a different name.', 'error')

        return redirect(url_for('budgets.budgets_page'))

    categories_list = get_categories()
    update_budget_progress_and_notify(current_user.user_id, category_icons)  # Update budgets and notify

    budgets_list = Budgets.query.filter_by(user_id=current_user.user_id).all()

    return render_template('show_budgets.html', page_title='Budgets', icon='fa-solid fa-coins',
                           budgets=budgets_list, categories=categories_list, category_gifs=category_gifs,
                           category_icons=category_icons)


@budgets.route('/budgets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_budget(id):
    budget = Budgets.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()

    if request.method == 'POST':
        budget.name = request.form['name']
        budget.monthly_limit = request.form['monthly_limit']
        budget.category_id = request.form['category_id']
        db.session.commit()  # commit the changes to the budget

        budget.calculate_spent_percentage()  # recalculate percentage after update
        db.session.commit()  # commit after updating the spent percentage

        flash('Budget updated successfully!', 'success')
        return redirect(url_for('budgets.budgets_page'))

    categories_list = get_categories()

    return render_template('edit_budget.html', budget=budget,
                           budgets=Budgets.query.filter_by(user_id=current_user.user_id).all(),
                           category_gifs=category_gifs, categories=categories_list)

@budgets.route('/budgets/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    budget = Budgets.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budgets.budgets_page'))