from collections import defaultdict
import argparse
import string
import random
import time
import csv
import os

def is_printable(s):
    return all(c in string.printable for c in s)

def add_urls(transactions_file, urls_file, output_file, threshold):
    print("Reading urls CSV file...")
    # Read the urls CSV file and extract the good and bad urls
    urls = defaultdict(list)
    with open(urls_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls[row['Label']].append(row['URL'])

    # Drop rows containing non-printable characters from the urls lists
    print('Drop rows containing non-printable characters...')
    urls = {label: [url for url in urls[label] if is_printable(url)] for label in urls}

    print("Processing transactions...")
    num_good_urls = 0
    num_bad_urls = 0
    num_incorrect_bad_urls = 0
    num_incorrect_good_urls = 0
    # Process the transactions using multiple threads
    with open(output_file, 'w', newline='') as f_out, open(transactions_file, 'r') as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ['url']
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        # Instantiating the lists
        good_urls = urls['good']
        bad_urls = urls['bad']
        # Loop through rows
        i_good = 0
        i_bad = 0
        for i, row in enumerate(reader):
            print(f"Processing transaction {i}...")
            # Get the url for this row
            url = None
            if int(row['is_fraud']) == 1:
                if random.random()+.00521 <= threshold:                          
                    if i_good == len(urls['good']):
                        i_good = 0
                    url = good_urls[i_good]
                    num_incorrect_good_urls += 1
                    i_good += 1
                else:
                    if i_bad >= len(bad_urls):
                        i_bad = 0
                    url = bad_urls[i_bad]
                    num_bad_urls += 1
                    i_bad += 1
            elif int(row['is_fraud']) == 0:
                if random.random()+.995 <= threshold:
                    if i_bad >= len(bad_urls):
                        i_bad = 0
                    url = bad_urls[i_bad]
                    num_incorrect_bad_urls += 1
                    i_bad += 1
                else:
                    if i_good >= len(urls['good']):
                        i_good = 0
                    url = good_urls[i_good]
                    num_good_urls +=1
                    i_good += 1

            # Update the urls column
            row['url'] = url
            writer.writerow(row)

    print("Finished processing transactions.")
    print(f"Number of good urls: {num_good_urls}")
    print(f"Number of bad urls: {num_bad_urls}")
    print(f"Number of incorrectly paired good urls: {num_incorrect_good_urls}")
    print(f"Number of incorrectly paired bad urls: {num_incorrect_bad_urls}")
    # Play a sound to indicate that the process is complete.
    os.system('afplay /System/Library/Sounds/Glass.aiff')
    time.sleep(5)
    # Indicate that the process is complete.
    os.system('say "Process complete, bro"')

def main():
    parser = argparse.ArgumentParser(description='Add urls to transactions')
    parser.add_argument('transactions_file', type=str, help='Path to the transactions CSV file')
    parser.add_argument('urls_file', type=str, help='Path to the urls CSV file')
    parser.add_argument('output_file', type=str, help='Path to the output CSV file')
    parser.add_argument('threshold', type=float, help='Probability threshold for adding bad urls')
    args = parser.parse_args()

    add_urls(args.transactions_file, args.urls_file, args.output_file, args.threshold)


if __name__ == '__main__':
    main()

# Example usage:
# add_urls('transactions.csv', 'urls.csv', 'output.csv', 1, 4)

# Example input CSV:
# Card Number,Zipcode,Amount,is_fraud
# 123456789,12345,100,0
# 234567890,23456,200,0
# 345678901,34567,300,1

# Example output CSV:
# Card Number,Zipcode,Amount,is_fraud,url
# 123456789,12345,100,0,https://good-url.com
# 234567890,23456,200,0,https://good-url.com
# 345678901,34567,300,1,https://bad-url.com