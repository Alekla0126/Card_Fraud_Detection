#!/usr/bin/env python3

import sys
import csv

def clean_and_quote_url(url):
    cleaned_url = url.replace('"', '""')
    return f'"{cleaned_url}"'

if __name__ == "__main__":
    for line in sys.stdin:
        url = line.strip()
        cleaned_url = clean_and_quote_url(url)
        print(cleaned_url)