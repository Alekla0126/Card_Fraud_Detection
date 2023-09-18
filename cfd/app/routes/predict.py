# from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, jsonify, request, render_template
# from nltk.stem.snowball import SnowballStemmer
# from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer
from flask import Blueprint, current_app
from nltk.stem import PorterStemmer
from functools import wraps
import pandas as pd
import joblib
# from keras.models import load_model
# from flask import request, jsonify
# from app.models.user import User
# # from config import API_KEY
# import pandas as pd
# import traceback
# import datetime
# import requests
# import pickle
# import jwt
# import os

# Adding the blueprint.
prediction = Blueprint('prediction', __name__, url_prefix='/prediction')

# Load the trained SVM model
clf = joblib.load('one_class_svm.pkl')
# Intialize the tokenizer.
cv = CountVectorizer(max_features=1000)
tokenizer = RegexpTokenizer(r'[A-Za-z]+')
stemmer = PorterStemmer()

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is missing!'}), 401 
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'status': 'error', 'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401
        
        # Check user's tier and enforce limitations
        if current_user.tier == 'free' and limitation_exceeded(current_user):
            return jsonify({'status': 'error', 'message': 'Free tier limitation exceeded!'}), 403
        elif current_user.tier == 'professional' and limitation_exceeded(current_user):
            return jsonify({'status': 'error', 'message': 'Professional tier limitation exceeded!'}), 403
        elif current_user.tier == 'business' and limitation_exceeded(current_user):
            return jsonify({'status': 'error', 'message': 'Business tier limitation exceeded!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function

# Function to check if user's prediction limit has been exceeded.
def limitation_exceeded(user):
    today = datetime.date.today()
    remaining_predictions = user.remaining_scans()
    return remaining_predictions <= 0

# Decode the token to access according to the tier.
def decode_token(token):
    try:
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        raise Exception('Token has expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

@prediction.route('/prediction', methods=['GET'])
def get_predict_screen():
    return render_template('predict.html')

@prediction.route('/prediction', methods=['POST'])
@token_required
def predict():
    # Get the URL from the request.
    data = request.get_json()
    url = data['URL']
    # Create a dataframe.
    df = pd.DataFrame([url], columns=['URL'])
    # Ensure URL is a string.
    df['URL'] = df['URL'].fillna('').astype(str)
    # Extract features.
    df = extract_features(df)
    # Prepare the data.
    _, features = prepare_data(df)
    # Predict.
    prediction = clf.predict(features)
    # Check if the URL is malicious (-1) or not (1)
    result = "Malicious" if prediction[0] == -1 else "Safe"
    return jsonify({"prediction": result})