import pandas as pd

# Read the CSV file into a pandas DataFrame
data = pd.read_csv('/Users/alejandro/Desktop/Life/Card-Fraud-Detection/Datasets/master.csv')

# Extract the 'amount' column
amounts = data['amt']

# Calculate the average transaction value
average_transaction_value = amounts.mean()

# Print the average transaction value
print("Average Transaction Value:", average_transaction_value)
