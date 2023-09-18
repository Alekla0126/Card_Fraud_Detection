from flask_login import LoginManager
from app.extensions import db
from flask import Flask

login_manager = LoginManager()

def create_app(config_class):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)
    
    db.init_app(app)  # Tie the db instance to the app
    login_manager.init_app(app)  # Initialize Flask-Login

    @app.route('/')
    def home():
        return render_template('index.html')

    from app.routes.predict import prediction
    from app.routes.auth import auth
    # Register the blueprints
    app.register_blueprint(auth)
    app.register_blueprint(prediction)
    
    # Import User here to avoid circular imports
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app