from flask import render_template, url_for, redirect, flash, request
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_required, current_user, logout_user, login_user
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.main.models import User
from app.register_login import auth


@auth.route('/register_login', methods=['GET', 'POST'])
def register_login():
    if request.method == 'POST':
        form_type = request.form.get('form_type')  # get the form type (register or login)

        if form_type == 'register':
            user_name = request.form.get('user_name')
            user_email = request.form.get('user_email')
            user_password = request.form.get('user_password')
            user_password_confirmed = request.form.get('user_password_confirmed')

            if user_password != user_password_confirmed:
                flash("Passwords do not match.", 'error')
            elif User.query.filter_by(user_name=user_name).first():
                flash("User already exists.", 'error')
            else:
                hashed_password = generate_password_hash(user_password).decode('utf-8')
                user = User(user_name=user_name,
                            user_password=hashed_password,
                            user_email=user_email)
                try:
                    db.session.add(user)
                    db.session.commit()
                    flash("Registration successful!", 'success')
                except IntegrityError:
                    db.session.rollback()
                    flash("Username or email already exists.", 'error')
                except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred: {str(e)}", 'error')

        elif form_type == 'login':
            user_name = request.form.get('user_name')
            user_password = request.form.get('user_password')

            try:
                user = User.query.filter_by(user_name=user_name).first()  # find the user by username
                if user and check_password_hash(user.user_password, user_password):  # check password hash
                    login_user(user)
                    return redirect(url_for('main.overview'))
                else:
                    flash("Invalid username or password.", 'error')

            except Exception as e:
                flash(f"An error occurred during the login process: {str(e)}", 'error')

    return render_template('register_login_page.html', page_title='Register/Login', icon='fas fa-user')

@auth.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        print("Debug: Current user " + current_user.user_name + " is logged out")
    logout_user()
    return redirect(url_for('auth.register_login'))

