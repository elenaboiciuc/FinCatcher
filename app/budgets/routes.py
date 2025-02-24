from datetime import datetime, timedelta

from flask_login import login_required, current_user
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import current_date

from app.extensions import db, category_gifs
from app.budgets import budgets
from flask import render_template, request, flash, redirect, url_for

from app.main.chart_helpers import get_transactions_by_date
from app.main.models import Budgets, Categories, Transactions

@budgets.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets_page():
    if request.method == 'POST':
        # Create a new budget from form data
        new_budget = Budgets(
            name=request.form['name'],
            monthly_limit=request.form['monthly_limit'],
            category_id=request.form['category_id'],
            user_id=current_user.user_id
        )
        try:
            # Attempt to add and commit the new budget to the database
            db.session.add(new_budget)
            db.session.commit()
            flash('New budget created successfully!', 'success')
        except IntegrityError:
            # Rollback the session in case of error
            db.session.rollback()
            flash('Budget name already exists. Please choose a different name.', 'error')

        return redirect(url_for('budgets.budgets_page'))

    # Fetch all categories from the database
    categories_list = Categories.query.filter(
        or_(Categories.id <= 16, Categories.user_id == current_user.user_id)
    ).all()

    # Calculate the start and end of the current month
    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Now we use the Transaction model directly in the query
    budgets_list = (db.session.query(Budgets, func.coalesce(func.sum(Transactions.amount), 0).label('spent'))
                    .outerjoin(Transactions, (Budgets.category_id == Transactions.category_id) &
                               (Transactions.user_id == current_user.user_id) &
                               (Transactions.date >= start_of_month) &
                               (Transactions.date <= end_of_month))
                    .filter(Budgets.user_id == current_user.user_id)
                    .group_by(Budgets)
                    .all())

    for budget, spent in budgets_list:
        budget.percent_spent = (spent / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0

        if budget.percent_spent >= 100:
            flash(f'Budget "{budget.name}" is over budget! Please review.', 'error')
        elif budget.percent_spent >= 80:
            flash(f'Warning: You have spent {budget.percent_spent | round}% of your "{budget.name}" budget.', 'warning')
        elif budget.percent_spent >= 50:
            flash(f'Notice: You have spent {budget.percent_spent | round}% of your "{budget.name}" budget.', 'info')

    # Render the page with budgets and categories
    return render_template('show_budgets.html', page_title='Budgets', icon='fa-solid fa-coins',
                           budgets=budgets_list, categories=categories_list, category_gifs=category_gifs)


@budgets.route('/budgets/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    budget = Budgets.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()

    # Delete the budget
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully!', 'success')

    # Redirect to the budgets page after deletion
    return redirect(url_for('budgets.budgets_page'))

@budgets.route('/budgets/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_budget(id):
    budget = Budgets.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    if request.method == 'POST':
        try:
            budget.name = request.form['name']
            budget.monthly_limit = request.form['monthly_limit']
            budget.category_id = request.form['category_id']
            db.session.commit()
            flash('Budget updated successfully!', 'success')
            return redirect(url_for('budgets.budgets_page'))
        except IntegrityError:
            # Rollback the session in case of error
            db.session.rollback()
            flash('Budget name already exists. Please choose another name.', 'warning')

    # Fetch all categories from the database
    categories_list = Categories.query.filter(
        or_(Categories.id <= 16, Categories.user_id == current_user.user_id)
    ).all()

    return render_template('edit_budget.html', budget=budget,
                           budgets=Budgets.query.filter_by(user_id=current_user.user_id).all(),
                           category_gifs=category_gifs, categories=categories_list)