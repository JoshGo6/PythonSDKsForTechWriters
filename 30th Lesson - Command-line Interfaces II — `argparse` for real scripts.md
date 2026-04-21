# Lesson 30: Command-line Interfaces II — `argparse` for real scripts

## Terminology and Theory

**`argparse`** is the Python standard library module for building command-line interfaces. It sits on top of `sys.argv` (Lesson 29) and handles the repetitive work for you: usage messages, `--help` output, type conversion, missing-argument errors, and clean access to parsed values.

Key vocabulary:

- **Parser** — the `ArgumentParser` object. You configure it by adding arguments, then ask it to parse the command line.
- **Positional argument** — an argument identified by its _position_ on the command line. Positional arguments are **mandatory** by default: if the caller forgets one, `argparse` prints a usage error and exits the script. In `script.py input.txt out.txt`, both `input.txt` and `out.txt` are positional.
- **Optional argument** — an argument identified by a _flag name_ (typically starting with `--`). Optional arguments are **not required** by default; the caller can omit them, in which case the argument takes a default value (either `None`, or whatever you supplied with `default=`). Examples: `--verbose`, `--output`.
- **Boolean flag** — an optional argument that takes no value; only its presence matters. `--dry-run` is either given (True) or not given (False).
- **Namespace** — a plain object whose attributes are the parsed argument values. It is what `parse_args()` returns. You read the values with dot-notation (`args.input`, `args.verbose`). The class is `argparse.Namespace`, and it's not much more than a labeled container for attributes. Two things are worth knowing about it beyond attribute access: `print(args)` shows every parsed attribute and its value in a single line, which is useful when debugging a CLI to confirm exactly what `argparse` parsed; and `vars(args)` returns the same data as a regular dictionary, which is useful when you need to pass parsed arguments to something that expects dict-shaped input.

When to prefer `argparse` over `sys.argv`:

- Your script has more than one or two arguments.
- You want `--help` to document the tool.
- You want an optional flag, a default value, or automatic type conversion.

> [!note] `sys.argv` is still fine for quick throwaway scripts. `argparse` is the default for anything you expect to keep, share, or put in a repo.

One behavior worth internalizing up front: `parse_args()` takes over error handling for you. If the caller forgets a required argument or passes a bad type, `argparse` prints a usage message and exits the script with a nonzero status — you do not have to write any of that yourself.

## Syntax Section

The minimal `argparse` template:

```python
import argparse

parser = argparse.ArgumentParser(description="One-line explanation of the tool.")
parser.add_argument("input_file", help="Path to the input file.")
parser.add_argument("--verbose", action="store_true", help="Print extra output.")
args = parser.parse_args()

print(args.input_file)
print(args.verbose)
```

Breakdown:

- `argparse.ArgumentParser(description=...)` creates the parser. The `description` string appears at the top of `--help` output.
- `add_argument("input_file", help=...)` adds a **positional** argument. The name `"input_file"` also becomes the attribute name on the returned Namespace.
- `add_argument("--verbose", action="store_true", help=...)` adds a **boolean flag**. If `--verbose` is on the command line, `args.verbose` is `True`; otherwise it is `False`.
- `parse_args()` reads `sys.argv`, validates, and returns a Namespace. It exits the script automatically on bad input or on `--help`.
- `args.input_file`, `args.verbose` — access parsed values as attributes.

Two other patterns you will see constantly:

```python
parser.add_argument("--name", default="world", help="Who to greet.")
parser.add_argument("--count", type=int, default=10, help="How many items.")
```

- `default=...` is the value used when the flag is not provided on the command line.
- `type=int` tells `argparse` to convert the string argument to an `int` (and error out cleanly if it cannot).

### Argument order on the command line

The order in which you call `add_argument` for **positional** arguments determines the order in which the caller must provide them on the command line. `argparse` consumes positionals left-to-right, matching them to positionals in definition order:

```python
parser.add_argument("input")    # first positional
parser.add_argument("output")   # second positional
```

With those two definitions, `script.py a.txt b.txt` binds `args.input = "a.txt"` and `args.output = "b.txt"`. Swapping the order of the `add_argument` calls in the source swaps which file is the input and which is the output — it's a source-code-order relationship, not a "first argument in the call to `parse_args`" relationship.

**Optional** arguments behave differently: they can appear anywhere on the command line, in any order, because `argparse` identifies them by their flag name rather than by position. They may appear before all positionals, after all positionals, or interleaved between them. All three of the following invocations are equivalent:

```
script.py a.txt b.txt --verbose --count 5
script.py --verbose a.txt --count 5 b.txt
script.py --count 5 --verbose a.txt b.txt
```

In every case, `argparse` pulls `--verbose` and `--count 5` out of the command line by name, and whatever tokens remain are treated as positionals consumed left-to-right. This is one of the concrete reasons to prefer optionals for anything the caller might want to omit or reorder: you get ordering flexibility for free, without writing any parsing logic yourself.

> [!important]  Dashes in _optional_ flag names become underscores in attribute names. `--dry-run` is accessed as `args.dry_run`, not `args.dry-run` (which would be invalid Python). This conversion applies only to optional arguments; for positional arguments, use single-word names or underscores (`input_file`, not `input-file`) — positional names are preserved literally, and a hyphenated positional can only be reached via `getattr(args, "input-file")`.

## Worked Examples

### Example 1: One positional argument, nothing else

Save as `show_file.py`:

```python
import argparse

parser = argparse.ArgumentParser(description="Print the contents of a text file.")
parser.add_argument("path", help="Path to the file to display.")
args = parser.parse_args()

with open(args.path, "r", encoding="utf-8") as f:
    print(f.read())
```

Run it:

```
$ python show_file.py notes.txt
(contents of notes.txt)

$ python show_file.py --help
usage: show_file.py [-h] path

Print the contents of a text file.

positional arguments:
  path        Path to the file to display.

options:
  -h, --help  show this help message and exit

$ python show_file.py
usage: show_file.py [-h] path
show_file.py: error: the following arguments are required: path
```

Two things to notice:

- `--help` works automatically. You did not write any of that output.
- Forgetting the argument produces a clean error message and a nonzero exit code — no manual `len(sys.argv)` check required.

### Example 2: Positional argument plus an optional boolean flag

Save as `count_lines.py`:

```python
import argparse

parser = argparse.ArgumentParser(description="Count lines in a text file.")
parser.add_argument("path", help="Path to the file.")
parser.add_argument(
    "--non-empty",
    action="store_true",
    help="Count only lines that contain non-whitespace characters.",
)
args = parser.parse_args()

with open(args.path, "r", encoding="utf-8") as f:
    lines = f.readlines()

if args.non_empty:
    count = 0
    for line in lines:
        if line.strip():
            count = count + 1
else:
    count = len(lines)

print(f"{args.path}: {count} lines")
```

Run it:

```
$ python count_lines.py notes.txt
notes.txt: 42 lines

$ python count_lines.py notes.txt --non-empty
notes.txt: 31 lines
```

Notice: `--non-empty` on the command line becomes `args.non_empty` in Python. That dash-to-underscore conversion is automatic and silent; watch for it.

### Example 3: Converting a `sys.argv` script to `argparse`

A Lesson 29-style `sys.argv` script:

```python
import sys

if len(sys.argv) != 3:
    print("Usage: upper.py INPUT OUTPUT")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

with open(input_path, "r", encoding="utf-8") as f:
    text = f.read()

with open(output_path, "w", encoding="utf-8") as f:
    f.write(text.upper())

print(f"Wrote {output_path}")
```

The `argparse` rewrite:

```python
import argparse

parser = argparse.ArgumentParser(description="Copy a file, uppercasing its contents.")
parser.add_argument("input", help="Source file.")
parser.add_argument("output", help="Destination file.")
args = parser.parse_args()

with open(args.input, "r", encoding="utf-8") as f:
    text = f.read()

with open(args.output, "w", encoding="utf-8") as f:
    f.write(text.upper())

print(f"Wrote {args.output}")
```

What you gained by converting:

- No manual `len(sys.argv)` check.
- No hand-written usage message.
- Automatic `--help`.
- Named attribute access (`args.input`, `args.output`) instead of magic numeric indices (`sys.argv[1]`, `sys.argv[2]`).

> [!info] The rewrite is shorter and clearer, and it will stay shorter as the script grows. Every new argument you add to `argparse` gets `--help` documentation and validation for free; every new argument in `sys.argv` style adds more index-checking and more `print("Usage: ...")` branches.

### Example 4: Two mandatory arguments and two optional arguments

This example combines both kinds of arguments. Save as `report.py`:

```python
import argparse

parser = argparse.ArgumentParser(description="Generate a report from an input file.")
parser.add_argument("input", help="Source file.")
parser.add_argument("output", help="Destination file.")
parser.add_argument("--format", default="md", help="Output format (default: md).")
parser.add_argument("--verbose", action="store_true", help="Print extra output.")
args = parser.parse_args()

print(f"input:   {args.input}")
print(f"output:  {args.output}")
print(f"format:  {args.format}")
print(f"verbose: {args.verbose}")

# You can also inspect the entire Namespace in one shot.
print(args)
```

The script defines four arguments. Two are **mandatory** because they are positional (`input`, `output`): the caller must supply both, in that order, or `argparse` will exit with a usage error. Two are **optional** (`--format`, `--verbose`): the caller can omit them, and they'll take their defaults (`"md"` for `--format`, `False` for `--verbose`).

Because positionals are matched by position and optionals are matched by name, the following invocations all parse to the same Namespace — `argparse` doesn't care where the optionals appear, only that the two positionals show up in the right order relative to each other:

```
$ python report.py in.txt out.txt --format html --verbose
input:   in.txt
output:  out.txt
format:  html
verbose: True
Namespace(input='in.txt', output='out.txt', format='html', verbose=True)

$ python report.py --verbose in.txt --format html out.txt
input:   in.txt
output:  out.txt
format:  html
verbose: True
Namespace(input='in.txt', output='out.txt', format='html', verbose=True)

$ python report.py --format html --verbose in.txt out.txt
input:   in.txt
output:  out.txt
format:  html
verbose: True
Namespace(input='in.txt', output='out.txt', format='html', verbose=True)
```

But swapping the two positionals relative to _each other_ changes the parse, because position is how `argparse` identifies them:

```
$ python report.py out.txt in.txt --format html
input:   out.txt
output:  in.txt
format:  html
verbose: False
Namespace(input='out.txt', output='in.txt', format='html', verbose=False)
```

Here `argparse` happily binds `args.input = "out.txt"` and `args.output = "in.txt"` — it has no way to know the caller meant the opposite. Getting positional order right is the caller's job; `argparse` only checks that the _number_ of positionals is correct.

Finally, omitting the optionals falls back to the defaults:

```
$ python report.py in.txt out.txt
input:   in.txt
output:  out.txt
format:  md
verbose: False
Namespace(input='in.txt', output='out.txt', format='md', verbose=False)
```

Notice how the final `print(args)` line shows the full Namespace on one line. That's the `repr` of the Namespace object, and it's one of the fastest ways to sanity-check a CLI while you're building it.

## Quick Reference

```python
# Import argparse from the standard library.
import argparse

# Create a parser. The description shows at the top of --help.
parser = argparse.ArgumentParser(description="What the script does.")

# Positional arguments are MANDATORY by default. Their name (with no leading dashes)
# becomes the attribute name on args. The order of add_argument calls determines
# the order in which positionals must appear on the command line.
parser.add_argument("path", help="Path to the input file.")

# A second positional. Must appear after 'path' on the command line.
parser.add_argument("output", help="Path to the output file.")

# Optional arguments are NOT required by default. They are identified by their
# flag name, not by position, so they can appear anywhere on the command line.
# The action="store_true" parameter tells Python that this is a Boolean parameter set to True only if the argument is given by the user at the CLI
parser.add_argument("--verbose", action="store_true", help="Print extra output.")

# An optional argument with a default value thats' used when the flag is not given.
parser.add_argument("--name", default="world", help="Who to greet.")

# An optional argument that argparse converts to an int.
parser.add_argument("--count", type=int, default=10, help="How many items.")

# Parse sys.argv. Returns a Namespace. Exits automatically on bad input or --help.
args = parser.parse_args()

# Access parsed values as attributes on the Namespace.
print(args.path)
print(args.verbose)

# Print the whole Namespace at once — handy for debugging a CLI.
print(args)

# Convert the Namespace to a regular dict when you need dict-shaped data.
print(vars(args))
```

```bash
# Get help at the CLI based on the argparse content in the file
python3 <python_file_name> -h
```

> [!important]
> For the help to work at the terminal, you must have an `args = parser.parse_args()` assignment in your script. There's no reason you wouldn't have it. Otherwise you'd be specifying arguments that you'd never use in your script, but if you're testing the help before building out the logic, for the CLI help to work, your script must invoke the `.parse_args()` method. 

## Exercise

You have this `sys.argv`-based script, `summarize.py`, from Lesson 29. It reads a JSON file containing a list of issue records and prints one summary line per record.

```python
import sys
import json

if len(sys.argv) != 2:
    print("Usage: summarize.py FILE")
    sys.exit(1)

with open(sys.argv[1], "r", encoding="utf-8") as f:
    records = json.load(f)

for record in records:
    print(f"- {record['name']}: {record['status']}")
```

Create a test input file, `issues.json`:

```json
[
  {"name": "login bug", "status": "open"},
  {"name": "typo fix", "status": "closed"},
  {"name": "docs update", "status": "open"}
]
```

### Your task

Convert `summarize.py` to use `argparse` instead of `sys.argv`. Then **add one new optional boolean flag**: `--count-only`. When `--count-only` is provided, the script must print only the total number of records (not the per-record lines). When the flag is absent, the script must print the per-record lines exactly as the original did.

### Requirements

- One positional argument named `path`, for the JSON file.
- One optional flag, `--count-only`, using `action="store_true"`.
- The script must support `--help` without any extra code on your part.
- Do not use `sys.argv` or a manual `len(...)` usage check.
- Preserve the original per-record output format when `--count-only` is not given.

### Expected output

```
$ python summarize.py issues.json
- login bug: open
- typo fix: closed
- docs update: open

$ python summarize.py issues.json --count-only
3 records

$ python summarize.py --help
usage: summarize.py [-h] [--count-only] path

Summarize a JSON list of records.

positional arguments:
  path          Path to the JSON file.

options:
  -h, --help    show this help message and exit
  --count-only  Print only the number of records.

$ python summarize.py
usage: summarize.py [-h] [--count-only] path
summarize.py: error: the following arguments are required: path
```

> [!tip] The exact wording of your `description=` and `help=` strings does not have to match the expected output character-for-character, but the _structure_ of the `--help` output (positional section, options section, usage line) will match automatically once you configure the arguments correctly.