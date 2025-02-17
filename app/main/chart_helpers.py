import random
import pandas as pd
import plotly.express as px
from app.main.models import Transactions

def get_random_quote(quotes):
    return quotes[random.choice(list(quotes.keys()))]

def get_transactions_by_date(start_date):
    return Transactions.query.filter(Transactions.date >= start_date).all()

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
        color_discrete_map={'income': '#659157', 'expense': '#db6c79'},
        barmode='group').to_html(full_html=False)

def create_pie_chart(transactions):
    data = {'Category': [],
            'Amount': []}
    for t in transactions:
        if t.type == 'expense':
            data['Category'].append(t.category.name)
            data['Amount'].append(t.amount)
    df = pd.DataFrame(data).groupby('Category').sum().reset_index().nlargest(5, 'Amount')
    return px.pie(df, values='Amount', names='Category',
                  title='Top 5 Category Distribution for Expenses',
                  color_discrete_sequence=px.colors.sequential.Sunset_r
                  ).to_html(full_html=False)


def create_donut_chart(transactions, title):
    # Prepare a DataFrame for transactions
    df = pd.DataFrame({
        'Type': [t.type for t in transactions if t.category_id != 10],
        'Amount': [t.amount for t in transactions if t.category_id != 10]
    })
    df = df.groupby(['Type']).sum().reset_index()

    # Create the donut chart with explicit color mapping
    donut_fig = px.pie(
        df,
        values='Amount',
        names='Type',
        title=title,
        hole=0.5,
        color='Type',  # Set colors based on the Type column
        color_discrete_map={'income': '#CCDF92', 'expense': '#DE3163'},  # Map income to green and expense to red
        width=300,
        height=250
    ).update_traces(textinfo='none')  # Do not display any text on the chart itself

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