import csv
import argparse

# Create the argument parser
parser = argparse.ArgumentParser(description='Add quotes to fields in a CSV file')
parser.add_argument('input_file', help='Path to the input CSV file')
parser.add_argument('output_file', help='Path to the output CSV file')

# Parse the arguments
args = parser.parse_args()

# Open the input file for reading and the output file for writing
with open(args.input_file, 'r', newline='') as infile, \
     open(args.output_file, 'w', newline='') as outfile:
    
    # Create the CSV reader and writer objects
    # Create the CSV reader and writer objects
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONE, escapechar='\\')

    
    # Write the header row to the output file
    writer.writeheader()
    
    # Loop through each row in the input file and write it to the output file
    for row in reader:
        # Create a new dictionary to hold the modified row
        new_row = {}
        
        # Loop through each field in the row and add quotes to the value
        for fieldname in fieldnames:
            value = row[fieldname]
            new_value = f'"{value}"' if value else ''
            new_row[fieldname] = new_value
        
        # Write the modified row to the output file
        writer.writerow(new_row)