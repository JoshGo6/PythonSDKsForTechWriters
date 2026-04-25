'''Sometimes you need to manually insert items in a document, including new headings, where the headings contain numerals, which makes the later headings have incorrect numberings. This script fixes that.'''

import argparse
import re
from pathlib import Path
from tabulate import tabulate
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
def updated_line(content):
    match_text = re.match(r'^#(.*?)(\d+)(.*?)', content)
    if not match_text:
        return content

parser = argparse.ArgumentParser(description="Increment the integer in headings that occur beyond a certain point in a Markdown document.")
parser.add_argument("path", help="Path to input file.")
parser.add_argument("start_text", help="Text to look for after which headings should be updated.")
parser.add_argument("--verbose", action="store_true", help="Writes changes to terminal.")
args=parser.parse_args()

input_file = Path(args.path)
search_text = args.start_text
unaffected_lines = []

if not input_file.exists():
    logging.error("The file doesn't exist.")
    sys.exit(1)

with open(input_file, 'r', encoding='utf-8') as f:
    in_code_block = False
    for line_num, content in enumerate(f):
        logging.debug(f"{line_num}: {content}")
        if re.findall(r'^```', content):
            in_code_block = not in_code_block
            unaffected_lines.append(content)
            continue
        elif in_code_block:
            unaffected_lines.append(content)
            continue
        elif re.findall(rf'^#.*?{search_text}', content):
            replacement_line_start = line_num
            break

with open(input_file, 'w', encoding='utf-8') as f:
    for line_num, content in enumerate(f):
        if line_num < replacement_line_start:
            f.write(unaffected_lines[line_num])
        else:
            f.write(updated_line(content))
