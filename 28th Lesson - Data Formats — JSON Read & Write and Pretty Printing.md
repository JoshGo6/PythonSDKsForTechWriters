# Lesson 28: Data Formats — JSON Read/Write and Pretty Printing

## Terminology and Theory

**JSON** (JavaScript Object Notation) is a text-based data format used almost everywhere in software: API responses, configuration files, data exports, and SDK object representations. Despite the name, JSON is language-independent. You will encounter JSON constantly when working with APIs and SDKs, because it is the standard format for sending and receiving structured data over HTTP.

**Serialization** is the process of converting a Python object (a dict, a list, etc.) into a JSON string so it can be saved to a file or sent across a network. **Deserialization** is the reverse: reading a JSON string and converting it back into a Python object.

The `json` module in the standard library handles both directions. You imported it briefly in Lesson 17; now you will use it in depth.

The mapping between JSON types and Python types is direct and predictable:

|JSON type|Python type|
|---|---|
|`{}`|`dict`|
|`[]`|`list`|
|`"string"`|`str`|
|`123`|`int`|
|`1.5`|`float`|
|`true/false`|`bool` (`True`/`False`)|
|`null`|`None`|

This means that every JSON file you load will become a combination of dicts, lists, strings, numbers, booleans, and `None` — types you already know how to work with.

There are four core functions in the `json` module. They come in two pairs:

- **String pair:** `json.loads()` reads a JSON string into a Python object. `json.dumps()` writes a Python object into a JSON string. The trailing `s` stands for "string."
- **File pair:** `json.load()` reads a JSON file into a Python object. `json.dump()` writes a Python object into a JSON file. These work with file handles, not strings.

> [!tip] Remember the `s` suffix: `loads`/`dumps` work with **s**trings. `load`/`dump` work with file objects.

## Syntax Section

### Deserializing: JSON string → Python object

```python
import json

json_string = '{"name": "repo-tools", "stars": 42, "archived": false}'
data = json.loads(json_string)
```

`json.loads()` takes a single string argument containing valid JSON and returns the corresponding Python object. After this call, `data` is a plain Python `dict` and you access its values exactly the way you learned in Lessons 11–12: `data["name"]`, `data.get("stars", 0)`, and so on.

### Serializing: Python object → JSON string

```python
import json

config = {"output_dir": "build", "verbose": True, "retries": 3}
json_string = json.dumps(config)
```

`json.dumps()` takes a Python object and returns a JSON string. By default, the string is compact — no extra whitespace or line breaks.

To produce human-readable output, pass the `indent` parameter:

```python
json_string = json.dumps(config, indent=2)
```

This adds newlines and indentation (two spaces per level in this case), making the output easy to read and inspect.

Another useful parameter is `sort_keys`, which alphabetizes the keys:

```python
json_string = json.dumps(config, indent=2, sort_keys=True)
```

Sorted keys make output predictable and diffable, which matters when you are comparing two JSON files or writing tests.

### Reading JSON from a file

```python
import json
from pathlib import Path

path = Path("config.json")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
```

`json.load()` takes a file object (not a filename string) and returns the parsed Python object. You open the file with a `with` statement exactly as you learned in Lesson 22, then pass the file handle `f` to `json.load()`.

### Writing JSON to a file

```python
import json
from pathlib import Path

output_path = Path("output.json")
result = {"status": "complete", "count": 17}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2)
```

`json.dump()` takes two required arguments: the Python object and a file handle. The `indent` parameter works the same way as in `json.dumps()`. The function writes directly to the file; it does not return a string.

### Handling `json.JSONDecodeError`

When `json.loads()` or `json.load()` receives invalid JSON, it raises `json.JSONDecodeError`. You can catch this with `try/except` (Lesson 19) to handle malformed data gracefully:

```python
import json

bad_string = '{"name": "broken", "stars": }'

try:
    data = json.loads(bad_string)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

## Worked Examples

### Example 1: Loading a JSON string and extracting fields

This example simulates receiving an API response as a JSON string, parsing it, and printing selected fields.

```python
import json

# Simulated API response (a JSON string)
response_text = '''
{
    "repository": "sdk-docs",
    "owner": "acme-corp",
    "open_issues": 14,
    "topics": ["python", "sdk", "documentation"],
    "private": false
}
'''

# Deserialize the JSON string into a Python dict
repo = json.loads(response_text)

# Access values using dict operations from Lessons 11-12
print(f"Repo: {repo['owner']}/{repo['repository']}")
print(f"Open issues: {repo['open_issues']}")

# Iterate over a nested list
for topic in repo["topics"]:
    print(f"  Topic: {topic}")

# Use .get() for safe access
license_name = repo.get("license", "not specified")
print(f"License: {license_name}")
```

**Output:**

```
Repo: acme-corp/sdk-docs
Open issues: 14
  Topic: python
  Topic: sdk
  Topic: documentation
License: not specified
```

The key point here is that after `json.loads()`, you are working with ordinary Python dicts and lists. There is nothing special about the objects — they are the same types you have been using since Lessons 7 and 11.

### Example 2: Reading a JSON file, filtering data, and writing a summary

This example reads a JSON file containing a list of issues, filters for open ones, and writes a summary to a new JSON file.

```python
import json
from pathlib import Path

# --- Setup: create a sample JSON file to work with ---
issues = [
    {"id": 101, "title": "Fix login timeout", "state": "open", "labels": ["bug"]},
    {"id": 102, "title": "Add dark mode", "state": "closed", "labels": ["feature"]},
    {"id": 103, "title": "Update README links", "state": "open", "labels": ["docs"]},
    {"id": 104, "title": "Refactor auth module", "state": "open", "labels": ["bug", "refactor"]}
]

input_path = Path("issues.json")
with open(input_path, "w", encoding="utf-8") as f:
    json.dump(issues, f, indent=2)

print(f"Wrote {len(issues)} issues to {input_path}")

# --- Read the file back and filter ---
with open(input_path, "r", encoding="utf-8") as f:
    all_issues = json.load(f)

open_issues = []
for issue in all_issues:
    if issue["state"] == "open":
        open_issues.append(issue)

# --- Write the filtered results ---
output_path = Path("open_issues.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(open_issues, f, indent=2, sort_keys=True)

print(f"Wrote {len(open_issues)} open issues to {output_path}")
```

**Output:**

```
Wrote 4 issues to issues.json
Wrote 3 open issues to open_issues.json
```

The resulting `open_issues.json` file contains:

```json
[
  {
    "id": 101,
    "labels": [
      "bug"
    ],
    "state": "open",
    "title": "Fix login timeout"
  },
  {
    "id": 103,
    "labels": [
      "docs"
    ],
    "state": "open",
    "title": "Update README links"
  },
  {
    "id": 104,
    "labels": [
      "bug",
      "refactor"
    ],
    "state": "open",
    "title": "Refactor auth module"
  }
]
```

Notice that `sort_keys=True` alphabetized the keys within each object (`id`, `labels`, `state`, `title`). This makes the output consistent regardless of the insertion order in the original Python dicts.

### Example 3: Pretty printing for inspection and debugging

When you are debugging a script or inspecting SDK output, you often want to dump a Python object to the terminal in a readable format. `json.dumps()` with `indent` is the standard way to do this.

```python
import json

# A nested structure like you might get from an API
user_data = {
    "login": "jsmith",
    "name": "J. Smith",
    "repos": [
        {"name": "dotfiles", "stars": 2, "language": "Shell"},
        {"name": "notes", "stars": 0, "language": None}
    ],
    "active": True
}

# Compact (default) — hard to read
print("Compact:")
print(json.dumps(user_data))
print()

# Pretty printed — easy to scan
print("Pretty:")
print(json.dumps(user_data, indent=2))
```

**Output:**

```
Compact:
{"login": "jsmith", "name": "J. Smith", "repos": [{"name": "dotfiles", "stars": 2, "language": "Shell"}, {"name": "notes", "stars": 0, "language": null}], "active": true}

Pretty:
{
  "login": "jsmith",
  "name": "J. Smith",
  "repos": [
    {
      "name": "dotfiles",
      "stars": 2,
      "language": "Shell"
    },
    {
      "name": "notes",
      "stars": 0,
      "language": null
    }
  ],
  "active": true
}
```

Notice that Python's `True` became `true`, `None` became `null`, and strings kept their double quotes. These are the JSON equivalents — `json.dumps()` handles the translation automatically.

> [!note] `json.dumps()` with `indent` is a better inspection tool than raw `print()` for nested structures. A raw `print()` on a dict will show Python syntax (`True`, `None`, single quotes), while `json.dumps()` shows valid JSON. Either works for debugging, but `json.dumps()` output can be pasted directly into other tools that expect JSON.

## Quick Reference

```python
import json
from pathlib import Path

# Deserialize a JSON string into a Python object
data = json.loads('{"key": "value", "count": 5}')

# Serialize a Python object into a JSON string (compact)
compact = json.dumps({"key": "value", "count": 5})

# Serialize with pretty printing (indent controls spacing)
pretty = json.dumps({"key": "value", "count": 5}, indent=2)

# Serialize with sorted keys for consistent output
sorted_output = json.dumps({"b": 2, "a": 1}, indent=2, sort_keys=True)

# Read JSON from a file using a file handle
with open(Path("data.json"), "r", encoding="utf-8") as f:
    loaded = json.load(f)

# Write JSON to a file using a file handle
with open(Path("output.json"), "w", encoding="utf-8") as f:
    json.dump({"result": "ok"}, f, indent=2)

# Catch invalid JSON with try/except
try:
    broken = json.loads("not valid json")
except json.JSONDecodeError as e:
    print(f"Parse error: {e}")
```

## Exercise

### Scenario

You have a directory containing several JSON files, each representing metadata for a documentation page (title, status, tags, and a word count). Your task is to write a script that scans the directory for all `.json` files, loads each one, extracts and validates the data, and writes two output files: a filtered JSON summary and a Markdown report.

### Setup

Before writing your script, create a directory called `pages` and populate it with the following five JSON files. You can do this by hand or by writing a small setup script.

**`pages/quickstart.json`**

```json
{
    "title": "Quickstart Guide",
    "status": "published",
    "tags": ["getting-started", "tutorial"],
    "word_count": 1250
}
```

**`pages/api-reference.json`**

```json
{
    "title": "API Reference",
    "status": "draft",
    "tags": ["api", "reference"],
    "word_count": 3400
}
```

**`pages/changelog.json`**

```json
{
    "title": "Changelog",
    "status": "published",
    "tags": ["changelog"],
    "word_count": 870
}
```

**`pages/auth-guide.json`**

```json
{
    "title": "Authentication Guide",
    "status": "review",
    "tags": ["auth", "security", "getting-started"],
    "word_count": 2100
}
```

**`pages/broken.json`**

```json
{"title": "Bad Entry", "status": "published", "tags": ["oops"]
```

Note: `broken.json` is intentionally invalid JSON (missing the closing brace and the `word_count` field).

### Requirements

Write a single script called `page_report.py` that does the following:

1. Uses `pathlib` to scan the `pages` directory and collect all files ending in `.json`.
2. For each file, attempts to load the JSON. If a file contains invalid JSON, logs a warning that includes the filename and skips that file. Use the `logging` module at the `WARNING` level for this.
3. For each successfully loaded file, validates that the dict contains all four expected keys: `title`, `status`, `tags`, and `word_count`. If any key is missing, logs a warning and skips that file.
4. Collects the valid page records into a list.
5. Filters the list to include only pages whose `status` is `"published"`.
6. Sorts the published pages by `word_count` from highest to lowest. Use `sorted()` with a named function as the `key` argument (you learned to define functions in Lesson 15; lambda expressions are not introduced until Lesson 41).
7. Writes the sorted, published pages to `published_summary.json` with an indent of 2 and sorted keys.
8. Writes a Markdown report to `published_report.md` with the following structure. Build the Markdown using string methods and f-strings — do not use a Markdown library for this output. The report must use this exact format:

```
# Published Pages Report

Total published pages: 2
Combined word count: 2120

## Quickstart Guide

- **Status:** published
- **Tags:** getting-started, tutorial
- **Word count:** 1250

## Changelog

- **Status:** published
- **Tags:** changelog
- **Word count:** 870
```

9. Uses `try/except` around the JSON loading step to catch `json.JSONDecodeError`.
10. Wraps the core logic in a `main()` function.
11. Logs an `INFO` message for each file successfully loaded, and a final `INFO` message stating how many published pages were written. Configure logging to show messages at the `INFO` level and above.

### Expected terminal output

Your script's logging output should match this (the order of the file-loading messages may vary since directory iteration order is not guaranteed, but the content must be the same):

```
INFO:root:Loaded quickstart.json (published)
INFO:root:Loaded api-reference.json (draft)
INFO:root:Loaded changelog.json (published)
INFO:root:Loaded auth-guide.json (review)
WARNING:root:Skipping broken.json: invalid JSON
INFO:root:Wrote 2 published pages to published_summary.json
INFO:root:Wrote report to published_report.md
```

### Expected file output

**`published_summary.json`** must contain exactly:

```json
[
  {
    "status": "published",
    "tags": [
      "getting-started",
      "tutorial"
    ],
    "title": "Quickstart Guide",
    "word_count": 1250
  },
  {
    "status": "published",
    "tags": [
      "changelog"
    ],
    "title": "Changelog",
    "word_count": 870
  }
]
```

**`published_report.md`** must match the format shown in requirement 8 above.

---

## Audit

|Operation|Lesson introduced|
|---|---|
|`import json`|Lesson 17 (modules/imports); current lesson (in-depth usage)|
|`json.load()` / `json.loads()`|Lesson 28 (current)|
|`json.dump()` / `json.dumps()`|Lesson 28 (current)|
|`json.JSONDecodeError`|Lesson 28 (current)|
|`indent=`, `sort_keys=`|Lesson 28 (current)|
|`from pathlib import Path`|Lesson 23|
|`Path.iterdir()` / suffix check|Lesson 23|
|`open()` with `with`, `encoding="utf-8"`|Lesson 22|
|`try/except` (specific exception)|Lesson 19|
|`logging.basicConfig()`, `logging.info()`, `logging.warning()`|Lesson 21|
|`def main()`, `def sort_key_func()`|Lesson 15|
|`sorted()` with `key=` (named function)|Lesson 15 (functions as arguments are a standard pattern; `sorted()` is a built-in)|
|Conditionals (`if`/`elif`/`else`)|Lesson 10|
|`for` loops|Lesson 9|
|f-strings|Lesson 6|
|`.join()` on strings|Lesson 5|
|List `.append()`|Lesson 7|
|Dict key access, `.get()`|Lessons 11–12|
|Boolean/truthiness checks|Lesson 14|
|Writing to a file (`"w"` mode)|Lesson 22|

**Previous-three-lesson coverage:** The exercise requires `pathlib` directory scanning (Lessons 23/26), file I/O patterns (Lesson 22/25), and logging (Lesson 21). Lessons 25 and 26 reinforced `pathlib` traversal and the preview-before-write discipline. Lesson 27 (Markdown parsing with `mistune`) is not required because the exercise writes Markdown output using string formatting rather than parsing existing Markdown — importing `mistune` for output generation would be inappropriate, and forcing a parsing step would make the exercise awkward. All operations used are from the current lesson or prior lessons. No future-lesson concepts (such as `lambda`, list comprehensions, `argparse`, or `sys.argv`) are required.