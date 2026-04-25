# Lesson 13: Tuples and Unpacking (Python Idioms You Must Recognize)

---

## Terminology and Theory

**Tuple**: A tuple is an ordered, immutable sequence of values. "Immutable" means that once a tuple is created, you cannot change its elements — you cannot append to it, remove from it, or reassign individual items. Tuples are used throughout Python and SDK code to group related values together when you don't need the ability to modify the container afterward.

**Tuple literal**: A tuple is written as values separated by commas, optionally surrounded by parentheses. The parentheses are often present for readability, but it is the _commas_ that actually create the tuple, not the parentheses.

**The "comma makes a tuple" rule**: This is a frequent source of confusion. A single value in parentheses is _not_ a tuple — it's just a value in parentheses. To make a single-element tuple, you need a trailing comma: `(42,)`. This is an idiom you will encounter when reading Python code, and you need to recognize it on sight.

**Tuple unpacking** (also called "destructuring"): Tuple unpacking is the act of assigning each element of a tuple (or any sequence) to a separate variable in a single statement. Unpacking appears in two contexts, and recognizing the difference between them is important:

- **Assignment unpacking**: You reference the tuple directly on the right side of `=`. For example, `name, age = ("Alice", 30)` assigns `"Alice"` to `name` and `30` to `age`.
- **Loop unpacking**: You reference a _container_ that yields tuples — not the tuple itself. You have already been doing this without knowing it: when you write `for k, v in d.items()`, the `k, v` part is tuple unpacking. The `.items()` call produces a sequence of tuples, and on each iteration Python takes one tuple from that sequence and unpacks it into `k` and `v`.

In assignment unpacking, you point at the tuple. In loop unpacking, you point at whatever holds or produces the tuples. This distinction matters because confusing the two is one of the most common sources of errors when learning tuple unpacking (see "Common Confusions" below).

**Why this matters for SDK work**: SDK documentation and examples are full of tuple unpacking. Configuration pairs, coordinate values, key-value iteration, and function return values that bundle multiple pieces of data are all commonly expressed as tuples. If you can't read tuple syntax fluently, SDK code will look mysterious.

---

## Syntax Section

### Creating tuples

```python
# With parentheses (most common style)
coordinates = (40.7128, -74.0060)

# Without parentheses — commas are what matter
coordinates = 40.7128, -74.0060

# Single-element tuple requires a trailing comma
single = ("only_item",)

# This is NOT a tuple — it's just a string in parentheses
not_a_tuple = ("only_item")

# Empty tuple
empty = ()
```

The parentheses are optional in most contexts. The commas are what Python uses to recognize a tuple. However, parentheses are strongly recommended for readability, especially inside `print()` calls or complex expressions where the commas could be misread.

### Accessing elements

Tuples support indexing and slicing, just like lists and strings:

```python
point = (10, 20, 30)
print(point[0])    # 10
print(point[-1])   # 30
print(point[0:2])  # (10, 20)
```

The key difference from lists: you **cannot** reassign an element. `point[0] = 99` will raise a `TypeError`.

### Tuple unpacking

Unpacking works in two contexts. Recognizing which one you're in prevents the most common tuple-related errors.

**Assignment unpacking** — you reference the tuple directly:

```python
# Basic unpacking
name, role = ("Alice", "engineer")

# Unpacking without parentheses on the right side
host, port = "localhost", 8080
```

**Loop unpacking** — you reference a _container_ that yields tuples, not the tuple itself:

```python
# Unpacking in a for loop (you already know this pattern)
user = {"login": "octocat", "id": 1, "site_admin": False}
for key, value in user.items():
    print(f"{key}: {value}")
```

In loop unpacking, the iterable (here, `user.items()`) yields one tuple per iteration. Python then unpacks that tuple into `key` and `value` as a separate step. The iterable always yields the same objects regardless of how many variables you put on the left side of `for`. Writing `for item in user.items()` and `for key, value in user.items()` both iterate over the same tuples — the only difference is whether Python assigns each tuple to a single variable or unpacks it into multiple variables.

**A common mistake — iterating over a single tuple with unpacking:**

```python
my_tuple = ("Alice", "engineer", 30)

# ❌ WRONG — this iterates over the tuple's elements, not over sub-tuples
for name, role, age in my_tuple:
    print(name)
# TypeError: cannot unpack non-sequence str

# What actually happens: Python iterates over my_tuple and gets "Alice" first,
# then tries to unpack the string "Alice" into three variables — which fails.
```

If you want to unpack a single tuple, use assignment unpacking, not a loop:

```python
# ✅ Correct — assignment unpacking, no loop needed
name, role, age = my_tuple
```

If you want loop unpacking, you need a container _of_ tuples (a list of tuples, `dict.items()`, `enumerate()`, `zip()`, etc.):

```python
# ✅ Correct — iterating over a list of tuples
people = [("Alice", "engineer", 30), ("Bob", "designer", 25)]
for name, role, age in people:
    print(f"{name} is a {role}")
```

The number of variables on the left side **must** match the number of elements in the tuple on the right side. If they don't match, Python raises a `ValueError`.

### Checking the type

```python
t = (1, 2, 3)
print(type(t))  # <class 'tuple'>
```

### The `len()` function works on tuples

```python
t = ("a", "b", "c")
print(len(t))  # 3
```

### Tuples can contain any type, including mixed types

```python
record = ("octocat", 42, True, ["repo1", "repo2"])
```

Tuples can hold strings, integers, booleans, and even lists. The tuple itself is immutable, but if it contains a mutable object (like a list), that inner object can still be changed. You don't need to worry about that nuance for now — just know that tuples can hold a mix of types.

---

## Common Confusions

Three closely related mistakes trip people up when learning tuple unpacking. Each one is explained in detail in the Syntax and Worked Examples sections above, but here they are in summary:

1. **Iterating over a single tuple with unpacking variables.** Writing `for a, b, c in my_tuple:` does _not_ unpack `my_tuple` — it iterates over the tuple's individual elements and tries to unpack each one, which fails. To unpack a single tuple, use assignment: `a, b, c = my_tuple`. See the "A common mistake" subsection under Tuple unpacking in the Syntax section.
    
2. **Thinking the iterable changes based on the left side of `for`.** It doesn't. `for item in x` and `for a, b in x` yield the same objects from `x`. The left side controls what Python does with each object _after_ it's yielded — assign it whole or unpack it. See Example 3 in Worked Examples.
    
3. **Confusing `for` (iteration) with `=` (assignment) when unpacking inside a loop body.** If you already have a tuple in a variable, unpack it with `=`, not with another `for`. Writing `for a, b in item` starts a new loop over `item`'s elements; writing `a, b = item` unpacks it. See the Syntax section for both contexts side by side.
    

---

## Worked Examples

### Example 1: Recognizing tuple creation and verifying types

This example shows the different ways tuples are created and uses `type()` to confirm what Python actually built.

```python
# Parenthesized tuple
repo_info = ("octocat/Hello-World", 1296269)
print(type(repo_info))
print(repo_info)

# Comma-only tuple (no parentheses)
status_pair = "open", 47
print(type(status_pair))
print(status_pair)

# Single-element tuple — trailing comma required
tag = ("v1.0.0",)
print(type(tag))
print(tag)

# Common mistake: forgetting the trailing comma
not_a_tuple = ("v1.0.0")
print(type(not_a_tuple))
print(not_a_tuple)
```

**Output:**

```
<class 'tuple'>
('octocat/Hello-World', 1296269)
<class 'tuple'>
('open', 47)
<class 'tuple'>
('v1.0.0',)
<class 'str'>
v1.0.0
```

The first three are tuples. The last one is just a string because there's no trailing comma. This is the "comma makes a tuple" rule in action. When you encounter code that looks like a single value in parentheses with a trailing comma, now you know it's a one-element tuple.

### Example 2: Unpacking tuples for readable variable assignment

This example demonstrates how unpacking lets you extract values from a tuple into clearly named variables — a pattern you'll see constantly in SDK code and documentation.

```python
# A tuple representing a GitHub issue summary
issue = ("Fix login bug", "open", 3, "octocat")

# Unpack into descriptive variable names
title, state, comment_count, author = issue

print(f"Issue: {title}")
print(f"  State: {state}")
print(f"  Comments: {comment_count}")
print(f"  Author: {author}")
```

**Output:**

```
Issue: Fix login bug
  State: open
  Comments: 3
  Author: octocat
```

Without unpacking, you would have to write `issue[0]`, `issue[1]`, etc., which is harder to read. Unpacking gives each value a meaningful name in one line.

### Example 3: Unpacking inside a `for` loop with `.items()`

You have already used `for k, v in d.items()` in Lesson 12. This example shows why that works: `.items()` returns tuples, and the `for` loop unpacks each one.

```python
repo_metadata = {
    "name": "Hello-World",
    "owner": "octocat",
    "stars": 1500,
    "language": "Python"
}

# Each iteration, .items() yields a tuple like ("name", "Hello-World")
# The for loop unpacks it into field and value
for field, value in repo_metadata.items():
    print(f"{field:>10}: {value}")
```

**Output:**

```
      name: Hello-World
     owner: octocat
     stars: 1500
  language: Python
```

The right-alignment formatting `{field:>10}` is just an extension of f-string syntax from Lesson 6: the `>10` means "right-align inside a 10-character-wide space." The important concept here is that `.items()` returns tuples, and `for field, value` is tuple unpacking happening on every iteration.

Note that writing `for item in repo_metadata.items()` and `for field, value in repo_metadata.items()` both iterate over the exact same tuples. The iterable always yields the same objects regardless of what's on the left side of `for`. The only difference is what happens _after_ each tuple is yielded: Python either assigns it to one variable or unpacks it into multiple variables. Unpacking is a separate step from iteration.

Now consider a list of tuples — a pattern you'll see when SDK data arrives as pairs:

```python
# A list of (label, url) tuples
endpoints = [
    ("Issues", "https://api.github.com/repos/octocat/Hello-World/issues"),
    ("Pulls", "https://api.github.com/repos/octocat/Hello-World/pulls"),
    ("Commits", "https://api.github.com/repos/octocat/Hello-World/commits"),
]

print("API Endpoints:")
for label, url in endpoints:
    print(f"  {label}: {url}")
```

**Output:**

```
API Endpoints:
  Issues: https://api.github.com/repos/octocat/Hello-World/issues
  Pulls: https://api.github.com/repos/octocat/Hello-World/pulls
  Commits: https://api.github.com/repos/octocat/Hello-World/commits
```

Each element of `endpoints` is a two-element tuple. The `for label, url` unpacks each one cleanly. This pattern — a list of tuples iterated with unpacking — appears frequently in SDK configuration, API routing tables, and batch operations.

---

## Quick Reference

```python
#!/usr/bin/env python3

# Create a tuple with parentheses
# Output: (1, 2, 3) — <class 'tuple'>
t = (1, 2, 3)
print(t)
print(type(t))

# Create a tuple without parentheses — commas are what matter
# Output: (1, 2, 3) — <class 'tuple'>
t = 1, 2, 3
print(t)
print(type(t))

# Single-element tuple requires a trailing comma
# Output: ('hello',) — <class 'tuple'>
t = ("hello",)
print(t)
print(type(t))

# Without the trailing comma, it's just the value itself
# Output: hello — <class 'str'>
t = ("hello")
print(t)
print(type(t))

# Empty tuple
# Output: () — <class 'tuple'>
t = ()
print(t)
print(type(t))

# Index into a tuple (same syntax as lists)
# Output: a, then c
t = ("a", "b", "c")
print(t[0])
print(t[-1])

# Slice a tuple (returns a new tuple)
# Output: (20, 30)
t = (10, 20, 30, 40)
print(t[1:3])

# Get the length of a tuple
# Output: 3
t = ("x", "y", "z")
print(len(t))

# Assignment unpacking — reference the tuple directly
# Output: Alice, then 30
name, age = ("Alice", 30)
print(name)
print(age)

# Loop unpacking — reference a container that yields tuples
# Output: a 1, then b 2
d = {"a": 1, "b": 2}
for k, v in d.items():
    print(k, v)

# Tuples are immutable — element assignment raises TypeError
t = (1, 2, 3)
# t[0] = 99  # → TypeError: 'tuple' object does not support item assignment
```

---

## Exercise

### Scenario

You have a list of dictionaries representing GitHub repository data. Your job is to produce a formatted summary report that groups repositories by their status and displays them with clean alignment.

### Starting Data

Use the following data in your script:

```python
repos = [
    {"name": "auth-service", "owner": "acme-corp", "stars": 230, "status": "active"},
    {"name": "legacy-api", "owner": "acme-corp", "stars": 14, "status": "archived"},
    {"name": "docs-site", "owner": "acme-corp", "stars": 87, "status": "active"},
    {"name": "test-harness", "owner": "acme-corp", "stars": 5, "status": "archived"},
    {"name": "sdk-python", "owner": "acme-corp", "stars": 412, "status": "active"},
    {"name": "old-dashboard", "owner": "acme-corp", "stars": 31, "status": "archived"},
]
```

### Requirements

1. Iterate through each repo dictionary and build two separate lists: one for active repos and one for archived repos. Use conditionals to decide which list each repo goes into.
2. For the active repos list and the archived repos list, store each repo as a **tuple** of `(name, owner, stars)` — not as the original dictionary.
3. Print a report with two sections. Each section has a header line, then one line per repo. Use tuple unpacking in the `for` loop to extract the values from each tuple when printing.
4. Within each section, print each repo on its own line using the format shown in the expected output below. Use f-string formatting to right-align the star count in a 5-character-wide field.
5. After each section, print the total number of repos in that section using `len()`.

### Expected Output

```
=== Active Repos ===
  auth-service (acme-corp) | Stars:   230
  docs-site (acme-corp) | Stars:    87
  sdk-python (acme-corp) | Stars:   412
Total active: 3

=== Archived Repos ===
  legacy-api (acme-corp) | Stars:    14
  test-harness (acme-corp) | Stars:     5
  old-dashboard (acme-corp) | Stars:    31
Total archived: 3
```