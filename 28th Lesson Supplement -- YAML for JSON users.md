# Companion: YAML for JSON Users

This is a companion reference to Lesson 28 (Data Formats — JSON Read/Write and Pretty Printing). It covers everything you need to read, write, and convert YAML in Python using the same patterns you already know from the `json` module.

## Why YAML Matters Alongside JSON

JSON and YAML represent the same kinds of structures — mappings, sequences, strings, numbers, booleans, and nulls. You will encounter YAML in three places that JSON doesn't typically occupy:

- **Markdown front matter.** The metadata block at the top of a `.md` file, delimited by `---` lines, is almost always YAML.
- **OpenAPI Specification (OAS) files.** API definitions are commonly authored in YAML because the format is easier to read and edit by hand than the equivalent JSON.
- **Configuration files.** Tools like Docker Compose, GitHub Actions, MkDocs, and Ansible use YAML for configuration.

In Python, you work with YAML through the third-party `PyYAML` library. Its API deliberately mirrors the `json` module, so the patterns you learned in Lesson 28 carry over directly.

## Installing PyYAML

PyYAML is not in the standard library. Install it with pip:

```bash
pip install pyyaml
```

The package name on PyPI is `pyyaml`, but you import it as `yaml`:

```python
import yaml
```

## API Mapping: `json` → `yaml`

The following table shows the direct correspondence between the `json` functions you already know and their `yaml` equivalents. The calling conventions are the same — string functions take/return strings, file functions take file handles.

|Operation|`json` module|`yaml` module|
|---|---|---|
|Parse a string|`json.loads(s)`|`yaml.safe_load(s)`|
|Parse a file|`json.load(f)`|`yaml.safe_load(f)`|
|Write to a string|`json.dumps(obj)`|`yaml.safe_dump(obj)`|
|Write to a file|`json.dump(obj, f)`|`yaml.safe_dump(obj, stream=f)`|
|Parse error|`json.JSONDecodeError`|`yaml.YAMLError`|

> [!warning] Always use `yaml.safe_load()` and `yaml.safe_dump()`, never the bare `yaml.load()` or `yaml.dump()`. The bare versions can execute arbitrary Python code embedded in a YAML file. `safe_load` restricts parsing to plain data types (strings, numbers, lists, dicts, booleans, and `None`), which is all you need.

One difference in the function signatures: `yaml.safe_load()` accepts both strings and file objects — there is no separate `safe_loads()` function. You pass whichever you have.

## Type Mapping

YAML maps to the same Python types as JSON, with one addition worth noting:

|YAML value|Python type|JSON equivalent|
|---|---|---|
|`key: value`|`dict`|`{}`|
|`- item`|`list`|`[]`|
|`"hello"` or `hello`|`str`|`"hello"`|
|`42`|`int`|`42`|
|`3.14`|`float`|`3.14`|
|`true` / `yes` / `on`|`bool` (`True`)|`true`|
|`false` / `no` / `off`|`bool` (`False`)|`false`|
|`null` or `~`|`None`|`null`|

> [!tip] YAML treats several bare words as booleans: `yes`, `no`, `on`, `off`, `true`, `false` (case-insensitive). If you have a string value like `country: no` (meaning Norway's ISO code), YAML will parse it as `False`. Quote the value — `country: "no"` — to force it to be a string. This is YAML's most common gotcha.

## Core Operations

### Reading a YAML string

```python
import yaml

yaml_text = """
name: sdk-docs
owner: acme-corp
open_issues: 14
topics:
  - python
  - sdk
  - documentation
private: false
"""

data = yaml.safe_load(yaml_text)
```

After this call, `data` is a plain Python `dict` — identical in structure to what you would get from `json.loads()` on the equivalent JSON. You access values the same way: `data["name"]`, `data.get("owner")`, and so on.

### Reading a YAML file

```python
import yaml
from pathlib import Path

path = Path("config.yaml")
with open(path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)
```

Same `with`/`open` pattern from Lesson 22. Same file handle passed to the load function. The only difference is `yaml.safe_load(f)` instead of `json.load(f)`.

### Writing YAML to a file

```python
import yaml
from pathlib import Path

config = {"output_dir": "build", "verbose": True, "retries": 3}

output_path = Path("config.yaml")
with open(output_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(config, stream=f, default_flow_style=False)
```

`default_flow_style=False` tells PyYAML to write block-style YAML (the readable, indented kind) rather than inline/flow-style (which looks like compressed JSON). You almost always want this set to `False`.

The resulting file looks like:

```yaml
output_dir: build
retries: 3
verbose: true
```

> [!note] `yaml.safe_dump()` sorts keys alphabetically by default (the opposite of `json.dumps()`, which preserves insertion order by default). To preserve insertion order, pass `sort_keys=False`. To sort keys in JSON output, you pass `sort_keys=True`. Opposite defaults, same parameter name.

### Writing YAML to a string

```python
import yaml

config = {"output_dir": "build", "verbose": True, "retries": 3}
yaml_string = yaml.safe_dump(config, default_flow_style=False)
print(yaml_string)
```

When you omit the `stream=` argument, `safe_dump` returns a string instead of writing to a file. This is the equivalent of `json.dumps()`.

### Handling parse errors

```python
import yaml

bad_yaml = "key: [unclosed bracket"

try:
    data = yaml.safe_load(bad_yaml)
except yaml.YAMLError as e:
    print(f"Invalid YAML: {e}")
```

Same `try`/`except` pattern from Lesson 19 and from the `json.JSONDecodeError` handling in Lesson 28. The exception class is `yaml.YAMLError`.

## Converting Between YAML and JSON

Since both formats parse into the same Python types, conversion is a two-step process: load with one library, dump with the other. The Python dict in the middle is the bridge.

### YAML → JSON

```python
import json
import yaml
from pathlib import Path

# Read YAML
yaml_path = Path("api-spec.yaml")
with open(yaml_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

# Write JSON
json_path = Path("api-spec.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
```

### JSON → YAML

```python
import json
import yaml
from pathlib import Path

# Read JSON
json_path = Path("api-spec.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Write YAML
yaml_path = Path("api-spec.yaml")
with open(yaml_path, "w", encoding="utf-8") as f:
    yaml.safe_dump(data, stream=f, default_flow_style=False, sort_keys=False)
```

Passing `sort_keys=False` here preserves the key order from the original JSON, which matters when converting OAS files or other documents where key order is meaningful to human readers.

## Extracting YAML Front Matter from Markdown

Markdown files used by static site generators (MkDocs, Docusaurus, Hugo, Jekyll) typically start with a YAML front matter block: a chunk of YAML between two `---` lines, followed by the Markdown body.

A file might look like this:

```markdown
---
title: Authentication Guide
status: review
tags:
  - auth
  - security
---

# Authentication Guide

This guide explains how to authenticate with the API.
```

You can extract and parse the front matter using string operations you already know, combined with `yaml.safe_load()`:

```python
import yaml
from pathlib import Path

def extract_front_matter(path):
    """Return (metadata_dict, body_string) from a Markdown file with YAML front matter."""
    text = path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        return None, text

    # Find the closing '---' delimiter (skip the opening one)
    end_index = text.index("---", 3)
    yaml_block = text[3:end_index]
    body = text[end_index + 3:].lstrip("\n")

    metadata = yaml.safe_load(yaml_block)
    return metadata, body


# Usage
page_path = Path("auth-guide.md")
metadata, body = extract_front_matter(page_path)

if metadata is not None:
    print(f"Title: {metadata['title']}")
    print(f"Status: {metadata['status']}")
    print(f"Tags: {', '.join(metadata['tags'])}")
```

> [!note] This extraction approach handles the common case. Libraries like `python-frontmatter` exist for edge cases (multiple documents, custom delimiters), but for standard `---`-delimited front matter, the string-slicing approach above is sufficient and keeps your dependencies minimal.

## Quick Reference

```python
import yaml
import json
from pathlib import Path

# Parse a YAML string into a Python object
data = yaml.safe_load('name: sdk-docs\nstars: 42')

# Parse a YAML file into a Python object
with open(Path("config.yaml"), "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

# Write a Python object to a YAML string (block style)
yaml_string = yaml.safe_dump({"key": "value"}, default_flow_style=False)

# Write a Python object to a YAML file (block style, preserve key order)
with open(Path("output.yaml"), "w", encoding="utf-8") as f:
    yaml.safe_dump({"key": "value"}, stream=f, default_flow_style=False, sort_keys=False)

# Catch invalid YAML with try/except
try:
    broken = yaml.safe_load("key: [unclosed")
except yaml.YAMLError as e:
    print(f"Parse error: {e}")

# Convert YAML to JSON: load with yaml, dump with json
with open(Path("input.yaml"), "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)
with open(Path("output.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# Convert JSON to YAML: load with json, dump with yaml
with open(Path("input.json"), "r", encoding="utf-8") as f:
    data = json.load(f)
with open(Path("output.yaml"), "w", encoding="utf-8") as f:
    yaml.safe_dump(data, stream=f, default_flow_style=False, sort_keys=False)

# Extract YAML front matter from a Markdown file
text = Path("page.md").read_text(encoding="utf-8")
if text.startswith("---"):
    end = text.index("---", 3)
    metadata = yaml.safe_load(text[3:end])
```