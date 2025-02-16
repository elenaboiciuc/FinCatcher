import pandas as pd
import plotly.express as px
from app.main.models import Transactions


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

def create_bar_chart(df):
    df['YearMonth'] = pd.to_datetime(df['YearMonth'], format='%Y-%m')
    df = df.groupby(['YearMonth', 'Type']).sum().reset_index()
    df['Month'] = df['YearMonth'].dt.strftime('%B')
    return px.bar(
        df, x='Month', y='Amount', color='Type',
        title='Last 6 Months Expenses vs Income',
        color_discrete_map={'income': 'rgb(0, 204, 153)', 'expense': 'rgb(242, 85, 59)'},
        barmode='group').to_html(full_html=False)

def create_pie_chart(transactions):
    data = {'Category': [],
            'Amount': []}
    for t in transactions:
        if t.type == 'expense':
            data['Category'].append(t.category.name)
            data['Amount'].append(t.amount)
    df = pd.DataFrame(data).groupby('Category').sum().reset_index().nlargest(5, 'Amount')
    return px.pie(df, values='Amount', names='Category', title='Top 5 Category Distribution for Expenses').to_html(full_html=False)


def create_donut_chart(transactions, title):
    df = pd.DataFrame({'Type': [t.type for t in transactions], 'Amount': [t.amount for t in transactions]})
    df = df.groupby(['Type']).sum().reset_index()

    # Specify your own colors for income and expense
    color_discrete_sequence = ['#DE3163', '#CCDF92']  # Cerise for expense, Light Green for income

    # Calculate percentages for the labels
    df['Percentage'] = (df['Amount'] / df['Amount'].sum()) * 100
    df['Label'] = df['Type'] + ': ' + df['Percentage'].round(1).astype(str) + '%'

    # Create the donut chart
    donut_fig = px.pie(
        df, values='Amount', names='Label', title=title,
        hole=0.5,
        color_discrete_sequence=color_discrete_sequence,
        width=300, height=250
    ).update_traces(textinfo='none')  # Do not display any text on the chart itself

    donut_fig.update_layout(
        title_font_size=14,
        legend=dict(font=dict(size=10))
    )

    return donut_fig.to_html(full_html=False)