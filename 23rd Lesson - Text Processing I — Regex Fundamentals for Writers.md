# Lesson 23: Text Processing I — Regex Fundamentals for Writers

## Terminology and Theory

**Regular expression (regex):** A pattern language for searching and manipulating text. Instead of looking for a fixed string like `"TODO"`, a regex lets you describe a _shape_ of text — "a word followed by a colon," "any line that starts with `#`," "a URL inside parentheses." You write one pattern and Python checks every part of the string for a match.

**Pattern:** The regex string you pass to `re` functions. In Python, you almost always write patterns as **raw strings** (see below).

**Raw string:** A string literal prefixed with `r`, like `r"\d+"`. In a **plain string** (Lesson 4), Python processes backslash sequences before the string is used anywhere — `"\n"` becomes a newline character, `"\t"` becomes a tab, and `"\d"` either becomes an unrecognized escape (triggering a deprecation warning) or silently mangles the text. In a **raw string**, Python leaves every backslash alone — `r"\d"` stays as the literal two characters `\` and `d`, which is exactly what the regex engine expects to receive. An **f-string** (Lesson 6) processes `{expressions}` inside the string to embed values, but it also processes backslash escapes the same way plain strings do. You _can_ combine the two prefixes as `rf"..."` to get both features, but for regex patterns you almost never need embedded expressions, so plain `r"..."` is the standard choice.

|String type|Prefix|`\d` becomes|Typical use|
|---|---|---|---|
|Plain string|`"..."`|Interpreted by Python (mangled)|General text|
|Raw string|`r"..."`|Left as literal `\d`|Regex patterns|
|f-string|`f"..."`|Interpreted by Python (mangled)|Formatted output|
|Raw f-string|`rf"..."`|Left as literal `\d`|Rare — regex with embedded values|

**Match object:** What `re.search()` returns when it finds something. A match object holds the matched text and positional information. If nothing matches, `re.search()` returns `None` — which is why you'll almost always see a truthiness check (Lesson 14) before using the result.

**`re.search(pattern, string)`:** Scans the string left to right and returns a **match object** for the _first_ occurrence of the pattern, or **`None`** if there's no match. It does not return a string, a position number, or a list — it returns a match object, which is a special container you then query for details. Use `.group()` or `.group(0)` on the match object to get the full matched text as a string. Use `.group(1)`, `.group(2)`, etc. to get the contents of captured groups (see **Groups** below).

**`re.findall(pattern, string)`:** Returns a list — not a match object, not a set, not positions. The _contents_ of that list depend on whether your pattern contains groups:

- **No groups in the pattern:** Each list element is a string containing the full text of a match. For example, `re.findall(r"\d+", "a1 b22")` returns `["1", "22"]`.
- **One group in the pattern:** Each list element is a string containing only what the _group_ captured — not the full match. For example, `re.findall(r"issue #(\d+)", "issue #5 and issue #12")` returns `["5", "12"]`, not `["issue #5", "issue #12"]`.
- **Multiple groups in the pattern:** Each list element is a **tuple** of strings, one per group. Each tuple corresponds to one match of the entire regex expression, where the first item in the tuple is the contents of the first group in the match, the second item in the tuple is the contents of the second group of the match, and so forth. For example, `re.findall(r"(\w+)=(\d+)", "x=1 y=2")` returns `[("x", "1"), ("y", "2")]`.

This distinction is critical — the same function returns different shapes of data depending on the pattern you give it.

**`re.finditer(pattern, string)`:** Returns an **iterator** of **match objects** — one match object per occurrence of the pattern in the string. Unlike `findall`, which gives you strings (or tuples of strings) in a list, `finditer` gives you full match objects, so you can call `.group()`, `.start()`, `.end()`, and `.span()` on each one. And unlike `findall`, which builds the entire list in memory at once, `finditer` produces match objects lazily — one at a time as you loop. If nothing matches, the iterator simply produces zero items (your `for` loop executes zero iterations).

**`findall` vs. `finditer` — when to use which:** Use `findall` when you only need the matched text (or captured group text) and want a simple list you can check `len()` on, index into, or pass to `", ".join()`. Use `finditer` when you need **positional information** — where each match starts and ends in the string — or when you need multiple pieces of information from the match object per occurrence (e.g., the full match _and_ a captured group). A common sign you need `finditer` is any time you'd otherwise call `findall` and then separately try to figure out _where_ each match occurred.

**`re.sub(pattern, replacement, string)`:** Returns a new string with every match of the pattern replaced by the replacement text. The original string is unchanged — just like `str.replace()` from Lesson 5, `re.sub()` returns a new string.

**Anchors:** Symbols that match a _position_ rather than a character.

- `^` — matches the start of the string.
- `$` — matches the end of the string.

**Character classes:** Shorthand for "any single character from this set."

- `\d` — any digit (`0`–`9`).
- `\w` — any "word character" (letters, digits, underscore).
- `\s` — any whitespace (space, tab, newline).
- `.` (dot) — any single character _except_ a newline.
- `[abc]` — any one of `a`, `b`, or `c`. You define your own set inside brackets.
- `[^abc]` — any character _not_ in the set.

**Quantifiers:** Control how many times a character or class can repeat.

- `+` — one or more.
- `*` — zero or more.
- `?` — zero or one (makes something optional).

**Groups:** Parentheses `()` in a pattern do two things: they group part of the pattern together, and they **capture** the matched text so you can extract it. Groups are numbered starting at **1**, counting from left to right by opening parenthesis. On a match object:

- `.group(0)` returns the **entire match** — everything the full pattern matched. Calling `.group()` with no argument does the same thing.
- `.group(1)` returns the text captured by the **first** parenthesized group.
- `.group(2)` returns the text captured by the **second** parenthesized group, and so on.

In other words, group 0 is always the full match and is not a "captured group" — the captured groups start at 1.

**Passing a function as an argument:** In Python, a function name without parentheses — like `my_func` instead of `my_func()` — is a reference to the function itself rather than a call to it. You can pass that reference to another function as an argument, and the receiving function will call it internally at the right moment. This is a broadly useful Python concept, and this lesson uses it in a specific way: `re.sub()` accepts either a replacement _string_ or a replacement _function_. When you pass a function, `re.sub()` calls that function once per match it finds, passes the match object as the argument, and uses the function's return value as the replacement text. You don't call the function yourself — `re.sub()` does.

**Iterator:** An object that produces items one at a time when you loop over it with a `for` loop. You've already been working with iterators without knowing it — when you write `for item in some_list`, the list produces items one at a time through the iteration protocol. The term becomes visible now because `pathlib` methods like `.iterdir()` return iterator objects rather than lists. The practical difference: you can loop over an iterator, but you can't index into it with `[0]` or check its `len()` the way you can with a list.

**`.iterdir()`:** A method on a `pathlib.Path` object (Lesson 22) that returns an iterator yielding one `Path` object for each item — file or subdirectory — inside the directory. It is the `pathlib` equivalent of "list everything in this folder." Because it returns an iterator, you use it in a `for` loop or wrap it in `sorted()` or `list()` if you need a sorted or indexable sequence.

> [!note] 
> Regex is powerful but also easy to over-use. If a plain string method like `.startswith()`, `.endswith()`, or `.replace()` can do the job, prefer that — it's simpler and easier to maintain. Reach for regex when the pattern is variable or you need to match a _shape_ of text rather than a fixed string.

---

## Syntax Section

### Importing the module

```python
import re
```

You already imported `re` briefly in Lesson 17. From now on you'll use it for real.

### `re.search()` — find the first match

```python
match = re.search(r"pattern", some_string)
if match:
    print(match.group())   # the full matched text (same as .group(0))
    print(match.group(0))  # also the full matched text
    print(match.group(1))  # text captured by the first parenthesized group
```

`re.search()` returns either a **match object** or **`None`**. It never returns a string, an integer, or a list. Because `None` is falsy (Lesson 14), always check with a conditional before calling `.group()`, since calling `.group()` on `None` raises an `AttributeError`. To access the values stored in the match object, use `.group()`.

```python
# Safe pattern — always check before accessing the match:
match = re.search(r"\d+", "no digits here")
if match:
    print(match.group())
else:
    print("No match found")
```

### `re.findall()` — collect every match

`re.findall()` always returns a **list**. What's _inside_ the list depends on the groups in your pattern:

```python
# No groups → list of full-match strings:
re.findall(r"\d+", "a1 b22 c333")
# Returns: ['1', '22', '333']

# One group → list of strings, each being the group's captured text:
re.findall(r"issue #(\d+)", "issue #5 and issue #12")
# Returns: ['5', '12']  — NOT ['issue #5', 'issue #12']

# Multiple groups → list of tuples, each tuple holding the captured groups:
re.findall(r"(\w+)=(\d+)", "x=1 y=2")
# Returns: [('x', '1'), ('y', '2')]
```

If nothing matches, all three cases return an empty list `[]`.

### `re.finditer()` — iterate over every match with full details

`re.finditer()` returns an **iterator of match objects**. Each match object gives you the matched text _and_ its position in the string:

```python
for m in re.finditer(r"\d+", "a1 b22 c333"):
    print(m.group())    # the matched text — same as what findall would give
    print(m.start())    # index where the match begins
    print(m.end())      # index after the match ends (half-open, like a slice)
    print(m.span())     # tuple of (start, end)
```

Because `finditer` returns match objects, groups work the same way they do with `re.search()` — you call `.group(1)`, `.group(2)`, etc.:

```python
for m in re.finditer(r"issue #(\d+)", "issue #5 and issue #12"):
    print(m.group(0))   # 'issue #5', then 'issue #12' — the full match
    print(m.group(1))   # '5', then '12' — just the captured group
    print(m.start())    # 0, then 13 — where each match starts
```

Because the return value is an iterator, it can only be consumed once. If you need to loop over the results more than once, or check `len()`, convert to a list first:

```python
matches = list(re.finditer(r"\d+", "a1 b22 c333"))
print(len(matches))       # 3
print(matches[0].group()) # '1'
```

If nothing matches, the iterator produces zero items.

### `re.sub()` — search and replace with a pattern

```python
new_string = re.sub(r"pattern", "replacement", some_string)
```

Every match gets replaced. The original string is not changed.

### Raw strings

```python
# Without raw string — Python interprets \b as a backspace character:
re.search("\bword\b", text)   # WRONG — silent bug

# With raw string — \b reaches the regex engine as a word boundary:
re.search(r"\bword\b", text)  # CORRECT
```

### Anchors

```python
re.search(r"^Title", line)    # matches only if line starts with "Title"
re.search(r"\.md$", filename) # matches only if filename ends with ".md"
```

### Character classes and quantifiers

```python
re.findall(r"\d+", text)       # all sequences of one or more digits
re.findall(r"[A-Z]\w*", text)  # words that start with a capital letter
re.search(r"\s{2,}", text)     # two or more consecutive whitespace characters
```

`{2,}` is an additional quantifier syntax meaning "two or more." You can also write `{3}` for exactly three, or `{2,5}` for two to five.

### Groups — capturing part of a match

```python
match = re.search(r"issue[- ]?#?(\d+)", text)
if match:
    print(match.group(1))  # just the digit portion
```

With `re.findall()` and a single group, you get a list of the group contents:

```python
re.findall(r"\[(.+?)\]\(.+?\)", markdown_line)
# Captures the link text from Markdown links like [text](url)
```

> [!tip] 
> The `?` after `+` or `*` makes the quantifier **non-greedy** — it matches as _few_ characters as possible instead of as many as possible. This matters when a line has multiple matches, like two Markdown links on the same line. Without `?`, the pattern would try to swallow everything between the first `[` and the last `)`.

### Passing a function as an argument

In Lesson 15, you learned to define functions and call them. Here's a new concept: you can pass a function _itself_ as an argument to another function. The key is to use the function's name **without parentheses** — parentheses mean "call this function right now," while the bare name means "here's a reference to this function, for you to call later."

```python
def shout(match):
    return match.group().upper()

# Passing the function itself — note: no parentheses after 'shout':
print(re.sub(r"todo", shout, "todo: fix bug"))
TODO: fix bug

# Compare — this would be WRONG:
re.sub(r"todo", shout(), "todo: fix bug")
# This calls shout() immediately with no arguments, which crashes.
# You want to pass the function, not call it.
```

When `re.sub()` receives a function as the second argument, the following happens for each match it finds:

1. `re.sub` creates a match object from the match.
2. `re.sub` calls the `shout` function with that match object as the sole argument.
3. `shout` processes the match object and returns a replacement.
4. `re.sub` uses the replacement text to replace the matched text, leaving the rest of the text unaltered.

You write the logic of the replacement function `shout()`, and `re.sub()` handles the calling.

> [!note] 
> The match object isn't a string. To access the matched content as a string, we used `match.group()`.

The following example finds numbers and replaces them with stars of length equal to the number of digits:

```python
def replace_with_stars(match):
    original = match.group()          # get the matched text
    return "*" * len(original)        # replace with same number of stars

re.sub(r"\d+", replace_with_stars, "order 42 and order 108")
# Returns: 'order ** and order ***'
```

### Iterators and `.iterdir()`

An **iterator** is looped over the same way as a list — with a `for` loop:

```python
from pathlib import Path

# .iterdir() returns an iterator of Path objects for each item in the directory:
for item in Path("some_folder").iterdir():
    print(item.name)
```

`.iterdir()` returns items in arbitrary filesystem order. If you need the results sorted, or need to use them more than once, wrap the iterator in `sorted()` or `list()`:

```python
# Sorted alphabetically:
for item in sorted(Path("some_folder").iterdir()):
    print(item.name)

# Converted to a list (so you can index, slice, or check len()):
# Each list item is a path object
all_items = list(Path("some_folder").iterdir())
print(len(all_items))

# The first list item is a path object, so you can access its name
print(all_items[0].name)
```

The items inside the list are still `Path` objects. The `.name` attribute reads the file name of the `all_items[0]` object.

> [!warning] 
> An iterator can only be consumed **once**. If you loop over it and then try to loop over it again, the second loop produces nothing — the iterator is exhausted. If you need to loop more than once, convert to a list first with `list()`.

## Worked Examples

### Example 1: Extracting issue numbers from a changelog file

A changelog file might contain lines like `"Fixed crash on login (issue #42)"` or `"Resolved issue-108: timeout bug"`. You want to pull out just the issue numbers.

```python
import re

changelog_lines = [
    "Fixed crash on login (issue #42)",
    "Updated README formatting",
    "Resolved issue-108: timeout bug",
    "Closed issue #7 and issue #15 in the same PR",
]

for line in changelog_lines:
    numbers = re.findall(r"issue[- ]?#?(\d+)", line)
    if numbers:
        print(f"{line}")
        print(f"  → Issue numbers found: {numbers}")
    else:
        print(f"{line}")
        print(f"  → No issue references")
```

**Output:**

```
Fixed crash on login (issue #42)
  → Issue numbers found: ['42']
Updated README formatting
  → No issue references
Resolved issue-108: timeout bug
  → Issue numbers found: ['108']
Closed issue #7 and issue #15 in the same PR
  → Issue numbers found: ['7', '15']
```

**What's happening:**

- The pattern `r"issue[- ]?#?(\d+)"` matches the literal text `issue`, then optionally a hyphen or space (`[- ]?`), then optionally a `#` sign (`#?`), then one or more digits captured in a group (`(\d+)`).
- `re.findall()` returns a list of the captured group contents — just the digit strings.
- When `numbers` is an empty list, the truthiness check (Lesson 14) treats it as falsy.

### Example 2: Using `finditer` to locate issue references with positions

Example 1 used `findall` to extract issue numbers as a list of strings. But suppose you also need to know _where_ each reference appears in the text — for instance, to report character offsets in an audit log. `findall` cannot tell you that. `finditer` can, because it returns match objects instead of strings.

```python
import re

changelog_lines = [
    "Fixed crash on login (issue #42)",
    "Updated README formatting",
    "Resolved issue-108: timeout bug",
    "Closed issue #7 and issue #15 in the same PR",
]

pattern = r"issue[- ]?#?(\d+)"

for line in changelog_lines:
    matches = list(re.finditer(pattern, line))
    if matches:
        print(f"{line}")
        for m in matches:
            number = m.group(1)
            start, end = m.span()
            print(f"  → Issue {number} — full match: '{m.group()}' at positions {start}–{end}")
    else:
        print(f"{line}")
        print(f"  → No issue references")
```

**Output:**

```
Fixed crash on login (issue #42)
  → Issue 42 — full match: 'issue #42' at positions 22–31
Updated README formatting
  → No issue references
Resolved issue-108: timeout bug
  → Issue 108 — full match: 'issue-108' at positions 9–18
Closed issue #7 and issue #15 in the same PR
  → Issue 7 — full match: 'issue #7' at positions 7–15
  → Issue 15 — full match: 'issue #15' at positions 20–29
```

**What's happening:**

- The pattern is the same as Example 1. The only change is using `re.finditer()` instead of `re.findall()`.
- `re.finditer()` returns an iterator of match objects. Because we need to check whether there are any matches (with `if matches`) before looping, we convert the iterator to a list with `list()` first. This lets us use the truthiness check and then loop over the list afterward without exhaustion issues.
- Each match object `m` gives us `.group()` (the full match, e.g., `"issue #42"`), `.group(1)` (the captured group, e.g., `"42"`), and `.span()` (the start and end positions as a tuple).
- `.span()` returns half-open positions: `start` is the index of the first character of the match, and `end` is the index _after_ the last character — the same convention Python uses for slicing. `line[start:end]` would give you back the full matched text.

> [!tip] 
> If you only need the matched text and don't care about positions, use `findall` — it's simpler and gives you a ready-made list. If you need to know _where_ matches are, or you need access to both the full match and captured groups from the same occurrence, use `finditer`.

### Example 3: Using a function as a replacement in `re.sub()`

Before tackling a realistic use case, here's a small example that shows the mechanics clearly. The goal: replace every sequence of digits in a string with the word-length of that sequence (e.g., `"42"` is 2 digits long, so replace it with `"2"`).

```python
import re

def digit_length(match):
    matched_text = match.group()
    return str(len(matched_text))

text = "order 42 has 7 items and code 10053"
result = re.sub(r"\d+", digit_length, text)
print(result)
```

**Output:**

```
order 2 has 1 items and code 5
```

**What's happening, step by step:**

1. `re.sub(r"\d+", digit_length, text)` — notice that `digit_length` has **no parentheses**. You are not calling `digit_length` here. You are passing the function itself to `re.sub()`, saying "here's a function I want you to use."
    
2. `re.sub()` scans `text` from left to right. Each time it finds a match for `\d+`, it creates a match object from that match.
    
3. `re.sub()` then calls `digit_length(match)` — it passes the match object as the one argument. You didn't write this call. `re.sub()` wrote it internally, once per match.
    
4. Inside `digit_length`, `match.group()` returns the full matched text as a string (e.g., `"42"`). `len("42")` is `2`. `str(2)` converts that back to the string `"2"`, which the function returns.
    
5. `re.sub()` takes the return value `"2"` and uses it as the replacement for that match. Then it moves on to the next match and repeats steps 2–4.
    

The flow is: **you define the logic → you pass the function to `re.sub()` → `re.sub()` calls your function once per match → your function receives the match object and returns a string → `re.sub()` uses that string as the replacement.**

### Example 4: Replacing placeholder tokens in a template

Suppose you have a template string where placeholders look like `{{NAME}}` and you want to replace them with values from a dictionary.

```python
import re

template = "Hello {{FIRST_NAME}}, your role is {{ROLE}}. Welcome!"

replacements = {
    "FIRST_NAME": "Josh",
    "ROLE": "technical writer",
}

def replace_token(match):
    key = match.group(1)
    return replacements.get(key, match.group(0))

result = re.sub(r"\{\{(\w+)\}\}", replace_token, template)
print(result)
```

**Output:**

```
Hello Josh, your role is technical writer. Welcome!
```

**What's happening:**

This example builds on the mechanic from Example 3. Here's how to read it:

**The pattern:** `r"\{\{(\w+)\}\}"` matches literal double curly braces around one or more word characters. The curly braces are escaped with backslashes because `{` and `}` have special meaning in regex (quantifier syntax). The `(\w+)` group captures the token name — the text between the braces. So when the pattern matches `{{FIRST_NAME}}`, group 0 (the full match) is `"{{FIRST_NAME}}"` and group 1 (the captured group) is `"FIRST_NAME"`.

**The function:** `replace_token` is defined to accept one argument: `match`. You never call this function yourself. `re.sub()` calls it once for each match it finds in `template`. Here's what happens on the first match:

1. `re.sub()` finds `{{FIRST_NAME}}` in the template string and creates a match object.
2. `re.sub()` calls `replace_token(match)`, passing in that match object.
3. Inside the function, `match.group(1)` returns `"FIRST_NAME"` — the captured group, not the full match with curly braces.
4. `replacements.get("FIRST_NAME", match.group(0))` looks up `"FIRST_NAME"` in the `replacements` dictionary. It finds `"Josh"`, so it returns `"Josh"`.
5. The function returns `"Josh"`, and `re.sub()` replaces `{{FIRST_NAME}}` with `"Josh"` in the output string.

Then `re.sub()` finds the next match (`{{ROLE}}`), repeats the process, and replaces it with `"technical writer"`.

**The safety net:** `replacements.get(key, match.group(0))` uses `.get()` with a default (Lesson 11). If the template contained a placeholder like `{{UNKNOWN}}` that isn't in the dictionary, `.get()` would return `match.group(0)` — the original text including the curly braces — leaving the placeholder untouched instead of crashing with a `KeyError`.

### Example 5: Listing directory contents with `.iterdir()`

This example uses `.iterdir()` without regex to show how the method works on its own, before Example 6 combines both concepts.

Suppose you have a folder of documentation files and you want to print a summary: how many files it contains, which are Markdown files, and which are something else.

```python
from pathlib import Path

docs_dir = Path("sample_docs")

if not docs_dir.exists():
    print(f"Directory not found: {docs_dir}")
else:
    md_count = 0
    other_count = 0

    for item in sorted(docs_dir.iterdir()):
        if item.is_file():
            if item.name.endswith(".md"):
                md_count += 1
                print(f"  [MD]    {item.name}")
            else:
                other_count += 1
                print(f"  [OTHER] {item.name}")

    total = md_count + other_count
    print(f"---\nTotal files: {total} ({md_count} Markdown, {other_count} other)")
```

**What's happening:**

- `docs_dir.iterdir()` returns an **iterator** — an object that produces one `Path` object per item in the directory, each time the `for` loop asks for the next item. It does not return a list, and it does not return strings.
- `sorted(...)` wraps the iterator and collects all the items into a sorted list before the loop begins. Without `sorted()`, the items would come back in whatever order the filesystem stores them, which is often not alphabetical.
- Each `item` in the loop is a `Path` object, not a plain string. That's why you use `item.name` (a `Path` attribute from Lesson 22) to get the filename as a string, and `item.is_file()` to confirm it's a file rather than a subdirectory.
- The `.endswith(".md")` check (Lesson 5) works here because `item.name` is a regular string. This is a case where a plain string method is simpler than regex.

### Example 6: Validating that filenames follow a naming convention

Imagine a docs repo where every file should be named like `YYYY-MM-DD-slug.md` — a date prefix followed by a hyphenated slug. You want to scan a directory and flag any files that don't match.

```python
import re
from pathlib import Path

docs_dir = Path("sample_docs")

naming_pattern = r"^\d{4}-\d{2}-\d{2}-.+\.md$"

if docs_dir.exists():
    for item in sorted(docs_dir.iterdir()):
        if item.is_file():
            name = item.name
            if re.search(naming_pattern, name):
                print(f"  PASS: {name}")
            else:
                print(f"  FAIL: {name}")
else:
    print(f"Directory not found: {docs_dir}")
```

**What's happening:**

- `^\d{4}-\d{2}-\d{2}-.+\.md$` anchors the pattern to the full filename. It expects exactly four digits, a hyphen, two digits, a hyphen, two digits, a hyphen, then one or more of any character, ending with `.md`.
- `\.` escapes the dot so it matches a literal period rather than "any character."
- The `^` and `$` anchors ensure the _entire_ filename must match the pattern — not just a substring.
- `pathlib` (Lesson 22) handles the directory iteration, and the conditional check (Lesson 10) branches on the match result.

---

## Quick Reference

```bash
# Import the regex module
$ python3 -c "import re; print(type(re))"
<class 'module'>

# re.search() — returns a match object (not a string, not a position)
$ python3 -c "import re; m = re.search(r'\d+', 'issue 42'); print(m); print(type(m))"
<re.Match object; span=(6, 8), match='42'>
<class 're.Match'>

# .group() on a match object — extracts the matched text as a string
# .group() and .group(0) both return the full match.
# No parenthesized groups are needed — group 0 is always the full match.
$ python3 -c "import re; m = re.search(r'\d+', 'issue 42'); print(m.group()); print(m.group(0))"
42
42

# re.findall() — return list of all matches
$ python3 -c "import re; print(re.findall(r'\d+', 'issues 42, 108, and 7'))"
['42', '108', '7']

# re.finditer() — return iterator of match objects (not strings)
$ python3 -c "
import re
for m in re.finditer(r'\d+', 'issues 42, 108, and 7'):
    print(m.group(), m.start())
"
42 7
108 11
7 20

# re.finditer() with .span() — returns (start, end) tuple
$ python3 -c "
import re
m = list(re.finditer(r'\d+', 'item 42'))[0]
print(m.span())
"
(5, 7)

# re.sub() — replace all matches
$ python3 -c "import re; print(re.sub(r'TODO', 'DONE', 'TODO: fix bug, TODO: update docs'))"
DONE: fix bug, DONE: update docs

# Anchors — ^ for start, $ for end
$ python3 -c "import re; print(bool(re.search(r'^#', '# Heading')))"
True

# Character class with quantifier
$ python3 -c "import re; print(re.findall(r'[A-Z]\w+', 'Hello World foo Bar'))"
['Hello', 'World', 'Bar']

# Group capture — .group(1) for first group
$ python3 -c "import re; m = re.search(r'name: (\w+)', 'name: Josh'); print(m.group(1))"
Josh

# Findall with a group returns group contents only
$ python3 -c "import re; print(re.findall(r'issue #(\d+)', 'issue #5 and issue #12'))"
['5', '12']

# Non-greedy quantifier with ?
$ python3 -c "import re; print(re.findall(r'\[(.+?)\]', '[one] and [two]'))"
['one', 'two']

# re.sub with no match — returns original string unchanged
$ python3 -c "import re; print(re.sub(r'XYZ', 'ABC', 'hello world'))"
hello world

# re.sub with a function — function receives match object, returns replacement string
$ python3 -c "
import re
def stars(m): return '*' * len(m.group())
print(re.sub(r'\d+', stars, 'order 42 code 108'))
"
order ** code ***

# .iterdir() — returns an iterator of Path objects for items in a directory
$ python3 -c "
from pathlib import Path
for p in sorted(Path('.').iterdir()):
    if p.is_file(): print(p.name)
"
(no fixed output — depends on your current directory)
```

---

## Exercises

### Exercise: Doc-Link Auditor

You are auditing a set of documentation lines. Each line may contain one or more Markdown-style links in the format `[link text](URL)`. Your job is to write a script that:

1. Reads the following lines from a list (do not read from a file — just define them in your script):

```
"See the [installation guide](https://example.com/install) for details."
"No links on this line."
"Check [API reference](https://api.example.com/v2) and [changelog](https://example.com/changes)."
"Visit [docs](https://example.com/docs)."
"    "
"Refer to issue #203 and issue #48 for background."
```

2. For each line, extract all Markdown link texts (the part inside `[...]`) using a regex.
    
3. Also extract all issue numbers from lines that contain references in the format `issue #` followed by digits.
    
4. Skip any line that is blank or contains only whitespace (use a truthiness/defensive check — don't use regex for this part).
    
5. For lines that contain links, print the line number and the extracted link texts as a comma-separated list. For lines that contain issue references, print the line number and the issue numbers. For lines that have neither, print the line number and `"No links or issues found"`.
    
6. After processing all lines, print a summary line showing the total count of links found and the total count of issue references found across all lines.
    

Write the entire script as a function called `audit_links(lines)` that accepts the list of line strings as a parameter and returns `None` (it only prints). Call the function at the bottom of your script.

Use `enumerate()` (Lesson 9) to track line numbers starting from 1.

**Expected output:**

```
Line 1: Links: installation guide
Line 2: No links or issues found
Line 3: Links: API reference, changelog
Line 4: Links: docs
Line 5: [skipped blank line]
Line 6: Issues: 203, 48
---
Total links found: 4
Total issue references found: 2
```

---

## Audit

|Requirement|Introduced in|
|---|---|
|`import re`|Lesson 17 (introduced), Lesson 23 (used in depth)|
|`re.findall()` with groups|Lesson 23|
|Raw strings (`r"..."`)|Lesson 23|
|`\d+`, `+?`, `[...]`, groups `()`|Lesson 23|
|Defining a function, parameters, `return None`|Lesson 15|
|`for` loop with `enumerate()`|Lesson 9|
|`if/elif/else` conditionals|Lesson 10|
|Truthiness check on stripped string (`.strip()`)|Lesson 5 (`.strip()`), Lesson 14 (truthiness)|
|f-strings for formatted output|Lesson 6|
|`", ".join()` on a list|Lesson 5 (`.join()`)|
|`len()` for counting|Lesson 7|
|List creation, `.append()` or `+=` for accumulation|Lesson 7|
|Variable accumulation (counters)|Lesson 2 (variables), Lesson 9 (loop accumulation)|

**Additional concepts taught in this lesson (used in worked examples, not required by the exercise):**

|Concept|Used in|
|---|---|
|`re.finditer()`, `.span()`, `.start()`, `.end()`|Example 2|
|Passing a function as an argument to `re.sub()`|Examples 3, 4|
|`.iterdir()` and iterators|Examples 5, 6|
|`sorted()` wrapping an iterator|Examples 5, 6|
|`.is_file()` on a `Path` object|Examples 5, 6|

All operations required by the exercise were introduced in the current lesson or in prior lessons. No future-lesson concepts are needed.