from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, jsonify, request, render_template
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from keras.optimizers import Adagrad
from keras.models import load_model
from flask import request, jsonify
# from config import API_KEY
from flask import Blueprint
from functools import wraps
import tensorflow as tf
import pandas as pd
import numpy as np
import traceback
import requests
import pickle
import os

# Load categories.
with open('encoded_categories.pkl', 'rb') as f:
    encoded_categories = pickle.load(f)
    
# Load the saved scaler object
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
    
# Initialize the tokenizer, stemmer, and vectorizer.
tokenizer = RegexpTokenizer(r'[A-Za-z]+')
stemmer = SnowballStemmer('english')
cv = CountVectorizer()

# Load your model with the custom optimizer.
model = load_model('LSTM.h5', custom_objects={'Adagrad': Adagrad})

# Adding the blueprint.
main = Blueprint('main', __name__)

#  Prepare the data for the model.
def prepare_data(X):
    # Tokenize the text.
    X['text_tokenized'] = X.url.map(lambda t: tokenizer.tokenize(t))
    # Stem the text.
    X['text_stemmed'] = X.text_tokenized.map(lambda t: [stemmer.stem(word) for word in t])
    # Join the text.
    X['text_sent'] = X.text_stemmed.map(lambda t: ' '.join(t))
    # Vectorize the text.
    features = cv.fit_transform(X.text_sent)
    # Return the features and the target.
    return X, features

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # Here you should validate the token, e.g., check if it's valid, expired, etc.
        # If invalid:
        # return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated

# Define the home page route.
@main.route('/')
def home():
    return render_template('index.html')

@main.route('/predict', methods=['POST'])
@token_required
def predict():
    try:
        # Get the input data.
        input_data = request.get_json()

        # Preprocess the input data.
        input_df = pd.DataFrame({
            'hour_of_day': [input_data.get('hour_of_day', '')],
            'category': [input_data.get('category', '')],
            'amount(usd)': [input_data.get('amount(usd)', '')],
            'merchant': [input_data.get('merchant', '')],
            'job': [input_data.get('job', '')],
            'zip': [input_data.get('zip', '')],
            'lat': [input_data.get('lat', '')],
            'long': [input_data.get('long', '')],
            'url': [input_data.get('url', '')],
        })
        
        # Check if the merchant starts with "fraud_" and add it if it doesn't.
        input_df['merchant'] = input_df['merchant'].apply(lambda x: 'fraud_' + x if not x.startswith('fraud_') else x)
        
        # Stemmed text, tokenize and vectorize.
        input_df, features = prepare_data(input_df)

        
        # Checking the format.
        input_df['hour_of_day'] = input_df['hour_of_day'].astype('string') 
        input_df['category'] = input_df['category'].astype('string')
        input_df['amount(usd)'] = input_df['amount(usd)'].astype('float64')
        input_df['merchant'] = input_df['merchant'].astype('string')
        input_df['job'] = input_df['job'].astype('string')
        # Convert the columns to float.
        input_df['zip'] = input_df['zip'].astype(float) 
        input_df['lat'] = input_df['lat'].astype(float)
        input_df['long'] = input_df['long'].astype(float)
        input_df['url'] = input_df['url'].astype('string')
        input_df['text_tokenized'] = input_df['text_tokenized'].astype('string')
        input_df['text_stemmed'] = input_df['text_stemmed'].astype('string')
        input_df['text_sent'] = input_df['text_sent'].astype('string')

        print("After text processing: ")
        print(input_df)
        
        
        # Instantiate the encoder with the loaded categories
        enc = OrdinalEncoder(categories=encoded_categories, dtype=np.int64) 
        # Encode the categorical features.
        enc.fit(input_df.loc[:,['category','merchant','job', 'url', 'text_tokenized', 'text_stemmed', 'text_sent']])
        # Transforming the categorical features into numerical.
        # Here are the parameters that we will use for the final model.
        input_df.loc[:, ['category','merchant','job', 'url', 'text_tokenized', 'text_stemmed', 'text_sent']] = enc.transform(input_df[['category','merchant','job', 'url', 'text_tokenized', 'text_stemmed', 'text_sent']])

        print("After encoding: ")
        print(input_df)

        
        # Scale the features.
        cols = input_df.columns
        input_df = scaler.transform(input_df)
        input_df = pd.DataFrame(input_df, columns=cols)
                
        print("After scaling: ")
        print(input_df)
        
        # Fomat for the LTSM model.
        # input_data = np.asarray(input_data).astype(np.float32)

        # Make the prediction.
        prediction = model.predict(input_df)
        prediction_class = int((prediction >= .40).astype(int))

        # Check if the URL is in the Safe Browsing database.
        headers = {'Content-Type': 'application/json'}
        url = 'https://safebrowsing.googleapis.com/v4/threatMatches:find?key=' + API_KEY
        payload = {
            "client": {
                "clientId": "mycompany",
                "clientVersion": "1.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "POTENTIALLY_HARMFUL_APPLICATION", "UNWANTED_SOFTWARE"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": input_data['url']}
                ]
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            # The URL is in the Safe Browsing database.
            in_safebrowsing = True
        elif response.status_code == 204:
            # The URL is not in the Safe Browsing database.
            in_safebrowsing = False
        else:
            # There was an error.
            raise Exception(f'Safe Browsing API error: {response.status_code}')

        # Return the prediction and whether the URL is in the Safe Browsing database.
        return jsonify({'prediction': prediction_class, 'in_safebrowsing': in_safebrowsing})

    except Exception as e:
        # Handle the exception and return an error message
        error_message = f"An error occurred: {str(e)}"
        print(traceback.format_exc())  # Print the error traceback to the console
        return jsonify({'status': 'error', 'message': error_message})

if __name__ == '__main__':
    # Remove the debug=True parameter for production.
    app.run()
