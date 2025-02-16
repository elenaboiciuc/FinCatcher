from flask import render_template
from app.help_sign_out import help_sign_out

@help_sign_out.route('/help')
def help_page():
    return render_template('help.html', page_title='Help', icon='fas fa-question-circle')