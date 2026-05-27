# Lesson 40: List Comprehensions — Reading Compact Python

## Terminology and Theory

**List comprehension:** A one-line syntax for building a new list from an iterable. Instead of writing a `for` loop that calls `.append()` on each pass, a comprehension puts the entire operation inside square brackets. You will see comprehensions constantly in SDK source code, example scripts, and Python documentation — they are one of the most common Python idioms.

**Expression:** The part of the comprehension that produces each value in the new list. It can be a variable, a function call, an f-string, a method call, a dict lookup — anything that evaluates to a value.

**Filter clause:** An optional `if` at the end of the comprehension that keeps only the items where the condition is `True`. Items that fail the condition are silently skipped.

**Mental model — "unpack to a loop":** Every comprehension can be rewritten as an equivalent `for` loop with `.append()`. When you encounter a comprehension you don't immediately understand, translate it into the loop form. Once the loop form makes sense, you understand the comprehension. This is the single most useful skill for reading Python written by other developers.

The basic form:

```
[expression for variable in iterable]
```

The filtered form:

```
[expression for variable in iterable if condition]
```

Both forms produce a new list. The original iterable is never modified.

> [!note] This lesson teaches comprehensions as both a reading and a writing skill. You need to be able to look at someone else's comprehension and understand it, and you need to be able to write simple ones yourself. The emphasis is on recognition — being able to mentally unpack a comprehension into a loop — because that is what you'll do most often when reading SDK code.

## Syntax Section

### Basic comprehension

```python
new_list = [expression for item in iterable]
```

This is equivalent to:

```python
new_list = []
for item in iterable:
    new_list.append(expression)
```

The `expression` is evaluated once per item, and the result is added to `new_list`. The `item` variable is available inside the expression.

### Filtered comprehension

```python
new_list = [expression for item in iterable if condition]
```

This is equivalent to:

```python
new_list = []
for item in iterable:
    if condition:
        new_list.append(expression)
```

The `condition` is checked for each item. Only items where the condition evaluates to `True` make it into the new list.

### What goes in the expression

The expression can be anything that produces a value:

- A variable by itself: `[x for x in items]` (copies the list)
- A method call: `[name.lower() for name in names]`
- An f-string: `[f"{name}: {score}" for name, score in pairs]`
- A function call: `[len(word) for word in words]`
- A dictionary lookup: `[d["name"] for d in records]`
- Arithmetic: `[n * 2 for n in numbers]`

### What goes in the condition

The condition is any expression that evaluates to a truthy or falsy value:

- A comparison: `if x > 0`
- A method call that returns a bool: `if name.startswith("test_")`
- A truthiness check: `if name` (keeps non-empty strings)
- A membership test: `if status in ("open", "pending")`
- A combined condition: `if x > 0 and x < 100`

### Tuple unpacking in comprehensions

When the iterable yields tuples or pairs (like `dict.items()`), you can unpack directly in the `for` clause:

```python
pairs = {"alice": 90, "bob": 75, "carol": 88}
labels = [f"{name}: {score}" for name, score in pairs.items()]
```

This works the same way tuple unpacking works in a regular `for` loop (Lesson 13).

## Worked Examples

### Example 1: Transforming a list of strings

Suppose you have a list of endpoint paths from an API and you want to normalize them to lowercase and strip leading slashes.

**Loop version:**

```python
endpoints = ["/Users/List", "/Repos/Create", "/issues/Search"]

cleaned = []
for ep in endpoints:
    cleaned.append(ep.strip("/").lower())

print(cleaned)
```

**Comprehension version:**

```python
endpoints = ["/Users/List", "/Repos/Create", "/issues/Search"]

cleaned = [ep.strip("/").lower() for ep in endpoints]

print(cleaned)
```

Both produce:

```
['users/list', 'repos/create', 'issues/search']
```

The comprehension does the same thing in one line. Read it as: "For each `ep` in `endpoints`, produce `ep.strip("/").lower()`, and collect the results into a list."

### Example 2: Filtering with a condition

You have a list of dictionaries representing API responses, and you want to extract only the successful ones.

**Loop version:**

```python
responses = [
    {"url": "/users", "status": 200, "body": "OK"},
    {"url": "/repos", "status": 404, "body": "Not Found"},
    {"url": "/issues", "status": 200, "body": "OK"},
    {"url": "/teams", "status": 403, "body": "Forbidden"},
]

successful = []
for r in responses:
    if r["status"] == 200:
        successful.append(r["url"])

print(successful)
```

**Comprehension version:**

```python
responses = [
    {"url": "/users", "status": 200, "body": "OK"},
    {"url": "/repos", "status": 404, "body": "Not Found"},
    {"url": "/issues", "status": 200, "body": "OK"},
    {"url": "/teams", "status": 403, "body": "Forbidden"},
]

successful = [r["url"] for r in responses if r["status"] == 200]

print(successful)
```

Both produce:

```
['/users', '/issues']
```

Read it as: "For each `r` in `responses`, if `r["status"]` equals 200, produce `r["url"]`."

### Example 3: Unpacking and formatting in one pass

You have a dictionary of configuration values and want to produce a list of formatted strings for a log message or a report.

**Loop version:**

```python
config = {"timeout": 30, "retries": 3, "base_url": "https://api.example.com"}

lines = []
for key, value in config.items():
    lines.append(f"  {key} = {value}")

print("Current config:")
for line in lines:
    print(line)
```

**Comprehension version:**

```python
config = {"timeout": 30, "retries": 3, "base_url": "https://api.example.com"}

lines = [f"  {key} = {value}" for key, value in config.items()]

print("Current config:")
for line in lines:
    print(line)
```

Both produce:

```
Current config:
  timeout = 30
  retries = 3
  base_url = https://api.example.com
```

The comprehension unpacks each `(key, value)` pair directly in the `for` clause, just as a regular loop would.

## Quick Reference

```python
# Basic list comprehension — transform every item
squares = [n * 2 for n in [1, 2, 3, 4]]

# Filtered comprehension — keep only items that pass the condition
short = [w for w in ["hi", "hello", "hey", "greetings"] if len(w) <= 3]

# Call a method on each item
lowered = [name.lower() for name in ["Alice", "BOB", "Carol"]]

# Use an f-string as the expression
labels = [f"item: {x}" for x in [10, 20, 30]]

# Access a dict key from each element in a list of dicts
names = [d["name"] for d in [{"name": "a"}, {"name": "b"}]]

# Filter by a dict value
active = [d["name"] for d in [{"name": "a", "ok": True}, {"name": "b", "ok": False}] if d["ok"]]

# Unpack tuples in the for clause (works with dict.items())
pairs = [f"{k}={v}" for k, v in {"x": 1, "y": 2}.items()]

# Chain two string methods in the expression
cleaned = [s.strip().lower() for s in ["  Hello ", " WORLD "]]

# Comprehension with a function call as the expression
lengths = [len(word) for word in ["cat", "elephant", "dog"]]

# Equivalent loop for any comprehension — mentally unpack to this form
result = []
for item in [1, 2, 3]:
    if item > 1:
        result.append(item * 10)
# same as: result = [item * 10 for item in [1, 2, 3] if item > 1]
```

## Exercise

### Scenario

You have a JSON file containing a list of SDK method records. Each record has a `"name"`, a `"module"`, a `"deprecated"` flag (boolean), and an optional `"description"` field that may be missing or may be an empty string.

Your task is to write a script that reads the JSON file, processes the records using list comprehensions, and prints a formatted summary report.

### Setup

Create a file called `methods.json` with the following content:

```json
[
    {"name": "get_user", "module": "auth", "deprecated": false, "description": "Fetch the authenticated user."},
    {"name": "list_repos", "module": "repos", "deprecated": false, "description": "List repositories for a user or org."},
    {"name": "create_gist", "module": "gists", "deprecated": true, "description": "Create a new gist."},
    {"name": "get_rate_limit", "module": "core", "deprecated": false, "description": ""},
    {"name": "edit_issue", "module": "issues", "deprecated": false, "description": "Edit an existing issue's title or body."},
    {"name": "delete_repo", "module": "repos", "deprecated": true},
    {"name": "list_issues", "module": "issues", "deprecated": false, "description": "List issues for a repository."},
    {"name": "get_commit", "module": "repos", "deprecated": false, "description": "Fetch a single commit by SHA."},
    {"name": "legacy_search", "module": "search", "deprecated": true, "description": "Old search endpoint."},
    {"name": "list_pulls", "module": "repos", "deprecated": false, "description": "List pull requests for a repository."}
]
```

### Requirements

Write a script called `method_report.py` that accepts the JSON file path as a positional argument via `argparse`. The script must:

1. Read and parse the JSON file.
2. Use a list comprehension to build a list of the names of all **non-deprecated** methods.
3. Use a list comprehension to build a list of formatted strings for all methods in the `"repos"` module. Each string should read `" - method_name (deprecated)"` if the method is deprecated, or `" - method_name"` if it is not.
4. Use a list comprehension to build a list of the names of methods that are missing a description. A method is "missing a description" if the `"description"` key is absent from the record **or** if its value is an empty string.
5. Print the three sections shown in the expected output below, in order.

### Expected output

```
Active methods (7):
  get_user, list_repos, get_rate_limit, edit_issue, list_issues, get_commit, list_pulls

Repos module:
  - list_repos
  - delete_repo (deprecated)
  - get_commit
  - list_pulls

Missing descriptions (2):
  get_rate_limit, delete_repo
```