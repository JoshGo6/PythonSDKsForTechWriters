import logging
import re
from pathlib import Path as input_file

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def read_lines(filepath):
    lines = []
    try:
        with open (filepath, "r", encoding="UTF-8") as f:
            for line in f:
                lines.append(line.strip())
    except OSError as e:
        logging.error("We have a problem: %s", e)
    return lines

files = ("20a.txt", "nonexistent_file.txt")
combined_lines=""

for file in files:
    lines = read_lines(file)
    logging.debug(f"The lines object has type {type(lines)}.")
    if not lines:
        continue
    for line in lines:
        logging.debug(line)
    combined_lines = "\n".join(lines)
    print(f"The file {file} has {len(lines)} lines.")
    error_match_objects = re.finditer("ERROR", combined_lines)
    error_match_list = list(error_match_objects)
    print(f"The match object is of type {type(error_match_objects)}.")
    enumerated_matches = enumerate(error_match_objects, 1)
    print("Here's the first time through the iterable loop:")
    for match in enumerated_matches:
        print(f"The match at position {match[0]} starts at the {match[1].start()} position.")
    print("\nHere's the second time through the iterable loop:")
    for match in enumerated_matches:
        print(f"The match at position {match[0]} starts at the {match[1].start()} position.")
    print(f"Now let's make loop through the list a few times:")
    for num in range(0,3):
        if num < 3:
            for item in error_match_list:
                print(item)
    print()

    