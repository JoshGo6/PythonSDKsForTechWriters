# Lesson 29: Command-Line Interfaces I — `sys.argv` and Basic Arguments

## Terminology and Theory

When you run a Python script from the terminal, you often want to pass information into it — a file path to process, a mode to operate in, or options that control behavior. Until now, you've hardcoded paths and values directly into your scripts. This lesson teaches you how to accept inputs from the command line, making your scripts reusable tools rather than one-off programs.

**Command-line arguments** are the words you type after the script name when running it:

```bash
python process_docs.py input.md output.md --verbose
```

In this example, `input.md`, `output.md`, and `--verbose` are all command-line arguments.

**`sys.argv`** is a list provided by Python's `sys` module that contains all the command-line arguments passed to your script. The first element (`sys.argv[0]`) is always the script's own name. The remaining elements are the arguments you passed.

**Argument validation** is the practice of checking that the user provided the expected arguments before your script tries to use them. Without validation, a missing argument causes an `IndexError` when you try to access `sys.argv[1]` or beyond.

**Usage messages** are short help texts printed when the user runs your script incorrectly. They tell the user what arguments are expected and how to use the script properly.

> [!note] `sys.argv` always contains strings. If you need a number, you must convert it yourself using `int()` or `float()`.

## Syntax Section

### Importing `sys` and accessing `argv`

```python
import sys

# sys.argv is a list of strings
# sys.argv[0] is the script name
# sys.argv[1] is the first argument, sys.argv[2] is the second, etc.
```

### Checking the number of arguments

```python
import sys

# len(sys.argv) tells you how many items are in the list
# If you expect 2 arguments (plus the script name), check for 3 total
if len(sys.argv) != 3:
    print("Usage: python myscript.py <input_file> <output_file>")
    sys.exit(1)
```

`sys.exit(1)` terminates the script immediately with an exit code of `1`, which conventionally signals an error. An exit code of `0` means success.

### Extracting arguments into variables

```python
import sys

script_name = sys.argv[0]
input_path = sys.argv[1]
output_path = sys.argv[2]
```

### Detecting optional flags

For simple flag detection, check whether a string is present in `sys.argv`:

```python
import sys

verbose = "--verbose" in sys.argv or "-v" in sys.argv
```

This pattern works for presence/absence flags. For flags that take values (like `--count 5`), you would need more logic — but that complexity is better handled by `argparse`, which you'll learn in Lesson 30.

## Worked Examples

### Example 1: A script that expects one argument

This script expects a single filename and prints its contents.

```python
import sys
from pathlib import Path

# Check argument count (script name + 1 argument = 2)
if len(sys.argv) != 2:
    print("Usage: python show_file.py <filename>")
    sys.exit(1)

file_path = Path(sys.argv[1])

# Validate that the file exists
if not file_path.exists():
    print(f"Error: File not found: {file_path}")
    sys.exit(1)

# Read and print the file contents
content = file_path.read_text(encoding="utf-8")
print(content)
```

Run it:

```bash
python show_file.py notes.txt
```

What happens here:

1. The script checks that exactly one argument was provided (plus the script name).
2. If not, it prints a usage message and exits with code `1`.
3. It converts the argument to a `Path` object and checks existence.
4. If the file exists, it reads and prints the content.

### Example 2: A script that copies content between files

This script reads from one file and writes to another, with basic validation.

```python
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: python copy_file.py <source> <destination>")
    sys.exit(1)

source_path = Path(sys.argv[1])
dest_path = Path(sys.argv[2])

if not source_path.exists():
    print(f"Error: Source file not found: {source_path}")
    sys.exit(1)

if dest_path.exists():
    print(f"Error: Destination already exists: {dest_path}")
    sys.exit(1)

content = source_path.read_text(encoding="utf-8")
dest_path.write_text(content, encoding="utf-8")

print(f"Copied {source_path} to {dest_path}")
```

Run it:

```bash
python copy_file.py original.md backup.md
```

What happens here:

1. The script expects exactly two arguments: source and destination.
2. It validates that the source exists and the destination does not (to avoid accidental overwrites).
3. It reads the source content and writes it to the destination.
4. It prints a confirmation message.

### Example 3: A script with an optional verbose flag

This script processes a JSON file and optionally prints extra information when `--verbose` is passed.

```python
import sys
import json
from pathlib import Path

# Check for verbose flag first
verbose = "--verbose" in sys.argv

# Remove the flag from argv so we can count positional arguments cleanly
args = [arg for arg in sys.argv if arg != "--verbose"]

if len(args) != 2:
    print("Usage: python summarize_json.py <json_file> [--verbose]")
    sys.exit(1)

json_path = Path(args[1])

if not json_path.exists():
    print(f"Error: File not found: {json_path}")
    sys.exit(1)

content = json_path.read_text(encoding="utf-8")
data = json.loads(content)

if verbose:
    print(f"Loaded JSON from: {json_path}")
    print(f"Type of data: {type(data).__name__}")

if isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
elif isinstance(data, list):
    print(f"List with {len(data)} items")
else:
    print(f"Value: {data}")
```

Run it:

```bash
python summarize_json.py config.json --verbose
```

What happens here:

1. The script checks whether `--verbose` appears anywhere in `sys.argv`.
2. It builds a filtered list `args` that excludes the flag, so positional argument counting stays simple.
3. It validates the file path, loads the JSON, and prints information based on the data type.
4. If `--verbose` was passed, it prints additional diagnostic information.

> [!tip] Filtering flags out of `sys.argv` before counting positional arguments is a practical pattern for scripts with one or two simple flags. For anything more complex, use `argparse`.

## Quick Reference

```python
# Import the sys module
import sys

# Access the full argument list (first element is script name)
all_args = sys.argv

# Get the script's own name
script_name = sys.argv[0]

# Get the first positional argument (index 1)
first_arg = sys.argv[1]

# Count total arguments including script name
arg_count = len(sys.argv)

# Check if enough arguments were provided
if len(sys.argv) < 3:
    print("Usage: python script.py <arg1> <arg2>")
    sys.exit(1)

# Exit the script with an error code
sys.exit(1)

# Exit the script successfully
sys.exit(0)

# Check for presence of a flag
verbose = "--verbose" in sys.argv

# Filter out flags to isolate positional arguments
positional_args = [arg for arg in sys.argv if not arg.startswith("--")]
```

## Exercise

### Markdown Link Extractor with Configurable Output

Write a script called `extract_links.py` that accepts two command-line arguments:

1. An input Markdown file path
2. An output JSON file path

The script should:

1. Validate that exactly two arguments were provided (plus the script name). If not, print a usage message and exit with code `1`.
2. Validate that the input file exists. If not, print an error message and exit with code `1`.
3. Read the input Markdown file.
4. Use a regular expression to extract all Markdown links. A Markdown link has the form `[link text](url)`. Extract both the link text and the URL.
5. Build a list of dictionaries, where each dictionary has keys `"text"` and `"url"`.
6. Write the list to the output file as JSON with indentation for readability.
7. Print a summary line showing how many links were extracted.

If the script is run without proper arguments, it should print:

```
Usage: python extract_links.py <input_markdown> <output_json>
```

### Example

Given an input file `sample.md` containing:

```markdown
# My Resources

Check out [Python docs](https://docs.python.org) for reference.
Also see [Real Python](https://realpython.com) for tutorials.
```

Running:

```bash
python extract_links.py sample.md links.json
```

Should produce `links.json`:

```json
[
  {
    "text": "Python docs",
    "url": "https://docs.python.org"
  },
  {
    "text": "Real Python",
    "url": "https://realpython.com"
  }
]
```

And print to the terminal:

```
Extracted 2 links to links.json
```