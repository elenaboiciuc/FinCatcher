from sqlalchemy import UniqueConstraint
from app.extensions import db, login_manager
from flask_login import UserMixin


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_name = db.Column(db.String, unique=True, nullable=False)
    user_email = db.Column(db.String, unique=True, nullable=False)
    user_password = db.Column(db.String, nullable=False)

    # one-to-many relationships to multiple tables
    transactions = db.relationship('Transactions', backref='owner', lazy=True)
    categories = db.relationship('Categories', backref='owner', lazy=True)
    budgets = db.relationship('Budgets', backref='owner', lazy=True)
    goals = db.relationship('Goals', backref='owner', lazy=True)

    def get_id(self):
        return self.user_id  # retrieves the user's ID for user loading functionality

# function to load a user based on user_id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # query the database to retrieve the user instance corresponding to the user_id

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    type = db.Column(db.String(10), nullable=False)

    # foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # references Categories table
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # link to User

    # relationship to table categories
    category = db.relationship('Categories', backref=db.backref('transactions', lazy=True))

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(1000), nullable=True)

    # foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)  # link to User

    # relationships to budgets and goals
    budgets = db.relationship('Budgets', backref='category', lazy=True)
    goals = db.relationship('Goals', backref='category', lazy=True)

    # unique constraint on the combination of name and user_id
    __table_args__ = (UniqueConstraint('name', 'user_id', name='uix_name_user_id'),)

class Budgets(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)

    # foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # references Categories table
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # link to User

    # unique constraint on the combination of name and user_id
    __table_args__ = (UniqueConstraint('name', 'user_id', name='uix_name_user_id'),)

    def calculate_percent_spent(self, spent):
        """ calculate the percentage spent based on the monthly limit """
        return (spent / self.monthly_limit * 100) if self.monthly_limit > 0 else 0

class Goals(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    current_amount = db.Column(db.Float, nullable=False)

    # foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)  # references Categories table
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # link to User

    # unique constraint on the combination of name and user_id
    __table_args__ = (UniqueConstraint('name', 'user_id', name='uix_name_user_id'),)


