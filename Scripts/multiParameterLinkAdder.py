import concurrent.futures
import argparse
import random
import time
import csv
import os

def add_links(transactions_file, links_file, output_file, threshold, num_threads):
    print("Reading links CSV file...")
    # Read the links CSV file and extract the phishing, benign and defacement links
    phishing_links = []
    benign_links = []
    defacement_links = []
    with open(links_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['type'] == 'phishing':
                phishing_links.append(row['url'])
            elif row['type'] == 'benign':
                benign_links.append(row['url'])
            elif row['type'] == 'defacement':
                defacement_links.append(row['url'])

        # Make copies of the original phishing and benign links lists so we can reinitialize them
        phishing_links_original = list(phishing_links)
        benign_links_original = list(benign_links)
        defacement_links_original = list(defacement_links)
    
    print("Processing transactions...")
    num_phishing_links = 0
    num_benign_links = 0
    num_defacement_links = 0
    num_incorrect_phishing_links = 0
    num_incorrect_benign_links = 0
    num_incorrect_defacement_links = 0
    # Process the transactions using multiple threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        with open(output_file, 'w', newline='') as f_out, open(transactions_file, 'r') as f_in:
            reader = csv.DictReader(f_in)
            fieldnames = reader.fieldnames + ['Link']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for i, row in enumerate(reader):
                print(f"Processing transaction {i}...")
                if int(row['is_fraud']) == 1:
                    if random.random() <= .9948:
                        url = executor.submit(random.choice, benign_links)
                        num_incorrect_benign_links += 1
                    else:
                        if(random.random() <= .2251):
                            url = executor.submit(random.choice, defacement_links)
                            num_defacement_links += 1
                        else:
                            url = executor.submit(random.choice, phishing_links)
                            num_phishing_links += 1
                elif int(row['is_fraud']) == 0:
                    if random.random() <= .0052:
                            url = executor.submit(random.choice, phishing_links)
                            num_incorrect_phishing_links += 1
                    else:
                        if random.random() <= 1.0249:
                            url = executor.submit(random.choice, defacement_links)
                            num_defacement_links += 1
                        else:
                            url = executor.submit(random.choice, benign_links)
                            num_benign_links += 1
                # Update the links column
                link = url.result()
                row['Link'] = link
                writer.writerow(row)

    print("Finished processing transactions.")
    print(f"Number of phishing links: {len(phishing_links_original)}")
    print(f"Number of benign links: {len(benign_links_original)}")
    print(f"Number of defacement links: {len(defacement_links_original)}")
    print(f"Number of incorrectly paired phishing links: {num_incorrect_phishing_links}")
    print(f"Number of incorrectly paired benign links: {num_incorrect_benign_links}")
    print(f"Number of incorrectly paired defacement links: {num_incorrect_defacement_links}")
    os.system('afplay /System/Library/Sounds/Glass.aiff')
    
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
# 234567890,23456,200,0,https://deface-link.com
# 345678901,34567,300,1,https://bad-link.com
