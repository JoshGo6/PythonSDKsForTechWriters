from pathlib import Path
import logging
import json

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
            if status == "published":
                published_pages.append(contents)
        except json.JSONDecodeError as e:
            logging.warning(f"Filename {file.name} contains invalid JSON.")
        except KeyError as e:
            logging.warning(f"File {file.name} is missing the following key(s): {e}")

published_pages = sorted(published_pages, key=lambda x: x["word_count"], reverse=True)
logging.debug(json.dumps(published_pages, indent=2, sort_keys=True))
try:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "published_summary.json", 'w', encoding='utf-8') as f:
        json.dump(published_pages, f, indent=2)
    logging.debug(f"Wrote {len(published_pages)} records to published_summary.json.")
except Exception as e:
    logging.warning(f"Unable to write published_summary.json: {e}")        
