from pathlib import Path
import logging
import json
import re

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

valid_pages = []
published_pages = []
working_dir = Path("pages")

for file in working_dir.glob("*.json"):
    with open(file, 'r', encoding='utf-8') as f:
        try:
            contents = json.load(f)
            title = contents["title"]
            status = contents["status"]
            tags = contents["tags"]
            word_count = contents["word_count"]
            valid_pages.append(contents)
            logging.info(f"Loaded file {file.name}.")
            published_pages = list(filter(lambda x: x["status"] == "published", valid_pages))
        except json.JSONDecodeError as e:
            logging.warning(f"Filename {file.name} contains invalid JSON.")
        except KeyError as e:
            logging.warning(f"File {file.name} is missing the following key(s): {e}")

logging.info(f"Successfully loaded {len(valid_pages)} files.")

published_pages.sort(key=lambda x: x["word_count"])
word_count=0
logging.debug(json.dumps(published_pages, indent=2, sort_keys=True))

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
try:
    with open(output_dir / "published_summary.json", 'w', encoding='utf-8') as f:
        json.dump(published_pages, f, indent=2)
    logging.info(f"Wrote {len(published_pages)} records to published_summary.json.")
except Exception as e:
    logging.warning(f"Unable to write published_summary.json: {e}")

with open(output_dir / "published_summary.json", 'r', encoding='utf-8') as f:
    try:
        structured_content = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Problem loading JSON: {e}")
    with open(output_dir / "published_report.md", 'w', encoding='utf-8') as f:
        f.write("# Published Pages Report\n\n")
        f.write(f"Total published pages: {len(published_pages)}\n")
        for record in structured_content:
            word_count += int(record.get("word_count", 0))
        f.write(f"Combined word count: {word_count}\n")
        for record in structured_content:
            f.write(f"\n## {record["title"]}\n\n")
            for key, value in record.items():
                if key == "title":
                    continue
                elif isinstance(value, list):
                    f.write(f"- **{key.capitalize().replace("_", " ")}**: {', '.join(value)}\n")
                else:
                    f.write(f"- **{key.capitalize().replace("_", " ")}**: {value}\n")        
