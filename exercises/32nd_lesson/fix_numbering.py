'''Sometimes you need to manually insert items in a document, including new headings, where the headings contain numerals, which makes the later headings have incorrect numberings. This script fixes that.'''

import argparse
import re
from pathlib import Path
from tabulate import tabulate
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
def update(content):
    match_text = re.match(r'^(#+ Lesson )(\d+)(.*?)', content)
    if not match_text:
        return content
    else:
        old_num = match_text.group(2)
        new_num = str(int(old_num) + 1)
        logging.info(f"Old num: {old_num}. New num: {new_num}.")
        return(re.sub(old_num, new_num, content))

parser = argparse.ArgumentParser(description="Increment the integer in headings that occur beyond a certain point in a Markdown document.")
parser.add_argument("path", help="Path to input file.")
parser.add_argument("start_text", help="Text to look for after which headings should be updated.")
parser.add_argument("--verbose", action="store_true", help="Writes changes to terminal.")
args=parser.parse_args()

input_file = Path(args.path)
search_text = args.start_text
unaffected_lines = []
replacement_lines = []

if not input_file.exists():
    logging.error("The file doesn't exist.")
    sys.exit(1)

with open(input_file, 'r', encoding='utf-8') as f:
    numbered_lines = list(enumerate(f))
    in_code_block = False
    for line_num, content in numbered_lines:
        unaffected_lines.append(content)
        logging.debug(f"{line_num}: {content}")
        if re.findall(r'^```', content):
            in_code_block = not in_code_block
            continue
        elif in_code_block:
            continue
        elif re.findall(rf'^#.*?{search_text}', content):
            replacement_line_start = line_num
            unaffected_lines.pop()
            break
    for line_num, content in numbered_lines:
        if line_num >= replacement_line_start:
            replacement_lines.append(update(content))

logging.info(f"Line replacement begins with the following line: '{replacement_line_start}'")
logging.info(f"The unaffected_lines list contains {len(unaffected_lines)} lines.")
logging.info(f"The replacement_lines list contains {len(replacement_lines)} lines.")

with open(input_file, 'w', encoding='utf-8') as f:
    for line in unaffected_lines:
        f.write(line)
    for line in replacement_lines:
        f.write(line)
    