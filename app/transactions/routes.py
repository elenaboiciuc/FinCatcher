from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.transactions import transactions
from app.extensions import db, category_icons
from app.main.models import Transactions, Categories
from datetime import date
from dateutil.relativedelta import relativedelta

def apply_filters(query, filter_month, filter_category, filter_type):
    """ apply filters to the transaction query based on month, category, and type """
    if filter_month: # if a month filter is provided
        year, month = map(int, filter_month.split('-')) # parse year and month
        # calculate the start and end dates for the filter
        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
        # filter transactions by the calculated date range
        query = query.filter(Transactions.date >= start_date, Transactions.date <= end_date).order_by(Transactions.date.asc())
    if filter_category: # if a category filter is provided
        query = query.filter(Transactions.category_id == filter_category) # filter by the specified category
    if filter_type: # if a type filter is provided
        query = query.filter(Transactions.type == filter_type) # filter by the specified type
    return query # return the filtered query object

# route for the transactions page, allowing both GET and POST methods
@transactions.route('/transactions', methods=['GET', 'POST'])
@login_required # protects this route to ensure only logged-in users can access it
def transactions_page():
    # handle transaction creation when the form is submitted (POST request)
    if request.method == 'POST':
        # create a new transaction object from form data
        new_transaction = Transactions(
            date=date.fromisoformat(request.form['date']), # parse the date from the form
            amount=request.form['amount'],
            category_id=request.form['category_id'],
            description=request.form['description'],
            type=request.form['type'],
            user_id=current_user.user_id  # associate the transaction with the logged-in user
        )
        db.session.add(new_transaction) # add the new transaction to the database session
        db.session.commit() # commit the changes to the database
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions.transactions_page')) # redirect to the transactions page

    today = date.today() # get today's date
    filter_month = request.args.get('filter_month', f'{today.year}-{today.month:02}') # get the filter month (default: current month)
    change_month = request.args.get('change_month', 0, type=int) # change_month will allow for navigating to previous or next months

    # parse the year and month from the filter_month parameter
    year, month = map(int, filter_month.split('-'))
    # calculate the new date based on the current year, month, and any changes
    new_date = date(year, month, 1) + relativedelta(months=change_month)
    filter_month = f'{new_date.year}-{new_date.month:02}' # to keep filter_month updated

    # create a query for the user's transactions, joining with categories
    user_transactions_query = Transactions.query.join(Categories).filter(Transactions.user_id == current_user.user_id)
    # apply any filters to the transactions query based on filter criteria
    filtered_transactions_query = apply_filters(user_transactions_query, filter_month, request.args.get('filter_category'), request.args.get('filter_type'))

    # render the transactions page template with the filtered transactions and category information
    return render_template(
        'show_transactions.html',
        transactions=filtered_transactions_query.all(),
        categories=Categories.query.all(),
        category_icons=category_icons,
        page_title='Transactions',
        icon='fas fa-credit-card',
        current_month=new_date.month,
        current_year=new_date.year,
        current_month_name=new_date.strftime('%B'),
        filter_month=filter_month
    )

# route to delete a specific transaction by its ID
@transactions.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = Transactions.query.get_or_404(id) # fetch the transaction or return 404 if not found
    db.session.delete(transaction) # delete the transaction from the session
    db.session.commit() # commit the changes to the database
    flash('Transaction deleted successfully.', 'success')
    return redirect(url_for('transactions.transactions_page')) # redirect to the transactions page

# route to edit an existing transaction
@transactions.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    transaction = Transactions.query.get_or_404(id)
    # if the form is submitted (POST request)
    if request.method == 'POST':
        # update the transaction's details from the form data
        transaction.date = date.fromisoformat(request.form['date'])
        transaction.amount = request.form['amount']
        transaction.category_id = request.form['category_id']
        transaction.description = request.form['description']
        transaction.type = request.form['type']
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.transactions_page'))
    return render_template('edit_transaction.html', transaction=transaction, categories=Categories.query.all(), category_icons=category_icons)