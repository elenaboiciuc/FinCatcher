from app.extensions import db
from flask_login import UserMixin

# class User(db.Model, UserMixin):
#     user_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
#     user_name = db.Column(db.String, unique=True, nullable=False)
#     user_email = db.Column(db.String, unique=True, nullable=False)
#     user_password = db.Column(db.String, nullable=False)
#     #items = db.relationship('Transactions', backref='owner', lazy=True) #relationship 1 -> many ???????

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # References Categories table
    description = db.Column(db.String(1000), nullable=True)
    type = db.Column(db.String(10), nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    # Define the relationship to Category
    category = db.relationship('Categories', backref=db.backref('transactions', lazy=True))

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(1000), nullable=True)

class Budgets(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # References Categories table
    monthly_limit = db.Column(db.Float, nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class Goals(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    current_amount = db.Column(db.Float, nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)


