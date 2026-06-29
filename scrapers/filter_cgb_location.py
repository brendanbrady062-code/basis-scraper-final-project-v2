"""
Filter CGB CSV by location substring and write a new CSV.
Usage: python scrapers/filter_cgb_location.py --location Hennepin [--input data/file.csv]
"""
import argparse
import csv
import glob
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--location', required=True, help='Location substring to filter (case-insensitive)')
parser.add_argument('--input', help='Input CSV path (optional)')
args = parser.parse_args()

loc = args.location.lower()

# Find latest combined/CGB CSV if input not provided
if args.input:
    input_path = args.input
else:
    files = glob.glob(os.path.join('data', 'basis_values_*.csv'))
    files.extend(glob.glob(os.path.join('data', 'CGB_bids_*.csv')))
    if not files:
        raise SystemExit('No basis_values_*.csv or CGB_bids_*.csv files found in data/')
    input_path = max(files, key=os.path.getmtime)

output_name = f"CGB_bids_{loc.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
output_path = os.path.join('data', output_name)

count = 0
with open(input_path, newline='', encoding='utf-8') as inf, open(output_path, 'w', newline='', encoding='utf-8') as outf:
    reader = csv.DictReader(inf)
    writer = csv.DictWriter(outf, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        if row.get('location') and loc in row['location'].lower():
            writer.writerow(row)
            count += 1

print(f"✓ Filtered {count} rows for location '{args.location}'")
print(f"✓ Saved to: {output_path}")
