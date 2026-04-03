# Lesson 18: Exceptions I — What Errors Mean and How to Read Them

---

## Terminology and Theory

**Exception:** An event that disrupts the normal flow of your program. When Python hits something it cannot do — accessing a missing dictionary key, adding a string to an integer, indexing past the end of a list — it _raises_ an exception and stops.

**Traceback:** The block of text Python prints when an unhandled exception occurs. A traceback is your primary debugging tool. It tells you _what_ went wrong, _where_ it went wrong, and _what type_ of error it was.

**Raising:** When Python encounters a problem, it "raises" an exception. You will also hear people say the code "throws" an error — same idea.

**Unhandled exception:** An exception that nothing in your program catches or deals with. When an exception is unhandled, Python prints the traceback and stops the program. (Lesson 19 will teach you how to _handle_ exceptions so your program can keep running.)

**Exception type (class name):** Every exception has a specific type that tells you the _category_ of the problem. Learning to recognize a few common types is the single fastest way to debug your scripts.

Here are the four exception types this lesson focuses on. These are the ones you will encounter most often in everyday scripting and SDK work:

- **`TypeError`** — You tried an operation on the wrong _kind_ of value. Example: adding a string and an integer, or calling something that is not callable.
- **`KeyError`** — You used bracket access (`d["key"]`) on a dictionary with a key that does not exist.
- **`IndexError`** — You used an index that is outside the valid range of a list (or other sequence).
- **`ValueError`** — The _type_ of the value is correct, but its _content_ is wrong. Example: calling `int("hello")` — a string is the right type for `int()` to receive, but `"hello"` cannot be converted to a number.

---

## Syntax Section

### Reading a traceback

When Python raises an unhandled exception, the traceback follows a consistent structure. Here is a small script that triggers an error:

```python
# broken.py
names = ["Alice", "Bob"]
print(names[5])
```

Running it produces:

```
Traceback (most recent call last):
  File "broken.py", line 2, in <module>
    print(names[5])
          ~~~~~^^^
IndexError: list index out of range
```

There are three parts to read, and you should read them **from the bottom up**:

1. **Last line — the exception type and message.** `IndexError: list index out of range` This is the most important line. It tells you the _category_ of the problem (`IndexError`) and a human-readable description (`list index out of range`).
    
2. **Middle section — the code location.** `File "broken.py", line 2, in <module>` This tells you the file name, the line number, and the scope where the error happened. `<module>` means top-level script code (not inside a function).
    
3. **First line — the header.** `Traceback (most recent call last):` This just announces that a traceback is being printed. The phrase "most recent call last" means the _deepest_ call — the one that actually failed — is shown last (at the bottom).
    

### Tracebacks with function calls

When the error happens inside a function, the traceback shows the _chain_ of calls that led to it. The bottom entry is where the error occurred; the entries above it show how Python got there:

```python
# helpers.py
def get_label(record):
    return record["label"]

data = {"name": "repo-tools"}
print(get_label(data))
```

```
Traceback (most recent call last):
  File "helpers.py", line 5, in <module>
    print(get_label(data))
  File "helpers.py", line 2, in get_label
    return record["label"]
           ~~~~~~^^^^^^^^^
KeyError: 'label'
```

Read from the bottom: the `KeyError` happened on line 2, inside `get_label`, because the dictionary `record` does not have a `"label"` key. Line 5 shows where `get_label` was called.

### Deliberately causing errors to learn their shapes

The best way to internalize exception types is to trigger them on purpose in the REPL or in short scripts. You see the traceback, read it, and connect the type name to the mistake. Here is the pattern for each of the four types:

**TypeError — wrong kind of value:**

```python
result = "count: " + 5
```

```
TypeError: can only concatenate str (not "int") to str
```

**KeyError — missing dictionary key:**

```python
d = {"name": "Alice"}
print(d["age"])
```

```
KeyError: 'age'
```

**IndexError — index out of range:**

```python
items = [10, 20, 30]
print(items[10])
```

```
IndexError: list index out of range
```

**ValueError — right type, wrong content:**

```python
number = int("abc")
```

```
ValueError: invalid literal for int() with base 10: 'abc'
```

---

## Worked Examples

### Worked Example 1: Reading a traceback from a data-processing script

This script tries to build a formatted summary from a list of SDK-style dictionaries, but contains a bug.

```python
# example1.py
repos = [
    {"name": "sdk-python", "stars": 340},
    {"name": "docs-site", "stars": 120},
    {"name": "cli-tools"}
]

for repo in repos:
    line = repo["name"] + " — " + str(repo["stars"]) + " stars"
    print(line)
```

Running this produces:

```
sdk-python — 340 stars
docs-site — 120 stars
Traceback (most recent call last):
  File "example1.py", line 8, in <module>
    line = repo["name"] + " — " + str(repo["stars"]) + " stars"
                                       ~~~~^^^^^^^^^
KeyError: 'stars'
```

**How to read it:**

Start at the bottom. The exception type is `KeyError`, and the missing key is `'stars'`. Line 8 is where it happened. The first two dictionaries printed fine, so the problem is specific to the third dictionary, which is missing the `"stars"` key.

**The fix:** Use `.get()` (from Lesson 11) to provide a default value when the key might be missing:

```python
# example1_fixed.py
repos = [
    {"name": "sdk-python", "stars": 340},
    {"name": "docs-site", "stars": 120},
    {"name": "cli-tools"}
]

for repo in repos:
    stars = repo.get("stars", 0)
    line = repo["name"] + " — " + str(stars) + " stars"
    print(line)
```

```
sdk-python — 340 stars
docs-site — 120 stars
cli-tools — 0 stars
```

### Worked Example 2: TypeError from mixing types in string building

When building output strings, you must convert non-string values explicitly. Forgetting to do so is one of the most common early mistakes.

```python
# example2.py
issue_number = 42
title = "Fix login bug"
summary = "Issue #" + issue_number + ": " + title
print(summary)
```

```
Traceback (most recent call last):
  File "example2.py", line 3, in <module>
    summary = "Issue #" + issue_number + ": " + title
              ~~~~~~~~~~^~~~~~~~~~~~~~
TypeError: can only concatenate str (not "int") to str
```

**How to read it:**

The last line says `TypeError` — you tried to concatenate a string and an `int`. The caret points to the exact spot where the `+` between `"Issue #"` and `issue_number` failed.

**The fix:** Use an f-string (from Lesson 6) instead of concatenation. F-strings handle type conversion automatically:

```python
# example2_fixed.py
issue_number = 42
title = "Fix login bug"
summary = f"Issue #{issue_number}: {title}"
print(summary)
```

```
Issue #42: Fix login bug
```

### Worked Example 3: Traceback through a function call

This example shows how a traceback reveals the chain of calls when an error happens inside a function.

```python
# example3.py
def format_user(user_list, index):
    user = user_list[index]
    return f"{user['name']} ({user['role']})"

team = [
    {"name": "Dana", "role": "writer"},
    {"name": "Eli", "role": "reviewer"}
]

print(format_user(team, 0))
print(format_user(team, 1))
print(format_user(team, 5))
```

```
Dana (writer)
Eli (reviewer)
Traceback (most recent call last):
  File "example3.py", line 12, in <module>
    print(format_user(team, 5))
  File "example3.py", line 3, in format_user
    user = user_list[index]
           ~~~~~~~~~^^^^^^^
IndexError: list index out of range
```

**How to read it:**

Start at the bottom: `IndexError` on line 3 inside `format_user`. Then look one level up: line 12 is where `format_user(team, 5)` was called. The list `team` has only 2 elements (valid indices 0 and 1), so index `5` is out of range.

**The fix:** Check the index before accessing the list. A truthiness-based guard (from Lesson 14) or a direct comparison works:

```python
# example3_fixed.py
def format_user(user_list, index):
    if index >= len(user_list):
        return f"No user at index {index}"
    user = user_list[index]
    return f"{user['name']} ({user['role']})"

team = [
    {"name": "Dana", "role": "writer"},
    {"name": "Eli", "role": "reviewer"}
]

print(format_user(team, 0))
print(format_user(team, 1))
print(format_user(team, 5))
```

```
Dana (writer)
Eli (reviewer)
No user at index 5
```

---

## Quick Reference

```
# Anatomy of a traceback: read from the BOTTOM UP
# 1. Last line = exception type + message
# 2. Middle lines = file, line number, code
# 3. First line = "Traceback (most recent call last):"

# TypeError: wrong kind of value for the operation
$ python3 -c "print('hello' + 5)"
TypeError: can only concatenate str (not "int") to str

# KeyError: dictionary key does not exist
$ python3 -c "d = {'a': 1}; print(d['b'])"
KeyError: 'b'

# IndexError: list index out of range
$ python3 -c "x = [1, 2]; print(x[10])"
IndexError: list index out of range

# ValueError: right type, wrong content
$ python3 -c "print(int('abc'))"
ValueError: invalid literal for int() with base 10: 'abc'

# Fix TypeError: convert with str() or use f-strings
$ python3 -c "n = 5; print(f'count: {n}')"
count: 5

# Fix KeyError: use .get() with a default
$ python3 -c "d = {'a': 1}; print(d.get('b', 'missing'))"
missing

# Fix IndexError: check length before accessing
$ python3 -c "x = [1, 2]; print(x[1] if len(x) > 1 else 'out of range')"
2

# Fix ValueError: check content before converting
$ python3 -c "s = '42'; print(int(s) if s.isdigit() else 'not a number')"
42
```

---

## Exercises

### Exercise 1: Debug a broken report-builder script

The following script is supposed to process a list of issue records and print a formatted report. It contains **four bugs**, each of which produces a different exception type from this lesson (`TypeError`, `KeyError`, `IndexError`, `ValueError`). The bugs are in the data and in the code — not in the structure of the program itself.

Your task:

1. Save the script below to a file called `debug_report.py`.
2. Run it. It will crash on the first bug.
3. Read the traceback, identify the exception type and the line, and fix the bug.
4. Run it again. It will crash on the next bug.
5. Repeat until all four bugs are fixed and the script runs cleanly.

**Rules:**

- You may only use techniques from Lessons 1–18 to fix each bug.
- Each fix should be minimal — correct the specific problem without rewriting the whole script.
- After fixing all four bugs, the script must produce the exact expected output shown below.

```python
# debug_report.py

def build_label(record):
    priority = record["priority"]
    return "P" + priority

def summarize_issue(records, index):
    rec = records[index]
    title = rec["title"]
    author = rec.get("author", "unassigned")
    label = build_label(rec)
    return f"[{label}] {title} (by {author})"

issues = [
    {"title": "Fix auth flow", "priority": 1, "author": "Dana"},
    {"title": "Update README", "priority": 2, "author": "Eli"},
    {"title": "Add rate-limit docs", "priority": "1"},
    {"title": "Refactor parser", "priortiy": 3, "author": "Sam"}
]

header = "=== Issue Report ==="
print(header)
print("")

for i in range(len(issues)):
    line = summarize_issue(issues, i)
    print(line)

print("")
footer_count = int("four")
print(f"Total issues: {footer_count}")
```

**Expected output after all fixes:**

```
=== Issue Report ===

[P1] Fix auth flow (by Dana)
[P2] Update README (by Eli)
[P1] Add rate-limit docs (by unassigned)
[P3] Refactor parser (by Sam)

Total issues: 4
```

**What to hand in:** Your corrected `debug_report.py` that produces the expected output when run with `python3 debug_report.py`.

---

## Audit

|Bug / Operation|Exception Type|Required Knowledge|Introduced In|
|---|---|---|---|
|`"P" + priority` where `priority` is `int`|`TypeError`|String concatenation, `str()` conversion or f-strings|Lesson 4 (strings), Lesson 6 (f-strings)|
|`record["priority"]` on a dict with a typo `"priortiy"`|`KeyError`|Dictionary bracket access, `.get()`|Lesson 11|
|`int("four")` — string cannot convert to int|`ValueError`|`int()` built-in, understanding of valid conversion|Lesson 2 (types)|
|Fix concatenation type mismatch|`str()` or f-string|Type conversion|Lesson 2, Lesson 6|
|Fix missing key via `.get()` or correcting the typo|Dict `.get()` with default, or fixing the data|Dictionary operations|Lesson 11|
|Fix `int("four")` by replacing with `len(issues)` or literal `4`|`len()`, integer literal|List operations, basic types|Lesson 2, Lesson 7|
|`for i in range(len(...))` loop|`range()`, `len()`, `for` loop|Loop iteration|Lesson 9|
|`def`, parameters, `return`|Function definition|Functions|Lesson 15|
|Default parameter via `.get()`|Dict safe access|Dictionary methods|Lesson 11|
|f-strings for formatted output|String formatting|f-strings|Lesson 6|
|`print()` with empty string for blank line|Printing|Basic output|Lesson 3|

All operations required by the exercise were introduced in Lessons 1–18. No future-lesson concepts are required. Each of the four bugs maps to one of the four exception types taught in this lesson, and the fixes use only techniques from prior lessons.