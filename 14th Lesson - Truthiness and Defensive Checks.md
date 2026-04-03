# Lesson 14: Truthiness and Defensive Checks

## Terminology and Theory

**Truthiness** is the idea that every Python value — not just `True` and `False` — can be evaluated as either true or false when used in a condition. You have been writing `if` statements since Lesson 10, but so far you have only tested things like `if count > 0` or `if name == "admin"`. Python also lets you write `if name:` or `if items:`, and the language has clear rules about what that means.

A value is **falsy** if Python treats it as `False` in a boolean context. The complete set of falsy values you will encounter in your work is:

- `False` (the boolean itself)
- `None` (Python's "no value" placeholder)
- `0` (integer zero)
- `0.0` (float zero)
- `""` (empty string)
- `[]` (empty list)
- `{}` (empty dictionary)
- `()` (empty tuple)

Everything else is **truthy**. A non-empty string is truthy. A list with one item is truthy. A dictionary with one key is truthy. The integer `1` is truthy — and so is `-7`.

A **guard clause** is a short `if` check placed near the top of a block of code that exits early or skips processing when the data is missing, empty, or wrong. Instead of nesting your real logic deeper and deeper inside `if` blocks, you test for the bad case first and move on. Guard clauses keep scripts flat and readable.

**Defensive checking** means writing your code so that it does not crash when it encounters missing keys, empty containers, or unexpected `None` values. You have already seen `.get()` in Lessons 11 and 12 as one defensive tool. Truthiness gives you another: you can test whether a value exists and is non-empty in a single expression.

**Explicit comparison** means writing out the full comparison yourself — `if x == ""` or `if x is None` — rather than relying on truthiness. Sometimes explicit is better, especially when `0` or `0.0` might be a valid value that you do not want to treat as "missing."

---

## Syntax Section

### Truthiness in `if` statements

```python
if value:
    # runs when value is truthy (non-empty, non-zero, not None)
    print("value is present")
```

This is equivalent to writing `if bool(value) == True:`, but nobody writes it that way. Python evaluates `value` in a boolean context automatically.

### Negated truthiness

```python
if not value:
    # runs when value is falsy (empty, zero, None, False)
    print("value is missing or empty")
```

The `not` keyword flips the truthiness. If `value` is an empty string, `not value` is `True`.

### Guard clause pattern

```python
data = some_dict.get("key")
if not data:
    print("No data found, skipping.")
else:
    # proceed with data
    print(f"Processing: {data}")
```

The guard clause checks for the bad case first. Your main logic lives in the `else` block or after the guard. This is the pattern you will use constantly when processing SDK results that might come back empty.

### Explicit comparison with `is None`

```python
if value is None:
    print("value was not provided at all")
```

Use `is None` when you need to distinguish between "no value" and "an empty but valid value." For example, an empty string `""` might mean "the user left the field blank," while `None` might mean "the field does not exist." In those situations, truthiness alone would treat both the same way.

### Explicit comparison with `== ""`

```python
if value == "":
    print("value is an empty string specifically")
```

Use this when you care specifically about the empty string and do not want to catch `None`, `0`, or other falsy values.

### Combining `.get()` with truthiness

```python
description = repo.get("description")
if description:
    print(f"Description: {description}")
else:
    print("No description available.")
```

This is a very common SDK pattern. A dictionary key may be present but set to `None` or `""`. Using `.get()` with a truthiness check handles all three cases — missing key, `None` value, and empty string — in one clean test.

---

## Worked Examples

### Example 1: Filtering empty fields from a record

Imagine you pulled a record from an API response and some fields came back empty. You want to print only the fields that actually contain data.

```python
record = {
    "name": "PyGithub",
    "description": "Typed interactions with the GitHub API v3",
    "homepage": "",
    "license": None,
    "language": "Python"
}

print("Repository details:")
for key, value in record.items():
    if value:
        print(f"  {key}: {value}")
    else:
        print(f"  {key}: (not provided)")
```

Output:

```
Repository details:
  name: PyGithub
  description: Typed interactions with the GitHub API v3
  homepage: (not provided)
  license: (not provided)
  language: Python
```

Here, both `""` and `None` are falsy, so the truthiness check catches both without needing separate comparisons. The loop uses `for key, value in record.items()`, which is tuple unpacking from Lesson 13.

### Example 2: Guard clause to skip processing on empty input

You have a list of repository names to process. Some entries might be empty strings (bad data). You want to skip those and only process valid names.

```python
repo_names = ["octocat/Hello-World", "", "PyGithub/PyGithub", "", "psf/requests"]

clean_names = []
for name in repo_names:
    if not name:
        continue
    clean_names.append(name)

print(f"Valid repos ({len(clean_names)}):")
for name in clean_names:
    print(f"  - {name}")
```

Output:

```
Valid repos (3):
  - octocat/Hello-World
  - PyGithub/PyGithub
  - psf/requests
```

The guard clause `if not name: continue` skips empty strings at the top of the loop body, keeping the rest of the logic unindented and easy to read. `continue` is not new syntax here — it is part of `for` loop control you can use to skip to the next iteration. If you have not seen `continue` before, think of it as "go back to the top of the loop and grab the next item."

> **Note on `continue`:** The `continue` statement is part of Python's loop mechanics. When Python hits `continue`, it skips the remaining body of the current iteration and moves to the next item. It works inside any `for` loop.

### Example 3: Distinguishing `None` from empty with explicit checks

Sometimes truthiness is too broad. Here, a numeric field of `0` is a valid value (zero open issues), and you do not want to treat it as "missing."

```python
repos = [
    {"name": "docs-site", "open_issues": 0},
    {"name": "api-client", "open_issues": 12},
    {"name": "legacy-tool", "open_issues": None},
]

for repo in repos:
    name = repo.get("name", "(unknown)")
    issues = repo.get("open_issues")

    if issues is None:
        print(f"{name}: issue count unavailable")
    else:
        print(f"{name}: {issues} open issues")
```

Output:

```
docs-site: 0 open issues
api-client: 12 open issues
legacy-tool: issue count unavailable
```

If you had written `if not issues:` instead of `if issues is None:`, the `docs-site` repo would have been incorrectly reported as "unavailable" because `0` is falsy. This is the most important lesson about truthiness: use it when any falsy value means "skip," but use explicit checks when some falsy values (like `0`) are legitimate.

---

## Quick Reference

```
# Check if a value is truthy (non-empty, non-zero, not None)
$ python3 -c "name = 'hello'; print(bool(name))"
True

# Check if a value is falsy (empty string)
$ python3 -c "name = ''; print(bool(name))"
False

# Check if a value is falsy (empty list)
$ python3 -c "items = []; print(bool(items))"
False

# Check if a value is falsy (None)
$ python3 -c "val = None; print(bool(val))"
False

# Check if a value is falsy (zero)
$ python3 -c "count = 0; print(bool(count))"
False

# Guard clause with 'not' to detect falsy values
$ python3 -c "data = ''; print('empty' if not data else 'has data')"
empty

# Explicit None check with 'is None'
$ python3 -c "val = 0; print('is None' if val is None else f'value: {val}')"
value: 0

# Using .get() with truthiness for safe dict access
$ python3 -c "d = {'a': ''}; val = d.get('a'); print('truthy' if val else 'falsy')"
falsy

# Falsy empty dict
$ python3 -c "config = {}; print('has config' if config else 'no config')"
no config

# Truthy non-empty tuple
$ python3 -c "pair = (1, 2); print('has data' if pair else 'empty')"
has data
```

---

## Exercises

### Exercise 1: SDK Response Cleaner

You are processing a batch of repository records pulled from an API. Each record is a dictionary inside a list. Some fields are missing (key not present), some are `None`, and some are empty strings. Your job is to write a script that processes these records and produces a clean, formatted report.

Use this data:

```python
repos = [
    {
        "name": "webhook-service",
        "description": "Handles incoming GitHub webhooks",
        "language": "Python",
        "stars": 42,
        "topics": ["webhooks", "github", "automation"],
    },
    {
        "name": "old-experiment",
        "description": "",
        "language": None,
        "stars": 0,
        "topics": [],
    },
    {
        "name": "data-pipeline",
        "description": None,
        "language": "Python",
        "stars": 7,
        "topics": ["etl"],
    },
    {
        "name": "",
        "description": "A mystery repo with no name",
        "language": "Go",
        "stars": 3,
        "topics": ["experimental"],
    },
]
```

Your script must:

1. Loop through each repo in the list.
2. Skip any repo whose `"name"` value is falsy (empty or missing). Print a message like `Skipping unnamed repo.` for each skipped entry.
3. For each valid repo, print a header line: `Repository: <name>`
4. For the `"description"` field: use `.get()` and a truthiness check. If the description is truthy, print it. If not, print `(no description)`.
5. For the `"language"` field: use an explicit `is None` check. If the language is `None`, print `Language: unknown`. Otherwise, print the language value — even if it were hypothetically an empty string, you would still print it (though that case does not appear in this data, your code should handle it correctly by using `is None` rather than truthiness).
6. For the `"stars"` field: use an explicit `is None` check (not a truthiness check), because `0` is a valid star count. Print the star count.
7. For the `"topics"` field: use a truthiness check. If the list is truthy (non-empty), print the topics joined into a comma-separated string. If the list is falsy (empty), print `(no topics)`.
8. Print a blank line after each repo's block.

**Expected output:**

```
Repository: webhook-service
  Description: Handles incoming GitHub webhooks
  Language: Python
  Stars: 42
  Topics: webhooks, github, automation

Repository: old-experiment
  Description: (no description)
  Language: unknown
  Stars: 0
  Topics: (no topics)

Repository: data-pipeline
  Description: (no description)
  Language: Python
  Stars: 7
  Topics: etl

Skipping unnamed repo.
```

## Audit

| Requirement                           | Operation / Concept          | Introduced In                               |
| ------------------------------------- | ---------------------------- | ------------------------------------------- |
| List of dictionaries                  | List literals, dict literals | Lesson 7, Lesson 11                         |
| `for repo in repos` loop              | `for` loop over a list       | Lesson 9                                    |
| Truthiness check (`if not name`)      | **Lesson 14 (current)**      | Current                                     |
| Guard clause with `continue`          | Loop control, guard pattern  | Lesson 9 (loops), Lesson 14 (guard pattern) |
| `print()` with f-strings              | `print()`, f-strings         | Lesson 1, Lesson 6                          |
| `.get()` for safe dict access         | `.get()` method              | Lesson 11                                   |
| Truthiness check on `.get()` result   | **Lesson 14 (current)**      | Current                                     |
| Explicit `is None` comparison         | **Lesson 14 (current)**      | Current                                     |
| `", ".join(list)` for topics          | `.join()` method             | Lesson 5                                    |
| `len()` not required                  | —                            | —                                           |
| Tuple unpacking not required          | —                            | (Lesson 13, not needed here)                |
| No functions, no imports, no file I/O | —                            | Not introduced until Lessons 15+            |

All operations required by the exercise have been introduced in Lesson 14 or earlier. No future-lesson concepts are required. The exercise reinforces loops (Lesson 9), conditionals (Lesson 10), dictionary access and `.get()` (Lessons 11–12), `.join()` (Lesson 5), f-strings (Lesson 6), and list iteration (Lesson 9), while requiring the new truthiness and defensive-check patterns taught in this lesson.