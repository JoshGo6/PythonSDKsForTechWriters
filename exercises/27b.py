import re
import mistune
from pathlib import Path
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

working_dir = Path("lesson_27/docs/config.md")
code_block_pattern = re.compile(r"^```")
comment_pattern = re.compile(r"^#+\s+.*$")
inside_code_block = False

def heading_increment(heading):
    return '#' + heading.group(0)

with open (working_dir, 'r', encoding='utf-8') as f:
    for line in f:
        if code_block_pattern.search(line):
            inside_code_block = not inside_code_block
        if comment_pattern.search(line) and not inside_code_block:
            print(comment_pattern.sub(heading_increment, line).rstrip())
        else:
            print(line.rstrip())
