# from sklearn.feature_extraction.text import CountVectorizer
# from flask import Flask, jsonify, request, render_template
# from nltk.stem.snowball import SnowballStemmer
# from nltk.tokenize import RegexpTokenizer
# from flask import Blueprint, current_app
# from keras.models import load_model
# from flask import request, jsonify
# from app.models.user import User
# # from config import API_KEY
# from functools import wraps
# import pandas as pd
# import traceback
# import datetime
# import requests
# import pickle
# import jwt
# import os
    
# # Initialize the tokenizer, stemmer, and vectorizer.
# tokenizer = RegexpTokenizer(r'[A-Za-z]+')
# stemmer = SnowballStemmer('english')
# cv = CountVectorizer()

# # Load your model with the custom optimizer.
# # model = load_model('LSTM.h5', custom_objects={'Adagrad': Adagrad})

# # Adding the blueprint.
# main = Blueprint('main', __name__)

# # Modify the token_required decorator
# def token_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         token = request.cookies.get('token')
#         if not token:
#             return jsonify({'status': 'error', 'message': 'Token is missing!'}), 401 
#         try:
#             data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             current_user = User.query.filter_by(id=data['user_id']).first()
#         except jwt.ExpiredSignatureError:
#             return jsonify({'status': 'error', 'message': 'Token has expired!'}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401
        
#         # Check user's tier and enforce limitations
#         if current_user.tier == 'free' and limitation_exceeded(current_user):
#             return jsonify({'status': 'error', 'message': 'Free tier limitation exceeded!'}), 403
#         elif current_user.tier == 'professional' and limitation_exceeded(current_user):
#             return jsonify({'status': 'error', 'message': 'Professional tier limitation exceeded!'}), 403
#         elif current_user.tier == 'business' and limitation_exceeded(current_user):
#             return jsonify({'status': 'error', 'message': 'Business tier limitation exceeded!'}), 403
#         return f(current_user, *args, **kwargs)
#     return decorated_function
    
# # Function to check if user's prediction limit has been exceeded.
# def limitation_exceeded(user):
#     today = datetime.date.today()
#     remaining_predictions = user.remaining_scans()
#     return remaining_predictions <= 0

# # Decode the token to access according to the tier.
# def decode_token(token):
#     try:
#         decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
#         return decoded_token
#     except jwt.ExpiredSignatureError:
#         raise Exception('Token has expired')
#     except jwt.InvalidTokenError:
#         raise Exception('Invalid token')

# # Define the home page route.
# @main.route('/')
# def home():
#     return render_template('index.html')

# @main.route('/predict', methods=['GET'])
# @token_required
# def predict_screen(current_user):
    # You can now use current_user inside this function if needed
    return render_template('predict.html')
    
    try:
        
        user = User.query.filter_by(id=current_user.id).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'})

        # Check the remaining scans for the user
        remaining = user.remaining_scans()
        if remaining <= 0:
            return jsonify({'status': 'error', 'message': f'You have exceeded your daily scan limit for {user.tier} tier'})

        # If the user has scans remaining, log the scan in the database
        scan = Scan(user_id=user.id)
        db.session.add(scan)
        db.session.commit()
        
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
    
    return jsonify({'prediction': prediction})