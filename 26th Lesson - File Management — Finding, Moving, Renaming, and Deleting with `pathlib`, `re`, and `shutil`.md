# Lesson 26: File Management — Finding, Moving, Renaming, and Deleting with `pathlib`, `re`, and `shutil`

## Terminology and Theory

**`shutil`** (short for "shell utilities") is a standard library module that provides high-level file and directory operations — the kind of thing you'd do with `mv`, `cp`, and `rm -r` in Bash. Where `pathlib` handles paths and metadata, as well as reading and writing single files, `shutil` copies files and directories.

**`shutil.move()`** moves a file or an entire directory from one location to another. It works like `mv` in Bash, and it operates according to these rules:

- This method doesn't create new directories.
- If the destination exists, this method moves the source *into* the destination.
- If the destination involves renaming a filename (inside of existing directories), the filename is renamed, even if that new filename doesn't yet exist.

**`Path.rename()`** renames a file or directory. Unlike `shutil.move()`, it does not create missing parent directories, and its behavior is platform-dependent if the destination already exists. Use it for simple same-directory renames.

**`Path.unlink()`** deletes a single file. It raises `FileNotFoundError` if the file does not exist, unless you pass `missing_ok=True`. It cannot delete directories.

**`shutil.rmtree()`** recursively deletes an entire directory tree — the directory and everything inside it. This is the Python equivalent of `rm -rf`. There is no undo.

**`Path.rglob()`** performs a recursive glob over a directory tree. Where `Path.iterdir()` only lists the immediate children of a directory, and `Path.glob()` matches a pattern in the immediate directory (or one level deeper with `*/`), `rglob()` descends into every subdirectory. `Path.rglob("*.md")` finds every Markdown file in the entire tree below the starting path.

**Dry run** is a pattern you learned in Lesson 25: before performing destructive or irreversible operations (deletes, moves, renames at scale), print what would happen first and only execute when the user confirms. This is even more important for filesystem management than for text editing, because deleted files and overwritten destinations cannot be recovered from a script.

> [!warning] 
> `Path.unlink()` and `shutil.rmtree()` permanently delete files and directories. There is no trash can, no undo. Always preview what will be affected before executing.

## Syntax Section

### Importing `shutil`

```python
import shutil
```

`shutil` is a standard library module. You import it the same way you imported `pathlib`, `re`, and `logging`.

### Recursive globbing with `Path.rglob()`

```python
from pathlib import Path

base = Path("docs")
for p in base.rglob("*.md"):
    print(p)
```

`rglob(pattern)` returns an iterator that yields every `Path` object matching `pattern` in the entire directory tree under `base`. The pattern uses the same glob syntax you've seen: `*` matches any filename characters, `**` is implicit in `rglob` (that's what makes it recursive).

### Moving files and directories with `shutil.move()`

```python
import shutil

shutil.move("reports/draft.md", "archive/draft.md")
```

The first argument is the source, the second is the destination. Both can be strings or `Path` objects. If the destination directory does not exist, Python raises an error — `shutil.move()` does not create parent directories for you. If the destination *does* exist, this method moves the source *into* the destination. If the destination involves renaming a filename, the filename is renamed, even if that new filename doesn't yet exist.

### Renaming with `Path.rename()`

```python
from pathlib import Path

old = Path("notes/meeting.txt")
new = old.rename("notes/meeting_2025.txt")
```

`rename()` returns a new `Path` pointing to the renamed file. The destination must include the full path — it is not "just a new name," it is "the new full path." If you only supply a bare filename, the file moves relative to the current working directory, which is rarely what you want.

### Deleting a file with `Path.unlink()`

```python
from pathlib import Path

target = Path("temp/scratch.txt")
target.unlink()
```

If the file does not exist, this raises `FileNotFoundError`. To suppress that error:

```python
target.unlink(missing_ok=True)
```

### Deleting a directory tree with `shutil.rmtree()`

```python
import shutil

shutil.rmtree("temp/old_build")
```

This deletes the directory and everything inside it. There is no confirmation prompt and no recovery.

### Combining `rglob()` and `re` to find files by regex

`rglob()` uses glob patterns, which are limited. When you need the full power of regular expressions to match filenames — for example, finding files that match `report_\d{4}\.md` — combine `rglob("*")` with `re.search()`:

```python
from pathlib import Path
import re

base = Path("docs")
pattern = re.compile(r"report_\d{4}\.md$")

for p in base.rglob("*"):
    if p.is_file() and pattern.search(p.name):
        print(p)
```

`p.name` gives you just the filename (no directory components), which is usually what you want to match against.

## Worked Examples

### Example 1: Find and list all `.log` files recursively

This script scans a project directory for `.log` files buried anywhere in the tree and prints each one with its size.

```python
from pathlib import Path

project = Path("my_project")

print("Log files found:")
for p in project.rglob("*.log"):
    size = p.stat().st_size
    print(f"  {p}  ({size} bytes)")
```

`rglob("*.log")` descends into every subdirectory under `my_project`. For each match, `p.stat().st_size` returns the file size in bytes — the same information you'd get from `ls -l`. The result is a quick inventory of log files scattered across a project.

### Example 2: Move files matching a regex into an archive directory

This script finds all files whose names match a date pattern like `notes_2024-01-15.md` and moves them into an `archive/` directory. It uses the dry-run-then-execute pattern from Lesson 25.

```python
from pathlib import Path
import shutil
import re
import sys

source = Path("notes")
archive = Path("notes/archive")
pattern = re.compile(r"notes_\d{4}-\d{2}-\d{2}\.md$")

# Find matches
matches = []
for p in source.iterdir():
    if p.is_file() and pattern.search(p.name):
        matches.append(p)

if not matches:
    print("No matching files found.")
    sys.exit(0)

# Dry run: preview
print(f"Found {len(matches)} file(s) to archive:")
for p in matches:
    print(f"  {p.name}  ->  {archive / p.name}")

# Check for confirmation flag
if "--execute" not in sys.argv:
    print("\nDry run complete. Pass --execute to move files.")
    sys.exit(0)

# Execute
archive.mkdir(exist_ok=True)
for p in matches:
    shutil.move(str(p), str(archive / p.name))
    print(f"  Moved: {p.name}")

print("Done.")
```

A few things to notice:

- `source.iterdir()` is used instead of `rglob()` because we only want files in the top-level `notes/` directory, not in subdirectories.
- `archive.mkdir(exist_ok=True)` creates the archive directory if it does not exist and does nothing if it already does. You learned `mkdir()` as part of `pathlib` in Lesson 23.
- `sys.argv` is used to check for `--execute`. You have not formally studied `argparse` yet, but you know `sys.argv` is a list of command-line arguments (it is just a list of strings, and you've worked with lists since Lesson 7). The script treats the absence of `--execute` as "dry run mode."
- `str(p)` is passed to `shutil.move()` because older Python versions expect string paths. In Python 3.9+, `Path` objects work directly, but wrapping in `str()` is a safe habit.

### Example 3: Delete empty directories from a tree

After moving or deleting files, you often end up with empty directories cluttering a project. This script finds and removes them.

```python
from pathlib import Path
import sys

base = Path("workspace")

# Collect empty directories (deepest first so children are removed before parents)
empty_dirs = []
for p in sorted(base.rglob("*"), reverse=True):
    if p.is_dir() and not any(p.iterdir()):
        empty_dirs.append(p)

if not empty_dirs:
    print("No empty directories found.")
    sys.exit(0)

print(f"Found {len(empty_dirs)} empty directory(ies):")
for d in empty_dirs:
    print(f"  {d}")

if "--execute" not in sys.argv:
    print("\nDry run complete. Pass --execute to delete.")
    sys.exit(0)

for d in empty_dirs:
    d.rmdir()
    print(f"  Deleted: {d}")

print("Done.")
```

Key details:

- `sorted(..., reverse=True)` processes deeper directories first. If `workspace/a/b/` is empty and you delete it, then `workspace/a/` might become empty too. Processing deepest-first handles this naturally.
- `any(p.iterdir())` returns `True` if there is at least one item inside the directory. You learned `any()` indirectly — it consumes an iterator (Lesson 20) and returns `True` if any element is truthy (Lesson 14). `not any(p.iterdir())` means "the directory is empty."
- `p.rmdir()` is a `pathlib` method that removes a single empty directory. It is different from `shutil.rmtree()`, which removes a directory and all its contents. `rmdir()` raises `OSError` if the directory is not empty, which is a safety net here.

## Quick Reference

```shellsession
# Recursively find all .md files under docs/
$ python3 -c "from pathlib import Path; [print(p) for p in Path('docs').rglob('*.md')]"
docs/README.md
docs/guides/setup.md
docs/guides/advanced/config.md

# Move a file into another directory
$ python3 -c "import shutil; shutil.move('draft.txt', 'archive/draft.txt')"
(no output on success)

# Rename a file in the same directory
$ python3 -c "from pathlib import Path; Path('old_name.txt').rename('new_name.txt')"
(no output on success)

# Delete a single file
$ python3 -c "from pathlib import Path; Path('temp.txt').unlink()"
(no output on success)

# Delete a single file, suppressing error if it does not exist
$ python3 -c "from pathlib import Path; Path('temp.txt').unlink(missing_ok=True)"
(no output on success)

# Delete an entire directory tree
$ python3 -c "import shutil; shutil.rmtree('build_output')"
(no output on success)

# Remove a single empty directory
$ python3 -c "from pathlib import Path; Path('empty_folder').rmdir()"
(no output on success)

# Find files whose names match a regex pattern
$ python3 -c "
from pathlib import Path
import re
pat = re.compile(r'report_\d{4}\.md$')
for p in Path('docs').rglob('*'):
    if p.is_file() and pat.search(p.name):
        print(p)
"
docs/report_2024.md
docs/archive/report_2023.md
```

## Exercises

### Exercise 1: Organize files by extension

Write a script called `organize_by_ext.py` that performs the following:

1. Accept a directory path as a command-line argument via `sys.argv[1]`. If no argument is provided, print a usage message and exit.
2. Scan the given directory (non-recursively, immediate children only) for all files.
3. For each file found, determine its extension (e.g., `.txt`, `.md`, `.log`). Skip files that have no extension.
4. For each unique extension, create a subdirectory named after the extension without the dot (e.g., a `txt` subdirectory for `.txt` files, a `md` subdirectory for `.md` files).
5. In dry-run mode (the default), print every planned move in the format shown below. Do not move anything.
6. When `--execute` is passed as an additional argument, create the subdirectories and move the files.
7. Use `logging` at the `INFO` level to log each move operation during execution. Use `logging` at the `WARNING` level to log any file that is skipped because it has no extension.

Before running the script, create a test directory with the following structure:

```
test_files/
├── notes.txt
├── readme.md
├── app.log
├── data.txt
├── report.md
├── .hidden
├── Makefile
```

> [!tip] 
> You can create this test structure with a few lines of Python using `Path.mkdir()` and `Path.write_text()`, or you can create the files manually from the shell.

**Dry-run output** (order of files may vary, but grouping and format must match):

```
Planned operations:
  notes.txt   -> txt/notes.txt
  data.txt    -> txt/data.txt
  readme.md   -> md/readme.md
  report.md   -> md/report.md
  app.log     -> log/app.log
Skipped (no extension): .hidden
Skipped (no extension): Makefile

Dry run complete. Pass --execute to move files.
```

**Execute output** (with `--execute`):

```
INFO:root:Created directory: txt
INFO:root:Created directory: md
INFO:root:Created directory: log
INFO:root:Moved: notes.txt -> txt/notes.txt
INFO:root:Moved: data.txt -> txt/data.txt
INFO:root:Moved: readme.md -> md/readme.md
INFO:root:Moved: report.md -> md/report.md
INFO:root:Moved: app.log -> log/app.log
WARNING:root:Skipped (no extension): .hidden
WARNING:root:Skipped (no extension): Makefile
```

After execution, the directory should look like this:

```
test_files/
├── .hidden
├── Makefile
├── log/
│   └── app.log
├── md/
│   ├── readme.md
│   └── report.md
└── txt/
    ├── data.txt
    └── notes.txt
```

---

## Audit

The exercise requires the following operations. Each one is verified against the lesson it was introduced in:

|Operation / Concept|Introduced In|
|---|---|
|`from pathlib import Path`|Lesson 17 (imports), Lesson 23 (pathlib)|
|`import shutil`|**Lesson 26 (this lesson)**|
|`import sys`|Lesson 17 (imports)|
|`import logging`|Lesson 21 (logging)|
|`sys.argv` for command-line arguments|Lesson 17 (modules — `sys` introduced), used in Lesson 25|
|`Path.iterdir()`|Lesson 23 (pathlib)|
|`Path.is_file()`|Lesson 23 (pathlib)|
|`Path.suffix` (file extension)|Lesson 23 (pathlib)|
|`Path.name`|Lesson 23 (pathlib)|
|`Path.mkdir(exist_ok=True)`|Lesson 23 (pathlib)|
|`shutil.move()`|**Lesson 26 (this lesson)**|
|`logging.basicConfig()`, `logging.info()`, `logging.warning()`|Lesson 21 (logging)|
|`if/elif/else` conditionals|Lesson 10 (conditionals)|
|`for` loops|Lesson 9 (loops)|
|`f-strings`|Lesson 6 (string formatting)|
|`print()`|Lesson 1 (REPL and scripts)|
|`sys.exit()`|Lesson 17 (modules)|
|`str.startswith()` (implicit in checking for dot-only files)|Lesson 5 (string methods)|
|Lists and `append()`|Lesson 7 (lists)|
|Truthiness / checking empty strings|Lesson 14 (truthiness)|
|`"--execute" in sys.argv` (list membership with `in`)|Lesson 7 (lists), Lesson 10 (conditionals)|

**Lessons reinforced**: Lesson 23 (pathlib — `iterdir`, `is_file`, `suffix`, `name`, `mkdir`), Lesson 24 (regex — not directly required but the pattern-matching mindset carries over), Lesson 25 (dry-run-then-execute pattern), Lesson 21 (logging), Lesson 9 (loops), Lesson 10 (conditionals), Lesson 7 (lists), Lesson 6 (f-strings), Lesson 5 (string methods), Lesson 14 (truthiness).

**Forward dependency check**: No operations from Lesson 27 or beyond are required. The exercise uses `sys.argv` for the confirmation flag rather than `argparse` (Lesson 30). All required operations are from the current lesson or earlier lessons. ✅