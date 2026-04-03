# Lesson 25: Text Processing II — Structured Transforms at Scale

## Terminology and Theory

**Multi-file transformation** — A script that opens more than one file, applies the same set of changes (usually regex-based substitutions or line rewrites) to each file, and writes the results out. This is the bread and butter of technical-writing automation: a term changes across your docs, a URL moves, a header format needs updating — and you want Python to do it instead of manual find-and-replace in an editor.

**Dry run** — Running your transformation logic without writing any changes to disk. Instead, the script prints what it _would_ change: which file, which line, and what the new content would look like. This is a safety net. You review the output, confirm it's correct, then run again with writes enabled. Every script that touches existing files should have a dry-run mode.

**Two-pass pattern** — A common script structure:

1. **Pass 1 (preview):** Walk the files, apply your regex or string transforms in memory, and print a report of planned changes. Write nothing.
2. **Pass 2 (apply):** If the preview looks correct, re-run with a flag that tells the script to write changes to disk.

This two-pass discipline prevents the most common "oops" scenario: a regex that matched more than you expected, silently corrupting dozens of files before you noticed.

**In-place vs. new-file output** — Two strategies for writing changes:

- **In-place:** Overwrite the original file with the transformed content. Dangerous but convenient. Always preview first.
- **New-file output:** Write transformed content to a new file (or a parallel directory), leaving the originals untouched. Safer, but you end up with two copies.

For learning purposes and in real-world scripts, the new-file strategy is often preferable. In-place writes are fine once you trust your logic and have a preview confirming the changes.

**Change report** — A summary printed during a dry run that tells you exactly what will be modified. A good change report includes the file path, the line number, the original line, and the replacement line. Without this, you're flying blind.

---

## Syntax Section

### Combining `pathlib`, `re`, and file I/O in a pipeline

The general pattern is:

```python
from pathlib import Path
import re

source_dir = Path("docs")

for filepath in source_dir.rglob("*.md"):
    text = filepath.read_text(encoding="utf-8")
    new_text = re.sub(r"old_pattern", "replacement", text)

    if text != new_text:
        print(f"CHANGED: {filepath}")
        filepath.write_text(new_text, encoding="utf-8")
```

`Path.rglob("*.md")` recursively finds every `.md` file under `source_dir`. You already know `rglob` from Lesson 23 — here it becomes the "file discovery" step of the pipeline.

`filepath.read_text(encoding="utf-8")` reads the entire file into a string. You learned this shorthand in Lesson 23; it's equivalent to opening with `open()` and calling `.read()`.

`re.sub(r"old_pattern", "replacement", text)` performs the substitution across the full text. From Lesson 24, you know `re.sub` returns a new string with all matches replaced.

`text != new_text` is the key check: if nothing matched, the strings are identical and you skip the file. This avoids rewriting files that don't need changes (and avoids printing noise in your report).

### Building a dry-run guard

Wrap the write operation behind a boolean flag:

```python
dry_run = True

if text != new_text:
    print(f"  Would change: {filepath}")
    if not dry_run:
        filepath.write_text(new_text, encoding="utf-8")
        print(f"  Written: {filepath}")
```

When `dry_run` is `True`, the script prints what it found but writes nothing. When you're ready to apply, set `dry_run = False` and re-run.

### Line-by-line change reporting

For more detailed previews, process files line by line:

```python
lines = text.splitlines(keepends=True)
```

`str.splitlines(keepends=True)` splits a string into a list of lines while preserving the newline characters at the end of each line. The `keepends=True` argument is important: without it, the newlines are stripped, and when you write the lines back, you'd need to re-add them. Keeping them means `"".join(lines)` reconstructs the original text exactly.

You can then iterate with `enumerate()` (Lesson 9) to get line numbers:

```python
for i, line in enumerate(lines, start=1):
    new_line = re.sub(pattern, replacement, line)
    if line != new_line:
        print(f"  Line {i}: {line.rstrip()}")
        print(f"       →  {new_line.rstrip()}")
    new_lines.append(new_line)
```

### Writing transformed content to a new output directory

Instead of overwriting originals, mirror the directory structure into an output folder:

```python
output_dir = Path("docs_updated")

for filepath in source_dir.rglob("*.md"):
    relative = filepath.relative_to(source_dir)
    out_path = output_dir / relative

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(new_text, encoding="utf-8")
```

`filepath.relative_to(source_dir)` gives you the path of the file relative to the source directory. If `filepath` is `docs/guides/setup.md` and `source_dir` is `docs`, then `relative` is `guides/setup.md`.

`out_path.parent.mkdir(parents=True, exist_ok=True)` creates any intermediate directories that don't exist yet. `parents=True` means it will create the full chain of directories (like `mkdir -p` in Bash). `exist_ok=True` means it won't raise an error if the directory already exists.

---

## Worked Examples

### Example 1: Replacing a term across all Markdown files (dry run)

Imagine your documentation refers to "GitHub token" in many places, and the style guide now requires "personal access token" instead. You want to find every occurrence across all `.md` files and preview the changes before committing them.

Create a directory with sample files to work with:

```
project/
├── transform_term.py
└── docs/
    ├── setup.md
    └── guides/
        └── auth.md
```

`docs/setup.md`:

```markdown
# Setup

First, generate a GitHub token from your account settings.
Store your GitHub token in an environment variable.
```

`docs/guides/auth.md`:

```markdown
# Authentication

Pass your GitHub token to the SDK constructor.
Never commit a GitHub token to version control.
If your GitHub token expires, generate a new one.
```

`transform_term.py`:

```python
from pathlib import Path
import re

source_dir = Path("docs")
pattern = r"GitHub token"
replacement = "personal access token"
dry_run = True

change_count = 0

for filepath in source_dir.rglob("*.md"):
    text = filepath.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    new_lines = []
    file_changed = False

    for i, line in enumerate(lines, start=1):
        new_line = re.sub(pattern, replacement, line)
        if line != new_line:
            print(f"  {filepath} line {i}:")
            print(f"    OLD: {line.rstrip()}")
            print(f"    NEW: {new_line.rstrip()}")
            file_changed = True
            change_count += 1
        new_lines.append(new_line)

    if file_changed and not dry_run:
        filepath.write_text("".join(new_lines), encoding="utf-8")

if dry_run:
    print(f"\nDry run complete. {change_count} line(s) would change.")
else:
    print(f"\nDone. {change_count} line(s) changed.")
```

Running this script produces:

```
  docs/setup.md line 3:
    OLD: First, generate a GitHub token from your account settings.
    NEW: First, generate a personal access token from your account settings.
  docs/setup.md line 4:
    OLD: Store your GitHub token in an environment variable.
    NEW: Store your personal access token in an environment variable.
  docs/guides/auth.md line 3:
    OLD: Pass your GitHub token to the SDK constructor.
    NEW: Pass your personal access token to the SDK constructor.
  docs/guides/auth.md line 4:
    OLD: Never commit a GitHub token to version control.
    NEW: Never commit a personal access token to version control.
  docs/guides/auth.md line 5:
    OLD: If your GitHub token expires, generate a new one.
    NEW: If your personal access token expires, generate a new one.

Dry run complete. 5 line(s) would change.
```

Nothing was written. You review the output, confirm every substitution is correct, then change `dry_run = False` and run again to apply.

The key details: `rglob("*.md")` finds both files regardless of depth. `splitlines(keepends=True)` lets us track line numbers while preserving newlines for accurate reconstruction. The `file_changed` flag prevents us from rewriting files that had no matches. And the `change_count` gives you a summary total.

---

### Example 2: Normalizing heading style across files (write to output directory)

Suppose some Markdown files use `# Title` (with a space after `#`) and others use `#Title` (no space). You want to normalize them all to have a space, but you'd rather write results to a new directory instead of overwriting originals.

`normalize_headings.py`:

```python
from pathlib import Path
import re

source_dir = Path("docs")
output_dir = Path("docs_normalized")
pattern = r"^(#{1,6})(\S)"
replacement = r"\1 \2"

files_changed = 0

for filepath in source_dir.rglob("*.md"):
    text = filepath.read_text(encoding="utf-8")
    new_text = re.sub(pattern, replacement, text, flags=re.MULTILINE)

    relative = filepath.relative_to(source_dir)
    out_path = output_dir / relative
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if text != new_text:
        files_changed += 1
        print(f"  Fixed headings in: {relative}")

    out_path.write_text(new_text, encoding="utf-8")

print(f"\n{files_changed} file(s) had heading fixes.")
print(f"Output written to: {output_dir}")
```

The regex `^(#{1,6})(\S)` matches lines that start with 1–6 `#` characters immediately followed by a non-whitespace character (i.e., no space between `#` and the heading text). The `re.MULTILINE` flag makes `^` match the start of every line, not just the start of the entire string. The replacement `\1 \2` inserts a space between the `#` characters and the first word.

`relative_to()` preserves the subdirectory structure. A file at `docs/guides/auth.md` is written to `docs_normalized/guides/auth.md`. `mkdir(parents=True, exist_ok=True)` ensures the output subdirectories exist.

Every file is written to the output directory — even unchanged ones. This gives you a complete, self-contained copy. The print statement only reports files that actually changed.

---

### Example 3: Multi-pattern substitution with a change log

Real-world transforms often involve several patterns at once. For instance, after a product rebrand, you might need to replace a product name, update a URL, and fix a capitalization inconsistency — all in the same pass.

`rebrand.py`:

```python
from pathlib import Path
import re

source_dir = Path("docs")
dry_run = True

substitutions = [
    (r"Acme CLI",        "Rocket CLI"),
    (r"acme-cli\.com",   "rocketcli.dev"),
    (r"AcmeCLI",         "RocketCLI"),
]

total_changes = 0

for filepath in source_dir.rglob("*.md"):
    text = filepath.read_text(encoding="utf-8")
    original = text

    file_changes = []

    for pattern, replacement in substitutions:
        matches = re.findall(pattern, text)
        if matches:
            file_changes.append(f"    {pattern!r} → {replacement!r}  ({len(matches)} match(es))")
            text = re.sub(pattern, replacement, text)

    if file_changes:
        total_changes += len(file_changes)
        print(f"  {filepath}:")
        for change in file_changes:
            print(change)

    if not dry_run and text != original:
        filepath.write_text(text, encoding="utf-8")

mode = "Dry run" if dry_run else "Applied"
print(f"\n{mode}: {total_changes} substitution(s) across all files.")
```

There are a few things to note here. The `substitutions` list is a list of tuples — each tuple contains a pattern and its replacement. You loop through the list with tuple unpacking (`for pattern, replacement in substitutions`), which you learned in Lesson 13.

The `!r` format specifier inside the f-string prints the "repr" (representation) of a value, which wraps strings in quotes and escapes special characters. This is useful in change logs because it makes the exact pattern and replacement unambiguous. For example, `f"{'Acme CLI'!r}"` outputs `'Acme CLI'` (with quotes), while `f"{'Acme CLI'}"` outputs `Acme CLI` (without quotes).

The script applies all substitutions to the full text in sequence. `findall` tells you how many matches each pattern found before `sub` replaces them. The result is a clear change log per file.

---

## Quick Reference

```
# Read all text from a file via pathlib
$ python3 -c "from pathlib import Path; print(Path('demo.txt').read_text(encoding='utf-8'))"
(contents of demo.txt)

# Write text to a file via pathlib
$ python3 -c "from pathlib import Path; Path('out.txt').write_text('hello\n', encoding='utf-8'); print('written')"
written

# Recursively find all .md files under a directory
$ python3 -c "from pathlib import Path; [print(p) for p in Path('docs').rglob('*.md')]"
docs/setup.md
docs/guides/auth.md

# Split text into lines while preserving newline characters
$ python3 -c "text = 'line1\nline2\nline3\n'; print(text.splitlines(keepends=True))"
['line1\n', 'line2\n', 'line3\n']

# Reconstruct text from lines preserving original formatting
$ python3 -c "lines = ['line1\n', 'line2\n']; print(repr(''.join(lines)))"
'line1\nline2\n'

# Get a file path relative to a parent directory
$ python3 -c "from pathlib import Path; print(Path('docs/guides/auth.md').relative_to(Path('docs')))"
guides/auth.md

# Create nested output directories (parents=True, exist_ok=True)
$ python3 -c "from pathlib import Path; Path('output/sub/deep').mkdir(parents=True, exist_ok=True); print('created')"
created

# Apply re.sub with re.MULTILINE so ^ matches every line start
$ python3 -c "import re; text = '#Bad\n##Also bad\n'; print(re.sub(r'^(#{1,6})(\S)', r'\1 \2', text, flags=re.MULTILINE))"
# Bad
## Also bad

# Use !r in f-strings to show repr of a value
$ python3 -c "val = 'hello world'; print(f'{val!r}')"
'hello world'

# Compare two strings to detect whether a substitution changed anything
$ python3 -c "old = 'foo bar'; new = 'foo baz'; print('changed' if old != new else 'no change')"
changed
```

---

## Exercise

### Multi-File Link Updater

Your documentation project has moved its repository from `github.com/old-org/docs` to `github.com/new-org/docs`. Several Markdown files contain links pointing to the old location. Your job is to write a script that finds every reference to the old URL, previews the changes, and then applies them — using the two-pass dry-run pattern taught in this lesson.

**Setup:** Create the following directory structure and file contents before writing your script.

Directory structure:

```
link_update/
├── update_links.py
└── content/
    ├── index.md
    └── reference/
        └── api.md
```

`content/index.md`:

```markdown
# Welcome

See the full source at https://github.com/old-org/docs for details.
You can also file issues at https://github.com/old-org/docs/issues.
```

`content/reference/api.md`:

```markdown
# API Reference

Code samples are in https://github.com/old-org/docs/tree/main/examples.
For setup instructions, visit https://github.com/old-org/docs#setup.
Unrelated link: https://github.com/other-project/tools is not affected.
```

**Requirements:**

1. Your script must define a `dry_run` variable set to `True`.
2. Scan every `.md` file under the `content/` directory recursively.
3. Replace every occurrence of `https://github.com/old-org/docs` with `https://github.com/new-org/docs`.
4. During a dry run, print each affected file's path (relative to `content/`), the line number, the old line, and the new line. Do not write any files.
5. Print a summary line at the end showing the total number of lines that would change and the total number of files affected.
6. When `dry_run` is changed to `False`, write the changed files to an output directory called `content_updated/`, preserving the subdirectory structure. Print the same report, but with a summary indicating changes were applied.
7. The unrelated link (`https://github.com/other-project/tools`) must not be affected.

**Expected output with `dry_run = True`:**

```
index.md line 3:
  OLD: See the full source at https://github.com/old-org/docs for details.
  NEW: See the full source at https://github.com/new-org/docs for details.
index.md line 4:
  OLD: You can also file issues at https://github.com/old-org/docs/issues.
  NEW: You can also file issues at https://github.com/new-org/docs/issues.
reference/api.md line 3:
  OLD: Code samples are in https://github.com/old-org/docs/tree/main/examples.
  NEW: Code samples are in https://github.com/new-org/docs/tree/main/examples.
reference/api.md line 4:
  OLD: For setup instructions, visit https://github.com/old-org/docs#setup.
  NEW: For setup instructions, visit https://github.com/new-org/docs#setup.

Dry run complete. 4 line(s) across 2 file(s) would change.
```

**Expected output with `dry_run = False`:**

```
index.md line 3:
  OLD: See the full source at https://github.com/old-org/docs for details.
  NEW: See the full source at https://github.com/new-org/docs for details.
index.md line 4:
  OLD: You can also file issues at https://github.com/old-org/docs/issues.
  NEW: You can also file issues at https://github.com/new-org/docs/issues.
reference/api.md line 3:
  OLD: Code samples are in https://github.com/old-org/docs/tree/main/examples.
  NEW: Code samples are in https://github.com/new-org/docs/tree/main/examples.
reference/api.md line 4:
  OLD: For setup instructions, visit https://github.com/old-org/docs#setup.
  NEW: For setup instructions, visit https://github.com/new-org/docs#setup.

Applied. 4 line(s) across 2 file(s) changed. Output written to: content_updated
```

---

## Audit

| Operation                                       | Introduced in                                        |
| ----------------------------------------------- | ---------------------------------------------------- |
| `from pathlib import Path`                      | Lesson 17 (modules/imports), Lesson 23 (pathlib)     |
| `Path.rglob("*.md")`                            | Lesson 23                                            |
| `Path.read_text(encoding="utf-8")`              | Lesson 23                                            |
| `Path.write_text()`                             | Lesson 23                                            |
| `Path.relative_to()`                            | Lesson 23                                            |
| `Path.parent`                                   | Lesson 23                                            |
| `Path.mkdir(parents=True, exist_ok=True)`       | Lesson 23                                            |
| `import re` / `re.sub()`                        | Lesson 17 (import), Lesson 24 (regex)                |
| `str.splitlines(keepends=True)`                 | Lesson 25 (this lesson)                              |
| `str.rstrip()`                                  | Lesson 5 (string methods)                            |
| `"".join(lines)`                                | Lesson 5 (`.join()`)                                 |
| `enumerate(lines, start=1)`                     | Lesson 9 (loops / `enumerate`)                       |
| `for` loops                                     | Lesson 9                                             |
| `if/else` conditionals                          | Lesson 10                                            |
| f-strings                                       | Lesson 6                                             |
| Boolean variable (`dry_run = True`)             | Lesson 2 (variables/types), Lesson 10 (conditionals) |
| `print()`                                       | Lesson 1–3                                           |
| Integer counter variables (`+= 1`)              | Lesson 2 (variables)                                 |
| Tuple unpacking in loops                        | Lesson 13                                            |
| `not` operator                                  | Lesson 10                                            |
| String comparison (`!=`)                        | Lesson 10 (comparisons)                              |
| Writing to output directory (new-file strategy) | Lesson 25 (this lesson)                              |

All operations in the exercise are covered by Lessons 1–25. No future-lesson dependencies.