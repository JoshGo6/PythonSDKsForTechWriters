import json
from tabulate import tabulate
from pathlib import Path
import argparse
import logging
import sys

logging.basicConfig(level=20, format="%(levelname)s: %(message)s")

parser = argparse.ArgumentParser(description="Outputs to the CLI tabulated data from a JSON file.")
parser.add_argument("json_path", help="Path to the input JSON file.")
parser.add_argument("--category", help="Filter the output to data matching this value of the 'category' key.")
cli_args = parser.parse_args()

category = None

try:
    with open(Path(cli_args.json_path), "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError as e:
    logging.error(f"File {cli_args.json_path} does not exist.")
    sys.exit(1)

data.sort(key=lambda dictionary: dictionary["category"].lower())
logging.debug(json.dumps(data, indent=2, sort_keys=True))
loaded_num = len(data)

if cli_args.category:
    category = cli_args.category
    categories = set()
    for item in data:
        categories.add(item["category"])
    if not category in categories:
        logging.warning(f"'category' key value '{cli_args.category}' not present in JSON file.")
        sys.exit(2)
    data = list(filter(lambda x: x["category"] == category, data))
    data.sort(key=lambda x: (x["name"]).lower())

print(tabulate(data, headers="keys", tablefmt="grid"))
logging.info(f"{loaded_num} dependencies were loaded, and {len(data)} were displayed.")