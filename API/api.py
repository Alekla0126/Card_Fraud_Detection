from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import SnowballStemmer
from flask import Flask, jsonify, request
from nltk.tokenize import RegexpTokenizer
import pandas as pd
import numpy as np
import joblib

# Initialize the Flask application
app = Flask(__name__)

# Load the trained model
model = joblib.load('model.joblib')

# Initialize the tokenizer, steamer and Vectorizer.
tokenizer = RegexpTokenizer(r'[A-Za-z]+')
stemmer = SnowballStemmer("english")
cv = CountVectorizer()

# Prepare the data for the model.
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
    return features

# Importing an ordinal encoder in order to turn the categorical features into numerical.
enc = OrdinalEncoder(dtype=np.int64)

# Create a StandardScaler object
scaler = StandardScaler()

# Define the endpoint for making predictions
@app.route('/predict', methods=['POST'])
def predict():
    # Get the request data as a pandas dataframe
    json_ = request.json
    query_df = pd.DataFrame(json_)

    # Give the appropriate data type to each column of the dataset.
    query_df['hour_of_day'] = query_df['hour_of_day'].astype('string') 
    query_df['category'] = query_df['category'].astype('string')
    query_df['amount(usd)'] = query_df['amount(usd)'].astype('float64')
    query_df['merchant'] = query_df['merchant'].astype('string')
    query_df['job'] = query_df['job'].astype('string')
    query_df['url'] = query_df['url'].astype('string')

    # Preprocess the data
    X = query_df[['url']].copy()
    features = prepare_data(X)

    merged_df = pd.concat([query_df.drop(columns='url'), pd.DataFrame(features.toarray())], axis=1)

    # Transform the categorical features into numerical
    merged_df.loc[:, ['category','merchant','job', 'text_tokenized', 'text_stemmed', 'text_sent']] = enc.transform(merged_df[['category','merchant','job', 'text_tokenized', 'text_stemmed', 'text_sent']])

    # Scale the features
    merged_df = scaler.transform(merged_df)

    # Make predictions
    predictions = model.predict(merged_df)

    # Return the predictions as a JSON response
    return jsonify({'predictions': predictions.tolist()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
