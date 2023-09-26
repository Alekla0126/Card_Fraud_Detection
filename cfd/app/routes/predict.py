# from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, jsonify, request, render_template
# from nltk.stem.snowball import SnowballStemmer
# from nltk.tokenize import RegexpTokenizer
# from sklearn.feature_extraction.text import CountVectorizer
# from nltk.tokenize import RegexpTokenizer
from flask import Blueprint, current_app
# from nltk.stem import PorterStemmer
from app.models.user import User
from functools import wraps
import pandas as pd
import datetime
import joblib
import jwt
# from keras.models import load_model
# from flask import request, jsonify
# from app.models.user import User
# # from config import API_KEY
# import pandas as pd
# import traceback
# import requests
# import pickle
# import jwt
# import os

# Adding the blueprint.
prediction = Blueprint('prediction', __name__, url_prefix='/prediction')

model = joblib.load('app/svm.pkl')

def extract_features(df):
    df['url_length'] = df['URL'].apply(len)
    df['num_subdomains'] = df['URL'].apply(lambda x: x.count('.'))
    df['num_special_chars'] = df['URL'].apply(lambda x: sum([1 for char in x if not char.isalnum()]))
    # Add other relevant features
    return df

def prepare_data(X):
    # Tokenize the text.
    X['text_tokenized'] = X['URL'].map(lambda t: tokenizer.tokenize(t)) 
    # Stem the text.
    X['text_stemmed'] = X['text_tokenized'].map(lambda t: [stemmer.stem(word) for word in t])
    # Join the text.
    X['text_sent'] = X['text_stemmed'].map(lambda t: ' '.join(t))
    # Vectorize the text.
    features = cv.fit_transform(X['text_sent'])
    return X, features

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

# Prediction view.
@prediction.route('/', methods=['GET'])
def get_predict_screen():
    return render_template('predict.html')

# Extract features from URL
def using_ip(url):
    # Check if URL contains an IP address
    return 1 if any(char.isdigit() for char in url.split('//')[-1].split('/')[0]) else 2

def long_url(url):
    # Check the length of the URL
    return 1 if len(url) < 54 else 2 if len(url) < 75 else 3

def short_url(url):
    # Check for URL shortening services
    shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 't.co']
    return 1 if any(shortener in url for shortener in shorteners) else 2

def symbol_at(url):
    # Check if URL contains '@'
    return 1 if '@' in url else 2

def redirecting(url):
    # Check if URL has '//' after the protocol
    return 1 if '//' in url.split('://')[-1] else 2

def https(url):
    # Check if URL uses HTTPS
    return 1 if 'https://' in url else 2 if 'http://' in url else 3

def sub_domains(url):
    # Count the number of subdomains
    return url.split('://')[-1].count('.')

def prefix_suffix(url):
    # Check if domain has '-'
    domain = url.split('://')[-1].split('/')[0]
    return 1 if '-' in domain else 2

def domain_reg_len(url):
    # Check the length of the domain name
    domain = url.split('://')[-1].split('/')[0]
    return 1 if len(domain) <= 6 else 2

def non_std_port(url):
    # Check for non-standard ports
    if ":80" in url or ":443" in url:
        return 2
    elif ":" in url.split('://')[-1]:
        return 1
    return 2

def https_domain_url(url):
    # Check if domain starts with "https"
    domain = url.split('://')[-1].split('/')[0]
    return 1 if domain.startswith("https") else 2

def request_url(url):
    # Basic check for ".js" in the URL
    return 1 if ".js" in url else 2

def anchor_url(url):
    # Check for anchor '#' in the URL
    return 1 if '#' in url else 2

def info_email(url):
    # Check for "mailto:"
    return 1 if "mailto:" in url else 2

def abnormal_url(url):
    # Basic check if domain is in the URL
    domain = url.split('://')[-1].split('/')[0]
    return 1 if domain in url else 2

def iframe_redirection(url):
    # Basic check for "iframe" in the URL
    return 1 if "iframe" in url else 2

def google_index(url):
    # Basic check for "google" in the URL
    return 1 if "google" in url else 2

def stats_report(url):
    # Check for common stats reporting paths
    return 1 if "/stats" in url or "/report" in url else 2

def hash_url(url):
    return hash(url)

@prediction.route('/', methods=['POST'])
# Uncomment for production.
# @token_required
def predict(current_user):
    # Get the URL from the POST request
    data = request.get_json(force=True)
    url = data['URL']

    # Create a DataFrame from the URL
    df = pd.DataFrame([url], columns=['URL'])

    # Preprocess the URL using the functions you've defined
    df = extract_features(df)
    df['UsingIP'] = df['URL'].apply(using_ip)
    df['LongURL'] = df['URL'].apply(long_url)
    df['ShortURL'] = df['URL'].apply(short_url)
    df['Symbol@'] = df['URL'].apply(symbol_at)
    df['Redirecting//'] = df['URL'].apply(redirecting)
    df['HTTPS'] = df['URL'].apply(https)
    df['SubDomains'] = df['URL'].apply(sub_domains)
    df['PrefixSuffix-'] = df['URL'].apply(prefix_suffix)
    df['DomainRegLen'] = df['URL'].apply(domain_reg_len)
    df['NonStdPort'] = df['URL'].apply(non_std_port)
    df['HTTPSDomainURL'] = df['URL'].apply(https_domain_url)
    df['RequestURL'] = df['URL'].apply(request_url)
    df['AnchorURL'] = df['URL'].apply(anchor_url)
    df['InfoEmail'] = df['URL'].apply(info_email)
    df['AbnormalURL'] = df['URL'].apply(abnormal_url)
    df['IframeRedirection'] = df['URL'].apply(iframe_redirection)
    df['GoogleIndex'] = df['URL'].apply(google_index)
    df['StatsReport'] = df['URL'].apply(stats_report)
    df['URL'] = df['URL'].apply(hash_url)

    # Predict the class using the model
    prediction = model.predict(df)

    # Return the prediction
    return jsonify({'prediction': int(prediction[0])})