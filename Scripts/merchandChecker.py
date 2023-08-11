import pandas as pd

# Read the CSV file.
df = pd.read_csv('/Users/alejandro/Desktop/Life/Card-Fraud-Detection/Datasets/linked_master.csv')

# Check if all rows in the 'merchant' column start with 'fraud_'.
all_merchants_start_with_fraud = df['merchant'].str.startswith('fraud_').all()

# Print the result.
print("All rows in the 'merchant' column start with 'fraud_':", all_merchants_start_with_fraud)
