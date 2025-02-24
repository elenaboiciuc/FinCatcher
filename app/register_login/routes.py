from flask import render_template, url_for, redirect, flash, request
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_required, current_user, logout_user, login_user
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.main.models import User
from app.register_login import auth

# route for user registration and login
@auth.route('/register_login', methods=['GET', 'POST'])
def register_login():
    # check if the request method is POST (form submission)
    if request.method == 'POST':
        form_type = request.form.get('form_type')  # get the form type (register or login)

        # handle user registration
        if form_type == 'register':
            user_name = request.form.get('user_name')
            user_email = request.form.get('user_email')
            user_password = request.form.get('user_password')
            user_password_confirmed = request.form.get('user_password_confirmed')

            # check if passwords match
            if user_password != user_password_confirmed:
                flash("Passwords do not match.", 'error') # show error message if they don't match
            # check if the username already exists
            elif User.query.filter_by(user_name=user_name).first():
                flash("User already exists.", 'error') # show error if user already in database
            else:
                # hash the password for security
                hashed_password = generate_password_hash(user_password).decode('utf-8')
                # create a new user object
                user = User(user_name=user_name,
                            user_password=hashed_password,
                            user_email=user_email)
                try:
                    db.session.add(user) # add user to the session
                    db.session.commit() # commit to the database
                    flash("Registration successful!", 'success') # show success message
                except IntegrityError:
                    db.session.rollback()
                    flash("Username or email already exists.", 'error')
                except Exception as e:
                    db.session.rollback() # rollback session in case of integrity error
                    flash(f"An error occurred: {str(e)}", 'error') # show general error message

        # handle user login
        elif form_type == 'login':
            user_name = request.form.get('user_name') # get username from the login form
            user_password = request.form.get('user_password') # get password from the login form

            try:
                # find the user by username
                user = User.query.filter_by(user_name=user_name).first()
                # verify password hash
                if user and check_password_hash(user.user_password, user_password):
                    login_user(user) # login the user
                    return redirect(url_for('main.overview')) # redirect to overview page if successful
                else:
                    flash("Invalid username or password.", 'error') # show error if credentials are invalid

            except Exception as e:
                flash(f"An error occurred during the login process: {str(e)}", 'error')  # show error message during login process

    # render the registration/login page template
    return render_template('register_login_page.html', page_title='Register/Login', icon='fas fa-user')

# route for user logout
@auth.route("/logout")
@login_required # requires the user to be logged in to logout
def logout():
    if current_user.is_authenticated: # check if the current user is authenticated
        print("Debug: Current user " + current_user.user_name + " is logged out") # debug message for logout
    logout_user() # log out the user
    return redirect(url_for('auth.register_login')) # redirect to the registration/login page

