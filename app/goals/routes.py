from flask import render_template
from flask_login import login_required

from app.goals import goals

@goals.route('/goals')
@login_required
def goals_page():
    return render_template('show_goals.html', page_title='Goals', icon='fas fa-bullseye')