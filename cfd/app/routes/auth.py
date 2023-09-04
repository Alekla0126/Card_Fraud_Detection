from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from flask_login import current_user, login_user, logout_user, login_required
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from app.models.user import User
from flask_wtf import FlaskForm
from app import login_manager
from flask import current_app
from functools import wraps
from app import db
import jwt 

# Form definitions
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    tier = SelectField('Tier', choices=[('free', 'Free'), ('professional', 'Professional'), ('enterprise', 'Enterprise')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Registration of the route.
auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=['GET'])
def display_register_form():
    return render_template('register.html')

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    tier = data.get('tier')

    # Ensure required fields are provided
    if not username or not password or not tier:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 409

    # Create the new user
    new_user = User(username=username, tier=tier)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    # Generate an access token for the registered user
    token = jwt.encode({'user_id': new_user.id, 'tier': new_user.tier}, current_app.config['SECRET_KEY'], algorithm='HS256') 
    print(token)
    return jsonify({'status': 'success', 'message': 'Successfully registered!', 'token': token}), 201

from flask import jsonify, request

@auth.route('/login', methods=['GET'])
def display_login_form():
    if current_user.is_authenticated:
        return redirect(url_for('main.predict_get'))
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        # If you're using Flask-Login, this will establish a user session
        login_user(user)

        # Generate an access token for the logged-in user
        token = jwt.encode({'user_id': user.id, 'tier': user.tier}, current_app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'status': 'success', 'message': 'Logged in successfully.', 'token': token}), 200

    return jsonify({'status': 'error', 'message': 'Invalid username or password.'}), 401

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'success', 'message': 'Logged out successfully.'}), 200

# Modify the token_required decorator
def token_required(required_tier):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('x-access-token')
            if not token:
                return jsonify({'status': 'error', 'message': 'Token is missing!'}), 401
            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = User.query.filter_by(id=data['user_id']).first()
                # Check if the user's tier matches the required tier
                if current_user.tier != required_tier:
                    return jsonify({'status': 'error', 'message': 'Insufficient permissions!'}), 403
            except jwt.ExpiredSignatureError:
                return jsonify({'status': 'error', 'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

@auth.route('/')
def home():
    return render_template('index.html')