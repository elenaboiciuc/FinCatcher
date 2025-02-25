from flask import Flask
from app.export import export
from app.help import help
from app.help.routes import help_page
from app.main import main
from app.register_login import auth
from app.transactions import transactions
from app.categories import categories
from app.budgets import budgets
from app.goals import goals
from app.extensions import db, migrate, bcrypt, login_manager


def create_app():
    app = Flask(__name__)  # create a flask application instance

    # configure DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # set the URI for the SQLite database
    # URI is used to define the connection string required to access the database
    # sqlite:///app.db is a URI that tells SQLAlchemy to use an SQLite database located in the file app.db
    # the sqlite:// part specifies the database type, and ///app.db specifies the path to the database file

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # disable the feature to track modifications, which avoids a warning
    app.secret_key = "1234"  # key for data decryption

    # initialize extensions
    db.init_app(app)  # bind the SQLAlchemy instance to the Flask app
    migrate.init_app(app, db)  # bind the Migrate instance to the Flask app and the database instance

    # initialize bcrypt and login_manager
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # protect some urls unless user is login
    login_manager.login_view = "auth.register_login"

    # register blueprints
    app.register_blueprint(main)
    app.register_blueprint(transactions)
    app.register_blueprint(budgets)
    app.register_blueprint(goals)
    app.register_blueprint(categories)
    app.register_blueprint(help)
    app.register_blueprint(export)
    app.register_blueprint(auth)

    return app
