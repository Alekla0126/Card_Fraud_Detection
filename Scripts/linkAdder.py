import concurrent.futures
import argparse
import string
import random
import time
import csv
import os

def is_printable(s):
    return all(c in string.printable for c in s)

def add_links(transactions_file, links_file, output_file, threshold, num_threads):
    print("Reading links CSV file...")
    # Read the links CSV file and extract the good and bad links
    good_links = []
    bad_links = []
    with open(links_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Label'] == 'good':
                good_links.append(row['URL'])
            elif row['Label'] == 'bad':
                bad_links.append(row['URL'])

    # Drop rows containing non-printable characters from the links lists
    print('Drop rows containing non-printable characters...')
    good_links = [link for link in good_links if is_printable(link)]
    bad_links = [link for link in bad_links if is_printable(link)]

    print("Processing transactions...")
    num_good_links = 0
    num_bad_links = 0
    num_incorrect_bad_links = 0
    num_incorrect_good_links = 0
    # Process the transactions using multiple threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        with open(output_file, 'w', newline='') as f_out, open(transactions_file, 'r') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = reader.fieldnames + ['Link']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            # Loop through rows.
            for i, row in enumerate(reader):
                print(f"Processing transaction {i}...")
                # Get the link for this row.
                link = None
                if int(row['is_fraud']) == 1:
                    if random.random()+.00521 <= threshold:
                        link = good_links[i % len(good_links)]
                    else:
                        link = bad_links[i % len(bad_links)]
                        num_incorrect_good_links += 1 
                elif int(row['is_fraud']) == 0:
                    if random.random()+.995 <= threshold:
                        link = bad_links[i % len(bad_links)]
                    else:
                        link = good_links[i % len(good_links)]
                        num_incorrect_bad_links += 1

                # Update the links column.
                row['Link'] = link
                writer.writerow(row)

                if link in good_links:
                    num_good_links += 1
                elif link in bad_links:
                    num_bad_links += 1

    print("Finished processing transactions.")
    print(f"Number of good links: {num_good_links}")
    print(f"Number of bad links: {num_bad_links}")
    print(f"Number of incorrectly paired good links: {num_incorrect_good_links}")
    print(f"Number of incorrectly paired bad links: {num_incorrect_bad_links}")
    # Play a sound to indicate that the process is complete.
    os.system('afplay /System/Library/Sounds/Glass.aiff')
    time.sleep(5)
    # Indicate that the process is complete.
    os.system('say "Process complete, bro"')
    

def main():
    parser = argparse.ArgumentParser(description='Add links to transactions')
    parser.add_argument('transactions_file', type=str, help='Path to the transactions CSV file')
    parser.add_argument('links_file', type=str, help='Path to the links CSV file')
    parser.add_argument('output_file', type=str, help='Path to the output CSV file')
    parser.add_argument('threshold', type=float, help='Probability threshold for adding bad links')
    parser.add_argument('num_threads', type=int, help='Number of threads to use')

    args = parser.parse_args()

    add_links(args.transactions_file, args.links_file, args.output_file, args.threshold, args.num_threads)

if __name__ == '__main__':
    main()

# Example usage:
# add_links('transactions.csv', 'links.csv', 'output.csv', 1, 4)

# Example input CSV:
# Card Number,Zipcode,Amount,is_fraud
# 123456789,12345,100,0
# 234567890,23456,200,0
# 345678901,34567,300,1

# Example output CSV:
# Card Number,Zipcode,Amount,is_fraud,Link
# 123456789,12345,100,0,https://good-link.com
# 234567890,23456,200,0,https://good-link.com
# 345678901,34567,300,1,https://bad-link.com