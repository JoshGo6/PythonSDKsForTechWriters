from pathlib import Path
from sys import argv, exit
import re
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def validate_write_path(write_path):
    if "/" in str(write_path):
        write_dir = str(write_path).rsplit("/", 1)[0]
        if not Path(write_dir).exists():
            print(f"The output directory doesn't exist.")
            Path(write_dir).mkdir(parents=True, exist_ok=True)
            print(f"Successfully created output directory.")


args = argv
input_path = Path(args[1])
write_path = Path(args[2])
valid_input = len(args) == 3 and input_path.name.endswith(".md") and input_path.exists() and write_path.name.endswith(".json")
if not valid_input:
    logging.critical("The correct format is python 29.py <input_markdown_file> <output_json_path>")
    exit(1)

write_path_contains_dir = "/" in str(write_path)
if write_path_contains_dir:
    validate_write_path(write_path)

output = []
input_text = input_path.read_text(encoding='utf-8')
for match in re.finditer(r'\[(.*?)\]\((.*?)\)', input_text):
    logging.debug(f"The link text is {match.group(1)}, and the URL is {match.group(2)}.")
    output.append(dict(link_text = match.group(1), url = match.group(2)))

try:
    with open(write_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, sort_keys=True)
    print(f"Extracted {len(output)} links to '{write_path}'")
except FileNotFoundError as e:
    logging.critical('Unable to write to file.')




