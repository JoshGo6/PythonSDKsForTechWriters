import sys
import json
import argparse
from pathlib import Path
import logging

import logging

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

parser = argparse.ArgumentParser(description="Converts a JSON file to a Python dictionary.")
parser.add_argument("input_file", help="path to input JSON file.")
parser.add_argument("--count-only", help="Only print a summary of file contents.", action="store_true")
args = parser.parse_args()
input_file = args.input_file
just_summarize = args.count_only

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
except FileNotFoundError as e:
    logging.error(e)

if just_summarize:
    print(f"There are {len(records)} records in the file.")
    sys.exit(0)

for record in records:
    if record.get("name", None) is None or record.get("status", None) is None:
        continue
    print(f"- {record.get("name", None)}: {record.get("status", "Died")}")