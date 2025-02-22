from flask import render_template, request, redirect, url_for, flash
from app.transactions import transactions
from app.extensions import db, category_icons
from app.main.models import Transactions, Categories
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Route for displaying and managing transactions
@transactions.route('/transactions', methods=['GET', 'POST'])
def transactions_page():
    if request.method == 'POST':
        # Create a new transaction from form data
        new_transaction = Transactions(
            date=date.fromisoformat(request.form['date']),
            amount=request.form['amount'],
            category_id=request.form['category_id'],
            description=request.form['description'],
            type=request.form['type']
        )
        # Add and commit the new transaction to the database
        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions.transactions_page'))

    # Logic for filtering transactions by month
    today = date.today()
    filter_month = request.args.get('filter_month', f'{today.year}-{today.month:02}')
    change_month = request.args.get('change_month', 0, type=int)

    # Calculate date for the month to be filtered
    year, month = map(int, filter_month.split('-'))
    new_date = date(year, month, 1) + relativedelta(months=change_month)
    filter_month = f'{new_date.year}-{new_date.month:02}'

    # Retrieve transactions based on filters applied
    query = Transactions.query.join(Categories)
    query = apply_filters(query, filter_month, request.args.get('filter_category'), request.args.get('filter_type'))

    # Render the transactions page template with appropriate context
    return render_template(
        'show_transactions.html',
        transactions=query.all(),
        categories=Categories.query.all(),
        category_icons=category_icons,
        page_title='Transactions',
        icon='fas fa-credit-card',
        current_month=new_date.month,
        current_year=new_date.year,
        current_month_name=new_date.strftime('%B'),
        filter_month=filter_month
    )

# Function to apply filters to the transactions query
def apply_filters(query, filter_month, filter_category, filter_type):
    if filter_month:
        # Determine start and end dates from the filter month
        year, month = map(int, filter_month.split('-'))
        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
        # Filter transactions by the determined date range
        query = query.filter(Transactions.date >= start_date, Transactions.date <= end_date).order_by(Transactions.date.asc())
    if filter_category:
        # Filter transactions if a specific category is selected
        query = query.filter(Transactions.category_id == filter_category)
    if filter_type:
        # Filter transactions if a specific type is selected
        query = query.filter(Transactions.type == filter_type)
    return query

# Route for deleting a transaction
@transactions.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    # Delete the transaction identified by id
    transaction = Transactions.query.get_or_404(id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully.', 'success')
    else:
        flash('Transaction does not exist.', 'error')
    return redirect(url_for('transactions.transactions_page'))

# Route for editing a transaction
@transactions.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transactions.query.get_or_404(id)
    if request.method == 'POST':
        # Update the transaction with form data
        transaction.date = date.fromisoformat(request.form['date'])
        transaction.amount = request.form['amount']
        transaction.category_id = request.form['category_id']
        transaction.description = request.form['description']
        transaction.type = request.form['type']
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.transactions_page'))
    # Render the edit_transaction template with transaction details
    return render_template('edit_transaction.html', transaction=transaction, categories=Categories.query.all(), category_icons=category_icons)