from datetime import date
from flask import request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.goals import goals
from app.extensions import db, category_gifs, category_icons
from app.main.helpers import get_categories, update_goal_progress_and_notify
from app.main.models import Goals

@goals.route('/goals', methods=['GET', 'POST'])
@login_required
def goals_page():
    if request.method == 'POST':
        new_goal = Goals(
            name=request.form['name'],
            target_amount=request.form['target_amount'],
            target_date=date.fromisoformat(request.form['target_date']),
            current_amount=0,
            category_id=request.form['category_id'],
            user_id=current_user.user_id
        )
        try:
            db.session.add(new_goal)
            db.session.commit()
            flash('New goal created successfully!', 'success')
            flash(
                'Only transactions that include the goal name in the description will be considered, so please set the descriptions carefully.',
                'info'
            )
            # Update current amounts and check notifications for all goals after the new goal is created
            update_goal_progress_and_notify(current_user.user_id, category_icons)
        except IntegrityError:
            db.session.rollback()
            flash('Goal name already exists. Please choose a different name.', 'error')

        return redirect(url_for('goals.goals_page'))

    # Fetch goals and categories for the current user
    goals_list = Goals.query.filter_by(user_id=current_user.user_id).all()
    categories_list = get_categories()

    # Update current amounts and check notifications for all goals
    update_goal_progress_and_notify(current_user.user_id, category_icons)

    return render_template('show_goals.html', goals=goals_list,
                           categories=categories_list, category_gifs=category_gifs, category_icons=category_icons,
                           page_title='Goals', icon='fas fa-bullseye',
                           current_date=date.today())


# Route to edit a specific goal
@goals.route('/goals/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_goal(id):
    goal = Goals.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    categories_list = get_categories()

    if request.method == 'POST':
        try:
            goal.name = request.form['name']
            goal.target_amount = float(request.form['target_amount'])
            goal.target_date = date.fromisoformat(request.form['target_date'])
            goal.category_id = request.form['category_id']
            db.session.commit()
            flash('Goal updated successfully!', 'success')
            return redirect(url_for('goals.goals_page'))
        except IntegrityError:
            db.session.rollback()
            flash('There was an error updating the goal. Please try again.', 'error')

    return render_template('edit_goal.html', goal=goal, categories=categories_list, page_title='Edit Goal')


# Route to delete a specific goal
@goals.route('/goals/delete/<int:id>', methods=['POST'])
@login_required
def delete_goal(id):
    goal = Goals.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('goals.goals_page'))