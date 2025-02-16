from flask import render_template, request, redirect, url_for
from app.transactions import transactions
from app.extensions import db, category_icons
from app.main.models import Transactions, Categories
from datetime import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta

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

    # Get the current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Check if a month change is requested
    change_month = request.args.get('change_month', 0, type=int)

    if filter_month:
        try:
            year, month = map(int, filter_month.split('-'))
        except ValueError:
            year, month = current_year, current_month
    else:
        year, month = current_year, current_month

    # Adjust the month and year based on the change_month value using relative delta
    new_date = datetime(year, month, 1) + relativedelta(months=change_month)
    new_month = new_date.month
    new_year = new_date.year

    # Format the filter_month
    filter_month = f'{new_year}-{new_month:02}'
    current_month_name = new_date.strftime('%B')

    # Base query with join, ensuring it returns model instances
    query = Transactions.query.join(Categories).filter(Transactions.category_id == Categories.id)

    # Apply filters
    if filter_month:
        start_date = datetime.strptime(filter_month + '-01', '%Y-%m-%d')
        last_day = monthrange(new_year, new_month)[1]
        end_date = datetime.strptime(f'{filter_month}-{last_day}', '%Y-%m-%d')
        query = query.filter(Transactions.date >= start_date, Transactions.date <= end_date)
    if filter_category:
        query = query.filter(Transactions.category_id == filter_category)
    if filter_type:
        query = query.filter(Transactions.type == filter_type)

    transactions_list = query.all()
    categories = Categories.query.all()

    return render_template(
        'show_transactions.html',
        transactions=transactions_list,
        categories=categories,
        category_icons=category_icons,
        page_title='Transactions',
        icon='fas fa-credit-card',
        current_month=new_month,
        current_year=new_year,
        current_month_name=current_month_name,
        filter_month=filter_month
    )

# Route for delete actions
@transactions.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = Transactions.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('transactions.transactions_page'))

# Route for edit actions
@transactions.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transactions.query.get_or_404(id)
    categories = Categories.query.all()

    if request.method == 'POST':
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        transaction.amount = request.form['amount']
        transaction.category_id = request.form['category_id']
        transaction.description = request.form['description']
        transaction.type = request.form['type']
        db.session.commit()
        return redirect(url_for('transactions.transactions_page'))

    return render_template('edit_transaction.html', transaction=transaction, categories=categories, category_icons=category_icons)
