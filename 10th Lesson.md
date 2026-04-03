# Lesson 10: Conditionals I — `if`, `elif`, `else`, and Comparisons

---

## Terminology and Theory

**Boolean expression** — Any expression that evaluates to `True` or `False`. Python evaluates these continuously as your code runs; they are the foundation of every decision a script makes.

**Comparison operator** — A symbol that compares two values and returns a boolean. You'll use these to ask questions like "is this string equal to that one?" or "is this number greater than zero?"

**Conditional statement** — A block of code that runs only when a boolean expression is `True`. The keywords `if`, `elif`, and `else` control which branches execute.

**Branch** — One possible path through a conditional block. Python evaluates the branches top to bottom and executes at most one of them.

**Indentation block** — Python uses consistent indentation (4 spaces by convention) to define what belongs inside a conditional branch. Everything at the same indent level under an `if` is part of that branch.

### Comparison Operators

|Operator|Meaning|Example|
|---|---|---|
|`==`|equal to|`"open" == "open"`|
|`!=`|not equal to|`status != "closed"`|
|`<`|less than|`count < 10`|
|`>`|greater than|`count > 0`|
|`<=`|less than or equal to|`age <= 18`|
|`>=`|greater than or equal to|`score >= 90`|
|`in`|membership test|`"py" in filename`|
|`not in`|negative membership test|`"md" not in name`|

### Logical Operators

You can combine comparisons using `and`, `or`, and `not`:

- `and` — both conditions must be `True`
- `or` — at least one condition must be `True`
- `not` — inverts a boolean (`not True` → `False`)

---

## Syntax Section

### Basic `if` statement

```python
if condition:
    # code runs only when condition is True
```

### `if` / `else`

```python
if condition:
    # runs when True
else:
    # runs when False
```

### `if` / `elif` / `else`

```python
if condition_one:
    # runs when condition_one is True
elif condition_two:
    # runs when condition_one is False AND condition_two is True
else:
    # runs when none of the above matched
```

**Key rules:**

- Only one branch executes per run, even if multiple conditions are `True`.
- `elif` and `else` are optional. You can use a bare `if` alone.
- You can chain as many `elif` branches as you need.
- Python evaluates branches in order and stops at the first match.

### Conditionals inside a loop

```python
for item in collection:
    if some_condition(item):
        print(item)
```

This is the foundational "filter" pattern — you'll see it constantly in SDK scripts.

---

## Worked Examples

### Example 1: Categorizing a single value

```python
score = 82

if score >= 90:
    label = "A"
elif score >= 80:
    label = "B"
elif score >= 70:
    label = "C"
else:
    label = "below C"

print(f"Score: {score} → Grade: {label}")
```

**What's happening:**

- Python checks `score >= 90` first — it's `False` (82 is not ≥ 90).
- It moves to `score >= 80` — `True`, so `label` is set to `"B"` and the rest of the block is skipped.
- The f-string formats the result into a readable line.

**Output:**

```
Score: 82 → Grade: B
```

---

### Example 2: Filtering a list of filenames

This pattern is common in SDK and file-processing scripts: loop over a collection, check a condition, and act only on matching items.

```python
files = [
    "readme.md",
    "config.yaml",
    "notes.txt",
    "api_reference.md",
    "setup.py",
]

print("Markdown files found:")
for filename in files:
    if filename.endswith(".md"):
        print(f"  {filename}")
```

**What's happening:**

- `filename.endswith(".md")` returns `True` or `False` for each filename (you learned `.endswith()` in Lesson 5).
- The `print()` inside the `if` block only executes when the condition is `True`.
- The two non-matching extensions (`".yaml"`, `".txt"`, `".py"`) are silently skipped.

**Output:**

```
Markdown files found:
  readme.md
  api_reference.md
```

---

### Example 3: Multi-condition filtering with `and` / `or`

Imagine you have a list of issue records as nested lists (each inner list: `[id, title, status]`), and you want to report only open issues that mention "auth" in the title.

```python
issues = [
    [101, "Fix auth token expiry", "open"],
    [102, "Update readme", "closed"],
    [103, "Auth endpoint returns 500", "open"],
    [104, "Pagination broken", "open"],
    [105, "Auth docs outdated", "closed"],
]

print("Open issues mentioning auth:")
for issue in issues:
    issue_id = issue[0]
    title    = issue[1]
    status   = issue[2]

    if status == "open" and "auth" in title.lower():
        print(f"  #{issue_id}: {title}")
```

**What's happening:**

- Each inner list is accessed by index (Lesson 7 and 8).
- `status == "open"` checks for an exact string match.
- `"auth" in title.lower()` checks membership in the lowercased title so capitalization doesn't matter (Lessons 4 and 5).
- Both conditions must be `True` (`and`) for the issue to print.

**Output:**

```
Open issues mentioning auth:
  #101: Fix auth token expiry
  #103: Auth endpoint returns 500
```

---

## Quick Reference

```shellsession
# Basic if/elif/else — only one branch runs
$ python3 -c "
x = 7
if x > 10:
    print('big')
elif x > 5:
    print('medium')
else:
    print('small')
"
medium

# Comparison operators
$ python3 -c "print(3 == 3, 3 != 4, 'py' in 'python')"
True True True

# Combining conditions with and / or
$ python3 -c "
status = 'open'
label = 'bug'
print(status == 'open' and label == 'bug')
print(status == 'closed' or label == 'bug')
"
True
True

# not inverts a boolean
$ python3 -c "print(not True, not False)"
False True

# Filtering in a loop
$ python3 -c "
items = ['readme.md', 'config.yaml', 'api.md']
for f in items:
    if f.endswith('.md'):
        print(f)
"
readme.md
api.md

# in operator for string membership check
$ python3 -c "print('auth' in 'auth token expiry'.lower())"
True
```

---

## Exercises

### Exercise 1: Report generator with status labels

You have the following list of software tickets. Each inner list has the format `[ticket_id, title, priority, status]`:

```python
tickets = [
    ["T-01", "Login page crash", "high",   "open"],
    ["T-02", "Typo in footer",   "low",    "closed"],
    ["T-03", "API timeout",      "high",   "open"],
    ["T-04", "Dark mode flicker","medium", "open"],
    ["T-05", "Broken image link","low",    "closed"],
    ["T-06", "Token refresh bug","high",   "closed"],
]
```

Write a script that loops over the tickets and prints a formatted line for each one. The line must include:

- The ticket ID
- The title
- A **label** that says `"ACTION REQUIRED"` if the ticket is both `"open"` and `"high"` priority, `"monitor"` if it is `"open"` but not high priority, and `"done"` if the status is `"closed"`

**Expected output:**

```
T-01 | Login page crash       | ACTION REQUIRED
T-02 | Typo in footer         | done
T-03 | API timeout            | ACTION REQUIRED
T-04 | Dark mode flicker      | monitor
T-05 | Broken image link      | done
T-06 | Token refresh bug      | done
```

_(Column spacing in your output does not need to match exactly — the labels and values must be correct.)_

---

### Exercise 2: Keyword scanner

Write a script that accepts a hard-coded list of strings (representing lines from a changelog or release note) and scans them for lines that contain **any** of the following keywords: `"fix"`, `"patch"`, `"security"`. The scan should be case-insensitive.

Use this list:

```python
lines = [
    "Added dark mode support",
    "Fixed crash on startup",
    "Security patch for token handling",
    "Improved pagination performance",
    "Patch applied to rate limiter",
    "Updated contributor guidelines",
    "Hotfix for null pointer exception",
]
```

Your script must:

1. Loop over all lines.
2. For each line, check whether it contains `"fix"`, `"patch"`, or `"security"` (case-insensitive).
3. Print only the matching lines, each preceded by `"[MATCH]"`.
4. After the loop, print a final count: `"X line(s) matched."`, where `X` is the number of matches found.

**Expected output:**

```
[MATCH] Fixed crash on startup
[MATCH] Security patch for token handling
[MATCH] Patch applied to rate limiter
[MATCH] Hotfix for null pointer exception
4 line(s) matched.
```

---

## Audit

|Exercise|Operations Required|Introduced In|
|---|---|---|
|Ex 1|List indexing (`issue[0]`, etc.)|Lessons 7–8|
|Ex 1|`for` loop over a list|Lesson 9|
|Ex 1|`if` / `elif` / `else`|Lesson 10|
|Ex 1|`==`, `and` comparison|Lesson 10|
|Ex 1|f-string formatting|Lesson 6|
|Ex 2|`for` loop|Lesson 9|
|Ex 2|`if` with `or`, `in` operator|Lesson 10|
|Ex 2|`.lower()` string method|Lesson 5|
|Ex 2|Counter variable (`count += 1`)|Lesson 9 (`range()`/accumulation pattern)|
|Ex 2|f-string for final count line|Lesson 6|

> **Note on counter variable:** The accumulation pattern (`count = 0` before a loop, `count += 1` inside) was introduced in Lesson 9 in the context of `range()` and loop counting. No new syntax is required.

All operations in both exercises have been taught in Lessons 1–10. Both exercises pass the audit.