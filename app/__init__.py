from flask import Flask
from app.main import main
from app.transactions import transactions
from app.categories import categories
from app.budgets import budgets
from app.goals import goals
from app.extensions import db,migrate

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ###
    app.register_blueprint(main)
    app.register_blueprint(transactions)
    app.register_blueprint(budgets)
    app.register_blueprint(goals)
    app.register_blueprint(categories)
    return app






