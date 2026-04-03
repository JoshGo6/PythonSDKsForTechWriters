import logging
from pathlib import Path

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

mydir = "scantest"
mypath = Path(mydir)
skipped_file_count = 0
included_file_count = 0
if not mypath.is_dir():
    logging.error("%s doesn't exist", mypath)
else:
    logging.debug(f"scan complete: {mypath}")
    for md_path in mypath.rglob("*.md"):
        md_path = str(md_path)
        md_file = md_path.rsplit("/", 1)[-1]
        if md_file.startswith("old"):
            skipped_file_count += 1
            logging.warning(f"Skipping file. Skipped file count is {skipped_file_count}")
            continue
        included_file_count += 1
        logging.debug(f"{md_file}")
        print(f"{md_file}")
        with open(md_path, 'r', encoding='UTF-8') as f:
            total_number_of_lines = 0
            for line_num, line_content in enumerate(f, 1):
                if line_num==1 and line_content.startswith("# "):
                    line_content = line_content.lstrip("# ").rstrip()
                    print(f"  Path: {md_path}")
                    print(f"  Title: {line_content}")
                elif line_num == 1 :
                    print("  No title")
                total_number_of_lines += 1
            print(f"  Lines: {total_number_of_lines}")
            print()
    print(f"There were {included_file_count} included files and {skipped_file_count} skipped files.")
