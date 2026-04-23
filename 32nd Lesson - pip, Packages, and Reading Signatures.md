# Lesson 32: pip, Packages, and Reading Signatures

## Terminology and Theory

**pip** is the standard package installer for Python. When you run `pip install somepackage`, pip downloads a distribution from the Python Package Index (PyPI) and installs it into your current Python environment so you can `import` what's inside it. You've been using the **standard library** — modules like `json`, `pathlib`, `re`, `os`, `logging`, and `argparse` that ship with Python. pip lets you install _third-party_ distributions that don't ship with Python.

**Module** vs. **package** vs. **distribution** — these three words get used loosely, and their distinctions matter when you're documenting software:

- A **module** is a single `.py` file you can import. You've already written modules — any Python file you import from is a module.
- A **package** is a directory of modules organized under a common name. It contains an `__init__.py` file (which can be empty) that tells Python "this directory is importable." When you write `from pathlib import Path`, `pathlib` is a package in the standard library.
- A **distribution** (also called a **distribution package**) is what pip installs. It's the thing you download from PyPI — a bundle that may contain one package, several packages, or even just a single module. When someone says "install the `tabulate` package," they're really talking about installing the `tabulate` _distribution_, which happens to provide a single module you can import as `tabulate`. Most distributions follow this one-to-one pattern, but not all: for example, the `setuptools` distribution installs both the `setuptools` package and the `pkg_resources` package — two separate importable units from a single `pip install`.

> [!note] 
> In casual speech, people use "package" for all three, and also use "library" as a loose synonym for a distribution ("the requests library"). "Library" is not a formal term in Python's packaging system — its only quasi-official use is in the compound noun "standard library," meaning the collection of modules and packages bundled with Python. When you're writing documentation, being precise about whether you mean "module," "package," or "distribution" prevents confusion.

**Pinning versions** means specifying an exact version of a distribution so that your script behaves the same way on every machine that runs it. Without pinning, `pip install tabulate` grabs whatever the latest version is today — which might behave differently from the version you tested against.

**Reading a function signature** means looking at a function's definition line and understanding what it accepts and what it returns. A signature tells you:

1. The function's **name**.
2. Its **parameters** — the names, the order, and whether they have default values.
3. From documentation or docstrings: what **types** each parameter expects and what the function **returns**.

You've been reading signatures since Lesson 15, where you learned to define functions with `def`. Now you need to read signatures written by _other people_ — in distributions you install — and figure out how to call them correctly. The primary tools for this are the distribution's documentation, the `help()` built-in, and the function's docstring.

**`help()`** is a built-in function that prints the docstring and signature of any object. You call it in the REPL or in a script: `help(some_function)`. It's your fastest way to see what a function expects without leaving the terminal.

---

## Syntax Section

### Installing distributions with pip

Run these commands in your terminal (not inside a Python script):

```bash
# Install the latest version of a distribution
pip install tabulate

# Install a specific version (pinning)
pip install tabulate==0.9.0

# Install with a minimum version
pip install tabulate>=0.9.0

# Show what's currently installed, with exact versions
pip freeze

# Show details about one installed distribution
pip show tabulate
```

> [!tip] 
> `pip freeze` outputs every installed distribution and its version in `package==version` format. This is the same format pip uses for installation, so you can save this output to a file (`pip freeze > requirements.txt`) and replay it on another machine (`pip install -r requirements.txt`). You'll learn this workflow formally in Lesson 33 with virtual environments.

### Importing from installed distributions

Once a distribution is installed, you import what's inside it — a module or a package — the same way you import from the standard library. The `tabulate` distribution provides a single module (a `.py` file), not a package (a directory). You import from it the same way you'd import any module:

```python
# Import the tabulate module (the entire .py file)
import tabulate

# Import just the tabulate function from the tabulate module
from tabulate import tabulate
```

There is no syntactic difference between importing a standard library module and importing a module from an installed distribution. Python searches a list of directories (the "module search path") and the installed module's location is on that list after installation.

### Reading a signature with `help()`

```python
from tabulate import tabulate

help(tabulate)
```

This prints the function's signature and its docstring — the block of text the module's author wrote to explain how the function works. A typical docstring tells you what each parameter does, what types it accepts, and what the function returns.

### Anatomy of a function signature

When you call `help(tabulate)` or read the project's documentation, you'll see something like this:

```
tabulate(tabular_data, headers=(), tablefmt="simple", ...)
```

Breaking this down using what you already know from Lessons 15 and 16:

- `tabular_data` — a **positional parameter**. It has no default value, so you must provide it.
- `headers=()` — a **keyword parameter with a default**. The default is an empty tuple, so if you don't provide headers, none are shown.
- `tablefmt="simple"` — another keyword parameter with a default. It controls the output format and defaults to `"simple"`.
- `...` — the documentation is showing you that there are more parameters. You can check `help()` or the docs for the full list.

To call this function, you must provide the required positional argument and can optionally override any defaults:

```python
# Minimum call: just the data
tabulate(my_data)

# Override one default
tabulate(my_data, headers="firstrow")

# Override two defaults
tabulate(my_data, headers="keys", tablefmt="grid")
```

> [!info] You already understand this from Lesson 16 (default parameters). The new skill here is applying that understanding to _someone else's_ function — one you didn't write — by reading its signature and docstring.

---

## Worked Examples

### Example 1: Installing and using `tabulate`

`tabulate` is a small, single-module distribution that formats tabular data as plain-text tables. It's useful for SDK documentation workflows where you want to print structured data in a readable format.

First, install it in your terminal:

```bash
pip install tabulate==0.9.0
```

Then create and run this script:

```python
from tabulate import tabulate

# A list of lists — each inner list is a row
rows = [
    ["PyGithub", "1.59.1", "GitHub API wrapper"],
    ["requests", "2.31.0", "HTTP library"],
    ["tabulate", "0.9.0", "Table formatter"],
]

headers = ["Package", "Version", "Description"]

output = tabulate(rows, headers=headers, tablefmt="grid")
print(output)
```

Output:

```
+-----------+-----------+---------------------+
| Package   | Version   | Description         |
+===========+===========+=====================+
| PyGithub  | 1.59.1    | GitHub API wrapper  |
+-----------+-----------+---------------------+
| requests  | 2.31.0    | HTTP library        |
+-----------+-----------+---------------------+
| tabulate  | 0.9.0     | Table formatter     |
+-----------+-----------+---------------------+
```

What happened here:

1. You imported the `tabulate` function from the `tabulate` module.
2. You prepared data as a list of lists — the same nested-list structure from Lesson 8.
3. You called `tabulate()` with three arguments: the data (required positional argument), `headers` (overriding the default empty tuple), and `tablefmt` (overriding the default `"simple"` format with `"grid"`).
4. The function returned a formatted string, which you printed.

### Example 2: Using `help()` to read a signature you haven't seen before

Suppose you've installed `tabulate` but you don't know what table formats are available. You can explore from the REPL:

```python
from tabulate import tabulate

help(tabulate)
```

This prints a long docstring. The relevant section looks something like:

```
tabulate(tabular_data, headers=(), tablefmt="simple",
         floatfmt="g", numalign="decimal", stralign="left", ...)

    Format a fixed-width table for pretty printing.

    >>> print(tabulate([["Alice", 24], ["Bob", 19]], headers=["Name", "Age"]))
    Name      Age
    ------  -----
    Alice      24
    Bob        19
```

From this, you can read:

- `tabular_data` is required (no default value).
- `headers` defaults to `()` — an empty tuple, so no headers by default.
- `tablefmt` defaults to `"simple"`.
- `floatfmt` controls float formatting and defaults to `"g"`.
- `numalign` and `stralign` control alignment.

You don't need to memorize every parameter. The skill is knowing how to find them and interpret what the defaults mean so you can decide which ones to override.

### Example 3: Reading a signature and calling with dict data

`tabulate` also accepts a list of dictionaries. You can discover this by reading the docstring (via `help()` or online documentation), which mentions that when the data is a list of dicts, you can pass `headers="keys"` to use the dictionary keys as column headers.

```python
import json
import logging
from tabulate import tabulate

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

json_text = '[{"name": "Alice", "role": "Writer"}, {"name": "Bob", "role": "Editor"}]'

data = json.loads(json_text)
logging.info("Loaded %d records from JSON", len(data))

output = tabulate(data, headers="keys", tablefmt="github")
print(output)
```

Output:

```
INFO: Loaded 2 records from JSON
| name   | role   |
|--------|--------|
| Alice  | Writer |
| Bob    | Editor |
```

What happened here:

1. You parsed a JSON string into a list of dictionaries using `json.loads()` (Lesson 28).
2. You logged the record count with `logging.info()` (Lesson 21).
3. You passed the list of dicts directly to `tabulate()`. Because each dict has the same keys, `tabulate` can use them as column headers when you pass `headers="keys"`.
4. You used `tablefmt="github"` — a format you discovered by reading the docstring — which produces a GitHub-flavored Markdown table.

---

## Quick Reference

```python
# Install a distribution from PyPI (run in terminal, not in Python)
# pip install tabulate

# Install a pinned version (run in terminal)
# pip install tabulate==0.9.0

# List installed distributions with versions (run in terminal)
# pip freeze

# Show info about an installed distribution (run in terminal)
# pip show tabulate

# Import a function from an installed module (same syntax as standard library)
from tabulate import tabulate

# Read a function's signature and docstring
help(tabulate)

# Call with only the required positional argument
print(tabulate([["a", 1], ["b", 2]]))

# Override default keyword arguments by name
print(tabulate([["a", 1], ["b", 2]], headers=["Letter", "Number"], tablefmt="grid"))

# Use dict data with headers="keys" to auto-detect column headers
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
print(tabulate(data, headers="keys", tablefmt="github"))
```

---

## Exercise

### Dependency Report Formatter

Write a script called `dep_report.py` that reads a JSON file containing a list of software dependencies and prints a formatted table to the terminal.

**Input file (`deps.json`):**

Create this file in your working directory:

```json
[
    {"name": "PyGithub", "version": "1.59.1", "category": "sdk"},
    {"name": "requests", "version": "2.31.0", "category": "http"},
    {"name": "tabulate", "version": "0.9.0", "category": "formatting"},
    {"name": "Flask", "version": "3.0.0", "category": "http"},
    {"name": "mistune", "version": "3.0.2", "category": "parsing"},
    {"name": "PyYAML", "version": "6.0.1", "category": "parsing"},
    {"name": "black", "version": "24.3.0", "category": "formatting"}
]
```

**Requirements:**

1. The script must accept two command-line arguments using `argparse`:
    - A required positional argument: the path to the JSON file.
    - An optional flag `--category` that filters the output to only show dependencies in that category. If omitted, show all dependencies.
2. Load the JSON file. If the file does not exist, catch the `FileNotFoundError`, log an error message, and exit.
3. If `--category` is provided, filter the list to only include entries where the `"category"` value matches the flag's value. If no entries match, log a warning and exit.
4. Sort the filtered list alphabetically by `"name"` using `sorted()` with a `key=` argument. The key should be a small function you define that returns the lowercase name of a dependency dict. (Do not use `lambda` — it has not been taught yet.)
5. Format the sorted list as a table using `tabulate` with `headers="keys"` and `tablefmt="grid"`.
6. Print the table.
7. Use `logging` at the `INFO` level to report how many dependencies were loaded and how many are being displayed.

**Expected output (no filter):**

```
$ python dep_report.py deps.json
INFO: Loaded 7 dependencies from deps.json
INFO: Displaying 7 dependencies
+----------+-----------+--------------+
| name     | version   | category     |
+==========+===========+==============+
| black    | 24.3.0    | formatting   |
+----------+-----------+--------------+
| Flask    | 3.0.0     | http         |
+----------+-----------+--------------+
| mistune  | 3.0.2     | parsing      |
+----------+-----------+--------------+
| PyGithub | 1.59.1    | sdk          |
+----------+-----------+--------------+
| PyYAML   | 6.0.1     | parsing      |
+----------+-----------+--------------+
| requests | 2.31.0    | http         |
+----------+-----------+--------------+
| tabulate | 0.9.0     | formatting   |
+----------+-----------+--------------+
```

**Expected output (with filter):**

```
$ python dep_report.py deps.json --category parsing
INFO: Loaded 7 dependencies from deps.json
INFO: Displaying 2 dependencies
+----------+-----------+------------+
| name     | version   | category   |
+==========+===========+============+
| mistune  | 3.0.2     | parsing    |
+----------+-----------+------------+
| PyYAML   | 6.0.1     | parsing    |
+----------+-----------+------------+
```

**Expected output (category not found):**

```
$ python dep_report.py deps.json --category testing
INFO: Loaded 7 dependencies from deps.json
WARNING: No dependencies found in category 'testing'
```

**Expected output (file not found):**

```
$ python dep_report.py missing.json
ERROR: File not found: missing.json
```

---

## Audit

|Operation / Syntax|Required By|Introduced In|
|---|---|---|
|`argparse.ArgumentParser`, `add_argument`, `parse_args`|CLI argument handling|Lesson 30|
|`json.load()`|Reading JSON from file|Lesson 28|
|`open()` with `with` statement|File reading|Lesson 22|
|`try` / `except FileNotFoundError`|Error handling for missing file|Lesson 19|
|`logging.basicConfig()`, `logging.info()`, `logging.warning()`, `logging.error()`|Status messages|Lesson 21|
|`for` loop with `if` conditional (filtering)|Filtering list of dicts|Lessons 9, 10|
|Dictionary key access (`d["key"]`)|Reading dict fields|Lesson 11|
|`sorted()` with `key=` parameter|Sorting the filtered list|Lesson 15 (functions), Lesson 16 (default params)|
|Defining a small function for `key=`|Sort key function|Lesson 15|
|`.lower()`|Case-insensitive sort|Lesson 5|
|`len()`|Counting items|Lesson 7|
|f-strings|Formatted log messages|Lesson 6|
|`pip install tabulate`|Installing a third-party distribution|**Lesson 32 (current)**|
|`from tabulate import tabulate`|Importing from an installed module|**Lesson 32 (current)**|
|`tabulate()` with `headers=` and `tablefmt=`|Reading and calling from a signature|**Lesson 32 (current)**|
|`sys.exit()`|Exiting on error|Lesson 29 (`sys` module)|
|List building via `.append()` in a loop|Accumulating filtered results|Lesson 7|
|Truthiness check (empty list)|Checking if filter produced results|Lesson 14|

All operations trace to the current lesson or a prior lesson. No forward dependencies detected.