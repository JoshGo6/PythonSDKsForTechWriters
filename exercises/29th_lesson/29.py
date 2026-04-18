from pathlib import Path
from sys import argv, exit
import re
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

args = argv
input_path = Path(args[1])
write_path = Path(args[2])
valid_input = len(args) == 3 and input_path.name.endswith(".md") and input_path.exists() and write_path.name.endswith(".json")
if not valid_input:
    logging.critical("The correct format is python 29.py <input_markdown_file> <output_json_path>")
    exit(1)

output = []
input_text = input_path.read_text(encoding='utf-8')
for match in re.finditer(r'\[(.*?)\]\((.*?)\)', input_text):
    logging.debug(f"The link text is {match.group(1)}, and the URL is {match.group(2)}.")
    output.append(dict(link_text = match.group(1), url = match.group(2)))

print(output)






