from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# declaration of DB and Migrate
db = SQLAlchemy()
migrate = Migrate()

# bcrypt =
# login_manager =

# category_icons = {
#     'Food': 'static/images/food.png',
#     'Utilities': 'static/images/utilities1.png',
#     'Entertainment': 'static/images/entertainment.png',
#     'Transportation': 'static/images/transportation.png',
#     'Housing': 'static/images/housing.png',
#     'Healthcare': 'static/images/healthcare2.png',
#     'Insurance': 'static/images/insurance.png',
#     'Education': 'static/images/education.png',
#     'Personal Care': 'static/images/personal_care2.png',
#     'Savings': 'static/images/savings.png',
#     'Gifts and Donations': 'static/images/gifts_donations.png',
#     'Vacations': 'static/images/vacations.png',
#     'Earnings': 'static/images/earnings.png',
#     'Shopping': 'static/images/shopping.png',
#     'Pets': 'static/images/pets.png',
#     'Others': 'static/images/others.png'
# }

category_icons = {
    1: 'static/images/food.png',
    2: 'static/images/utilities1.png',
    3: 'static/images/entertainment.png',
    4: 'static/images/transportation.png',
    5: 'static/images/housing.png',
    6: 'static/images/healthcare2.png',
    7: 'static/images/insurance.png',
    8: 'static/images/education.png',
    9: 'static/images/personal_care1.png',
    10: 'static/images/savings.png',
    11: 'static/images/gifts_donations.png',
    12: 'static/images/vacations.png',
    13: 'static/images/earnings.png',
    14: 'static/images/shopping.png',
    15: 'static/images/pets.png',
    16: 'static/images/others.png'
}




