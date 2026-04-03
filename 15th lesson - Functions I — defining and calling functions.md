# Lesson 15: Functions I — Defining and Calling Functions

## Terminology and Theory

A **function** is a named block of code that performs a specific task. You write the logic once, give it a name, and then **call** that name whenever you need the logic again. If you've been writing scripts where the same chunk of logic appears twice — say, cleaning up a string or summarizing a list — a function lets you collapse that into a single reusable unit.

A **function definition** is where you create the function. It starts with the `def` keyword, followed by the function's name, parentheses containing zero or more **parameters**, and a colon. The indented block beneath it is the **function body** — the code that runs when the function is called.

A **parameter** is a variable name listed in the function definition. It acts as a placeholder for the value you'll pass in later. When you actually call the function and pass a value, that value is called an **argument**. In casual usage, "parameter" and "argument" are often used interchangeably, but the distinction is: parameters are in the definition, arguments are in the call.

A **return value** is the result a function sends back to whoever called it. You specify it with the `return` keyword. When Python hits a `return` statement, the function stops immediately and hands the value back to the caller. If a function has no `return` statement, it returns `None` by default.

A **call** is when you execute a function by writing its name followed by parentheses containing any arguments. You've been calling functions since Lesson 1 — `print()`, `type()`, `len()`, `.split()`, `.strip()` — you just haven't written your own yet.

Why do functions matter for scripts?

- **Reuse.** Write the logic once, call it many times. If you're processing ten files the same way, the processing logic lives in one function, not pasted ten times.
- **Readability.** A well-named function tells a reader what a block of code does without forcing them to read every line. `clean_label(raw)` says more than eight lines of `.strip()`, `.lower()`, and `.replace()` calls.
- **Isolation.** Functions keep variables contained. A variable created inside a function doesn't leak out and collide with the rest of your script. This concept is called **scope** — variables defined inside a function exist only inside that function.

## Syntax Section

### Basic function definition and call

```python
def function_name(parameter1, parameter2):
    # function body — indented one level
    result = parameter1 + parameter2
    return result
```

- `def` — keyword that begins a function definition.
- `function_name` — follows the same naming rules as variables: lowercase, underscores, no spaces. Name it after what it does.
- `(parameter1, parameter2)` — comma-separated list of parameters. Can be zero or more.
- `:` — ends the definition line, just like `if` and `for`.
- The indented block is the body. Everything indented under `def` is part of the function.
- `return result` — sends `result` back to the caller. Optional; without it, the function returns `None`.

### Calling a function

```python
output = function_name("hello", "world")
print(output)
```

- The arguments `"hello"` and `"world"` are passed to `parameter1` and `parameter2`, in order.
- The return value is assigned to `output`.
- You can also call a function without capturing its return value, e.g. `function_name("hello", "world")`, which is common when the function does something like printing rather than returning.

### Functions with no parameters

```python
def greet():
    print("Starting script...")
```

The parentheses are still required, even when empty.

### Functions with no return value

```python
def show_header(title):
    print("=" * len(title))
    print(title)
    print("=" * len(title))
```

This function performs an action (printing) but doesn't return a value. If you captured the result, you'd get `None`:

```python
result = show_header("Report")
print(result)  # None
```

### Scope: variables inside functions stay inside

```python
def compute():
    x = 10
    return x

compute()
print(x)  # NameError — x does not exist out here
```

A variable defined inside a function cannot be accessed outside it. This is a feature, not a bug — it prevents accidental collisions between different parts of your script.

### Multiple parameters and return

```python
def build_label(name, count):
    label = f"{name}: {count} items"
    return label
```

Parameters are matched to arguments by position. In the call `build_label("widgets", 5)`, `name` gets `"widgets"` and `count` gets `5`.

## Worked Examples

### Example 1: A function that cleans a label string

Imagine you're processing a list of labels pulled from an API response. Each label has inconsistent casing and trailing whitespace. You want a function that normalizes any label to lowercase with no surrounding spaces.

```python
def clean_label(raw_label):
    cleaned = raw_label.strip().lower()
    return cleaned

labels = ["  Bug ", "FEATURE", " Enhancement ", "bug", "  FEATURE "]

for label in labels:
    print(clean_label(label))
```

Output:

```
bug
feature
enhancement
bug
feature
```

What's happening:

- `clean_label` takes one parameter, `raw_label`.
- Inside the body, it chains `.strip()` (removes whitespace) and `.lower()` (lowercases), then returns the result.
- The `for` loop calls `clean_label()` on each element, and `print()` displays the return value.
- The raw `labels` list is unchanged — the function produces new values without modifying the originals.

### Example 2: A function that summarizes a list of dictionaries

You have a list of dictionaries representing repositories. You want a function that takes one repo dictionary and returns a formatted summary string.

```python
def format_repo_summary(repo):
    name = repo.get("name", "unknown")
    stars = repo.get("stars", 0)
    language = repo.get("language", "not specified")
    summary = f"{name} ({language}) - {stars} stars"
    return summary

repos = [
    {"name": "docs-tools", "stars": 42, "language": "Python"},
    {"name": "api-client", "stars": 118, "language": "Python"},
    {"name": "infra-config", "stars": 7},
]

for repo in repos:
    print(format_repo_summary(repo))
```

Output:

```
docs-tools (Python) - 42 stars
api-client (Python) - 118 stars
infra-config (not specified) - 7 stars
```

What's happening:

- `format_repo_summary` takes a single dictionary as its parameter.
- It uses `.get()` with default values to safely handle missing keys — a defensive pattern from Lesson 14.
- It builds an f-string from the extracted values and returns it.
- The caller doesn't need to know how the formatting works. It just calls the function and gets a clean string back.

### Example 3: A function with a guard clause that returns early

Sometimes a function should bail out early if the input is bad. A `return` statement can appear anywhere in the body, and the function stops as soon as it hits one.

```python
def first_word(text):
    if not text:
        return "(empty)"
    words = text.split()
    return words[0]

test_inputs = ["hello world", "   Python SDK   ", "", "single"]

for item in test_inputs:
    print(f"Input: {repr(item):20s} -> First word: {first_word(item)}")
```

Output:

```
Input: 'hello world'        -> First word: hello
Input: '   Python SDK   '   -> First word: Python
Input: ''                   -> First word: (empty)
Input: 'single'             -> First word: single
```

What's happening:

- The guard clause `if not text` catches empty strings (which are falsy, as covered in Lesson 14). When hit, the function returns `"(empty)"` immediately — the rest of the body never runs.
- For non-empty strings, `.split()` breaks the text into words and the function returns the first one.
- `repr()` is used in the f-string to make the input visible (showing quotes and spaces explicitly). `repr()` is a built-in that returns a string showing how Python represents a value, including quotes around strings — useful for debugging when whitespace matters.

## Quick Reference

```
# Define a function with no parameters
$ python3 -c "
def greet():
    print('hello')
greet()
"
hello

# Define a function with a parameter and a return value
$ python3 -c "
def double(n):
    return n * 2
print(double(5))
"
10

# Call a function and capture its return value in a variable
$ python3 -c "
def tag(text):
    return f'[INFO] {text}'
msg = tag('started')
print(msg)
"
[INFO] started

# A function with no return statement returns None
$ python3 -c "
def do_nothing():
    pass
result = do_nothing()
print(result)
"
None

# Variables inside a function do not exist outside it (causes NameError)
$ python3 -c "
def inner():
    x = 99
inner()
print(x)
"
(NameError: name 'x' is not defined)

# Early return with a guard clause
$ python3 -c "
def safe_first(items):
    if not items:
        return 'N/A'
    return items[0]
print(safe_first([]))
print(safe_first(['a','b']))
"
N/A
a

# A function that processes a dictionary
$ python3 -c "
def label(d):
    name = d.get('name', '?')
    count = d.get('count', 0)
    return f'{name}: {count}'
print(label({'name': 'bugs', 'count': 3}))
"
bugs: 3
```

## Exercises

### Exercise 1

Write a script called `repo_report.py` that does the following:

You are given this data (paste it into your script):

```python
repos = [
    {"name": "docs-tools", "language": "Python", "open_issues": 4, "archived": False},
    {"name": "old-site", "language": "JavaScript", "open_issues": 0, "archived": True},
    {"name": "sdk-client", "language": "Python", "open_issues": 12, "archived": False},
    {"name": "test-runner", "language": "", "open_issues": 1, "archived": False},
    {"name": "legacy-api", "language": "Go", "open_issues": 0, "archived": True},
    {"name": "doc-linter", "language": "Python", "open_issues": 7, "archived": False},
]
```

**Requirements:**

1. Write a function called `format_issue_count` that takes a single integer parameter representing the number of open issues and returns a string. If the count is 0, return `"no open issues"`. Otherwise, return `"X open issue"` if the count is 1, or `"X open issues"` if the count is greater than 1 (where X is the count).
    
2. Write a function called `repo_line` that takes a single repo dictionary as a parameter. It should return a formatted string that contains the repo name and its issue count label (using `format_issue_count`). If the repo's `language` key is an empty string, display `"(no language)"` instead. The format for each line must be: `<name> [<language>] - <issue_count_label>`
    
3. In the main body of the script, loop through `repos`. Skip any repo where `"archived"` is `True`. For each non-archived repo, print the result of calling `repo_line` on that repo.
    

**Expected output:**

```
docs-tools [Python] - 4 open issues
sdk-client [Python] - 12 open issues
test-runner [(no language)] - 1 open issue
doc-linter [Python] - 7 open issues
```

---

## Audit

|Requirement|Operations used|Introduced in|
|---|---|---|
|List-of-dicts data|List literals, dictionary literals|L7, L11|
|`def` / parameters / `return`|Function definition and calls|**L15 (current)**|
|`if/elif/else` inside functions|Conditionals|L10|
|`== 0`, `== 1` comparisons|Comparison operators|L10|
|f-strings for formatted output|f-string formatting|L6|
|Direct key access on dicts|Dictionary key access|L11|
|Truthiness check on empty string|Truthiness / defensive checks|L14|
|`for repo in repos` loop|`for` loop over a list|L9|
|Skip archived repos with `if`|Conditional + truthiness|L10, L14|
|Calling one function from inside another|Function calls|**L15 (current)**|
|`print()`|Printing output|L1|

All operations are covered by Lesson 15 or earlier lessons. No future-lesson dependencies found.