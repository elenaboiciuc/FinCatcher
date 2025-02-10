from app.budgets import budgets
from flask import render_template

@budgets.route('/budgets')
def budgets_page():
    return render_template('show_budgets.html')
