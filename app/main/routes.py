from flask import render_template
from flask_login import login_required, current_user
from app.main import main
from app.main.models import Transactions, Budgets, Goals
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.extensions import financial_quotes, db, category_icons
from .helpers import (
    get_transactions_by_date, prepare_data, create_bar_chart,
    create_pie_chart, create_donut_chart, create_line_chart,
    get_random_quote, get_current_balance, get_categories,
    update_goal_progress_and_notify, update_budget_progress_and_notify, get_transactions
)


@main.route('/')
def home():
    return render_template('layout.html', page_title='Home', icon='fas fa-home')


@main.route('/overview')
@login_required
def overview():
    random_quote = get_random_quote(financial_quotes)
    current_date = datetime.now()

    # Calculate the start and end of last month
    first_day_last_month = (current_date.replace(day=1) - relativedelta(months=1)).replace(day=1)
    last_day_last_month = current_date.replace(day=1) - relativedelta(days=1)

    # Fetch transactions for the current user
    transactions_all = get_transactions()
    transactions_current_month = get_transactions_by_date(current_date.replace(day=1))
    transactions_last_month = Transactions.query.filter(
        Transactions.date >= first_day_last_month,
        Transactions.date <= last_day_last_month,
        Transactions.user_id == current_user.user_id
    ).all()
    transactions_six_months_ago = get_transactions_by_date(current_date - relativedelta(months=5))

    # Financial calculations
    current_balance = get_current_balance(transactions_current_month)

    # Graphs
    bar_graph = create_bar_chart(prepare_data(transactions_six_months_ago))
    pie_graph = create_pie_chart(transactions_all)
    last_month_donut_graph = create_donut_chart(transactions_last_month, 'Last Month')
    current_month_donut_graph = create_donut_chart(transactions_current_month, 'This Month')
    savings_line_chart = create_line_chart(get_transactions_by_date(datetime(current_date.year - 1, 1, 1)))

    # Update current amounts and check notifications for all goals and budgets
    update_goal_progress_and_notify(current_user.user_id, category_icons)
    update_budget_progress_and_notify(current_user.user_id, category_icons)

    return render_template('overview.html', page_title='Overview', icon='fas fa-home', now=current_date,
                           random_quote=random_quote, current_balance=current_balance,
                           bar_graph=bar_graph, pie_graph=pie_graph,
                           last_month_donut_graph=last_month_donut_graph,
                           current_month_donut_graph=current_month_donut_graph,
                           savings_line_chart=savings_line_chart,
                           category_gifs=category_icons)