from flask import render_template
from app.main import main
from app.main.models import Transactions
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .chart_helpers import (
    get_transactions_by_date, prepare_data,
    create_bar_chart, create_pie_chart, create_donut_chart
)

@main.route('/')
def home():
    return render_template('layout.html', page_title='Home', icon='fas fa-home')

@main.route('/overview')
def overview():
    current_date = datetime.now()
    transactions_all = Transactions.query.all()
    transactions_six_months_ago = get_transactions_by_date(current_date - relativedelta(months=6))
    transactions_last_month = get_transactions_by_date(current_date - relativedelta(months=1))
    transactions_current_month = get_transactions_by_date(current_date.replace(day=1))

    bar_graph = create_bar_chart(prepare_data(transactions_six_months_ago))
    pie_graph = create_pie_chart(transactions_all)
    last_month_donut_graph = create_donut_chart(transactions_last_month, 'Last Month')
    current_month_donut_graph = create_donut_chart(transactions_current_month, 'This Month')

    return render_template('overview.html', page_title='Overview', icon='fas fa-home',
                           bar_graph=bar_graph, pie_graph=pie_graph,
                           last_month_donut_graph=last_month_donut_graph,
                           current_month_donut_graph=current_month_donut_graph)