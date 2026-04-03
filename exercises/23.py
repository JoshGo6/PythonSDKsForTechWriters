import logging
import re

logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

md_lines = [
"See the [    installation guide](https://example.com/install) for details.",
"No links on this line.",
"Check [API reference](https://api.example.com/v2) and [changelog](https://example.com/changes).",
"Visit [docs](https://example.com/docs).",
"    ",
"Refer to issue #203 and issue #48 for background.",
]

def audit_links(lines):
    link_total = 0
    links = []
    nums = 0
    lines_with_nums = []
    
    for line in enumerate(lines, 1):
        link_text = re.search(r"\[((?:\s|\w)+)\]\(http.*?\)", line[1])
        issue_nums = re.findall(r"#(\d{1,4})\s", line[1])
        if link_text:
            link_total += 1
            link_text_string = link_text.group(1).strip()
            logging.debug(link_text_string)
            links.append((line[0], link_text_string))
        elif issue_nums:
            logging.debug(issue_nums)
            nums += 1
            lines_with_nums.append((line[0], issue_nums))

    print("These are the links:")
    for link in links:
        print(f"Line {link[0]}: {link[1]}")
    print("These are the numbers:")
    for line in lines_with_nums:
        list_of_nums=""
        for num in line[1]:
            list_of_nums += f"{num}, "
        print(f"Line: {line[0]}: {list_of_nums.rstrip(", ")}")

audit_links(md_lines)