# Lesson 11: Dictionaries I — Keys, Values, and Lookups

---

## 1. Terminology and Theory

A **dictionary** is a collection that maps **keys** to **values**. Unlike a list, which you index with an integer position, a dictionary lets you look up a value by a meaningful name — a key you chose yourself.

Dictionaries are the most important data structure for SDK and API work. Virtually every JSON response from an API, every SDK object serialized to a plain structure, and every configuration block you'll encounter is dict-shaped: a set of named fields, each holding a value.

A few terms to fix in your vocabulary:

- **Key** — the label you use to look something up. Keys are usually strings in API work, though Python allows other types.
- **Value** — the data associated with a key. A value can be anything: a string, a number, a list, another dict, `None`.
- **Key-value pair** — a single entry in a dictionary; one key and its value together.
- **Lookup** — retrieving a value by its key.

Dictionaries are **ordered** in Python 3.7+, meaning entries stay in the order you inserted them. They are also **mutable** — you can add, change, or remove entries after creation.

One important constraint: **keys must be unique** within a dictionary. If you assign to the same key twice, the second assignment silently overwrites the first.

---

## 2. Syntax

### Creating a dictionary

```python
# Empty dictionary
d = {}

# Dictionary with initial values
repo = {
    "name": "docs-site",
    "owner": "acme-corp",
    "private": False,
    "open_issues": 12
}
```

Curly braces `{}` delimit the dictionary. Each entry is written as `key: value`, and entries are separated by commas. Trailing commas after the last entry are legal and common.

### Accessing a value by key

```python
repo["name"]        # Returns "docs-site"
repo["open_issues"] # Returns 12
```

Square-bracket access returns the value if the key exists. If the key does not exist, Python raises a `KeyError` — the same error you practiced recognizing in Lesson 18 (coming later). For now, know that accessing a key that isn't there will crash your script.

### Safer lookups with `.get()`

```python
repo.get("name")              # Returns "docs-site"
repo.get("license")           # Returns None (key missing, no crash)
repo.get("license", "MIT")    # Returns "MIT" as the default
```

`.get(key)` returns `None` if the key is missing instead of raising an error. `.get(key, default)` returns the default you supply. This is the safer, more common pattern in SDK scripts where you can't always guarantee every field is present.

### Adding and updating keys

```python
repo["language"] = "Python"        # Adds a new key
repo["open_issues"] = 14           # Overwrites an existing key
```

Assignment to a key either creates it (if new) or overwrites it (if already present). There is no separate "add" method — the same syntax handles both cases.

### Checking whether a key exists

```python
"name" in repo      # True
"license" in repo   # False
```

The `in` operator tests key presence and returns a boolean. This is the correct way to check before accessing a key when you're uncertain.

### Getting a count of entries

```python
len(repo)   # Returns the number of key-value pairs
```

---

## 3. Worked Examples

### Example 1 — Building and reading a dict that mirrors an API response

Real SDK objects often expose their data as dictionaries when you inspect or serialize them. Here's a dict that looks like a simplified GitHub repository response, and a short script that extracts the fields a docs writer would care about.

```python
repo = {
    "name": "api-reference",
    "full_name": "acme-corp/api-reference",
    "private": False,
    "description": "Public API reference documentation",
    "open_issues_count": 7,
    "default_branch": "main"
}

print(f"Repository: {repo['full_name']}")
print(f"Description: {repo['description']}")
print(f"Default branch: {repo['default_branch']}")
print(f"Open issues: {repo['open_issues_count']}")
```

**Output:**

```
Repository: acme-corp/api-reference
Description: Public API reference documentation
Default branch: main
Open issues: 7
```

Notice that the keys are exactly the field names you'd see in a GitHub API JSON response. This is the mental model to hold: a dictionary _is_ the JSON object — just in Python form.

---

### Example 2 — Using `.get()` to handle optional fields safely

API responses often include optional fields that may or may not be present. Using direct key access for optional fields causes crashes; `.get()` handles this cleanly.

```python
issue = {
    "number": 42,
    "title": "Update authentication docs",
    "state": "open",
    "body": "The OAuth section needs a refresh.",
    # "assignee" is intentionally absent — not all issues have one
}

number = issue["number"]         # Required field: direct access is fine
title = issue["title"]           # Required field
assignee = issue.get("assignee", "unassigned")   # Optional: safe fallback
milestone = issue.get("milestone")               # Optional: returns None if missing

print(f"Issue #{number}: {title}")
print(f"Assignee: {assignee}")
print(f"Milestone: {milestone}")
```

**Output:**

```
Issue #42: Update authentication docs
Assignee: unassigned
Milestone: None
```

This pattern — direct access for required fields, `.get()` with a default for optional fields — is the standard pattern in SDK scripts. You'll use it constantly.

---

### Example 3 — Building a dict incrementally and using `in` to guard a lookup

Sometimes you build a dictionary from pieces rather than in one literal. You can also conditionally add entries based on whether a value exists.

```python
# Start with core metadata
pr = {
    "number": 118,
    "title": "Add rate limiting docs",
    "state": "open"
}

# Simulate additional data arriving later
merged_at = None      # This PR hasn't been merged yet
review_comment = "Looks good, minor edits needed."

# Add the merge timestamp only if it's real
if merged_at is not None:
    pr["merged_at"] = merged_at

# Always add the review comment
pr["review_comment"] = review_comment

# Safe read using `in`
if "merged_at" in pr:
    print(f"PR #{pr['number']} merged at: {pr['merged_at']}")
else:
    print(f"PR #{pr['number']} is still open.")

print(f"Review: {pr.get('review_comment', 'No review yet')}")
print(f"Total fields stored: {len(pr)}")
```

**Output:**

```
PR #118 is still open.
Review: Looks good, minor edits needed.
Total fields stored: 4
```

---

## 4. Quick Reference

```shellsession
# Create a dictionary literal
$ python3 -c "
repo = {'name': 'docs-site', 'stars': 42}
print(repo)
"
{'name': 'docs-site', 'stars': 42}

# Access a value by key
$ python3 -c "
repo = {'name': 'docs-site', 'stars': 42}
print(repo['name'])
"
docs-site

# Use .get() with a default to avoid a crash on missing keys
$ python3 -c "
repo = {'name': 'docs-site'}
print(repo.get('license', 'not specified'))
"
not specified

# Add a new key after creation
$ python3 -c "
repo = {'name': 'docs-site'}
repo['language'] = 'Python'
print(repo)
"
{'name': 'docs-site', 'language': 'Python'}

# Check whether a key exists
$ python3 -c "
repo = {'name': 'docs-site', 'stars': 42}
print('stars' in repo)
print('license' in repo)
"
True
False

# Get the number of entries with len()
$ python3 -c "
repo = {'name': 'docs-site', 'stars': 42, 'private': False}
print(len(repo))
"
3
```

---

## 5. Exercises

### Exercise 1 — Build a contributor record and look up its fields

Create a Python script that does the following:

1. Define a dictionary representing a GitHub contributor with these fields: `"login"`, `"contributions"`, and `"url"`.
2. Print each value using f-strings and direct key access.
3. Use `.get()` to retrieve a field called `"company"` that is not present in the dictionary. Provide the string `"not listed"` as the default.
4. Add a new key `"type"` with the value `"User"` to the dictionary after it's been created.
5. Print the final state of the dictionary and the total number of fields it contains.

**Expected output shape** (your values will differ, but the structure must match):

```
Login: monalisa
Contributions: 287
URL: https://github.com/monalisa
Company: not listed
Updated record: {'login': 'monalisa', 'contributions': 287, 'url': 'https://github.com/monalisa', 'type': 'User'}
Total fields: 4
```

---

### Exercise 2 — Classify a list of issues by priority

Create a Python script that does the following:

1. Define a list containing three dictionaries. Each dictionary represents a GitHub issue and has these fields: `"number"`, `"title"`, and `"open_issues_count"` (an integer representing how many related issues exist — treat this as a proxy for priority).
2. Loop over the list. For each issue:
    - Use `.get()` to retrieve `"open_issues_count"`, defaulting to `0` if the key is absent.
    - Use a conditional to classify the issue: if `open_issues_count` is greater than 10, label it `"High"`; if greater than 4, label it `"Medium"`; otherwise label it `"Low"`.
    - Print a formatted line showing the issue number, title, and priority label.

**Expected output shape** (your values and thresholds must produce this classification pattern):

```
Issue #3 — Update OAuth docs [Priority: High]
Issue #17 — Fix broken links [Priority: Medium]
Issue #22 — Typo in README [Priority: Low]
```