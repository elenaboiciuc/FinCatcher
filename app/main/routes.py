from flask import render_template
from flask_login import login_required, current_user
from app.main import main
from app.main.models import Transactions, Budgets, Goals
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.extensions import financial_quotes, db, category_icons
from .helpers import (
    get_transactions_by_date, prepare_data,
    create_bar_chart, create_pie_chart, create_donut_chart, create_line_chart, get_random_quote, get_current_balance,
    notify_budget_status, get_budgets_with_spent, check_goal_notifications, get_categories
)


@main.route('/')
def home():
    return render_template('layout.html', page_title='Home', icon='fas fa-home')

@main.route('/overview')
@login_required
def overview():
    random_quote = get_random_quote(financial_quotes)
    current_date = datetime.now()

    # Calculate the start of last month and the end of last month
    first_day_last_month = (current_date.replace(day=1) - relativedelta(months=1)).replace(day=1)
    last_day_last_month = current_date.replace(day=1) - relativedelta(days=1)

    # Fetch transactions for different periods and filter by user_id
    transactions_all = Transactions.query.filter(Transactions.user_id == current_user.user_id).all()
    transactions_six_months_ago = get_transactions_by_date(current_date - relativedelta(months=6))
    transactions_last_month = Transactions.query.filter(
        Transactions.date >= first_day_last_month,
        Transactions.date <= last_day_last_month,
        Transactions.user_id == current_user.user_id
    ).all()  # Update this line
    transactions_current_month = get_transactions_by_date(current_date.replace(day=1))
    transactions_current_year = get_transactions_by_date(datetime(current_date.year - 1, 1, 1)) #NOTE -1 just for testing

    current_balance = get_current_balance(transactions_current_month)
    bar_graph = create_bar_chart(prepare_data(transactions_six_months_ago))
    pie_graph = create_pie_chart(transactions_all)
    last_month_donut_graph = create_donut_chart(transactions_last_month, 'Last Month')
    current_month_donut_graph = create_donut_chart(transactions_current_month, 'This Month')
    savings_line_chart = create_line_chart(transactions_current_year)

    # Calculate the start and end of the month
    start_of_month = current_date.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)


    # Fetch budgets and their spent amounts
    budgets_list = get_budgets_with_spent(db.session, start_of_month, end_of_month)

    # Fetch transactions for the current user
    transactions_all = Transactions.query.filter(Transactions.user_id == current_user.user_id).all()

    categories_list = get_categories()
    for budget, spent in budgets_list:
        budget.percent_spent = budget.calculate_percent_spent(spent)
        notify_budget_status(budget, category_icons)

    # Fetch goals for the current user
    goals_list = Goals.query.filter_by(user_id=current_user.user_id).all()

    # Update current_amount for goals based on transactions and check for notifications
    for goal in goals_list:
        goal_current_amount = 0  # Initialize current amount counter for each goal
        for transaction in transactions_all:
            if goal.name.lower() in transaction.description.lower() and transaction.category_id == goal.category_id:
                goal_current_amount += transaction.amount

        # Update the goal's current amount
        goal.current_amount = goal_current_amount
        db.session.add(goal)  # Prepare to update this goal in the database

        # Check for notifications based on the updated current amount
        check_goal_notifications(goal, category_icons)



    return render_template('overview.html', page_title='Overview', icon='fas fa-home', now=current_date,
                           random_quote=random_quote, current_balance=current_balance,
                           bar_graph=bar_graph, pie_graph=pie_graph,
                           last_month_donut_graph=last_month_donut_graph,
                           current_month_donut_graph=current_month_donut_graph,
                           savings_line_chart = savings_line_chart,
                           category_gifs=category_icons)