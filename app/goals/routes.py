from datetime import date
from flask import request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from app.goals import goals
from app.extensions import db, category_gifs, category_icons
from app.main.helpers import get_categories, update_goal_progress_and_notify
from app.main.models import Goals

# route for the goals page, allows both GET and POST methods
@goals.route('/goals', methods=['GET', 'POST'])
@login_required # requires the user to be logged in to access this route
def goals_page():
    # if the form is submitted (POST request)
    if request.method == 'POST':
        # create a new goal from form data
        new_goal = Goals(
            name=request.form['name'],
            target_amount=request.form['target_amount'],
            target_date=date.fromisoformat(request.form['target_date']), # convert to a date object
            current_amount=0, # initialize current amount to zero
            category_id=request.form['category_id'],
            user_id=current_user.user_id # associate the goal with the logged-in user
        )
        try:
            # add the new goal to the database and commit
            db.session.add(new_goal)
            db.session.commit()
            flash('New goal created successfully!', 'success')
            flash(
                'Only transactions that include the goal name in the description will be considered, so please set the descriptions carefully.',
                'info'
            )
            # update current amounts and check notifications for all goals after the new goal is created
            update_goal_progress_and_notify(current_user.user_id, category_icons)
        except IntegrityError:
            db.session.rollback() # rollback if there's an integrity error
            flash('Goal name already exists. Please choose a different name.', 'error')

        return redirect(url_for('goals.goals_page')) # redirect to the goals page

    # fetch goals and categories for the current user
    goals_list = Goals.query.filter_by(user_id=current_user.user_id).all()  # get all goals for the user
    categories_list = get_categories()  # get categories for the dropdown

    # update current amounts and check notifications for all goals
    update_goal_progress_and_notify(current_user.user_id, category_icons)

    return render_template('show_goals.html', goals=goals_list,
                           categories=categories_list, category_gifs=category_gifs, category_icons=category_icons,
                           page_title='Goals', icon='fas fa-bullseye',
                           current_date=date.today()) # pass the current date to the template


# route to edit a specific goal
@goals.route('/goals/edit/<int:id>', methods=['GET', 'POST'])
@login_required # requires the user to be logged in
def edit_goal(id):
    # fetch the goal to edit or return a 404 error if not found
    goal = Goals.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    categories_list = get_categories() # get categories for the dropdown

    # if the form is submitted (POST request)
    if request.method == 'POST':
        try:
            # update the goal's attributes with new values from the form
            goal.name = request.form['name']
            goal.target_amount = float(request.form['target_amount']) # convert string input to float
            goal.target_date = date.fromisoformat(request.form['target_date']) # convert to a date object
            goal.category_id = request.form['category_id']
            db.session.commit() # commit the changes to the database
            flash('Goal updated successfully!', 'success')
            return redirect(url_for('goals.goals_page'))  # redirect to the goals page
        except IntegrityError:
            db.session.rollback() # rollback if there's an integrity error
            flash('Goal name already exists. Please choose another name.', 'error')

    return render_template('edit_goal.html', goal=goal, categories=categories_list, page_title='Edit Goal')


# route to delete a specific goal
@goals.route('/goals/delete/<int:id>', methods=['POST'])
@login_required
def delete_goal(id):
    # fetch the goal to delete or return a 404 error if not found
    goal = Goals.query.filter_by(id=id, user_id=current_user.user_id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('goals.goals_page'))