from app.main import main
from flask import render_template

@main.route('/overview')
def home():
    return render_template('layout.html')