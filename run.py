from app import create_app
from app.extensions import db

# create an instance of the Flask application using the create_app function
app = create_app()

# use the application context to perform operations related to the app
with app.app_context():
    # create all database tables that are defined in your models
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True) # run the Flask app with debugging enabled