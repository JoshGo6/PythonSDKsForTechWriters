# Lesson 41: List Comprehensions — Reading Compact Python

## Terminology and Theory

**List comprehension:** A compact syntax for building a new list by transforming and/or filtering the items in an existing iterable. Instead of writing a multi-line `for` loop that appends to an empty list, you write a single expression inside square brackets.

**Expression:** The part of the comprehension that describes what each element in the new list should look like. It can be the item itself, a method call on the item, an f-string, a dictionary lookup — anything that produces a value.

**Iteration variable:** The temporary name that takes on each value from the iterable, just like the variable in a `for` loop.

**Filter clause:** An optional `if` at the end of the comprehension that keeps only the items where the condition is `True`. Items that fail the condition are silently skipped.

**Mental model — "unrolling":** Every list comprehension can be mentally converted into an equivalent `for` loop that starts with an empty list and calls `.append()` inside the loop body. If you can unroll it, you can read it. This is the single most useful skill for encountering comprehensions in other people's code.

Here is the correspondence:

```
# Comprehension
result = [expression for item in iterable if condition]

# Equivalent for loop
result = []
for item in iterable:
    if condition:
        result.append(expression)
```

When there is no `if` clause, the comprehension simply transforms every element:

```
# Comprehension
result = [expression for item in iterable]

# Equivalent for loop
result = []
for item in iterable:
    result.append(expression)
```

**Why you need this:** SDK documentation, code samples, and open-source Python projects use comprehensions constantly. You will encounter lines like `labels = [issue["title"] for issue in issues if issue["state"] == "open"]` in PyGithub examples, tutorials, and Stack Overflow answers. If you can't read a comprehension, you can't document the code that uses one.

> [!note] This lesson treats comprehensions as a skill you need for reading _and_ writing. You will both read comprehensions written by others and write your own in exercises. The goal is comfortable fluency, not memorizing edge cases.

## Syntax Section

### Basic comprehension (transform every element)

```python
new_list = [expression for item in iterable]
```

- `new_list` — the variable that receives the newly built list.
- `[` and `]` — the square brackets tell Python "build a list."
- `expression` — what to put into the new list for each item. This is evaluated once per iteration.
- `for item in iterable` — the loop that drives the comprehension, identical in meaning to a regular `for` loop.

### Filtered comprehension (transform _some_ elements)

```python
new_list = [expression for item in iterable if condition]
```

- `if condition` — evaluated for every item. Only items where the condition is `True` appear in the result.

### Reading order

When you encounter a comprehension in someone else's code, read it in this order:

1. **`for item in iterable`** — what are we looping over?
2. **`if condition`** (if present) — which items survive the filter?
3. **`expression`** — what does each surviving item become in the new list?

This "middle → right → left" reading order matches the execution order: iterate, filter, then transform.

## Worked Examples

### Example 1 — Transforming a list of strings

Suppose you have a list of endpoint paths from an API and you need to normalize them to lowercase.

```python
endpoints = ["/Users/List", "/Repos/Search", "/Issues/CREATE"]

lower_endpoints = [ep.lower() for ep in endpoints]

print(lower_endpoints)
```

Output:

```
['/users/list', '/repos/search', '/issues/create']
```

**What is happening:** The comprehension iterates over `endpoints`. For each string `ep`, it calls `ep.lower()` and places the result into the new list. No items are filtered out — every element is transformed.

The equivalent `for` loop:

```python
lower_endpoints = []
for ep in endpoints:
    lower_endpoints.append(ep.lower())
```

### Example 2 — Filtering a list of dictionaries

You have a list of dictionaries representing API responses, and you want only the ones with a successful status code.

```python
responses = [
    {"endpoint": "/users", "status": 200, "body": "OK"},
    {"endpoint": "/repos", "status": 404, "body": "Not Found"},
    {"endpoint": "/issues", "status": 200, "body": "OK"},
    {"endpoint": "/pulls", "status": 500, "body": "Server Error"},
]

successful = [r for r in responses if r["status"] == 200]

for entry in successful:
    print(f"{entry['endpoint']} -> {entry['status']}")
```

Output:

```
/users -> 200
/issues -> 200
```

**What is happening:** The comprehension iterates over `responses`. The `if r["status"] == 200` clause filters out any dictionary whose `"status"` value is not `200`. The expression is just `r` — the entire dictionary — so the surviving dictionaries are placed into `successful` unchanged.

The equivalent `for` loop:

```python
successful = []
for r in responses:
    if r["status"] == 200:
        successful.append(r)
```

### Example 3 — Transform and filter together

You have a list of dictionaries representing issues from a project tracker. You want a list of formatted summary strings, but only for issues that are open.

```python
issues = [
    {"id": 1, "title": "Fix login bug", "state": "open"},
    {"id": 2, "title": "Add dark mode", "state": "closed"},
    {"id": 3, "title": "Update docs", "state": "open"},
    {"id": 4, "title": "Refactor auth", "state": "closed"},
    {"id": 5, "title": "Add search", "state": "open"},
]

summaries = [
    f"#{issue['id']}: {issue['title']}"
    for issue in issues
    if issue["state"] == "open"
]

for line in summaries:
    print(line)
```

Output:

```
#1: Fix login bug
#3: Update docs
#5: Add search
```

**What is happening:** Reading in execution order: (1) `for issue in issues` — loop over the list of dicts. (2) `if issue["state"] == "open"` — keep only open issues. (3) `f"#{issue['id']}: {issue['title']}"` — build a formatted string from each surviving dict. The result is a list of three strings.

The equivalent `for` loop:

```python
summaries = []
for issue in issues:
    if issue["state"] == "open":
        summaries.append(f"#{issue['id']}: {issue['title']}")
```

## Quick Reference

```python
# Basic list comprehension — transform every element
squares = [n * n for n in range(5)]

# Filtered list comprehension — keep only items that pass the condition
evens = [n for n in range(10) if n % 2 == 0]

# Comprehension with a method call as the expression
cleaned = [line.strip() for line in lines]

# Comprehension that transforms and filters
short_names = [name.upper() for name in names if len(name) < 5]

# Comprehension over a list of dicts — extract one field
titles = [item["title"] for item in records]

# Comprehension over a list of dicts — filter and extract
open_titles = [item["title"] for item in records if item["state"] == "open"]

# Comprehension with an f-string as the expression
labels = [f"{item['id']}: {item['name']}" for item in records]

# Unrolling a comprehension into an equivalent for loop
result = []
for item in iterable:
    if condition:
        result.append(expression)
```

## Exercise

### Issue Report Filter

You have the following data representing issues returned from a project API. Write a script called `filter_issues.py` that does the following:

1. Define the following list of dictionaries in your script:

```python
issues = [
    {"id": 101, "title": "Fix null pointer in auth module", "state": "open", "labels": ["bug", "critical"]},
    {"id": 102, "title": "Add unit tests for user endpoint", "state": "closed", "labels": ["testing"]},
    {"id": 103, "title": "Document rate limiting behavior", "state": "open", "labels": ["docs", "api"]},
    {"id": 104, "title": "Refactor database connection pool", "state": "open", "labels": ["refactor"]},
    {"id": 105, "title": "Update changelog for v2.1", "state": "closed", "labels": ["docs"]},
    {"id": 106, "title": "Handle timeout on large uploads", "state": "open", "labels": ["bug", "api"]},
    {"id": 107, "title": "Remove deprecated /v1/legacy endpoint", "state": "open", "labels": ["cleanup", "api"]},
    {"id": 108, "title": "Fix typo in README badges", "state": "closed", "labels": ["docs"]},
]
```

2. Use a list comprehension to build a list of only the issues whose `"state"` is `"open"`.
    
3. Use a second list comprehension on your filtered list to build a list of formatted strings. Each string should follow this format:
    

```
[OPEN] #101: Fix null pointer in auth module (bug, critical)
```

The labels inside the parentheses should be joined with `,` (comma-space).

4. Use a `for` loop to print each formatted string.
    
5. After the list of issues, print a blank line followed by a summary line showing how many open issues were found out of the total, in this format:
    

```
Open: 5/8
```

6. Write the same formatted lines (not the summary) to a file called `open_issues.txt`, one line per entry. Use `pathlib.Path` and `.write_text()`. Use `logging` to log an `INFO`-level message confirming the file was written, including the number of lines written.

### Expected output (stdout)

```
[OPEN] #101: Fix null pointer in auth module (bug, critical)
[OPEN] #103: Document rate limiting behavior (docs, api)
[OPEN] #104: Refactor database connection pool (refactor)
[OPEN] #106: Handle timeout on large uploads (bug, api)
[OPEN] #107: Remove deprecated /v1/legacy endpoint (cleanup, api)

Open: 5/8
```

### Expected output (open_issues.txt)

```
[OPEN] #101: Fix null pointer in auth module (bug, critical)
[OPEN] #103: Document rate limiting behavior (docs, api)
[OPEN] #104: Refactor database connection pool (refactor)
[OPEN] #106: Handle timeout on large uploads (bug, api)
[OPEN] #107: Remove deprecated /v1/legacy endpoint (cleanup, api)
```

### Expected output (stderr / log)

```
INFO:root:Wrote 5 lines to open_issues.txt
```

---

## Audit

|Requirement|Introduced in|
|---|---|
|List comprehension (basic)|Lesson 41 (current)|
|List comprehension with `if` filter|Lesson 41 (current)|
|List of dictionaries, key access|Lesson 11, 12|
|f-strings|Lesson 6|
|`str.join()`|Lesson 5|
|`for` loop|Lesson 9|
|`print()`|Lesson 1, 3|
|`len()`|Lesson 7|
|`pathlib.Path` / `.write_text()`|Lesson 23|
|`logging.basicConfig()`, `logging.info()`|Lesson 21|

All operations required by the exercise are covered by the current lesson or prior lessons. No future-lesson dependencies exist.