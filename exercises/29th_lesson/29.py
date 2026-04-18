from pathlib import Path
from sys import argv, exit
import re
import json
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

args = argv

def usage_error():
    logging.critical("The correct format is python 29.py <input_markdown_file> <output_json_path>")
    exit(1)

if len(args) != 3:
    usage_error()

input_path = Path(args[1])
if not input_path.name.endswith(".md") or not input_path.exists():
    usage_error()




