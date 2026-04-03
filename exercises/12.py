'''
config = {
    "project": "sdk-docs",
    "version": "2.1.0",
    "author": {
        "name": "J. Smith",
        "email": "jsmith@example.com",
    },
    "tags": ["python", "sdk", "documentation"],
    "deprecated": False,
}

for key, val in config.items():
    if isinstance(val, dict):
        output = "(nested)"
    elif isinstance(val, list):
        output = str(len(val)) + " item(s)"
    else:
        output = val
    print(f"{key}: {output}")
user_exists = config.get("author")
if user_exists:
    print(f"Contact: {user_exists.get("email", "unknown")}")
'''

issues = [
    {"id": 1, "title": "Update auth docs", "state": "open",   "assignee": {"login": "alice"}},
    {"id": 2, "title": "Fix sample code",   "state": "closed", "assignee": {"login": "bob"}},
    {"id": 3, "title": "Add rate-limit note","state": "open",   "assignee": {"login": "alice"}},
    {"id": 4, "title": "Draft: outline",    "state": "open"},
    {"id": 5, "title": "Remove stale links","state": "closed", "assignee": {"login": "carol"}},
]

count = 0
for issue in issues:
    if issue.get("state") == "open":
        id = issue.get("id")
        assignee = issue.get("assignee")
        login = assignee.get("login", "unknown") if assignee else "unknown"
        title = issue.get("title") 
        count += 1
        print(f"{id} {login:10s} {title}")
print(f"Open issues: {count}")
'''
1. Iterate over the list and print **only the open issues**.
2. For each open issue, print a line in this format: `#<id> [<assignee login or "unassigned">] <title>`
3. Use `.get()` with appropriate fallbacks to guard against missing `assignee` or `login` fields.
4. After the loop, print a final line: `Open issues: <count>` where count is the number of open issues printed.
'''