import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def generate_report(pages, min_word_count=100):
    logging.debug(f"DEBUG: generate_report called with {len(pages)} pages, min_word_count={min_word_count}")
    report_lines = []
    skipped = 0
    for page in pages:
        title = page.get("title")
        word_count = page.get("word_count")
        status = page.get("status")
        logging.debug(f"DEBUG: Checking page: {title}")
        if not title:
            logging.warning("WARNING: Page with missing title encountered, skipping")
            skipped = skipped + 1
            continue
        if word_count is None:
            print(f"ERROR: Page '{title}' has no word_count field")
            skipped = skipped + 1
            continue
        if word_count < min_word_count:
            logging.warning(f"WARNING: Page '{title}' has only {word_count} words (below minimum {min_word_count})")
        clean_status = status.strip().lower() if status else "unknown"
        line = f"{title} | {word_count} words | {clean_status}"
        report_lines.append(line)
        logging.debug(f"DEBUG: Added line: {line}")
    logging.info(f"INFO: Report complete. {len(report_lines)} pages included, {skipped} skipped.")
    return report_lines

pages = [
    {"title": "Installation Guide", "word_count": 350, "status": "Published"},
    {"title": "", "word_count": 200, "status": "Draft"},
    {"title": "API Overview", "word_count": None, "status": "Review"},
    {"title": "Quick Start", "word_count": 45, "status": " Draft "},
    {"title": "Authentication", "word_count": 210, "status": "Published"},
]

results = generate_report(pages)
print("--- Final Report ---")
for line in results:
    print(line)