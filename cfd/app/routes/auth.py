from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template, make_response
from flask_login import current_user, login_user, logout_user, login_required
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from datetime import datetime, timedelta
from flask import jsonify, request
from app.models.user import User
from flask_wtf import FlaskForm
from flask import current_app
from datetime import datetime
from app import login_manager
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
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 409
    # Create the new user
    new_user = User(username=username, tier=tier)
    new_user.set_password(password)
    # Set the last_reset attribute.
    new_user.last_reset = datetime.utcnow()
    db.session.add(new_user)
    db.session.commit()
    # Generate an access token for the registered user
    token = jwt.encode({'user_id': new_user.id, 'tier': new_user.tier}, current_app.config['SECRET_KEY'], algorithm='HS256') 
    return jsonify({'status': 'success', 'message': 'Successfully registered!', 'token': token}), 201

@auth.route('/login', methods=['GET'])
def display_login_form():
    if current_user.is_authenticated:
        return redirect(url_for('main.predict_screen'))
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
        # Generate an access token for the logged-in user using the `generate_token` function
        token = generate_token(user.id, user.tier)
        response = make_response(jsonify({'status': 'success', 'message': 'Logged in successfully.'}), 200)
        response.set_cookie('token', token)
        return response
    return jsonify({'status': 'error', 'message': 'Invalid username or password.'}), 401

def generate_token(user_id, tier, expiration_hours=1):
    payload = {
        'user_id': user_id,
        'tier': tier,
        'exp': datetime.utcnow() + timedelta(hours=expiration_hours)
    }
    secret_key = current_app.config['SECRET_KEY']
    return jwt.encode(payload, secret_key, algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def generate_api_token(user_id, tier):
    return generate_token(user_id, tier, expiration_hours=720)

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    response = make_response(jsonify({'status': 'success', 'message': 'Logged out successfully.'}), 200)
    response.delete_cookie('token')
    logout_user()
    return response

@auth.route('/authenticated', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        # User is authenticated
        return jsonify({'authenticated': True}), 200
    else:
        # User is not authenticated
        return jsonify({'authenticated': False}), 401