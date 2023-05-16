from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, jsonify, request, render_template
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from keras.optimizers import Adagrad
from keras.models import load_model
import tensorflow as tf
import pandas as pd
import numpy as np
import traceback
import requests
import os


API_KEY = 'AIzaSyC1H2IiSrQ7UqByfQobOVOxN6_0XsC9Fow'

# Load your model with the custom optimizer.
model = load_model('LSTM.h5', custom_objects={'Adagrad': Adagrad})

# Initialize the tokenizer, stemmer, and vectorizer.
tokenizer = RegexpTokenizer(r'[A-Za-z]+')
stemmer = SnowballStemmer('english')
cv = CountVectorizer()

# Initialize the ordinal encoder and scaler.
enc = OrdinalEncoder(dtype=np.int64)
scaler = StandardScaler()

app = Flask(__name__)

# Define the home page route.
@app.route('/')
def home():
    return render_template('index.html')

def check_numerical(value):
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid input: {value} is not a number.")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data.
        input_data = request.form.to_dict()

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

        # Tokenize and stem the text.
        input_df['text_tokenized'] = input_df['url'].apply(lambda t: tokenizer.tokenize(t))
        input_df['text_stemmed'] = input_df['text_tokenized'].apply(lambda t: [stemmer.stem(word) for word in t])
        input_df['text_sent'] = input_df['text_stemmed'].apply(lambda t: ' '.join(t))

        # Checking the format.
        # input_df['hour_of_day'] = input_df['hour_of_day'].astype('string') 
        # input_df['category'] = input_df['category'].astype('string')
        # input_df['amount(usd)'] = input_df['amount(usd)'].astype('float64')
        # input_df['merchant'] = input_df['merchant'].astype('string')
        # input_df['job'] = input_df['job'].astype('string')
        # Convert the column to float.
        input_df['zip'] = input_df['zip'].astype(float) 
        input_df['lat'] = input_df['lat'].astype(float)
        input_df['long'] = input_df['long'].astype(float)
        input_df['url'] = input_df['url'].astype('string')
        input_df['text_tokenized'] = input_df['text_tokenized'].astype('string')
        input_df['text_stemmed'] = input_df['text_stemmed'].astype('string')
        input_df['text_sent'] = input_df['text_sent'].astype('string') 

        # Encode the categorical features.
        enc.fit(input_df.loc[:,['category','merchant','job', 'url', 'text_tokenized', 'text_stemmed', 'text_sent']])
        # Transforming the categorical features into numerical.
        # Here are the parameters that we will use for the final model.
        input_df.loc[:, ['category','merchant','job', 'url', 'text_tokenized', 'text_stemmed', 'text_sent']] = enc.transform(input_df[['category','merchant','job', 'url', 'text_tokenized', 'text_stemmed', 'text_sent']])

        # Scale the features.
        scaler.fit(input_df)
        # Transform the resampled features using the scaler.
        input_df = scaler.transform(input_df)
        # The columns are passed.
        cols = ['hour_of_day', 'category', 'amount(usd)', 'merchant', 'job', 'zip', 'lat', 'long', 'url', 'text_tokenized', 'text_stemmed', 'text_sent']
        # Convert the numpy array to a pandas dataframe.
        input_df = pd.DataFrame(input_df, columns=cols)

        # Make the prediction.
        prediction = model.predict(input_df)
        prediction_class = int((prediction > .5).astype(int))
        print(prediction_class)

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
    app.run()