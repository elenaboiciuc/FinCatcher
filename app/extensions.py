from flask_migrate import Migrate # for database migrations
from flask_sqlalchemy import SQLAlchemy # for database interaction
from flask_bcrypt import Bcrypt # for hashing passwords
from flask_login import LoginManager # for managing user sessions


# declaration of DB and Migrate
db = SQLAlchemy()
migrate = Migrate()

# declaration of Bcrypt and LoginManager
bcrypt = Bcrypt() #  pass management for a registered user
login_manager = LoginManager()  # this will handle the user login/logout operations


category_icons = {
    1: 'static/images/food.png',
    2: 'static/images/utilities.png',
    3: 'static/images/entertainment.png',
    4: 'static/images/transportation.png',
    5: 'static/images/housing.png',
    6: 'static/images/healthcare.png',
    7: 'static/images/insurance.png',
    8: 'static/images/education.png',
    9: 'static/images/personal_care.png',
    10: 'static/images/savings.png',
    11: 'static/images/gifts_donations.png',
    12: 'static/images/vacations.png',
    13: 'static/images/earnings.png',
    14: 'static/images/shopping.png',
    15: 'static/images/pets.png',
    16: 'static/images/others.png',
    17: 'static/images/new_category.png'
}

category_gifs = {
    1: 'static/images/food.gif',
    2: 'static/images/utilities.gif',
    3: 'static/images/entertainment.gif',
    4: 'static/images/transportation.gif',
    5: 'static/images/housing.gif',
    6: 'static/images/healthcare.gif',
    7: 'static/images/insurance.gif',
    8: 'static/images/education.gif',
    9: 'static/images/personal_care.gif',
    10: 'static/images/savings.gif',
    11: 'static/images/gifts_donations.gif',
    12: 'static/images/vacations.gif',
    13: 'static/images/earnings.gif',
    14: 'static/images/shopping.gif',
    15: 'static/images/pets.gif',
    16: 'static/images/others.gif',
    17: 'static/images/new_category.gif'
}

financial_quotes = {
    1: "A penny saved is a penny earned. 💰",
    2: "Save first, spend what’s left. 💸",
    3: "Wealth is what you keep, not what you make. 🏦",
    4: "The best time to start saving is now. ⏰",
    5: "Budgeting makes room for what you love. ❤️",
    6: "Make saving a priority. 🔑",
    7: "Money helps you live on your terms. 🌟",
    8: "Financial freedom starts with knowledge. 📚",
    9: "Avoid impulse buys. ⛔",
    10: "Spend less than you earn. ✂️",
    11: "Smart saving today, secure tomorrow. 🌼",
    12: "Money should serve you, not rule you. ⚖️",
    13: "Saving teaches discipline. 📈",
    14: "Invest in yourself first. 🌍",
    15: "Stay financially educated. 🧠",
    16: "Don’t let money control your life. 🚫",
    17: "Save a little, gain a lot. 🌟",
    18: "Debt and ignorance don’t mix. ⚠️",
    19: "Only save what’s extra. ✨",
    20: "Start small, grow your savings. 🌿",
    21: "Shop smart, save big. 🛒",
    22: "Save for snow. ❄️",
}





