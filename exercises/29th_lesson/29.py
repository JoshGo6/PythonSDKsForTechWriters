from pathlib import Path
from sys import argv, exit
import re
import json
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

args = argv
input_path = Path(args[1])
write_path = Path(args[2])
valid_input = len(args) == 3 and input_path.name.endswith(".md") and input_path.exists() and write_path.name.endswith(".json")
if not valid_input:
    logging.critical("The correct format is python 29.py <input_markdown_file> <output_json_path>")
    exit(1)






