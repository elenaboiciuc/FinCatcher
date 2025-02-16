from flask import Flask

from app.help_sign_out import help_sign_out
from app.help_sign_out.routes import help_page
from app.main import main
from app.transactions import transactions
from app.categories import categories
from app.budgets import budgets
from app.goals import goals
from app.extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Path to your database file
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Avoids a warning
    app.secret_key = '1234'  # Key for data encryption

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(transactions)
    app.register_blueprint(budgets)
    app.register_blueprint(goals)
    app.register_blueprint(categories)
    app.register_blueprint(help_sign_out)

    return app
