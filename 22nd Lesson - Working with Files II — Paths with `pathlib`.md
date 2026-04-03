# Lesson 22: Working with Files II — Paths with `pathlib`

## Terminology and Theory

**`pathlib`** — A standard library module that represents filesystem paths as objects instead of raw strings. You imported it briefly in Lesson 17; this lesson teaches you to actually use it.

**`Path` object** — The main class from `pathlib`. A `Path` wraps a filesystem path (like `/home/josh/docs/README.md`) as an object with methods and attributes for inspecting, navigating, and manipulating that path. You create one with `Path("some/path")`.

**Path component attributes** — A `Path` object exposes the pieces of a path as attributes:

- `.name` — the final component of the path (e.g., `README.md`).
- `.stem` — the filename without its suffix (e.g., `README`).
- `.suffix` — the file extension including the dot (e.g., `.md`).
- `.parent` — a new `Path` object representing the directory that contains this path.

**Joining paths** — You join path segments with the `/` operator. `pathlib` overloads `/` so that `Path("docs") / "guides" / "setup.md"` produces a `Path` equivalent to `docs/guides/setup.md`. This replaces brittle string concatenation.

**Existence checking** — `.exists()` returns `True` if the path points to something on disk (file or directory). `.is_file()` and `.is_dir()` let you distinguish between the two.

**Directory iteration** — `.iterdir()` yields one `Path` object per entry in a directory (files and subdirectories, non-recursively). `.glob(pattern)` yields paths matching a shell-style pattern like `"*.md"`. `.rglob(pattern)` does the same but recurses into subdirectories.

**Glob pattern** — A pattern string with wildcards. `*` matches any sequence of characters within a single filename. `**` (used by `.rglob()` or inside a `.glob()` pattern) matches across directory levels.

**`Path.cwd()`** — A class method that returns a `Path` object representing the current working directory.

> [!note] 
> `pathlib` does not replace `open()`. You still open files the same way you learned in Lesson 21, but you can pass a `Path` object directly to `open()` instead of a string. You can also call `.read_text()` and `.write_text()` directly on a `Path` object for simple read/write operations.

## Syntax Section

### Creating a Path

```python
from pathlib import Path

p = Path("projects/docs/README.md")
```

`Path(...)` accepts a string and wraps it as a path object. Nothing on disk has to exist yet — you are just creating a representation.

### Component attributes

```python
p = Path("projects/docs/README.md")

p.name      # "README.md"
p.stem      # "README"
p.suffix    # ".md"
p.parent    # Path("projects/docs")
```

Each attribute returns either a string (`.name`, `.stem`, `.suffix`) or another `Path` object (`.parent`).

### Joining paths with `/`

```python
base = Path("projects")
full = base / "docs" / "guides" / "setup.md"
# Path("projects/docs/guides/setup.md")
```

Every `/` joins a new segment. The right-hand side can be a string or another `Path`.

### Checking existence

```python
p = Path("some_file.txt")

p.exists()    # True or False
p.is_file()   # True if it exists AND is a regular file
p.is_dir()    # True if it exists AND is a directory
```

### Iterating a directory

```python
folder = Path("docs")

# Every entry in the directory (one level deep)
for entry in folder.iterdir():
    print(entry.name)

# Only .md files in this directory
for md_file in folder.glob("*.md"):
    print(md_file)

# All .md files in this directory AND all subdirectories
for md_file in folder.rglob("*.md"):
    print(md_file)
```

### Reading and writing directly on a Path

```python
p = Path("output.txt")

# Write a string to a file (creates or overwrites)
p.write_text("Hello, pathlib!\n", encoding="utf-8")

# Read the entire file as a string
content = p.read_text(encoding="utf-8")
```

These are convenience methods. For line-by-line reading or appending, use `open()` with a context manager as you learned in Lesson 21 — you can pass the `Path` object directly:

```python
with open(p, "r", encoding="utf-8") as f:
    for line in f:
        print(line.rstrip("\n"))
```

### Getting the current working directory

```python
cwd = Path.cwd()
print(cwd)
```

## Worked Examples

### Example 1: Inspect path components

This example shows how to break a path into its pieces, which is useful when you need to check file extensions or strip them.

```python
from pathlib import Path

file_path = Path("repos/my-sdk/docs/quickstart.md")

print(f"Full path:  {file_path}")
print(f"Name:       {file_path.name}")
print(f"Stem:       {file_path.stem}")
print(f"Suffix:     {file_path.suffix}")
print(f"Parent dir: {file_path.parent}")
print(f"Grandparent: {file_path.parent.parent}")
```

**Output:**

```
Full path:  repos/my-sdk/docs/quickstart.md
Name:       quickstart.md
Stem:       quickstart
Suffix:     .md
Parent dir: repos/my-sdk/docs
Grandparent: repos/my-sdk
```

`.parent` returns a `Path`, so you can chain `.parent.parent` to walk up the directory tree. `.name`, `.stem`, and `.suffix` return plain strings, so you can use all the string methods you already know — `.lower()`, `.startswith()`, `.replace()`, and so on.

### Example 2: Build a path safely and check before reading

This example joins user-provided pieces into a path, confirms the file exists, and then reads it. This is the pattern you will use constantly in scripts that accept filenames as input.

```python
from pathlib import Path

base_dir = Path("project")
subfolder = "docs"
filename = "changelog.md"

target = base_dir / subfolder / filename
print(f"Looking for: {target}")

if target.is_file():
    content = target.read_text(encoding="utf-8")
    line_count = len(content.split("\n"))
    print(f"Found it — {line_count} lines.")
else:
    print("File does not exist.")
```

**Output (if the file exists):**

```
Looking for: project/docs/changelog.md
Found it — 42 lines.
```

**Output (if the file does not exist):**

```
Looking for: project/docs/changelog.md
File does not exist.
```

Notice how `/` replaces the fragile `"project" + "/" + "docs" + "/" + "changelog.md"` pattern. The existence check before reading avoids the `FileNotFoundError` you learned about in Lesson 18.

### Example 3: Scan a folder for Markdown files and summarize them

This is the realistic "docs repo" pattern: find every `.md` file in a directory tree and print a short summary of each one.

```python
from pathlib import Path

docs_dir = Path("docs")

if not docs_dir.is_dir():
    print(f"Error: '{docs_dir}' is not a directory.")
else:
    md_files = list(docs_dir.rglob("*.md"))

    if not md_files:
        print("No Markdown files found.")
    else:
        print(f"Found {len(md_files)} Markdown file(s):\n")
        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            first_line = lines[0].strip() if lines else "(empty file)"
            print(f"  {md_file}")
            print(f"    First line: {first_line}")
            print(f"    Total lines: {len(lines)}")
            print()
```

**Sample output:**

```
Found 3 Markdown file(s):

  docs/README.md
    First line: # Project Overview
    Total lines: 28

  docs/guides/install.md
    First line: # Installation Guide
    Total lines: 45

  docs/guides/auth.md
    First line: # Authentication
    Total lines: 33
```

This script combines several things you already know: a truthiness check on the list (`if not md_files`), a `for` loop, `.split()`, indexing, `.strip()`, `len()`, and f-strings. The only new piece is `pathlib` doing the directory walking.

## Quick Reference

```
# Import Path
$ python3 -c "from pathlib import Path; print(Path('a/b.txt'))"
a/b.txt

# Join paths with /
$ python3 -c "from pathlib import Path; print(Path('docs') / 'guides' / 'setup.md')"
docs/guides/setup.md

# Get the filename
$ python3 -c "from pathlib import Path; print(Path('docs/setup.md').name)"
setup.md

# Get the stem (filename without extension)
$ python3 -c "from pathlib import Path; print(Path('docs/setup.md').stem)"
setup

# Get the suffix (extension)
$ python3 -c "from pathlib import Path; print(Path('docs/setup.md').suffix)"
.md

# Get the parent directory
$ python3 -c "from pathlib import Path; print(Path('docs/guides/setup.md').parent)"
docs/guides

# Check if a path exists
$ python3 -c "from pathlib import Path; print(Path('.').exists())"
True

# Check if path is a file
$ python3 -c "from pathlib import Path; print(Path('.').is_file())"
False

# Check if path is a directory
$ python3 -c "from pathlib import Path; print(Path('.').is_dir())"
True

# List directory entries with iterdir()
$ python3 -c "from pathlib import Path; [print(e.name) for e in Path('.').iterdir()]"
(names of files and folders in the current directory)

# Glob for .md files in one directory
$ python3 -c "from pathlib import Path; [print(p) for p in Path('.').glob('*.md')]"
(any .md files in the current directory, if they exist)

# Recursive glob for .md files
$ python3 -c "from pathlib import Path; [print(p) for p in Path('.').rglob('*.md')]"
(any .md files in the current directory and all subdirectories)

# Read a file via Path
$ python3 -c "from pathlib import Path; Path('test.txt').write_text('hello\n', encoding='utf-8'); print(Path('test.txt').read_text(encoding='utf-8'))"
hello

# Get the current working directory
$ python3 -c "from pathlib import Path; print(Path.cwd())"
(your current working directory)
```

## Exercises

### Exercise 1: Markdown File Scanner

Create a directory structure for this exercise by running these shell commands first:

```bash
mkdir -p scantest/guides
mkdir -p scantest/reference
echo -e "# Welcome\n\nThis is the main README.\n\nIt has five lines." > scantest/README.md
echo -e "# Install Guide\n\nStep 1: Download.\nStep 2: Install.\nStep 3: Verify." > scantest/guides/install.md
echo -e "# API Reference\n\nEndpoint: /users\nMethod: GET\nReturns: JSON array" > scantest/reference/api.md
echo -e "This is a plain text changelog." > scantest/changelog.txt
echo -e "# Old Notes\n\nThese are old." > scantest/reference/old-notes.md
```

Write a script called `scan_docs.py` that does the following:

1. Accepts a directory path as a hardcoded variable (set it to `"scantest"`).
2. Verifies that the path is an existing directory. If it is not, logs an error using the `logging` module at the `ERROR` level and exits. (Configure logging to display the level name and message.)
3. Recursively finds every `.md` file in that directory.
4. Skips any Markdown file whose filename starts with `old` (case-insensitive comparison).
5. For each remaining file, reads its content and extracts the first line. If the first line starts with `#` , treat the text after `#` as the document's title. If the first line does not start with `#` , use `(No title)` as the title.
6. After processing, prints a summary report in exactly this format:

```
Scan complete: scantest

  README.md
    Path:  scantest/README.md
    Title: Welcome
    Lines: 5

  install.md
    Path:  scantest/guides/install.md
    Title: Install Guide
    Lines: 5

  api.md
    Path:  scantest/reference/api.md
    Title: API Reference
    Lines: 5

Total Markdown files: 3 (1 skipped)
```

> [!note] 
> The files may appear in any order depending on your operating system. Your output must match this format, but the order of the three files does not need to match.

**Desired output:**

The report shown above, with exactly that formatting. The "skipped" count reflects any files that were filtered out by the `old` filename check.

---

## Audit

|Operation / Concept|Required by exercise?|Introduced in|
|---|---|---|
|`from pathlib import Path`|Yes|Lesson 17 (imports), Lesson 22 (pathlib usage)|
|`Path(...)` constructor|Yes|Lesson 22|
|`.is_dir()`|Yes|Lesson 22|
|`.rglob("*.md")`|Yes|Lesson 22|
|`.name` attribute|Yes|Lesson 22|
|`.read_text(encoding="utf-8")`|Yes|Lesson 22|
|`open()` / file reading concepts|Background|Lesson 21|
|`logging.basicConfig()`, `logging.error()`|Yes|Lesson 20|
|`for` loop|Yes|Lesson 9|
|`if/elif/else`|Yes|Lesson 10|
|`.lower()`|Yes|Lesson 5|
|`.startswith()`|Yes|Lesson 5|
|`.strip()`|Yes|Lesson 5|
|`.split()`|Yes|Lesson 5|
|`len()`|Yes|Lesson 7|
|f-strings|Yes|Lesson 6|
|`list()` on an iterator|Yes|Lesson 7|
|Variable assignment|Yes|Lesson 2|
|`print()`|Yes|Lesson 1|
|Truthiness (`if not ...`)|Yes|Lesson 14|
|Functions|No (not required, but allowed)|Lesson 15|

All operations are from Lesson 22 or earlier. No future-lesson concepts are required. The exercise reinforces skills from Lessons 5 (string methods), 6 (f-strings), 9 (loops), 10 (conditionals), 14 (truthiness), and 20 (logging), satisfying the diversity requirement. The previous three lessons (19, 20, 21) are represented: Lesson 20 via logging, Lesson 21 via file reading concepts, and Lesson 19 concepts are available but not forced awkwardly.