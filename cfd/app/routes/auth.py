from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models.user import User
from flask_wtf import FlaskForm
from functools import wraps
from flask import current_app
from app import db
import jwt  # Ensure you've installed jwt

# Form definition
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username=username)
        new_user.set_password(password)  # Call the set_password method
        db.session.add(new_user)
        db.session.commit()

        flash('Successfully registered!', 'success')
        return redirect(url_for('main.home'))  # Redirect to the home page

    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            token = generate_token(user.id)  # Assuming you have a function for this
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))

        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'status': 'error', 'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth.route('/')
def home():
    return render_template('index.html')