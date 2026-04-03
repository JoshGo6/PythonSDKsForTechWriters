# Lesson 19: Exceptions II — `try/except` for Script Resilience

---

## Terminology and Theory

Lesson 18 taught you to read tracebacks and recognize common exception types. That is a diagnostic skill — you see an error after it happens and figure out where it came from. This lesson teaches a _structural_ skill: wrapping code so your script can encounter an error and keep running instead of crashing.

**`try` block** — A section of code you mark as "this might fail." Python attempts to run every line inside the `try` block normally. If no exception occurs, execution continues past the entire `try/except` structure.

**`except` block** — A section of code that runs _only_ when a specific exception occurs inside the paired `try` block. Think of it as a contingency plan: "If this particular thing goes wrong, do this instead of crashing."

**Catching a specific exception** — Writing `except ValueError` or `except KeyError` to handle one known failure mode. This is the standard practice. You name the exact exception you expect so that unexpected errors still crash loudly and tell you something is genuinely broken.

**Bare `except`** — Writing `except:` with no exception type. This catches _everything_, including errors you did not anticipate. Bare excepts are almost always a mistake because they hide bugs. If your script has a typo that causes a `NameError`, a bare `except` silently swallows it and you never find out.

**The `as` keyword in an `except` clause** — Captures the exception object into a variable so you can inspect its message. The pattern is `except ValueError as e`, where `e` is just a conventional name (you can use any valid variable name).

**When not to catch** — Do not wrap code in `try/except` when the error means your logic is wrong. A `TypeError` from passing a list where a string was expected usually means you wrote a bug, not that you need a safety net. Catch exceptions that represent _expected, recoverable situations_: bad user input, a missing dictionary key in data you did not create, or a file that may or may not exist on disk.

---

## Syntax Section

### Basic `try/except`

```python
try:
    # Code that might raise an exception
    risky_operation()
except SomeException:
    # Code that runs only if SomeException was raised
    handle_the_problem()
```

Python runs the `try` block line by line. The moment an exception matching `SomeException` occurs, Python stops executing the `try` block and jumps into the `except` block. Any lines in the `try` block after the failing line are skipped.

### Catching the exception object with `as`

```python
try:
    result = int(user_input)
except ValueError as e:
    print(f"Conversion failed: {e}")
```

The variable `e` holds the exception object. Printing it gives you the error message Python would normally display, which is useful for logging or for showing the user what went wrong.

### Multiple `except` blocks

```python
try:
    value = data[key]
    number = int(value)
except KeyError:
    print(f"Key '{key}' not found in data.")
except ValueError:
    print(f"Value for '{key}' is not a valid integer.")
```

Python checks each `except` block in order and runs the first one that matches the raised exception. Only one `except` block runs per exception. If the exception does not match any listed type, it propagates up and crashes the script as usual — which is the correct behavior for unexpected errors.

### Combining multiple exception types in one block

```python
try:
    value = data[key]
    number = int(value)
except (KeyError, ValueError) as e:
    print(f"Could not process key '{key}': {e}")
```

Use a tuple of exception types when you want the same handling for more than one kind of failure. The `as e` captures whichever exception actually occurred.

### What bare `except` looks like and why you should avoid it

```python
# BAD — hides bugs
try:
    result = int(data[key])
except:
    result = 0
```

This catches `KeyError`, `ValueError`, `TypeError`, `NameError`, `KeyboardInterrupt`, and everything else. If `data` is misspelled as `dta`, the resulting `NameError` is silently swallowed and you get `0` with no indication that your code has a bug. Always name the exception you expect.

---

## Worked Examples

### Example 1: Safe integer parsing from user input

Scripts that accept input often need to convert strings to numbers. The conversion fails with a `ValueError` if the string is not numeric. This example wraps the conversion so the script prints a clear message instead of crashing.

```python
def parse_age(text):
    try:
        age = int(text)
    except ValueError as e:
        print(f"Invalid age input: {e}")
        return None
    return age


inputs = ["29", "not_a_number", "42", "", "17"]

for item in inputs:
    result = parse_age(item)
    if result is not None:
        print(f"  Parsed age: {result}")
    else:
        print(f"  Skipped bad input: '{item}'")
```

**What happens:** The function tries `int(text)` for each input. For `"29"`, `"42"`, and `"17"`, the conversion succeeds and the function returns the integer. For `"not_a_number"` and `""`, `int()` raises a `ValueError`, the `except` block prints the error message, and the function returns `None`. The calling code uses a conditional to check whether parsing succeeded.

**Output:**

```
  Parsed age: 29
Invalid age input: invalid literal for int() with base 10: 'not_a_number'
  Skipped bad input: 'not_a_number'
  Parsed age: 42
Invalid age input: invalid literal for int() with base 10: ''
  Skipped bad input: ''
  Parsed age: 17
```

### Example 2: Safe dictionary key access

When processing data from an external source (like an API response stored as a dict), some records may be missing expected keys. This example processes a list of records and handles missing keys gracefully instead of crashing on the first bad record.

```python
records = [
    {"name": "auth-service", "version": "2.4.1", "status": "active"},
    {"name": "log-collector", "status": "active"},
    {"name": "cache-layer", "version": "1.0.0", "status": "deprecated"},
    {"name": "metrics-api"},
]

valid_count = 0

for record in records:
    name = record.get("name", "UNKNOWN")
    try:
        version = record["version"]
        status = record["status"]
    except KeyError as e:
        print(f"Skipping '{name}': missing key {e}")
        continue

    print(f"  {name} v{version} — {status}")
    valid_count = valid_count + 1

print(f"\nProcessed {valid_count} complete record(s).")
```

**What happens:** For each record, the code uses `.get()` to safely grab the name (so it always has something to print). Then it tries direct key access for `version` and `status`. If either key is missing, the `except KeyError` block prints which key was missing and `continue` skips to the next record. Records that have all required keys print normally.

**Output:**

```
  auth-service v2.4.1 — active
Skipping 'log-collector': missing key 'version'
  cache-layer v1.0.0 — deprecated
Skipping 'metrics-api': missing key 'status'

Processed 2 complete record(s).
```

### Example 3: Multiple exception types in one block

This example combines two failure modes — a missing key and a bad numeric conversion — into a single handler. It processes a list of item records where the `"quantity"` field might be missing or might contain a non-numeric string.

```python
def summarize_item(item):
    name = item.get("name", "UNKNOWN")
    try:
        qty = int(item["quantity"])
    except (KeyError, ValueError) as e:
        return f"SKIPPED '{name}': {e}"
    return f"{name}: {qty} unit(s)"


inventory = [
    {"name": "widget-A", "quantity": "50"},
    {"name": "widget-B"},
    {"name": "widget-C", "quantity": "ten"},
    {"name": "widget-D", "quantity": "12"},
]

for item in inventory:
    print(summarize_item(item))
```

**What happens:** `int(item["quantity"])` can fail two ways. If the key `"quantity"` is missing, Python raises `KeyError`. If the key exists but its value is not numeric (like `"ten"`), `int()` raises `ValueError`. The tuple `(KeyError, ValueError)` catches both. The function returns a skip message for bad records and a formatted summary for good ones.

**Output:**

```
widget-A: 50 unit(s)
SKIPPED 'widget-B': 'quantity'
SKIPPED 'widget-C': invalid literal for int() with base 10: 'ten'
widget-D: 12 unit(s)
```

---

## Quick Reference

```
# Basic try/except with a specific exception type
$ python3 -c "
try:
    x = int('abc')
except ValueError as e:
    print(f'Caught: {e}')
"
Caught: invalid literal for int() with base 10: 'abc'

# Handling a missing dictionary key
$ python3 -c "
d = {'a': 1}
try:
    val = d['z']
except KeyError as e:
    print(f'Missing key: {e}')
"
Missing key: 'z'

# Multiple exception types in one except clause
$ python3 -c "
d = {'x': 'hello'}
try:
    result = int(d['x'])
except (KeyError, ValueError) as e:
    print(f'Error: {e}')
"
Error: invalid literal for int() with base 10: 'hello'

# Separate except blocks for different handling
$ python3 -c "
d = {}
try:
    result = int(d['key'])
except KeyError:
    print('Key was missing')
except ValueError:
    print('Value was not numeric')
"
Key was missing

# Exception without 'as' — when you do not need the message
$ python3 -c "
try:
    num = int('')
except ValueError:
    print('Got empty string, using default')
    num = 0
print(f'num = {num}')
"
Got empty string, using default
num = 0

# Demonstrating that code after the failing line in try is skipped
$ python3 -c "
try:
    print('before')
    x = int('oops')
    print('after')
except ValueError:
    print('caught it')
print('script continues')
"
before
caught it
script continues
```

---

## Exercise

### Safe Score Report

You are given the following data representing student quiz submissions. Each record is a dictionary, but the data is messy: some records are missing the `"score"` key, some have non-numeric values for `"score"`, and some are complete.

```python
submissions = [
    {"student": "Alice", "score": "92"},
    {"student": "Bob", "score": "not_graded"},
    {"student": "Carol"},
    {"student": "Dan", "score": "78"},
    {"student": "Eve", "score": ""},
    {"student": "Frank", "score": "85"},
]
```

Write a script that:

1. Defines a function called `process_submission` that accepts a single submission dictionary and returns a tuple of two values: the student name and the integer score. If the record is missing the `"score"` key or the score cannot be converted to an integer, the function should catch the appropriate specific exception(s) and return a tuple of the student name and `None`.
2. Loops through `submissions`, calls `process_submission` on each record, and sorts the results into two separate lists: one for valid submissions (where the score is not `None`) and one for skipped submissions.
3. After the loop, prints a report with three sections:
    - A `"Valid scores:"` header, followed by one line per valid submission formatted as `" <name>: <score>"`.
    - A `"Skipped:"` header, followed by one line per skipped submission formatted as `" <name> (bad or missing score)"`.
    - A summary line formatted as `"Total: <valid_count> valid, <skipped_count> skipped"`.

**Expected output:**

```
Valid scores:
  Alice: 92
  Dan: 78
  Frank: 85
Skipped:
  Bob (bad or missing score)
  Carol (bad or missing score)
  Eve (bad or missing score)
Total: 3 valid, 3 skipped
```

---

## Audit

|Requirement|Introduced In|
|---|---|
|`print()` with f-strings|Lessons 3, 6|
|Variables and assignment|Lesson 2|
|Lists (creation, `append`)|Lesson 7|
|`for` loop over a list|Lesson 9|
|`if`/`else` conditional|Lesson 10|
|Dictionary key access (`d["key"]`)|Lesson 11|
|`.get()` for safe dict access|Lesson 11|
|Tuples and tuple unpacking|Lesson 13|
|`is not None` check|Lesson 14 (truthiness), Lesson 16 (`None`)|
|Defining and calling a function with `return`|Lesson 15|
|`try/except` with specific exceptions|**Lesson 19 (current)**|
|`except (Type1, Type2) as e`|**Lesson 19 (current)**|
|`continue` in a loop|Lesson 14 (guard clauses)|

All operations required by the exercise and worked examples have been introduced in the current lesson or in prior lessons. No future-lesson concepts are used. The exercise requires `try/except` from the current lesson combined with functions (15–16), tuples (13), loops (9), conditionals (10), dictionaries (11), lists (7), and f-strings (6), satisfying the requirement for diverse reinforcement across prior lessons.