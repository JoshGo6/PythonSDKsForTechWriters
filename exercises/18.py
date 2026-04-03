# debug_report.py

def build_label(record):
    priority = record.get("priority", None)
    if priority is not None:
        return "P" + str(priority)
    return "Priority unknown"

def summarize_issue(records, index):
    rec = records[index]
    title = rec["title"]
    author = rec.get("author", "unassigned")
    label = build_label(rec)
    return f"[{label}] {title} (by {author})"

issues = [
    {"title": "Fix auth flow", "priority": 1, "author": "Dana"},
    {"title": "Update README", "priority": 2, "author": "Eli"},
    {"title": "Add rate-limit docs", "priority": "1"},
    {"title": "Refactor parser", "priority": 3, "author": "Sam"}
]

header = "=== Issue Report ==="
print(header)
print("")

for i in range(len(issues)):
    line = summarize_issue(issues, i)
    print(line)

print("")
footer_count = 4
print(f"Total issues: {footer_count}")