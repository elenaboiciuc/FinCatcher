from flask import render_template
from flask_login import login_required, current_user
from app.main import main
from app.main.models import Transactions, Budgets, Goals
from datetime import datetime
from dateutil.relativedelta import relativedelta
from app.extensions import financial_quotes, category_icons
from .helpers import (get_transactions_by_date, prepare_data, create_bar_chart,
    create_pie_chart, create_donut_chart, create_line_chart,
    get_random_quote, get_current_balance, get_transactions,
    update_goal_progress_and_notify, update_budget_progress_and_notify
)

# route for the home page
@main.route('/')
def home():
    return render_template('layout.html', page_title='Home', icon='fas fa-home')

# route for the overview page, requires user to be logged in
@main.route('/overview')
@login_required
def overview():
    # get a random financial quote
    random_quote = get_random_quote(financial_quotes)
    current_date = datetime.now() # get the current date and time

    # calculate the start and end of the previous month
    first_day_last_month = (current_date.replace(day=1) - relativedelta(months=1)).replace(day=1) # first day of last month
    last_day_last_month = current_date.replace(day=1) - relativedelta(days=1) # last day of last month

    # fetch all transactions for the current user
    transactions_all = get_transactions() # get all transactions for the user
    transactions_current_month = get_transactions_by_date(current_date.replace(day=1)) # get transactions for the current month
    transactions_last_month = Transactions.query.filter(
        Transactions.date >= first_day_last_month,  # filter for transactions from the start of last month
        Transactions.date <= last_day_last_month, # to the end of last month
        Transactions.user_id == current_user.user_id # ensure transactions belong to the current user
    ).all()
    start_date_six_months_ago = (current_date.replace(day=1) - relativedelta(months=5))
    transactions_six_months_ago = get_transactions_by_date(start_date_six_months_ago) # get transactions from six months ago

    # calculate the current balance based on the current month's transactions
    current_balance = get_current_balance(transactions_current_month)


    # generate graphs
    bar_graph = create_bar_chart(prepare_data(transactions_six_months_ago)) # create a bar chart for the last six months of data
    pie_graph = create_pie_chart(transactions_all) # create a pie chart for the user's transactions
    last_month_donut_graph = create_donut_chart(transactions_last_month, 'Last Month') # create a donut chart for last month's transactions
    current_month_donut_graph = create_donut_chart(transactions_current_month, 'This Month') # create a donut chart for the current month's transactions
    savings_line_chart = create_line_chart(get_transactions_by_date(datetime(current_date.year, 1, 1))) # create a line chart for savings growth

    # update current amounts and check notifications for all goals and budgets
    update_goal_progress_and_notify(current_user.user_id, category_icons) # update goal progress and notify user if necessary
    update_budget_progress_and_notify(current_user.user_id, category_icons) # update budget progress and notify user if necessary

    # render the overview page with all calculated data and graphs
    return render_template('overview.html', page_title='Overview', icon='fas fa-home', now=current_date,
                           random_quote=random_quote, current_balance=current_balance,
                           bar_graph=bar_graph, pie_graph=pie_graph,
                           last_month_donut_graph=last_month_donut_graph,
                           current_month_donut_graph=current_month_donut_graph,
                           savings_line_chart=savings_line_chart,
                           category_gifs=category_icons) # pass all data to the template