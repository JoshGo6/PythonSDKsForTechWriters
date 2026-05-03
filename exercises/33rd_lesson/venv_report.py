import argparse
from pathlib import Path
import logging
import json
import os
import sys
import re
import idna
import importlib
from tabulate import tabulate

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

parser = argparse.ArgumentParser(description="Inspects a virtual environment's installed packages.")
parser.add_argument("path", help="Path to requirements file.")
parser.add_argument("--output", help="Path to output file.")
args = parser.parse_args()

if sys.prefix == sys.base_prefix:
    logging.error("You are not in a virtual environment. Exiting.")
    sys.exit(1)

package_name_regex = re.compile(r'^([\w-]+)==')
package_names = []
successful_imports = []
unsuccessful_imports = []

input_file = Path(args.path)
output_file = None
if args.output:
    output_file = Path(args.output)

if not input_file.name == "requirements.txt":
    logging.error("Input file must be named 'requirements.txt'. Exiting.")
    sys.exit(2)
try:
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            matched_line = package_name_regex.search(line)
            package_names.append(matched_line.group(1))
except FileNotFoundError as e:
    logging.error("Input file doesn't exist. Exiting.")
    sys.exit(3)

for package in package_names:
    try:
        importlib.import_module(package.replace("-", "_"))
        successful_imports.append(package)
    except ModuleNotFoundError as e:
        unsuccessful_imports.append(package)

output_label = os.getenv("REPORT_LABEL")
if not output_label:
    output_label = "unlabeled"

report = {"available": successful_imports, "missing": unsuccessful_imports}

if not output_file:
    print(output_label)
    print(tabulate(report, headers=["Installed", "Not installed"], tablefmt="fancy_grid"))
else:
    output_file.write_text(json.dumps(report, indent=2, sort_keys=True), encoding='utf-8')



