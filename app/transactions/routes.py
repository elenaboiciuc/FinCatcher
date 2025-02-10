from flask import render_template, request, session
from app.transactions import transactions
from app.extensions import db
from app.main.models import Transactions, Categories
from datetime import datetime

@transactions.route('/transactions', methods=['GET', 'POST'])
def transactions_page():
    message = ""
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        amount = request.form['amount']
        category_id = request.form['category_id']
        description = request.form['description']
        type = request.form['type']
        message = f'A new transaction was added on {date} with category id {category_id}'
        print(message)

        transaction = Transactions(
            date=date,
            amount=amount,
            category_id=category_id,
            description=description,
            type=type
        )

        db.session.add(transaction)
        db.session.commit()

    # Handle filtering
    filter_month = request.args.get('filter_month')
    filter_category = request.args.get('filter_category')
    filter_type = request.args.get('filter_type')
    filter_amount_comparison = request.args.get('filter_amount_comparison')
    filter_amount = request.args.get('filter_amount')

    # Base query
    query = db.session.query(Transactions, Categories).join(Categories, Transactions.category_id == Categories.id)

    # Apply filters
    if filter_month:
        start_date = datetime.strptime(filter_month + '-01', '%Y-%m-%d')
        end_date = datetime.strptime(filter_month + '-31', '%Y-%m-%d')
        query = query.filter(Transactions.date >= start_date, Transactions.date <= end_date)
    if filter_category:
        query = query.filter(Transactions.category_id == filter_category)
    if filter_type:
        query = query.filter(Transactions.type == filter_type)
    if filter_amount:
        if filter_amount_comparison == 'greater':
            query = query.filter(Transactions.amount > float(filter_amount))
        elif filter_amount_comparison == 'less':
            query = query.filter(Transactions.amount < float(filter_amount))

    transactions_list = query.all()
    categories = Categories.query.all()

    return render_template('show_transactions.html', transactions=transactions_list, categories=categories)
