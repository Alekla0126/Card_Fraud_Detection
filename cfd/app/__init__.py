from .extensions import db
from flask import Flask

def create_app(config_class):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    
    db.init_app(app)  # Tie the db instance to the app

    from app.routes.main import main
    from .routes.auth import auth
    # Register the blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)

    return app