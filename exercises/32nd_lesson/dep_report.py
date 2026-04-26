import json
from tabulate import tabulate
from pathlib import Path
import argparse
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

parser = argparse.ArgumentParser(description="Outputs to the CLI tabulated data from a JSON file.")
parser.add_argument("json_path", help="Path to the input JSON file.")
parser.add_argument("--category", help="Filter the output to data matching this value of the 'category' key.")
cli_args = parser.parse_args()

try:
    with open(Path(cli_args.json_path), "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError as e:
    logging.error(f"File {cli_args.json_path} does not exist.")

data.sort(key=lambda dictionary:dictionary["category"])
logging.debug(json.dumps(data, indent=2, sort_keys=True))
