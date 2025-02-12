from flask import render_template
from app.goals import goals

@goals.route('/goals')
def goals_page():
    return render_template('show_goals.html', page_title='Goals', icon='fas fa-bullseye')