from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


# declaration of DB and Migrate
db = SQLAlchemy()
migrate = Migrate()

# bcrypt =
# login_manager =


category_icons = {
    1: 'static/images/food.png',
    2: 'static/images/utilities1.png',
    3: 'static/images/entertainment.png',
    4: 'static/images/transportation.png',
    5: 'static/images/housing.png',
    6: 'static/images/healthcare2.png',
    7: 'static/images/insurance.png',
    8: 'static/images/education.png',
    9: 'static/images/personal_care3.png',
    10: 'static/images/savings.png',
    11: 'static/images/gifts_donations2.png',
    12: 'static/images/vacations.png',
    13: 'static/images/earnings.png',
    14: 'static/images/shopping.png',
    15: 'static/images/pets.png',
    16: 'static/images/others.png'
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





