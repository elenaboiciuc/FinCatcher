from flask import render_template
from app.help import help

@help.route('/help')
def help_page():
    return render_template('help.html', page_title='Help', icon='fas fa-question-circle')