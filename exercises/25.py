from pathlib import Path
import shutil
import os
import re
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

index_content = '''# Welcome

See the full source at https://github.com/old-org/docs for details.
You can also file issues at https://github.com/old-org/docs/issues.
'''

plain_content = '''# Welcome

This is a plain file with no substitutions.
'''

api_content = '''# API Reference

Code samples are in https://github.com/old-org/docs/tree/main/examples.
For setup instructions, visit https://github.com/old-org/docs#setup.
Unrelated link: https://github.com/other-project/tools is not affected.
'''
python_file_contents = '''import shutil
import os
import re
import logging

file = Path("file.txt")
Path.unlink(file)

Code samples are in https://github.com/some-org/docs/tree/main/examples.
For setup instructions, visit https://github.com/different-org/docs#setup.
Unrelated link: https://github.com/other-project/tools is not affected.
'''

# Create various path object directories and then create actual directories
root_dir = Path("25th_lesson")
try:
    shutil.rmtree(root_dir)
    logging.info("I was able to remove the root directory.")
except OSError:
    logging.info("Wasn't able to remove the root directory `25th_lesson`.")
    
nested_dir = Path(root_dir / "link_update/content/reference")
content_dir = root_dir / "link_update/content"
nested_dir.mkdir(parents=True, exist_ok=True)
try:
    nested_dir.is_dir()
    logging.info("Successfully created root and nested directories.")
except OSError:
    logging.error("Did not create nested directory.")

# Write index.md
index_file = nested_dir.parent / "index.md"
index_file.write_text(index_content, encoding='utf-8')

# Write plain.md
plain_file = nested_dir.parent / "plain.md"
plain_file.write_text(plain_content, encoding='utf-8')

# Write api.md
api_file = nested_dir / "api.md"
with open(api_file, 'w', encoding='utf-8') as f:
    f.write(api_content)

# Write update_links.py
python_file_path = nested_dir.parent / "update_links.py"
with open(python_file_path, 'w', encoding="utf-8") as f:
    f.write(python_file_contents)
    
content_dir = root_dir / "link_update/content"
dry_run = True
find_uri = "https://github.com/old-org/docs"
replacement_uri = "https://github.com/new-org/docs"
modified_files = []
modified_lines=[]
modified_files_count = 0

# Copy existing directory structure to updated directory structure if it's not a dry run
if dry_run == True:
    content_updated_dir = Path(content_dir.parent) / "content_updated"
    shutil.copytree(content_dir, content_updated_dir)

for file in content_dir.rglob("*.md"):
    modified_file_yes_or_no = False
    relative_path = file.relative_to(content_dir)
    with open(file, "r", encoding="utf-8") as f:
        original_file_contents = f.read()

        # Split file into lines, and each modified line becomes a list entry for later reporting.
        original_lines = original_file_contents.splitlines()
        for line_num, line in enumerate(original_lines, 1):
            original = line
            modified = original
            modified = re.sub(find_uri, replacement_uri, original)
            if modified != original:
                modified_lines.append({"file": file, "line number": line_num, "original": original, "modified": modified})
                modified_file_yes_or_no = True
        modified_file_content = re.sub(find_uri, replacement_uri, original_file_contents)
        
        # If the file is marked as modified, write the new version to the updated path.
        if modified_file_yes_or_no:
            modified_files_count += 1
            #modified_files.append({"file": file, "content": modified_file_content})
            if dry_run == False:
                write_path = content_updated_dir / relative_path
                with open(write_path, 'w', encoding="utf-8") as f:
                    f.write(modified_file_content)

# Whether it's a dry run or not, write the report about the substitutions.
for item in modified_lines:
    print(f"{item["file"].name} line {item["line number"]}:")
    print(f"   OLD: {item["original"].rstrip()}")
    print(f"   NEW: {item["modified"].rstrip()}")
print(f"Total # of affected lines = {len(modified_lines)}.")
print(f"Total # of affected files = {modified_files_count}.")