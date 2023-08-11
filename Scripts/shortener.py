import pandas as pd
import random

# read in the data as a pandas dataframe
df = pd.read_csv('/Users/alejandro/Desktop/Life/Credit-Card-Fraud-Detection/Datasets/linked_master.csv')

# separate the fraud and non-fraud data
fraud = df[df['is_fraud'] == 1]
non_fraud = df[df['is_fraud'] == 0]

# get the same number of non-fraud data as the fraud data
non_fraud_sampled = non_fraud.sample(n=len(fraud), random_state=42)

# concatenate the fraud and non-fraud data
df_combined = pd.concat([fraud, non_fraud_sampled])

# shuffle the rows
df_combined = df_combined.sample(frac=1, random_state=42)

# write out the combined and shuffled data to a new csv file
df_combined.to_csv('/Users/alejandro/Desktop/Life/Credit-Card-Fraud-Detection/Datasets/shortened.csv', index=False)