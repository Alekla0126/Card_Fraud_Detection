from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create the extension instances
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load configurations
    app.config.from_object('config.ConfigClass')

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # other setup like registering blueprints etc.
    
    return app
