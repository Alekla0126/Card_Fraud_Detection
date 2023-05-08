from datetime import datetime
import pandas as pd
import random
import json

# Read the CSV file.
df = pd.read_csv('/Users/alejandro/Desktop/Life/Card-Fraud-Detection/Datasets/linked_master.csv')

# Add a 'time' column and drop the 'unix_time' column.
df['time'] = df['unix_time'].apply(datetime.utcfromtimestamp)
df.drop('unix_time', axis=1, inplace=True)
# A column with hour of day was added.
df['hour_of_day'] = df.time.dt.hour

# Rename the 'amt' column to 'amount(usd)'.
df.rename(columns={'amt': 'amount(usd)'}, inplace=True)

# Select a random sample of 3 rows with is_fraud == 1 and is_fraud == 0.
fraud_samples = df[df['is_fraud'] == 1].sample(n=3)
not_fraud_samples = df[df['is_fraud'] == 0].sample(n=3)

# Define the list of columns to include in the sample data.
columns = ['hour_of_day', 'category', 'amount(usd)', 'merchant', 'job', 'zip', 'lat', 'long', 'url', 'is_fraud']

# Create a list of dictionaries containing the sample data.
samples = []
for _, row in fraud_samples.iterrows():
    sample_dict = {col: row[col] for col in columns}
    sample_dict['is_fraud'] = bool(sample_dict['is_fraud'])
    samples.append(sample_dict)

for _, row in not_fraud_samples.iterrows():
    sample_dict = {col: row[col] for col in columns}
    sample_dict['is_fraud'] = bool(sample_dict['is_fraud'])
    samples.append(sample_dict)

# Convert the list of dictionaries to a JSON string.
json_str = json.dumps(samples)

# Print the JSON string.
print(json_str)