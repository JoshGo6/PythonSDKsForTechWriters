# Lesson 20: The `logging` Module — Replacing `print()` for Real Scripts

## Audit

|Operation/Syntax Required|Introduced In|
|---|---|
|`import logging` (module import)|Lesson 17|
|`logging.basicConfig()`|Lesson 20 (current)|
|`logging.debug()`, `logging.info()`, `logging.warning()`, `logging.error()`, `logging.critical()`|Lesson 20 (current)|
|`level=logging.DEBUG` (setting threshold)|Lesson 20 (current)|
|`format` string with `%(levelname)s` / `%(message)s` placeholders|Lesson 20 (current)|
|`def` / functions with parameters and return values|Lessons 15–16|
|Default parameters and `None`|Lesson 16|
|`for` loop over a list|Lesson 9|
|`if/elif/else` conditionals|Lesson 10|
|Dictionary creation and key access|Lesson 11|
|`.get()` for safe key lookup|Lesson 11|
|`.items()` iteration|Lesson 12|
|Tuple unpacking in loop|Lesson 13|
|Truthiness checks|Lesson 14|
|`try/except` with specific exception types|Lesson 19|
|`continue`|Lesson 14|
|f-strings|Lesson 6|
|String methods (`.strip()`, `.lower()`)|Lesson 5|
|`.append()`|Lesson 7|
|`print()`|Lesson 1|
|`len()`|Lesson 7|

All operations verified as introduced in current or prior lessons. No future-lesson dependencies detected.

---

## Terminology and theory

**`logging` module**: A standard library module (no installation needed) that gives your scripts a structured way to emit status messages. Instead of scattering `print()` calls through your code, you call `logging.info()`, `logging.warning()`, and so on. Each call carries a _severity level_ that tells the reader — and the logging system — how important the message is.

**Log level (severity level)**: A label that ranks how urgent or important a message is. Python's `logging` module defines five standard levels, from least severe to most severe:

- `DEBUG` — Fine-grained detail useful during development. Example: printing the value of a variable on each loop iteration to trace behavior.
- `INFO` — Confirmation that things are working as expected. Example: reporting that a file was processed successfully.
- `WARNING` — Something unexpected happened, but the script can continue. Example: a config value was missing, so a default was used.
- `ERROR` — A serious problem prevented part of the script from doing its job. Example: a file couldn't be opened.
- `CRITICAL` — A fatal problem; the script probably cannot continue. Example: a required database connection failed completely.

**Threshold (effective level)**: The minimum severity a message must have before the logging system will actually display it. If you set the threshold to `WARNING`, then `DEBUG` and `INFO` messages are silently discarded — only `WARNING`, `ERROR`, and `CRITICAL` messages appear. This is the core mechanism that lets you leave debug messages in your code without cluttering production output.

**`logging.basicConfig()`**: A convenience function you call once, near the top of your script, to configure the logging system's threshold and output format in a single step. If you never call `basicConfig()`, the default threshold is `WARNING`, which means your `DEBUG` and `INFO` calls silently produce nothing — a common source of confusion.

**Why not just use `print()`?** You have been using `print()` as your primary inspection tool since Lesson 3. That approach works for quick checks, but it has real limits in scripts that do meaningful work:

- You cannot turn `print()` calls on and off without deleting or commenting them out. With `logging`, you change one threshold value and an entire category of messages appears or disappears.
- `print()` gives no indication of severity. With `logging`, each message is tagged, so you can scan output and immediately see what is informational versus what is a problem.
- When a script grows, `print()` debugging lines get mixed in with the script's actual intended output. `logging` writes to standard error (`stderr`) by default, keeping it separate from anything you send to standard output (`stdout`).

**`format` string**: An optional argument to `basicConfig()` that controls what each log line looks like. You define a pattern using special placeholders such as `%(levelname)s` (the level tag), `%(message)s` (the text you passed), and `%(asctime)s` (a timestamp). This is a separate formatting system from f-strings — the `%()s` placeholders are specific to the `logging` module's internal formatter.

---

## Syntax

### Importing and configuring

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

`import logging` makes the module available. `logging.basicConfig(level=logging.DEBUG)` sets the threshold to `DEBUG`, meaning all five levels will produce output. Replace `logging.DEBUG` with `logging.INFO`, `logging.WARNING`, `logging.ERROR`, or `logging.CRITICAL` to raise the threshold.

### Emitting messages at each level

```python
logging.debug("This is a debug message")
logging.info("This is an info message")
logging.warning("This is a warning message")
logging.error("This is an error message")
logging.critical("This is a critical message")
```

Each function accepts a string. The logging system checks the message's level against the configured threshold. If the message's level is at or above the threshold, it appears; otherwise it is silently discarded.

### Using `basicConfig()` with a format string

```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(message)s"
)
```

`%(levelname)s` inserts the level name (e.g., `DEBUG`, `INFO`). `%(message)s` inserts the text you passed. The output of `logging.info("Script started")` with this format would be:

```
INFO: Script started
```

Without a custom format, Python uses a default that includes the level name and the message, prefixed by the logger name. Common placeholders you may encounter:

- `%(asctime)s` — a human-readable timestamp
- `%(levelname)s` — the level name
- `%(message)s` — the log message text

### Embedding variable data in log messages

You can use f-strings as the argument to a logging call:

```python
filename = "report.md"
logging.info(f"Processing file: {filename}")
```

This works because the f-string evaluates to a regular string, which the logging function then handles normally.

### Key point: `basicConfig()` only works once

`logging.basicConfig()` configures the root logger the first time it is called. If you call it a second time in the same script, the second call is silently ignored. This means you should call it once, early in your script, before any logging calls.

---

## Worked examples

### Example 1: Basic threshold behavior

This script demonstrates how changing the threshold controls which messages appear.

```python
import logging

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

logging.debug("Checking each item in the list")
logging.info("Started processing")
logging.warning("Input list is empty, using default values")
logging.error("Could not find the expected key")
logging.critical("Script cannot continue without valid input")
```

**Output:**

```
WARNING: Input list is empty, using default values
ERROR: Could not find the expected key
CRITICAL: Script cannot continue without valid input
```

The `DEBUG` and `INFO` messages do not appear because the threshold is set to `WARNING`. Only messages at `WARNING` or above pass through. If you change `level=logging.WARNING` to `level=logging.DEBUG`, all five messages would appear.

### Example 2: Replacing `print()` in a function that processes data

This example shows a before-and-after conversion. Here is a small function that uses `print()` for status messages:

```python
# BEFORE — print-based debugging
def summarize_scores(scores):
    print(f"DEBUG: Received {len(scores)} scores")
    total = 0
    for name, score in scores.items():
        print(f"DEBUG: Processing {name} = {score}")
        if score < 0:
            print(f"WARNING: Negative score for {name}, skipping")
            continue
        total = total + score
    print(f"INFO: Total score = {total}")
    return total

data = {"Alice": 90, "Bob": -1, "Carol": 85}
result = summarize_scores(data)
print(f"Result: {result}")
```

Here is the same function converted to use `logging`:

```python
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def summarize_scores(scores):
    logging.debug(f"Received {len(scores)} scores")
    total = 0
    for name, score in scores.items():
        logging.debug(f"Processing {name} = {score}")
        if score < 0:
            logging.warning(f"Negative score for {name}, skipping")
            continue
        total = total + score
    logging.info(f"Total score = {total}")
    return total

data = {"Alice": 90, "Bob": -1, "Carol": 85}
result = summarize_scores(data)
print(f"Result: {result}")
```

**Output (with threshold at DEBUG):**

```
DEBUG: Received 3 scores
DEBUG: Processing Alice = 90
DEBUG: Processing Bob = -1
WARNING: Negative score for Bob, skipping
DEBUG: Processing Carol = 85
INFO: Total score = 175
Result: 175
```

Notice that the final `print()` for the actual result stays as `print()`. That line is the script's real output — it is not a debugging or status message. A common pattern is: use `logging` for status and diagnostics, and `print()` for the script's intended output.

If you change the threshold to `level=logging.WARNING`, the output becomes:

```
WARNING: Negative score for Bob, skipping
Result: 175
```

All the debug and info detail disappears, leaving only the warning and the script's actual result. You did not delete a single line of code — you changed one value.

### Example 3: Logging inside `try/except` blocks

Logging pairs naturally with exception handling. When you catch an error, a `logging.error()` call records what went wrong without crashing the script.

```python
import logging

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def safe_lookup(records, key):
    logging.debug(f"Looking up key: {key}")
    try:
        value = records[key]
    except KeyError:
        logging.error(f"Key not found: {key}")
        return None
    logging.info(f"Found {key} = {value}")
    return value

inventory = {"apples": 12, "bananas": 5}

result_1 = safe_lookup(inventory, "apples")
result_2 = safe_lookup(inventory, "grapes")

print(f"Apples: {result_1}")
print(f"Grapes: {result_2}")
```

**Output:**

```
DEBUG: Looking up key: apples
INFO: Found apples = 12
DEBUG: Looking up key: grapes
ERROR: Key not found: grapes
Apples: 12
Grapes: None
```

The `KeyError` is caught and logged at the `ERROR` level. The script continues running and produces its final output. The combination of `try/except` (Lesson 19) and `logging.error()` is a pattern you will use constantly in real scripts.

---

## Quick reference

```
# Import the logging module
$ python3 -c "import logging; print(type(logging))"
<class 'module'>

# Configure with default threshold (WARNING)
$ python3 -c "import logging; logging.basicConfig(); logging.warning('visible'); logging.info('hidden')"
WARNING:root:visible

# Configure with DEBUG threshold to see all levels
$ python3 -c "import logging; logging.basicConfig(level=logging.DEBUG); logging.debug('detail'); logging.info('status')"
DEBUG:root:detail
INFO:root:status

# Set a custom format
$ python3 -c "import logging; logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s'); logging.info('ready')"
INFO: ready

# DEBUG messages hidden when threshold is INFO
$ python3 -c "import logging; logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s'); logging.debug('hidden'); logging.info('shown')"
INFO: shown

# Use f-strings inside logging calls
$ python3 -c "import logging; logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s'); name='test.md'; logging.info(f'Processing {name}')"
INFO: Processing test.md

# ERROR level for caught exceptions
$ python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
try:
    x = int('abc')
except ValueError:
    logging.error('Could not convert value')
"
ERROR: Could not convert value

# CRITICAL level for fatal conditions
$ python3 -c "import logging; logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s'); logging.critical('Cannot proceed')"
CRITICAL: Cannot proceed
```

---

## Exercises

### Exercise 1: Convert a `print()`-based report script to use `logging`

Below is a script that processes a list of documentation page records. It uses `print()` for all its status messages. Your task is to rewrite this script so that every status and diagnostic message uses the `logging` module at the appropriate level, while the script's actual report output remains as `print()`.

**Starting script:**

```python
def generate_report(pages, min_word_count=100):
    print(f"DEBUG: generate_report called with {len(pages)} pages, min_word_count={min_word_count}")
    report_lines = []
    skipped = 0
    for page in pages:
        title = page.get("title")
        word_count = page.get("word_count")
        status = page.get("status")
        print(f"DEBUG: Checking page: {title}")
        if not title:
            print("WARNING: Page with missing title encountered, skipping")
            skipped = skipped + 1
            continue
        if word_count is None:
            print(f"ERROR: Page '{title}' has no word_count field")
            skipped = skipped + 1
            continue
        if word_count < min_word_count:
            print(f"WARNING: Page '{title}' has only {word_count} words (below minimum {min_word_count})")
        clean_status = status.strip().lower() if status else "unknown"
        line = f"{title} | {word_count} words | {clean_status}"
        report_lines.append(line)
        print(f"DEBUG: Added line: {line}")
    print(f"INFO: Report complete. {len(report_lines)} pages included, {skipped} skipped.")
    return report_lines

pages = [
    {"title": "Installation Guide", "word_count": 350, "status": "Published"},
    {"title": "", "word_count": 200, "status": "Draft"},
    {"title": "API Overview", "word_count": None, "status": "Review"},
    {"title": "Quick Start", "word_count": 45, "status": " Draft "},
    {"title": "Authentication", "word_count": 210, "status": "Published"},
]

results = generate_report(pages)
print("--- Final Report ---")
for line in results:
    print(line)
```

**Requirements:**

1. Add `import logging` and configure `logging.basicConfig()` with the threshold set to `DEBUG` and a format string that displays the level name followed by a colon, a space, and the message text.
2. Replace every `print()` call that is currently acting as a status or diagnostic message with the appropriate `logging` call. Choose the correct level (`debug`, `info`, `warning`, or `error`) based on the severity indicated by the original print text.
3. Keep `print()` for the script's actual report output — the `"--- Final Report ---"` header and the report lines.
4. Do not change the function's logic, parameters, or return value.

**Expected output:**

```
DEBUG: generate_report called with 5 pages, min_word_count=100
DEBUG: Checking page: Installation Guide
DEBUG: Added line: Installation Guide | 350 words | published
DEBUG: Checking page: 
WARNING: Page with missing title encountered, skipping
DEBUG: Checking page: API Overview
ERROR: Page 'API Overview' has no word_count field
DEBUG: Checking page: Quick Start
WARNING: Page 'Quick Start' has only 45 words (below minimum 100)
DEBUG: Added line: Quick Start | 45 words | draft
DEBUG: Checking page: Authentication
DEBUG: Added line: Authentication | 210 words | published
INFO: Report complete. 3 pages included, 2 skipped.
--- Final Report ---
Installation Guide | 350 words | published
Quick Start | 45 words | draft
Authentication | 210 words | published
```