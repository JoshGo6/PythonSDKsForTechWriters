from pathlib import Path
import re
import logging
from sys import argv
from sys import exit
import shutil

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

if "--execute" in argv:
    dry_run = False
else:
    dry_run = True
file_types = []
hidden_files = []
regular_files_no_extensions = []
regular_files_with_extensions = []

def hidden_file_found(item):
    if item.is_file() and item.name[0] == ".":
        return True
    else:
        return False

def regular_file_found_with_extension(item):
    if item.is_file() and item.name[0] != "." and item.suffix:
        return True
    else:
        return False

def hidden_file_extension_needed(item, file_types):
    if hidden_file_found(item) and item.name.lstrip(".") not in file_types:
        return True
    else:
        return False
    
def regular_file_extension_needed(item, file_types):
    if regular_file_found_with_extension(item) and item.suffix.lstrip(".") not in file_types:
        return True
    else:
        return False

def make_subdirectories(working_dir):
    for item in working_dir.iterdir():
        suffix = item.suffix.lstrip(".")
        if regular_file_extension_needed(item, file_types):
            file_types.append(suffix)
            if dry_run == False:
                Path(working_dir / suffix).mkdir(exist_ok=True)
        elif hidden_file_extension_needed(item, file_types):
            extension = item.name.lstrip(".")
            file_types.append(extension)
            if dry_run == False:
                Path(working_dir / extension).mkdir(exist_ok=True)
    logging.debug(file_types)

try:
    working_dir = Path(argv[1])
    logging.debug(f"The working directory is '{working_dir.resolve()}'.")
except:
    logging.error("No working directory specified. Exiting.")
    exit(1)
make_subdirectories(working_dir)
top_level_files = sorted([entry for entry in working_dir.iterdir() if entry.is_file()])

print("Planned operations:")
for file in top_level_files:
    if hidden_file_found(file):
        hidden_files.append(file)
    elif regular_file_found_with_extension(file):
        regular_files_with_extensions.append(file)
    else:
        regular_files_no_extensions.append(file)

for file_type in file_types:
    for file in regular_files_with_extensions:
        if file.suffix.lstrip(".") == file_type:
            print(f"  {file.name:<10}    -> {file_type}/{file.name}")
            if dry_run == False:
                shutil.move(file, file_type)                
for file in hidden_files:
    print(f"Skipped (hidden file): {file.name}")
for file in regular_files_no_extensions:
    print(f"Skipped (regular file with no extension): {file.name}")