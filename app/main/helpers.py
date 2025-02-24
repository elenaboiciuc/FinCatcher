import random
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from flask import flash
from flask_login import current_user
from sqlalchemy import or_
from app.extensions import db
from app.main.models import Transactions, Categories, Budgets, Goals


def get_random_quote(quotes):
    return quotes[random.choice(list(quotes.keys()))]

def get_budgets():
    return Budgets.query.filter_by(user_id=current_user.user_id).all()

def get_transactions():
    return Transactions.query.filter_by(user_id=current_user.user_id).all()

def get_categories():
    """Fetch all relevant categories for the current user."""
    return Categories.query.filter(
        or_(Categories.id <= 16, Categories.user_id == current_user.user_id)
    ).all()

def update_budget_progress_and_notify(user_id, category_icons):
    """fetch budgets for the current user, update their spent amount based on transactions,
    then check for notifications to flash messages if certain thresholds are reached."""

    # Calculate the start and end of the month for fetching relevant transactions
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # Fetch transactions for the current user within the month's timeframe
    transactions = Transactions.query.filter(
        Transactions.user_id == user_id,
        Transactions.date >= start_of_month,
        Transactions.date <= end_of_month
    ).all()

    # Fetch budgets for the current user
    budgets_list = Budgets.query.filter_by(user_id=user_id).all()

    # Update spent amount for budgets based on transactions and check for notifications
    for budget in budgets_list:
        spent_amount = sum(transaction.amount for transaction in transactions
                           if transaction.category_id == budget.category_id)

        # Update the budget's spent amount
        budget.spent = spent_amount
        budget.calculate_spent_percentage()  # Calculate the spent percentage based on new spent value
        db.session.add(budget)

        # Check for notifications based on the updated spent amount
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
    """fetch goals for the current user and update their current amount based on transactions,
    then check for notifications to flash messages if certain thresholds are reached."""

    # Fetch transactions for the current user
    transactions_all = Transactions.query.filter(Transactions.user_id == user_id).all()

    # Fetch goals for the current user
    goals_list = Goals.query.filter_by(user_id=user_id).all()

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
        icon_url = category_icons[goal.category_id if goal.category_id <= 16 else 17]
        if goal.current_amount >= goal.target_amount:
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> Congratulations! You have reached your goal of {goal.name}!',
                'success')
        elif (goal.current_amount / goal.target_amount) >= 0.80:
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> Great job! You have reached 80% of your goal for {goal.name}. Keep it up!',
                'info')
        elif (goal.current_amount / goal.target_amount) >= 0.50:
            flash(
                f'<img src="{icon_url}" alt="Category gif" style="width:24px; height:24px;"> Nice work! You have reached 50% of your goal for {goal.name}.',
                'info')

    db.session.commit()  # Commit all goal updates

def get_transactions_by_date(start_date):
    return Transactions.query.filter(Transactions.date >= start_date, Transactions.user_id == current_user.user_id)

def prepare_data(transactions):
    data = {'YearMonth': [],
            'Type': [],
            'Amount': []}
    for transaction in transactions:
        data['YearMonth'].append(transaction.date.strftime('%Y-%m'))
        data['Type'].append(transaction.type)
        data['Amount'].append(transaction.amount)
    return pd.DataFrame(data)

def get_current_balance(transactions):
    current_balance = 0
    for transaction in transactions:
        if transaction.type == 'income':
            current_balance += transaction.amount
        elif transaction.type == 'expense':
            current_balance -= transaction.amount
    return current_balance

def create_bar_chart(df):
    df['YearMonth'] = pd.to_datetime(df['YearMonth'], format='%Y-%m')
    df = df.groupby(['YearMonth', 'Type']).sum().reset_index()
    df['Month'] = df['YearMonth'].dt.strftime('%B')
    return px.bar(
        df, x='Month', y='Amount', color='Type',
        title='Last 6 Months Expenses vs Income',
        color_discrete_map={'income': '#4e598c', 'expense': '#db6c79'},
        barmode='group').to_html(full_html=False)

def create_pie_chart(transactions):
    data = {'Category': [],
            'Amount': []}
    for t in transactions:
        if t.type == 'expense' and t.category_id != 10:
            data['Category'].append(t.category.name)
            data['Amount'].append(t.amount)
    df = pd.DataFrame(data).groupby('Category').sum().reset_index().nlargest(5, 'Amount')
    return px.pie(df, values='Amount', names='Category',
                  title='Top 5 Category Distribution for Expenses',
                  color_discrete_sequence=px.colors.sequential.Sunset_r
                  ).to_html(full_html=False)

def create_donut_chart(transactions, title):
    # Prepare a DataFrame for transactions and group by 'Type'
    df = (
        pd.DataFrame({
            'Type': [t.type for t in transactions if t.category_id != 10],
            'Amount': [t.amount for t in transactions if t.category_id != 10]
        }).groupby('Type').sum().reset_index()
    )

    # Create the donut chart
    donut_fig = px.pie(
        df,
        values='Amount',
        names='Type',
        title=title,
        hole=0.5,
        color='Type',
        color_discrete_map={'income': '#CCDF92', 'expense': '#DE3163'},
        width=300,
        height=250
    )
    # Set layout properties
    donut_fig.update_layout(
        title_font_size=14,
        legend=dict(font=dict(size=10))
    )

    return donut_fig.to_html(full_html=False)

def create_line_chart(transactions):
    # Filter transactions for category_id = 10 (Savings)
    filtered_transactions = [t for t in transactions if t.category_id == 10]

    # Use prepare_data to get the DataFrame for the filtered transactions
    df = prepare_data(filtered_transactions)

    # Group by YearMonth to get the total amount for that month
    monthly_totals = df.groupby('YearMonth')['Amount'].sum().reset_index()

    # Create the line chart for monthly totals
    line_fig = px.line(
        monthly_totals,
        x='YearMonth',
        y='Amount',
        title='Savings Growth',
        markers=True,
        line_shape='spline'
    ).update_layout(
        xaxis_title='Month',
        yaxis_title='Savings',
        title_font_size=15
    )

    # Set a single color
    line_fig.update_traces(line=dict(color='#48bfe3'))

    return line_fig.to_html(full_html=False)

