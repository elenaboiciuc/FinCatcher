from flask import render_template
from app.main import main
from app.main.models import Transactions, Categories
import pandas as pd
import plotly.express as px
from datetime import datetime


@main.route('/')
def home():
    return render_template('layout.html', page_title='Home', icon='fas fa-home')


from flask import render_template
from app.main import main
from app.main.models import Transactions, Categories
import pandas as pd
import plotly.express as px

from flask import render_template
from app.main import main
from app.main.models import Transactions, Categories
import pandas as pd
import plotly.express as px


@main.route('/overview')
def overview():
    try:
        # Query the database to get actual transactions data
        transactions = Transactions.query.all()
        if not transactions:
            raise ValueError("No transactions found")

        # Debug: Log number of transactions fetched
        print(f"Fetched {len(transactions)} transactions")

        # Create a DataFrame for expenses and income
        data = {
            'Month': [],
            'Type': [],
            'Amount': []
        }

        for transaction in transactions:
            try:
                # Ensure the date is properly formatted
                month = transaction.date.strftime('%B')
                amount = transaction.amount
                trans_type = transaction.type  # Type of transaction (expense or income)
                data['Month'].append(month)
                data['Type'].append(trans_type)
                data['Amount'].append(amount)
            except ValueError as e:
                print(f"Error parsing date for transaction {transaction.id}: {e}")

        df = pd.DataFrame(data)
        print("DataFrame:")
        print(df.head())  # Debug: Print the head of the DataFrame

        # Aggregate the data by month and type
        df_agg = df.groupby(['Month', 'Type']).sum().reset_index()
        print("Aggregated DataFrame:")
        print(df_agg.head())  # Debug: Print the head of the aggregated DataFrame

        # Create Plotly figure for the bar chart
        bar_fig = px.bar(df_agg, x='Month', y='Amount', color='Type', title='Monthly Expenses vs Income',
                         barmode='group')
        bar_graph = bar_fig.to_html(full_html=False)

        # Create a DataFrame for the pie chart (Category Distribution)
        pie_data = {
            'Category': [],
            'Amount': []
        }

        for transaction in transactions:
            if transaction.type == 'expense':  # Include only expenses
                try:
                    category_name = transaction.category.name
                    amount = transaction.amount
                    pie_data['Category'].append(category_name)
                    pie_data['Amount'].append(amount)
                except Exception as e:
                    print(f"Error processing transaction {transaction.id}: {e}")

        pie_df = pd.DataFrame(pie_data)
        print("Pie DataFrame:")
        print(pie_df.head())  # Debug: Print the head of the pie DataFrame

        # Aggregate the data by category
        pie_df_agg = pie_df.groupby('Category').sum().reset_index()
        print("Aggregated Pie DataFrame:")
        print(pie_df_agg.head())  # Debug: Print the head of the aggregated pie DataFrame

        # Sort by amount and select top 5 categories
        top_5_pie_df_agg = pie_df_agg.nlargest(5, 'Amount')
        print("Top 5 Aggregated Pie DataFrame:")
        print(top_5_pie_df_agg.head())  # Debug: Print the head of the top 5 aggregated pie DataFrame

        # Create Plotly figure for the pie chart
        pie_fig = px.pie(top_5_pie_df_agg, values='Amount', names='Category', title='Top 5 Category Distribution')
        pie_graph = pie_fig.to_html(full_html=False)

        return render_template('overview.html', page_title='Overview', icon='fas fa-home', bar_graph=bar_graph,
                               pie_graph=pie_graph)

    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return render_template('overview.html', page_title='Overview', icon='fas fa-home', bar_graph='', pie_graph='')