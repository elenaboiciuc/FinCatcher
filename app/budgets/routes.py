from datetime import datetime, timedelta
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.extensions import db, category_gifs, category_icons
from app.budgets import budgets
from flask import render_template, request, flash, redirect, url_for
from app.main.helpers import get_transactions_by_date, get_categories, notify_budget_status, get_budgets_with_spent
from app.main.models import Budgets, Categories, Transactions

@budgets.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets_page():
    if request.method == 'POST':
        new_budget = Budgets(
            name=request.form['name'],
            monthly_limit=request.form['monthly_limit'],
            category_id=request.form['category_id'],
            user_id=current_user.user_id
        )
        # try:
        db.session.add(new_budget)
        db.session.commit()
        flash('New budget created successfully!', 'success')
        # except IntegrityError:
        #     db.session.rollback()
        #     flash('Budget name already exists. Please choose a different name.', 'error')

        return redirect(url_for('budgets.budgets_page'))

    categories_list = get_categories()

    # Calculate the start and end of the month
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Fetch budgets and their spent amounts
    budgets_list = get_budgets_with_spent(db.session, start_of_month, end_of_month)

    for budget, spent in budgets_list:
        budget.percent_spent = budget.calculate_percent_spent(spent)
        notify_budget_status(budget, category_icons)

    return render_template('show_budgets.html', page_title='Budgets', icon='fa-solid fa-coins',
                           budgets=budgets_list, categories=categories_list, category_gifs=category_gifs, category_icons=category_icons)


@budgets.route('/budgets/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    budget = Budgets.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully!', 'success')
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
            db.session.rollback()
            flash('Budget name already exists. Please choose another name.', 'warning')

    categories_list = get_categories()

    return render_template('edit_budget.html', budget=budget,
                           budgets=Budgets.query.filter_by(user_id=current_user.user_id).all(),
                           category_gifs=category_gifs, categories=categories_list)