#!/bin/bash

# URL to the phishing links tar.gz file
URL="https://raw.githubusercontent.com/mitchellkrogza/Phishing.Database/master/ALL-phishing-links.tar.gz"

# Temporary directory to extract the tar.gz file
TEMP_DIR=$(mktemp -d)

# Download the tar.gz file using curl
curl -o "$TEMP_DIR/phishing-links.tar.gz" "$URL"

# Check if the download was successful
if [ $? -ne 0 ]; then
    echo "Failed to download the file."
    exit 1
fi

# Extract the contents of the tar.gz file
tar -xzf "$TEMP_DIR/phishing-links.tar.gz" -C "$TEMP_DIR"

# Create a CSV file and add header
echo "URL" > dataset.csv

# Find URLs in extracted files and add to the CSV
find "$TEMP_DIR" -type f -exec cat {} \; >> dataset.csv

# Clean up - remove the temporary directory
rm -rf "$TEMP_DIR"
