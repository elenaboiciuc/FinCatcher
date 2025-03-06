import random
from datetime import datetime, timedelta, time
import pandas as pd
import plotly.express as px
from flask import flash
from flask_login import current_user
from sqlalchemy import or_, func
from app.extensions import db
from app.main.models import Transactions, Categories, Budgets, Goals


def get_random_quote(quotes):
    """ return a random quote from the quotes dictionary """
    return quotes[random.choice(list(quotes.keys()))]

def get_transactions():
    """ fetch all transactions for the current user """
    return Transactions.query.filter_by(user_id=current_user.user_id).all()

def get_categories():
    """ fetch all categories for the current user + default categories """
    return Categories.query.filter(
        or_(Categories.id <= 18, Categories.user_id == current_user.user_id)
    ).all()

def update_budget_progress_and_notify(user_id, category_icons):
    """fetch budgets for the current user, update their spent amount based on transactions,
       then check for notifications to flash messages """

    # calculate the start and end of the month for fetching relevant transactions
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1) # sets the day to the first day of the month
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    # moves 32 days forward to make sure that you reach the next month and then set to end of month

    # fetch transactions for the current user within the month's timeframe
    transactions = Transactions.query.filter(
        Transactions.user_id == user_id,
        Transactions.date >= start_of_month,
        Transactions.date <= end_of_month
    ).all()

    # fetch budgets for the current user
    budgets_list = Budgets.query.filter_by(user_id=user_id).all()

    # update spent amount for budgets based on transactions and check for notifications
    for budget in budgets_list:
        # calculate the total spent amount for the budget's category
        spent_amount = sum(transaction.amount for transaction in transactions
                           if transaction.category_id == budget.category_id)

        # update the budget's spent amount
        budget.spent = spent_amount
        budget.calculate_spent_percentage()  # calculate the spent percentage based on new spent value
        db.session.add(budget)

        # check for notifications based on the updated spent amount
        icon_url = category_icons[budget.category_id if budget.category_id <= 16 else 17]
        if budget.spent >= budget.monthly_limit:
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> You have reached your monthly budget limit for {budget.name}.',
                'error')
        elif (budget.spent / budget.monthly_limit) >= 0.80:
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> Great job! You have spent 80% of your budget for {budget.name}. Keep an eye on your expenses!',
                'info')

    db.session.commit()  # commit all budget updates

def update_goal_progress_and_notify(user_id, category_icons):
    """ fetch goals for the current user and update their current amount based on transactions,
        then check for notifications to flash messages """

    # fetch transactions for the current user
    transactions_all = get_transactions()

    # fetch goals for the current user
    goals_list = Goals.query.filter_by(user_id=user_id).all()

    # update current_amount for goals based on transactions and check for notifications
    for goal in goals_list:
        goal_current_amount = 0  # initialize current amount counter for each goal
        for transaction in transactions_all:
            # check if the transaction description contains the goal name
            if goal.name.lower() in transaction.description.lower() and transaction.category_id == goal.category_id:
                goal_current_amount += transaction.amount

        # update the goal's current amount
        goal.current_amount = goal_current_amount
        db.session.add(goal)

        # check for notifications based on the updated current amount
        icon_url = category_icons[goal.category_id if goal.category_id <= 16 else 17]
        if goal.current_amount >= goal.target_amount: # check if the goal is reached
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> Congratulations! You have reached your goal of {goal.name}!',
                'success')
        elif (goal.current_amount / goal.target_amount) >= 0.80: # check for 80% progress
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> Great job! You have reached 80% of your goal for {goal.name}. Keep it up!',
                'info')
        elif (goal.current_amount / goal.target_amount) >= 0.50: # check for 50% progress
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> Nice work! You have reached 50% of your goal for {goal.name}.',
                'info')

    db.session.commit()  # commit all goal updates

def get_transactions_by_date(start_date):
    """ fetch transactions for the current user starting from a specific date """
    start_of_day = datetime.combine(start_date, time.min)
    query = Transactions.query.filter(
        func.date(Transactions.date) >= func.date(start_of_day),
        Transactions.user_id == current_user.user_id
    )

    transactions = query.all()
    return transactions

def prepare_data(transactions):
    """ prepare data for plotting from transactions, returning a DataFrame """
    data = {'YearMonth': [],
            'Type': [],
            'Amount': []}
    for transaction in transactions:
        data['YearMonth'].append(transaction.date.strftime('%Y-%m')) # format date as Year-Month
        data['Type'].append(transaction.type)
        data['Amount'].append(transaction.amount)
    return pd.DataFrame(data) # return as a DataFrame

def get_current_balance(transactions):
    """ calculate the current balance based on income and expenses """
    current_balance = 0  # initialize balance
    for transaction in transactions:
        if transaction.type == 'income':
            current_balance += transaction.amount  # add income
        elif transaction.type == 'expense':
            current_balance -= transaction.amount  # subtract expenses
    return round(current_balance, 2)  # return the current balance rounded to 2 decimal places

def create_bar_chart(df):
    """ create a bar chart comparing monthly expenses and income """
    df['YearMonth'] = pd.to_datetime(df['YearMonth'], format='%Y-%m') # convert to datetime
    df = df.groupby(['YearMonth', 'Type']).sum().reset_index() # group by YearMonth and Type
    df['Month'] = df['YearMonth'].dt.strftime('%B') # extract month name for display
    return px.bar(
        df, x='Month', y='Amount', color='Type',
        title='Last 6 Months Expenses vs Income',  # set title
        color_discrete_map={'income': '#4e598c', 'expense': '#db6c79'}, # set colors
        barmode='group').to_html(full_html=False) # return HTML representation of the chart

def create_pie_chart(transactions):
    """ create a pie chart showing the top 5 categories for expenses """
    data = {'Category': [],
            'Amount': []}  # initialize data storage
    for t in transactions:
        if t.type == 'expense' and t.category_id != 10: # ignore category ID 10 (savings)
            data['Category'].append(t.category.name) # append category name
            data['Amount'].append(t.amount) # append amount
    df = pd.DataFrame(data).groupby('Category').sum().reset_index().nlargest(5, 'Amount') # create DataFrame and find top 5
    return px.pie(df, values='Amount', names='Category',
                  title='Top 5 Category Distribution for Expenses', # set title
                  color_discrete_sequence=px.colors.sequential.Sunset_r
                  ).to_html(full_html=False) # return HTML representation of the pie chart

def create_donut_chart(transactions, title):
    """ create a donut chart to visualize income and expense distributions """
    # prepare a DataFrame for transactions by filtering Savings
    df = (
        pd.DataFrame({
            'Type': [t.type for t in transactions if t.category_id != 10], # get transaction types
            'Amount': [t.amount for t in transactions if t.category_id != 10] # get transaction amounts
        }).groupby('Type').sum().reset_index() # group by Type and sum amounts
    )

    # create the donut chart
    donut_fig = px.pie(
        df,
        values='Amount',
        names='Type',
        title=title,
        hole=0.5, # create a donut chart with a hole
        color='Type',
        color_discrete_map={'income': '#CCDF92', 'expense': '#DE3163'}, # set colors
        width=300,
        height=250
    )
    # set layout properties
    donut_fig.update_layout(
        title_font_size=14,
        legend=dict(font=dict(size=10))
    )

    return donut_fig.to_html(full_html=False) # return HTML representation of the donut chart

def create_line_chart(transactions):
    """ create a line chart to visualize savings growth """
    # filter transactions for category_id = 10 (Savings)
    filtered_transactions = [t for t in transactions if t.category_id == 10]

    # use prepare_data to get the DataFrame for the filtered transactions
    df = prepare_data(filtered_transactions)

    # group by YearMonth to get the total amount for that month
    monthly_totals = df.groupby('YearMonth')['Amount'].sum().reset_index()

    # create the line chart for monthly totals
    line_fig = px.line(
        monthly_totals,
        x='YearMonth',
        y='Amount',
        title='Savings Growth',
        markers=True, # show markers for each data point
        line_shape='spline' # use spline for smooth curves
    ).update_layout(
        xaxis_title='Month',
        yaxis_title='Savings',
        title_font_size=15
    )

    # set a single color for the line
    line_fig.update_traces(line=dict(color='#48bfe3'))

    return line_fig.to_html(full_html=False) # return HTML representation of the line chart

