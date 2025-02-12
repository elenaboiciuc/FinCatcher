from app.main import main
from flask import render_template

@main.route('/')
def home():
    return render_template('layout.html', page_title='Overview', icon='fas fa-home')