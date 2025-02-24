import random
import pandas as pd
import plotly.express as px
from flask import flash
from flask_login import current_user
from sqlalchemy import or_, func

from app.main.models import Transactions, Categories, Budgets


def get_random_quote(quotes):
    return quotes[random.choice(list(quotes.keys()))]

def get_categories():
    """Fetch all relevant categories for the current user."""
    return Categories.query.filter(
        or_(Categories.id <= 16, Categories.user_id == current_user.user_id)
    ).all()

def check_goal_notifications(goal,category_icons):
    gif_url = category_icons[goal.category_id if goal.category_id <= 16 else 17]

    """Check the progress of a goal and send notifications if certain thresholds are reached."""
    if goal.current_amount >= goal.target_amount:
        flash(f'<img src="{gif_url}" alt="Category gif" style="width:24px; height:24px;"> Congratulations! You have reached your goal of {goal.name}!', 'success')
    elif (goal.current_amount / goal.target_amount) >= 0.80:
        flash(f'<img src="{gif_url}" alt="Category gif" style="width:24px; height:24px;"> Great job! You have reached 80% of your goal for {goal.name}. Keep it up!', 'info')
    elif (goal.current_amount / goal.target_amount) >= 0.50:
        flash(f'<img src="{gif_url}" alt="Category gif" style="width:24px; height:24px;"> Nice work! You have reached 50% of your goal for {goal.name}.', 'info')

def get_budgets_with_spent(session, start_date=None, end_date=None):
    """fetch budgets along with spent amounts for the current user within the specified date range"""

    # set filters for the date range
    date_filter = (Transactions.date >= start_date) & (
                Transactions.date <= end_date) if start_date and end_date else True

    budgets_list = (session.query(Budgets, func.coalesce(func.sum(Transactions.amount), 0).label('spent'))
                    .outerjoin(Transactions, (Budgets.category_id == Transactions.category_id) &
                               (Transactions.user_id == current_user.user_id) & date_filter)
                    .filter(Budgets.user_id == current_user.user_id)
                    .group_by(Budgets)
                    .all())

    return budgets_list

def notify_budget_status(budget, category_icons):
    """ send notifications based on the budget spent percentage """
    gif_url = category_icons[budget.category_id if budget.category_id <= 16 else 17]

    if budget.percent_spent >= 100:
        flash(f'<img src="{gif_url}" alt="Category gif" style="width:24px; height:24px;"> You\'ve reached the limit for the budget "{budget.name}". Please review.', 'error')
    elif budget.percent_spent >= 80:
        flash(f'<img src="{gif_url}" alt="Category gif" style="width:24px; height:24px;"> You have spent {budget.percent_spent:.2f}% of your "{budget.name}" budget.', 'warning')
    elif budget.percent_spent >= 50:
        flash(f'<img src="{gif_url}" alt="Category gif" style="width:24px; height:24px;"> You have spent {budget.percent_spent:.2f}% of your "{budget.name}" budget.', 'warning')

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

