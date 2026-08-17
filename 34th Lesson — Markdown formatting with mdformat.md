# Lesson 34: Markdown formatting with `mdformat`

Phase 2 — Python package workflow

You now know how to build a virtual environment (Lesson 33) and install distributions into it (Lesson 32). This lesson puts that to work on a tool you will actually use every week: `mdformat`, a formatter that rewrites Markdown files into a single consistent style. You will drive it two ways — from the command line and from Python — and you will learn where it quietly destroys content if you point it at the wrong kind of file.

---

## 1. Terminology and theory

### Formatter vs. linter

A **formatter** rewrites a file into a canonical shape. It does not evaluate whether your writing is any good; it only normalizes syntax. `mdformat` is to Markdown what `black` is to Python.

A **linter** reports problems and leaves the file alone. `markdownlint` is a linter. `mdformat` is not.

The practical difference: a linter gives you a list to act on, a formatter hands you a changed file.

### CommonMark, flavors, and plugins

**CommonMark** is the standardized core of Markdown: headings, lists, emphasis, links, code fences, block quotes, thematic breaks. Out of the box, that is the entire universe `mdformat` understands.

A **flavor** (or dialect) is Markdown plus extra syntax that CommonMark never defined. GitHub Flavored Markdown adds tables, task lists, and strikethrough. YAML front matter is not CommonMark. Neither are MyST directives, footnotes, admonition blocks, or GitBook's `{% hint %}` syntax.

A **plugin** is an installed distribution, always named `mdformat-something`, that teaches `mdformat` one of those flavors. Plugins are never imported; they register themselves at install time. But installing one is only half the story, and the two halves differ depending on how you invoke `mdformat`:

- **On the command line**, an installed plugin is enabled automatically. `--extensions` defaults to "all enabled."
- **In the Python API**, an installed plugin is enabled by *nothing*. `mdformat.text()` and `mdformat.file()` format plain CommonMark unless you name the extension you want in the `extensions` argument.

This asymmetry is deliberate — the library authors did not want a `pip install` in an unrelated part of a project to silently change what your program outputs — and it is the single most common way to lose an afternoon with this tool. A CLI run and a Python call in the same virtual environment, against the same file, can produce different results.

### Why this matters more than it looks

`mdformat` does not fail when it meets syntax it does not understand. It reinterprets that syntax as ordinary CommonMark and writes the result out. The output is still valid Markdown — it is just no longer your document.

The classic case is front matter. Given this file:

```markdown
---
title: Release notes
---

# Release notes
```

...`mdformat` without the `frontmatter` extension enabled sees no front matter at all. It sees a thematic break (`---`), then a paragraph (`title: Release notes`), then a second `---` sitting directly beneath that paragraph — which in CommonMark is a _setext heading underline_, and an underline of dashes means level two. Your metadata comes out the other side like this:

```markdown
______________________________________________________________________

## title: Release notes

# Release notes
```

The horizontal rule is `mdformat`'s canonical thematic break: seventy underscores. The document now contains a stray H2 whose text is your YAML key and value, and a page that used to carry metadata no longer does.

No error. No warning. Exit status 0. `mdformat` does have a safety check — it re-parses its own output and refuses to write if the rendered HTML would differ — but that check does not help here. A thematic break followed by an H2 followed by an H1 is exactly what the *input* parsed to as well. The tool did not change the meaning of the document it read; it just read a different document than you wrote.

> [!warning] Nothing warns you
> `mdformat` is destructive in place and silent about what it did not understand.
> Your protection is a copy, a Git working tree, or a `--check` run — never the tool itself.

### Vocabulary you will see in the docs

- **In-place formatting** — the file on disk is overwritten. There is no backup, no prompt, and no undo.
- **Dry run** — determine what _would_ change without changing anything. The CLI does this with `--check`; in Python you compare the formatted string to the original.
- **Idempotence** — formatting an already-formatted file produces a byte-identical file. This is what makes the string comparison above a reliable test.

### What `mdformat` normalizes

Expect these changes on a first run against unformatted docs:

|Input|Output|
|---|---|
|`* item` or `+ item`|`- item`|
|`Title` over a row of `=`|`# Title`|
|a thematic break written `---`, `***`, or `___`|a row of exactly seventy `_` characters|
|a code block indented four spaces|the same code inside a backtick fence|
|`[changelog](<https://example.com>)`|`[changelog](https://example.com)`|
|link reference definitions written mid-document|all of them moved to the bottom, sorted by label, with unused and duplicate definitions dropped|
|a hard line break written as two trailing spaces|a `\` at the end of the line|
|trailing whitespace on a paragraph|removed|
|missing final newline|added|
|inconsistent blank lines around blocks|exactly one blank line|

Two of these surprise people. The thematic break is the loud one: a docs page with three `---` rules in it comes back with three seventy-character underscore rows, which is correct CommonMark and looks nothing like what you wrote. The link-reference rule is the quiet one: if you keep a reference definition next to the paragraph that uses it, that definition will be relocated to the end of the file.

Two things it does **not** do. It does not rewrap your paragraphs unless you ask it to — the default `wrap` setting is `"keep"`, which preserves the line breaks you already have. And it does not normalize emphasis markers. `_emphasis_` stays `_emphasis_`, `*emphasis*` stays `*emphasis*`, `__strong__` stays `__strong__`, and `**strong**` stays `**strong**`. If you were expecting a formatter to unify these across a docs set the way `black` unifies quote characters, it will not; `mdformat` treats the choice of marker as content and leaves it alone.

---

## 2. Syntax

### Installing

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install mdformat
pip install mdformat-frontmatter mdformat-gfm
pip freeze > requirements.txt
```

### The command line interface

```bash
mdformat notes.md            # format one file in place
mdformat docs/               # walk docs/ and format every .md file in place
mdformat --check docs/       # dry run: report files that would change, change nothing
mdformat --wrap 80 notes.md  # hard-wrap paragraphs at 80 columns
mdformat --number notes.md   # renumber ordered lists 1. 2. 3.
mdformat --no-extensions notes.md          # ignore every installed plugin
mdformat --extensions frontmatter notes.md # require and enable just this one
echo $?                      # 0 = nothing to do, non-zero = would change (or error)
```

The exit status is the useful part of `--check`: it is what makes `mdformat` usable in a pre-commit hook or a CI job.

On the command line you rarely need `--extensions`, because every installed plugin is on by default. It is worth knowing anyway, for two reasons. `--no-extensions` reproduces the Python API's default behavior, which is how you reproduce a Python bug from the shell. And naming an extension explicitly *requires* it: if the plugin is not installed, the run fails instead of quietly formatting as plain CommonMark.

### The Python API

```python
import mdformat

formatted = mdformat.text(raw_markdown)
mdformat.file("docs/page.md")
```

Two functions, and the difference between them is the whole API:

- `mdformat.text(s)` takes a string and **returns** a formatted string. Nothing on disk changes. This is the safe one.
- `mdformat.file(path)` reads the file, formats it, and **overwrites it in place**. It returns `None`.

Both accept the same keyword arguments:

```python
mdformat.text(raw, options={"wrap": 80, "number": True})
mdformat.file(path, options={"wrap": "no"})
mdformat.text(raw, extensions={"gfm"})
```

### The options dict

|Key|Values|Default|Effect|
|---|---|---|---|
|`wrap`|`"keep"`, `"no"`, or an integer|`"keep"`|Keep existing line breaks / join each paragraph onto one line / hard-wrap at N columns|
|`number`|`True` or `False`|`False`|Number ordered lists `1. 2. 3.` instead of repeating `1.`|
|`end_of_line`|`"lf"`, `"crlf"`, `"keep"`|`"lf"`|Line endings written out|

The keys match the CLI flags, with hyphens becoming underscores: `--end-of-line` is `end_of_line`.

### The `extensions` argument

In the Python API, `extensions` is not a filter. It is the switch. Omit it and you get plain CommonMark regardless of what is installed in the environment. Name an extension and you get it, using the plugin's registered short name rather than its distribution name (`mdformat-gfm` registers both `gfm` and `tables`; `mdformat-frontmatter` registers `frontmatter`):

```python
mdformat.text(raw)                                     # plain CommonMark; installed plugins ignored
mdformat.text(raw, extensions={"frontmatter"})         # front matter preserved
mdformat.text(raw, extensions={"frontmatter", "gfm"})  # front matter and GFM tables preserved
```

The first line is the one that costs people time, because it looks like the neutral choice and is in fact the most destructive call in this lesson. It reinterprets every piece of non-CommonMark syntax in the string you hand it, and it does so even in an environment where you carefully installed the plugin that would have prevented it. Installing `mdformat-frontmatter` changes what `mdformat` does on the command line; it changes nothing at all about `mdformat.text(raw)`.

Naming an extension also asserts that it is present. If `mdformat-frontmatter` is not installed, a call passing `extensions={"frontmatter"}` fails outright instead of quietly falling back to CommonMark. That failure is the behavior you want: a missing plugin becomes one crash at the top of the run rather than quiet damage spread across a docs directory.

Your script's correctness therefore still depends on the environment, just more honestly than the CLI's does. This is the concrete reason Lesson 33 insisted on pinning dependencies — `requirements.txt` is not bureaucracy here, it is the list of syntaxes your script is able to see.

### Errors from `mdformat.file()`

`mdformat.file()` raises `ValueError` when the path is not a regular file — that is, when it is missing or when it is a directory. *Raises* means it throws an exception rather than returning a value: the call stops there, nothing is written, and unless you catch it the program ends with a traceback.

Symlinks are not in that category. `mdformat` resolves a symlink and formats the file it points at, leaving the link itself in place.

Note also that `mdformat.file()` does not walk directories the way the CLI does. If you pass it a folder, you get an exception, not a recursive format. Directory traversal is your job in Python.

```python
try:
    mdformat.file(path)
except ValueError:
    print(f"Not a formattable file: {path}")
```

### Copying a file first: `shutil.copy()`

Lesson 26 introduced `shutil.move()` for relocating files. The safety discipline in this lesson needs its sibling:

```python
import shutil

shutil.copy(source, destination)
```

`destination` may be either a full file path or an existing directory. If it is a directory, the file keeps its name. The directory must already exist — `shutil.copy()` will not create it for you.

---

## 3. Worked examples

### Example 1: Normalize a string and see what changed

```python
# example1_text.py
import mdformat

messy = """Release notes
=============

*   Fixed the __login__ bug.
*   Fixed the _logout_ bug.

---

See the [changelog](<https://example.com/changelog>) for the full list.
"""

print("--- BEFORE ---")
print(messy)
print("--- AFTER ---")
print(mdformat.text(messy))
```

Run it with `python example1_text.py`. The `AFTER` block is:

```markdown
# Release notes

- Fixed the __login__ bug.
- Fixed the _logout_ bug.

______________________________________________________________________

See the [changelog](https://example.com/changelog) for the full list.
```

Four normalizations happened in one call: the setext heading became ATX, the bullet marker and its three spaces of padding became `- `, the `---` thematic break became seventy underscores, and the unnecessary angle brackets came off the link destination.

The non-change is worth as much as the changes. `__login__` and `_logout_` came through exactly as written. `mdformat` will not unify your emphasis markers, so if half a docs set uses `*italic*` and half uses `_italic_`, running the formatter over it will not fix that. The source file was never touched either, because `mdformat.text()` only moves strings around.

### Example 2: The options dict changes the answer

```python
# example2_options.py
import mdformat

source = """# Setup steps

1. Create the virtual environment.
1. Activate it.
1. Install the packages.

This paragraph
is split across
three source lines.
"""

print("--- DEFAULTS ---")
print(mdformat.text(source))

print("--- number=True, wrap=no ---")
print(mdformat.text(source, options={"number": True, "wrap": "no"}))
```

With defaults, the output is identical to the input: repeated `1.` markers are valid canonical style, and `wrap="keep"` preserves the three-line paragraph exactly as written.

With the options applied, the list becomes `1.`, `2.`, `3.` and the paragraph collapses onto a single line.

This is worth internalizing before you write any dry-run logic: **"would this file change?" is not a property of the file.** It is a property of the file _plus_ your options _plus_ the plugins installed in the environment. Change any of the three and the answer changes.

### Example 3: Format one file in place, safely

```python
# example3_file.py
import shutil
from pathlib import Path

import mdformat

target = Path("docs/getting-started.md")
backup = target.parent / (target.name + ".bak")

try:
    shutil.copy(target, backup)
    mdformat.file(target, extensions={"frontmatter"})
except ValueError:
    print(f"Not a formattable file: {target}")
except OSError as err:
    print(f"Could not copy {target}: {err}")
else:
    print(f"Formatted {target.name}, original saved as {backup.name}")
```

The order of operations is the point. The copy happens first, so that if `mdformat.file()` produces something you did not expect, the original is already on disk. Reversing those two lines makes the backup worthless.

Note that the backup path is built with plain string concatenation on `.name` rather than `Path.with_suffix()`. `with_suffix()` _replaces_ the extension, so it would give you `getting-started.bak` and hide which format the original was in.

`extensions={"frontmatter"}` is not optional decoration here. Without it this snippet is a two-line program that copies a file and then strips its metadata, and the copy is the only thing standing between you and a lost commit.

> [!tip] Run `--check` first, always
> Before running any of this against a real docs directory, run `mdformat --check docs/` and read the list.
> If it names files you did not expect to be touched, stop and inspect those files individually.
> A `--check` run costs nothing and is the cheapest possible way to discover that your Markdown flavor needs a plugin you have not installed.

---

## 4. Quick reference

```python
# Import the formatter (the distribution is "mdformat", the module is "mdformat")
import mdformat

# Format a string and return the result; nothing on disk is touched
formatted = mdformat.text(raw_markdown)

# Compare formatted output to the original to answer "would this change?"
would_change = formatted != raw_markdown

# Format a file in place; overwrites the file and returns None
mdformat.file("docs/page.md")

# mdformat.file() raises ValueError when the path is not a regular file
try:
    mdformat.file(some_path)
except ValueError:
    print(f"Not a formattable file: {some_path}")

# Pass formatting options as a dict; keys mirror the CLI flags
formatted = mdformat.text(raw_markdown, options={"number": True})

# wrap: "keep" (default) preserves line breaks, "no" joins paragraphs, an int hard-wraps
formatted = mdformat.text(raw_markdown, options={"wrap": 80})

# Options work identically on the in-place function
mdformat.file("docs/page.md", options={"wrap": "no", "number": True})

# extensions ENABLES plugins; omit it and you get plain CommonMark, whatever is installed
plain = mdformat.text(raw_markdown)
with_gfm = mdformat.text(raw_markdown, extensions={"gfm"})
with_both = mdformat.text(raw_markdown, extensions={"gfm", "frontmatter"})

# Naming an uninstalled extension is an error, not a silent fallback to CommonMark

# Copy a file before formatting it; destination may be a file path or an existing directory
import shutil
shutil.copy(source_path, backup_dir)

# CLI equivalents, for reference:
# mdformat docs/            format every .md file under docs/ in place
# mdformat --check docs/    dry run; non-zero exit status if any file would change
# mdformat --wrap 80 --number notes.md
# The CLI enables every installed plugin by default; the Python API enables none.
# mdformat --no-extensions notes.md    reproduce the Python API default from the shell
```

---

## 5. Exercise

Build `mdfix.py`, a preview-then-write Markdown formatter for a docs directory.

### Setup

Work inside a fresh virtual environment. Install `mdformat` and `mdformat-frontmatter` into it.

Create a directory named `docs` containing exactly these three files, byte for byte.

`docs/getting-started.md`:

```markdown
Getting started
===============

*   Create the virtual environment.
*   Activate it.
*   Install the __required__ packages.

See the _release notes_ for changes.
```

`docs/release-notes.md`:

```markdown
---
title: Release notes
---

# Release notes

1. Fixed the login bug.
1. Fixed the logout bug.
```

`docs/clean.md`:

```markdown
# Clean

This file is already formatted.
```

Also create an empty directory named `backups`.

### Part A — the script

Write `mdfix.py` so that it meets all of the following requirements.

1. It takes one required positional argument: the path of a directory to process.
2. It takes an optional `--write` flag and an optional `--number` flag.
3. If the given directory does not exist, it prints `No such directory: <path>` and stops without doing anything else.
4. It processes every file ending in `.md` directly inside that directory. It does not descend into subdirectories.
5. Every `mdformat` call it makes passes `extensions={"frontmatter"}`. Installing the plugin is not enough; the Python API ignores installed plugins unless you name them.
6. In its default mode it changes nothing on disk. For each file it prints either `WOULD CHANGE: <filename>` or `OK: <filename>`.
7. When `--number` is supplied, ordered-list renumbering is applied — and it must affect both the comparison and anything written.
8. When `--write` is supplied, it first reads the environment variable `MD_BACKUP_DIR`. If that variable is unset or empty, it prints `MD_BACKUP_DIR is not set; refusing to write.` and stops without modifying any file. If the variable names a directory that does not exist, it prints `Backup directory does not exist: <path>` and stops without modifying any file.
9. In `--write` mode, every file that needs changes is copied into the backup directory _before_ it is rewritten, and is reported as `FORMATTED: <filename>`. Files that need no changes are left alone and reported as `OK: <filename>`.
10. It ends with a summary line: `<n> of <total> files would change.` in default mode, or `<n> of <total> files formatted.` in `--write` mode.

### Part B — prove the `extensions` argument matters

Leave `mdformat-frontmatter` installed for this part; it is the argument you are testing, not the install.

Temporarily delete `extensions={"frontmatter"}` from every `mdformat` call in `mdfix.py` and change nothing else. Run the default mode against `docs` again and record what changes about the report. Then run `--write` and inspect `docs/release-notes.md` to see exactly what happened to the front matter. Restore the file from your backup directory and put the argument back.

Now do the other experiment. With the argument restored, run `pip uninstall -y mdformat-frontmatter` and run the script once more. It should fail on the first file rather than mangle anything, because naming an extension requires it. Reinstall the plugin.

The contrast between those two runs is the lesson. Same missing capability, two completely different outcomes: silent corruption spread across a directory, or one crash before any file is touched. Naming your extensions explicitly is what buys you the second one.

### Expected output

The three per-file lines may appear in any order — directory iteration order is not guaranteed. The summary line always comes last.

Default run, with `extensions={"frontmatter"}` in place:

```
$ python mdfix.py docs
OK: clean.md
WOULD CHANGE: getting-started.md
OK: release-notes.md
1 of 3 files would change.
```

With renumbering requested:

```
$ python mdfix.py docs --number
OK: clean.md
WOULD CHANGE: getting-started.md
WOULD CHANGE: release-notes.md
2 of 3 files would change.
```

Refusing to write without a backup destination:

```
$ python mdfix.py docs --write
MD_BACKUP_DIR is not set; refusing to write.
```

Writing, with the destination set:

```
$ MD_BACKUP_DIR=backups python mdfix.py docs --write
OK: clean.md
FORMATTED: getting-started.md
OK: release-notes.md
1 of 3 files formatted.
```

Immediately re-running the default mode — this is your idempotence check:

```
$ python mdfix.py docs
OK: clean.md
OK: getting-started.md
OK: release-notes.md
0 of 3 files would change.
```

`docs/getting-started.md` now reads:

```markdown
# Getting started

- Create the virtual environment.
- Activate it.
- Install the __required__ packages.

See the _release notes_ for changes.
```

The heading and the bullet markers changed; the emphasis markers did not. If you expected `__required__` to come back as `**required**`, that expectation is the thing to correct.

`backups/getting-started.md` still holds the original.

Part B, with `extensions={"frontmatter"}` removed from the calls:

```
$ python mdfix.py docs
OK: clean.md
OK: getting-started.md
WOULD CHANGE: release-notes.md
1 of 3 files would change.
```

A file that was correct thirty seconds ago is now scheduled for rewriting, and the only thing that changed was one keyword argument. The plugin is still installed. Write down what `release-notes.md` looks like after you let that write happen. That output is the reason this lesson exists.

> [!warning] GitBook syntax has no plugin
> GitBook's Markdown includes blocks that no standard plugin understands — `{% hint %}`, `{% tabs %}`, and similar.
> To `mdformat`, those are ordinary paragraph text with no special meaning, and any structure around them is fair game for rewriting.
> Before pointing this tooling at a Git-synced docs repository, run it against a copy of a single page and diff the result.
