import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()  # Initialize Migrate here

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        config_path = os.getenv('FLASK_CONFIG', 'app.config.Config')
        app.config.from_object(config_path)
    db.init_app(app)
    migrate.init_app(app, db)  # Pass db to migrate.init_app to associate with your database
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'main.login'  # Route for the login page
    Bootstrap(app)

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import User here to avoid circular imports
    return User.query.get(int(user_id))