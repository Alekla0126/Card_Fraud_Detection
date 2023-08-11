import csv
import argparse

def add_quotes(input_file, output_file):
    # Open the input file and read its contents
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)

    # Add quotes to the URLs
    for row in data[1:]:
        row[0] = f'"{row[0]}"'

    # Write the modified data to a new file
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Label'])
        for row in data[1:]:
            writer.writerow(row)

    # Open the new file and replace the triple quotes with double quotes
    with open(output_file, 'r') as f:
        content = f.read()
    content = content.replace('"""', '"')

    # Write the final output back to the new file
    with open(output_file, 'w') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description='Add quotes to URLs')
    parser.add_argument('input_file', type=str, help='Path to the input CSV file')
    parser.add_argument('output_file', type=str, help='Path to the output CSV file')

    args = parser.parse_args()

    add_quotes(args.input_file, args.output_file)

if __name__ == '__main__':
    main()
