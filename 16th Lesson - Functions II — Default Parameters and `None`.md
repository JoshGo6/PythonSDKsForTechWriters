# Lesson 16: Functions II — Default Parameters and `None`

---

## Terminology and Theory

**Default parameter** A parameter whose value is pre-assigned in the `def` line. When the caller omits that argument, Python uses the default automatically. This is how a single function adapts to multiple calling scenarios without duplicating code.

**Optional parameter** Any parameter that has a default value. The caller _can_ provide it, but isn't forced to. In conversation, "optional parameter" and "default parameter" refer to the same thing.

**Required parameter** A parameter with no default. The caller _must_ supply a value for it every time or Python raises a `TypeError`.

**`None`** Python's built-in constant meaning "no value." Its type is `NoneType`. `None` is commonly used as a default when any real value — including an empty string or zero — could be a legitimate argument. It acts as a signal: "the caller didn't explicitly pass anything here."

**Sentinel value** A value that exists only to indicate a condition. `None` is the standard Python sentinel. When you see `def fetch(label=None)`, the default isn't meant to be used as a real label — it is a flag that means "no label was requested."

**`is None` / `is not None`** The correct way to check whether something is `None`. `is` tests _identity_ — whether two names point at the exact same object in memory. Because there is exactly one `None` object in any Python process, identity is the right test. Never use `== None`; it tests _equality_, which can behave unexpectedly with objects that customize their `==` behavior.

**Keyword argument** An argument passed by name at the call site: `greet(name="Josh")`. You used positional arguments in Lesson 15 (matched by order). Keyword arguments let you skip optional parameters you don't care about and set only the ones you do, in any order.

**Argument ordering rule** In both definitions and calls, all required (non-default) parameters must appear before all optional (default) parameters. Python enforces this — violating it is a syntax error.

---

## Syntax Section

### Defining a default parameter

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
```

`name` is required. `greeting` is optional — it defaults to `"Hello"` if omitted.

### Calling with positional and keyword arguments

```python
greet("Josh")                   # positional only; greeting uses default
greet("Josh", "Hey there")      # positional override
greet("Josh", greeting="Yo")    # keyword override — clearest style
```

All three are valid. The keyword form is preferred when a function has multiple optional parameters because it documents what you're setting.

### Using `None` as a sentinel default

```python
def format_label(text, upper=None):
    if upper is None:
        return text
    if upper:
        return text.upper()
    return text.lower()
```

Here, `None` means "the caller didn't ask for either." `True` means "force uppercase." `False` means "force lowercase." A plain boolean default like `upper=False` would make it impossible to distinguish "the caller wants lowercase" from "the caller didn't say."

### Multiple optional parameters with selective overrides

```python
def build_entry(title, prefix="", suffix="", separator=": "):
    return f"{prefix}{title}{separator}{suffix}"
```

```python
build_entry("README")                           # all defaults
build_entry("README", suffix="(updated)")       # skip prefix, set suffix
build_entry("README", prefix=">> ", suffix="!") # set two, skip separator
```

Keyword arguments let you reach any optional parameter directly, without filling in the ones before it.

---

## Worked Examples

### Example 1: Labeling output lines with an optional header

This function prints a list of strings. If the caller supplies a header, it prints the header and a matching underline first. This pattern appears constantly when generating section-based reports from SDK data.

```python
def print_section(items, header=None):
    if header is not None:
        print(header)
        print("-" * len(header))
    for item in items:
        print(f"  {item}")

repos = ["docs-api", "sdk-python", "cli-tools"]

print_section(repos)
print()
print_section(repos, header="Repositories")
```

Output:

```
  docs-api
  sdk-python
  cli-tools

Repositories
------------
  docs-api
  sdk-python
  cli-tools
```

When `header` is `None`, the guard clause (`if header is not None`) keeps the heading block from printing. When a header is supplied, the underline width matches the header length using `len()` and string repetition (`*`), both from earlier lessons.

### Example 2: A configurable key-value formatter

SDK objects often look like dictionaries of metadata. This function formats a dictionary into labeled lines, with optional control over the separator string and whether to uppercase the keys.

```python
def format_metadata(data, separator=": ", uppercase_keys=None):
    lines = []
    for key, value in data.items():
        display_key = key
        if uppercase_keys is not None and uppercase_keys:
            display_key = key.upper()
        lines.append(f"{display_key}{separator}{value}")
    return lines

pr_info = {"title": "Fix typo in README", "state": "open", "number": 87}

for line in format_metadata(pr_info):
    print(line)
print()
for line in format_metadata(pr_info, separator=" -> ", uppercase_keys=True):
    print(line)
```

Output:

```
title: Fix typo in README
state: open
number: 87

TITLE -> Fix typo in README
STATE -> open
NUMBER -> 87
```

Three layers of prior knowledge are working here: dictionary iteration with `.items()` (Lesson 12), `.upper()` on strings (Lesson 5), and list building with `.append()` (Lesson 7). The new piece is that `separator` and `uppercase_keys` are optional — the function works fine without them and adapts when they're provided.

### Example 3: Filtering a list with an optional criterion

This function returns items from a list. If the caller provides a `starts_with` value, it filters; otherwise it returns everything. Using `None` as the default makes the "no filter" case unambiguous.

```python
def select_entries(items, starts_with=None):
    results = []
    for item in items:
        if starts_with is None:
            results.append(item)
        elif item.startswith(starts_with):
            results.append(item)
    return results

filenames = ["README.md", "setup.py", "README.txt", "config.yml", "setup.cfg"]

all_files = select_entries(filenames)
print(all_files)

readme_only = select_entries(filenames, starts_with="README")
print(readme_only)
```

Output:

```
['README.md', 'setup.py', 'README.txt', 'config.yml', 'setup.cfg']
['README.md', 'README.txt']
```

`None` is the right sentinel here because even an empty string (`""`) is a valid prefix — every string starts with `""`. If the default were `""` instead of `None`, there would be no way to say "don't filter at all."

---

## Quick Reference

```
# Define a function with one default parameter
$ python3 -c "
def greet(name, greeting='Hello'):
    print(f'{greeting}, {name}!')
greet('Josh')
greet('Josh', 'Hey')
"
Hello, Josh!
Hey, Josh!

# Override a default using a keyword argument
$ python3 -c "
def tag(text, prefix='', suffix=''):
    print(f'{prefix}{text}{suffix}')
tag('hello', suffix='!')
"
hello!

# Use None as a sentinel default
$ python3 -c "
def show(value, label=None):
    if label is not None:
        print(f'{label}: {value}')
    else:
        print(value)
show(42)
show(42, label='Answer')
"
42
Answer: 42

# Test for None with 'is' (identity) not '==' (equality)
$ python3 -c "
x = None
print(x is None)
print(x is not None)
"
True
False

# Confirm None is falsy (Lesson 14 review)
$ python3 -c "
if not None:
    print('None is falsy')
"
None is falsy

# Confirm None's type
$ python3 -c "print(type(None))"
<class 'NoneType'>
```

---

## Exercise

### Build a Configurable Repo-Inventory Formatter

You maintain an inventory of documentation repositories stored as a list of dictionaries. Write a script that defines the data, defines a function with optional parameters, and calls the function several ways to demonstrate its flexibility.

**Step 1 — Define the data.**

Create a list called `repos` containing exactly five dictionaries. Each dictionary must have the keys `"name"` (a string), `"language"` (a string), and `"archived"` (a boolean — `True` or `False`). Use the following data:

|name|language|archived|
|---|---|---|
|sdk-python|Python|False|
|docs-site|JavaScript|False|
|old-cli|Python|True|
|api-reference|Markdown|False|
|legacy-tools|Python|True|

**Step 2 — Write the function.**

Define a function called `build_inventory` that accepts:

- `repos` (required) — the list of repo dictionaries.
- `language_filter` (optional, defaults to `None`) — if provided, only repos whose `"language"` matches this string are included. If `None`, all repos are included.
- `include_archived` (optional, defaults to `True`) — if `True`, archived repos are included. If `False`, repos where `"archived"` is `True` are excluded.
- `bullet` (optional, defaults to `"-"`) — the string used at the start of each output line.

The function must return a list of formatted strings. Each string should look like:

```
- sdk-python (Python)
```

That is: `{bullet} {name} ({language})`

**Step 3 — Call the function four times and print the results.**

- **Call A**: All defaults. Print a heading of `All Repos`, then the results.
- **Call B**: Filter to `"Python"` only, include archived. Print a heading of `Python Repos`.
- **Call C**: No language filter, exclude archived. Print a heading of `Active Repos`.
- **Call D**: Filter to `"Python"`, exclude archived, use bullet `"*"`. Print a heading of `Active Python Repos`.

For each call, print the heading, print a line of `=` characters equal to the heading's length, print each returned string on its own line, then print a blank line to separate the groups.

**Expected output:**

```
All Repos
=========
- sdk-python (Python)
- docs-site (JavaScript)
- old-cli (Python)
- api-reference (Markdown)
- legacy-tools (Python)

Python Repos
============
- sdk-python (Python)
- old-cli (Python)
- legacy-tools (Python)

Active Repos
============
- sdk-python (Python)
- docs-site (JavaScript)
- api-reference (Markdown)

Active Python Repos
===================
* sdk-python (Python)

```

---

## Audit

The following table lists every Python operation the exercise requires and the lesson that introduced it.

|Operation|Lesson|
|---|---|
|`print()`|Lesson 1|
|Variable assignment|Lesson 2|
|`str`, `bool` types|Lesson 2|
|String repetition (`*`), `len()`|Lesson 4|
|f-strings|Lesson 6|
|List literals, `.append()`|Lesson 7|
|`for` loop over a list|Lesson 9|
|`if` / `elif` / `else`, `==` comparison|Lesson 10|
|Dictionary literals, bracket key access (`d["key"]`)|Lesson 11|
|Defining functions with `def`, parameters, `return`|Lesson 15|
|Default parameters, `None` sentinel, `is None`, keyword arguments|Lesson 16 (current)|

No operation from any future lesson (Lesson 17+) is required. The exercise draws on Lessons 1, 2, 4, 6, 7, 9, 10, 11, 15, and 16, providing diverse reinforcement across the curriculum so far.