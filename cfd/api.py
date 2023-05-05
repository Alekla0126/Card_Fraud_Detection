from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from flask import Flask, jsonify, request, render_template
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from keras.models import load_model
import tensorflow as tf
import pandas as pd
import numpy as np
import requests
import os

# Set the Safe Browsing API key.
API_KEY = 'AIzaSyBbMLheR2Y2PZ-UBFoFRAehbAWN2fs79xc'

# Set the CPU.
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Define your custom optimizer.
class Adagrad(tf.keras.optimizers.Optimizer):
    # Your custom implementation here.
    pass

# Load your model with the custom optimizer.
model = load_model('LSTM.h5', custom_objects={'Adagrad': Adagrad})

# Initialize the tokenizer, stemmer, and vectorizer.
tokenizer = RegexpTokenizer(r'[A-Za-z]+')
stemmer = SnowballStemmer('english')
cv = CountVectorizer()

# Initialize the ordinal encoder and scaler
enc = OrdinalEncoder(dtype=np.int64)
scaler = StandardScaler()

app = Flask(__name__)

# Define the home page route.


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data.
        input_data = request.form.to_dict()

        # Preprocess the input data.
        input_df = pd.DataFrame({'url': [input_data['url']]})
        input_df['category'] = input_data.get('category', '')
        input_df['merchant'] = input_data.get('merchant', '')
        input_df['job'] = input_data.get('job', '')
        input_df['label'] = 0

        # Tokenize and stem the text.
        input_df['text_tokenized'] = input_df.url.map(
            lambda t: tokenizer.tokenize(t))
        input_df['text_stemmed'] = input_df.text_tokenized.map(
            lambda t: [stemmer.stem(word) for word in t])
        input_df['text_encoded'] = input_df.text_stemmed.map(
            lambda t: [cv.vocabulary_.get(word, -1) + 1 for word in t])
        input_df['text_padded'] = tf.keras.preprocessing.sequence.pad_sequences(
            input_df['text_encoded'], maxlen=100)

        # Convert form values to float.
        input_data['category'] = float(input_data.get('category', ''))
        input_data['merchant'] = float(input_data.get('merchant', ''))
        input_data['job'] = float(input_data.get('job', ''))

        # Encode the categorical features.
        input_df['category_encoded'] = enc.fit_transform(
            input_df[['category']])
        input_df['merchant_encoded'] = enc.fit_transform(
            input_df[['merchant']])
        input_df['job_encoded'] = enc.fit_transform(input_df[['job']])

        # Scale the numerical features.
        numerical_features = ['category_encoded',
                              'merchant_encoded', 'job_encoded']
        input_df[numerical_features] = scaler.fit_transform(
            input_df[numerical_features])

        # Make the prediction.
        prediction = model.predict(
            input_df[['category_encoded', 'merchant_encoded', 'job_encoded', 'text_padded']])
        prediction_class = np.argmax(prediction)

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
                "platformTypes": ["WINDOWS"],
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

if name == 'main':
app.run()
