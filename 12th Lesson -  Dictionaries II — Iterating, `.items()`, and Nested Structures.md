# Lesson 12: Dictionaries II — Iterating, `.items()`, and Nested Structures

---

## Terminology and Theory

### Iteration

**Iteration** means stepping through a collection one item at a time. You already know how to iterate over lists and strings with a `for` loop. Dictionaries support iteration too, but with a twist: you can iterate over keys alone, values alone, or key-value **pairs** together.

### `.items()`

`.items()` is a dictionary method that returns all key-value pairs as a sequence of two-element groupings. When you loop over `.items()`, each loop turn hands you both the key and its value simultaneously. This is the most common and most readable way to walk through a dictionary.

### Key-Value Pair

A **key-value pair** is a single entry in a dictionary — one key and its associated value, bundled together. When you unpack a pair from `.items()`, you give each piece its own variable name on the left side of the `in` keyword.

### Nested Structure

A **nested structure** is a dict or list that contains other dicts or lists as values. API responses and SDK return values are almost always nested. For example, a GitHub issue object might contain a `user` field whose value is itself a dict with a `login` field. Reading nested structures means chaining key accesses: `issue["user"]["login"]`.

### Defensive Access

**Defensive access** means protecting your code against missing keys before they crash your script. You already learned `.get()` in Lesson 11. In Lesson 12, the pattern extends: use `.get()` first to retrieve an inner dict or value, and then guard with an `if` check before going deeper.

---

## Syntax Section

### Iterating with `.items()`

```python
for key, value in my_dict.items():
    print(key, value)
```

- `my_dict.items()` produces all key-value pairs.
- `key, value` on the left side of `in` unpacks each pair into two separate variables. You can name these anything — `k, v`, `field, data`, etc.
- The loop body runs once per pair.

### Iterating keys only (less common, but you'll see it)

```python
for key in my_dict:
    print(key)
```

Iterating a dict directly gives you keys only. `.items()` is preferred when you need both sides.

### Accessing a nested dict safely

```python
# Risky — crashes if "user" key is missing
login = record["user"]["login"]

# Safe — returns None (or a default) if "user" is absent
user = record.get("user")
if user:
    login = user.get("login", "unknown")
```

- `.get("user")` returns `None` if the key is absent instead of raising a `KeyError`.
- The `if user:` guard prevents you from calling `.get("login")` on `None`.
- `.get("login", "unknown")` supplies a fallback string when the inner key is also missing.

### Iterating a list of dicts

```python
records = [
    {"name": "alpha", "state": "open"},
    {"name": "beta"},          # missing "state"
]

for record in records:
    name = record.get("name", "unnamed")
    state = record.get("state", "unknown")
    print(f"{name}: {state}")
```

This is the pattern you will use constantly when processing SDK results — a list of dict-like objects where some fields may be absent.

---

## Worked Examples

### Example 1 — Printing all fields of a single dict

```python
repo = {
    "name": "docs-toolkit",
    "language": "Python",
    "stars": 42,
    "archived": False,
}

for field, value in repo.items():
    print(f"{field}: {value}")
```

**What is happening:** `repo.items()` produces four pairs. Each pass through the loop binds `field` to a key string and `value` to whatever that key holds. The f-string formats both into a readable line. The output is:

```
name: docs-toolkit
language: Python
stars: 42
archived: False
```

---

### Example 2 — Reading a nested dict safely

```python
issue = {
    "title": "Fix broken links in README",
    "state": "open",
    "user": {
        "login": "jdoe",
        "site_admin": False,
    },
}

title = issue.get("title", "No title")
state = issue.get("state", "unknown")

user = issue.get("user")
if user:
    login = user.get("login", "unknown")
else:
    login = "unknown"

print(f"Issue: {title}")
print(f"State: {state}")
print(f"Opened by: {login}")
```

**What is happening:** The outer dict is accessed with `.get()` for safety, even though these keys happen to exist. The `user` value is itself a dict, so it must be retrieved first and checked before drilling into it. If the `user` key had been missing, `.get("user")` would have returned `None`, the `if user:` branch would have been skipped, and `login` would have been set to `"unknown"` without a crash.

Output:

```
Issue: Fix broken links in README
State: open
Opened by: jdoe
```

---

### Example 3 — Iterating a list of nested dicts

```python
pull_requests = [
    {"number": 101, "title": "Add auth section", "author": {"login": "alice"}},
    {"number": 102, "title": "Fix typo in intro", "author": {"login": "bob"}},
    {"number": 103, "title": "Draft: WIP update"},   # missing "author"
]

for pr in pull_requests:
    number = pr.get("number", "?")
    title = pr.get("title", "Untitled")
    author_data = pr.get("author")
    if author_data:
        author = author_data.get("login", "unknown")
    else:
        author = "unknown"
    print(f"PR #{number} by {author}: {title}")
```

**What is happening:** The outer `for` loop steps through the list. Each `pr` is a dict, so `.get()` is used to pull fields safely. The `author` field is itself a nested dict — the same two-step pattern from Example 2 handles the case where it is absent entirely. PR #103 has no `author` key, so it falls through to `"unknown"` gracefully.

Output:

```
PR #101 by alice: Add auth section
PR #102 by bob: Fix typo in intro
PR #103 by unknown: Draft: WIP update
```

---

## Quick Reference

```shellsession
# Iterate over all key-value pairs in a dict
$ python3 -c "
d = {'a': 1, 'b': 2}
for k, v in d.items():
    print(k, v)
"
a 1
b 2

# Safely access a nested dict and guard against missing keys
$ python3 -c "
record = {'user': {'login': 'alice'}}
user = record.get('user')
login = user.get('login', 'unknown') if user else 'unknown'
print(login)
"
alice

# Safely handle a missing nested dict (no crash)
$ python3 -c "
record = {}
user = record.get('user')
login = user.get('login', 'unknown') if user else 'unknown'
print(login)
"
unknown

# Iterate a list of dicts, using .get() with a fallback on each field
$ python3 -c "
items = [{'name': 'alpha', 'state': 'open'}, {'name': 'beta'}]
for item in items:
    print(item.get('name', '?'), item.get('state', 'unknown'))
"
alpha open
beta unknown
```

---

## Exercises

### Exercise 1 — Summarize a configuration dict

Create a file called `config_summary.py`. At the top of the file, define the following dictionary exactly as written:

```python
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
```

Your script must:

1. Use `.items()` to iterate over the top-level keys and print each one, but format the output differently based on the value type:
    - If the value is a `dict`, print the key followed by `"(nested)"` instead of the value itself.
    - If the value is a `list`, print the key followed by the number of items in the list (e.g., `tags: 3 item(s)`).
    - Otherwise, print the key and value normally.
2. After the loop, safely retrieve the author's `email` using `.get()` on the nested `author` dict and print it on its own line prefixed with `"Contact:"`.

**Expected output:**

```
project: sdk-docs
version: 2.1.0
author: (nested)
tags: 3 item(s)
deprecated: False
Contact: jsmith@example.com
```

---

### Exercise 2 — Filter and report from a list of issue records

Create a file called `issue_report.py`. At the top of the file, define the following list exactly as written:

```python
issues = [
    {"id": 1, "title": "Update auth docs", "state": "open",   "assignee": {"login": "alice"}},
    {"id": 2, "title": "Fix sample code",   "state": "closed", "assignee": {"login": "bob"}},
    {"id": 3, "title": "Add rate-limit note","state": "open",   "assignee": {"login": "alice"}},
    {"id": 4, "title": "Draft: outline",    "state": "open"},
    {"id": 5, "title": "Remove stale links","state": "closed", "assignee": {"login": "carol"}},
]
```

Your script must:

1. Iterate over the list and print **only the open issues**.
2. For each open issue, print a line in this format: `#<id> [<assignee login or "unassigned">] <title>`
3. Use `.get()` with appropriate fallbacks to guard against missing `assignee` or `login` fields.
4. After the loop, print a final line: `Open issues: <count>` where count is the number of open issues printed.

**Expected output:**

```
#1 [alice] Update auth docs
#3 [alice] Add rate-limit note
#4 [unassigned] Draft: outline
Open issues: 3
```