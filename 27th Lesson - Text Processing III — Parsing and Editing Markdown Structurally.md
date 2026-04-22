# Lesson 27: Text Processing III — Parsing and Editing Markdown Structurally

## Terminology and Theory

Up to this point, every time you've worked with Markdown files, you've treated them as plain text — running regex substitutions, matching line patterns, reading and writing strings. That works surprisingly well for many tasks, but Markdown has _structure_: headings form a hierarchy, links have distinct text and URL components, code fences create boundaries that change how content inside them should be interpreted, and front matter blocks carry metadata about the document itself.

This lesson teaches you to recognize and work with that structure, first using the regex and string tools you already know, and then using a dedicated parsing library for the cases where regex falls short.

**Structural elements of Markdown you'll work with in this lesson:**

- **Headings**: Lines beginning with one or more `#` characters followed by a space. The number of `#` characters indicates the heading level (`#` = level 1, `##` = level 2, etc.).
- **Inline links**: Text in the pattern `[link text](URL)`. The square brackets hold the visible text; the parentheses hold the destination.
- **Code fences**: Blocks delimited by triple backticks (` ``` `). Everything between an opening fence and a closing fence is literal code — Markdown syntax inside a code fence is _not_ Markdown. This is where naive regex approaches break down.
- **Front matter**: A block of metadata at the very top of a file, delimited by `---` on its own line. Front matter typically uses YAML syntax — key-value pairs like `title: My Document`. Many documentation systems (MkDocs, Docusaurus, Jekyll, Hugo) use front matter to control page titles, sidebar positions, tags, and other metadata.

**Why regex breaks down:**

Regex operates on text one pattern at a time. It has no concept of "I'm currently inside a code fence, so this `# heading` is not really a heading." Consider this Markdown:

````markdown
# Real Heading

Here is a code example:

```bash
# This is a comment in a script, not a heading
echo "hello"
```

## Another Real Heading
````

A regex like `^#{1,6}\s+(.+)$` applied line-by-line would match _three_ lines: the two real headings and the Bash comment inside the code fence. You'd get a false positive. For simple, well-controlled files where you know there are no code fences, regex is fine. For arbitrary Markdown files (SDK documentation, READMEs, knowledge bases), you need something that understands structure.

**Parsing libraries:**

A Markdown parsing library reads the entire document and produces a list of _tokens_ — structured objects that describe each element and its role. A token for a heading knows it's a heading, knows its level, and knows its text content. A token for a code fence knows everything inside it is code, not Markdown. This is called _structural awareness_, and it's what regex lacks.

This lesson uses `mistune`, a lightweight, pure-Python Markdown parser. You install it with pip:

```bash
pip install mistune
```

> [!note] 
> Lesson 32 covers `pip` and package management in depth. For now, the command above is all you need — it downloads and installs the `mistune` library so you can import it in your scripts.

## Syntax Section

### Regex patterns for common Markdown elements

These patterns work reliably when you can guarantee that the content isn't inside a code fence.

**Headings:**

```python
import re

# Match a Markdown heading line and capture the level and text
heading_pattern = r"^(#{1,6})\s+(.+)$"
```

The `^` and `$` anchors pin the match to an entire line (when used with `re.MULTILINE` or when matching individual lines). Group 1 captures the `#` characters (whose length is the heading level). Group 2 captures the heading text.

**How `re.findall` behaves when your pattern has groups:**

In Lesson 24 you used `re.findall` with patterns that had no capture groups, and it returned a list of strings — each string being the full match. When your pattern contains _capture groups_ (parenthesized sections), `re.findall` changes behavior: instead of returning the full match, it returns only the captured portions. If the pattern has one group, you get a list of strings (one per match, containing only what that group captured). If the pattern has _two or more_ groups, you get a list of _tuples_, where each tuple contains one string per group:

```python
import re

text = "## Installation\n### Usage"
heading_pattern = r"^(#{1,6})\s+(.+)$"
matches = re.findall(heading_pattern, text, re.MULTILINE)
print(matches)
# [('##', 'Installation'), ('###', 'Usage')]
```

Each tuple has two elements because the pattern has two groups. The first element is whatever group 1 captured (the `#` characters), and the second element is whatever group 2 captured (the heading text). You can unpack these tuples directly in a `for` loop:

```python
for hashes, text in matches:
    level = len(hashes)
    print(f"Level {level}: {text}")
# Level 2: Installation
# Level 3: Usage
```

`hashes` receives the first element of each tuple, `text` receives the second — this is tuple unpacking, which you learned in Lesson 13.

**Inline links:**

```python
# Match [text](url) and capture both parts
link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
```

`[^\]]+` matches one or more characters that are not `]` — this captures the link text. `[^)]+` matches one or more characters that are not `)` — this captures the URL.

**Front matter:**

Front matter is the block between the first `---` and the next `---` at the top of a file. You can extract it with a regex applied to the full file content:

```python
# Match YAML front matter at the start of a file
front_matter_pattern = r"\A---\n(.*?)\n---"
```

`\A` anchors to the absolute start of the string (not just the start of a line). `(.*?)` captures the content between the delimiters non-greedily. You need `re.DOTALL` so that `.` matches newlines.

**Parsing front matter key-value pairs** once extracted:

```python
# Match simple "key: value" lines inside front matter
kv_pattern = r"^(\w[\w\s]*?):\s+(.+)$"
```

This handles single-line values. It does not handle multi-line YAML values or nested structures, but it covers the majority of front matter you'll encounter in documentation repos.

### Using `mistune` for structural parsing

`mistune` can be configured to return a list of tokens instead of rendered HTML. Each token is a dictionary with a `"type"` key that tells you what kind of element it is.

**Getting tokens from a Markdown string:**

```python
import mistune

md = mistune.create_markdown(renderer=None)
tokens = md(text)
```

When you pass `renderer=None`, `mistune` returns the raw token list instead of HTML. `tokens` is a list of dictionaries. Every dictionary has at least a `"type"` key. Some token types also have `"children"` (a list of nested token dictionaries), `"attrs"` (a dictionary of metadata like heading level or link URL), and `"raw"` (a string containing the literal text content).

#### Token structure in the abstract

Here is the general shape of a token, shown in YAML for readability. Not every key appears on every token — which keys are present depends on the `"type"`:

```yaml
- type: "<element type>"        # Always present. See the table below for types.
  attrs:                         # Present on headings, links, images, and block_code. A dict of metadata.
    level: <int>                 # On headings only. The heading level (1–6).
    url: "<string>"              # On links and images. The destination URL or file path.
    info: "<string>"             # On block_code only. The language from the opening fence (e.g., "python").
  children:                      # Present on block-level and some inline tokens. A list of nested tokens.
    - type: "<child type>"
      raw: "<string>"            # Present on leaf nodes like "text" and "codespan". The literal text content.
      children: [...]            # Children can themselves have children (e.g., a link inside a paragraph).
  raw: "<string>"                # Present on "block_code" and "text" tokens. The literal content.
```

**Token types you'll encounter:**

|Type|What it represents|Has `children`?|Has `raw`?|Has `attrs`?|
|---|---|---|---|---|
|`"heading"`|A heading (`#`, `##`, etc.)|Yes — contains `"text"` children|No|Yes — `level`|
|`"paragraph"`|A block of text|Yes — contains `"text"`, `"link"`, `"image"`, `"codespan"` children|No|No|
|`"block_code"`|A fenced code block|No|Yes — the code content|Yes — `info` (language)|
|`"block_quote"`|A blockquote (`>` lines)|Yes — contains `"paragraph"` children|No|No|
|`"text"`|A run of plain text (leaf node)|No|Yes — the text content|No|
|`"link"`|An inline link (child of paragraph/heading)|Yes — contains `"text"` children (the link text)|No|Yes — `url`|
|`"image"`|An image (child of paragraph)|Yes — contains `"text"` children (the alt text)|No|Yes — `url`|
|`"codespan"`|Inline code (child of paragraph/heading)|No|Yes — the code text|No|
|`"blank_line"`|Whitespace between elements|No|No|No|

The key insight: **block-level tokens** (headings, paragraphs, blockquotes) contain their text indirectly, inside `"children"`. You have to walk into `"children"` to reach the `"text"` tokens that hold the actual words. **Code blocks** are different — they store their content directly in `"raw"` at the top level, with no children. **`"blank_line"` tokens** appear between elements and carry no content — your code will skip them automatically because you'll always be checking for specific types like `"heading"` or `"paragraph"`.

#### The complete token list for a realistic document

Here is a Markdown document that contains every element type from the table above — multiple headings, multiple paragraphs, links, inline code, a code block, an image, a blockquote (Obsidian callout), and an Obsidian embed:

````markdown
# Installation Guide

The SDK requires Python 3.10 or later. Download it from [python.org](https://python.org).

## Quick Start

Import the `Client` class and create an instance:

```python
from example_sdk import Client
client = Client()
```

See the [API reference](https://docs.example.com/api) for the full method list.

## Configuration

![Settings panel](./images/settings.png)

> [!tip]
> Set your token before running any scripts.

For a working example, see ![[quickstart_example.md]].
````

Calling `md(text)` on this document returns a list of 19 tokens. The `"blank_line"` tokens are omitted below for readability — in practice, there is one between every block-level element:

```yaml
# Token 0 — heading (level 1)
- type: "heading"
  attrs:
    level: 1
  style: "atx"
  children:
    - type: "text"
      raw: "Installation Guide"

# Token 2 — paragraph containing a link
- type: "paragraph"
  children:
    - type: "text"
      raw: "The SDK requires Python 3.10 or later. Download it from "
    - type: "link"
      children:
        - type: "text"
          raw: "python.org"
      attrs:
        url: "https://python.org"
    - type: "text"
      raw: "."

# Token 4 — heading (level 2)
- type: "heading"
  attrs:
    level: 2
  style: "atx"
  children:
    - type: "text"
      raw: "Quick Start"

# Token 6 — paragraph containing inline code
- type: "paragraph"
  children:
    - type: "text"
      raw: "Import the "
    - type: "codespan"
      raw: "Client"
    - type: "text"
      raw: " class and create an instance:"

# Token 8 — fenced code block
- type: "block_code"
  raw: "from example_sdk import Client\nclient = Client()\n"
  style: "fenced"
  marker: "```"
  attrs:
    info: "python"

# Token 10 — paragraph containing a link
- type: "paragraph"
  children:
    - type: "text"
      raw: "See the "
    - type: "link"
      children:
        - type: "text"
          raw: "API reference"
      attrs:
        url: "https://docs.example.com/api"
    - type: "text"
      raw: " for the full method list."

# Token 12 — heading (level 2)
- type: "heading"
  attrs:
    level: 2
  style: "atx"
  children:
    - type: "text"
      raw: "Configuration"

# Token 14 — paragraph containing an image
- type: "paragraph"
  children:
    - type: "image"
      children:
        - type: "text"
          raw: "Settings panel"
      attrs:
        url: "./images/settings.png"

# Token 16 — blockquote (Obsidian callout)
- type: "block_quote"
  children:
    - type: "paragraph"
      children:
        - type: "text"
          raw: "["
        - type: "text"
          raw: "!tip]"
        - type: "softbreak"
        - type: "text"
          raw: "Set your token before running any scripts."

# Token 18 — paragraph containing an Obsidian embed
- type: "paragraph"
  children:
    - type: "text"
      raw: "For a working example, see "
    - type: "text"
      raw: "!"
    - type: "text"
      raw: "["
    - type: "text"
      raw: "["
    - type: "text"
      raw: "quickstart_example.md]]."
```

Study this list carefully — several things are worth noticing:

**The list is flat at the top level.** `tokens` is not a tree. It's a flat list of block-level elements in document order: heading, paragraph, heading, paragraph, code block, paragraph, heading, paragraph, blockquote, paragraph (with `blank_line` tokens in between). You iterate it with a regular `for` loop, the same way you'd iterate a list of strings.

**Children are one level down.** Links, images, inline code, and plain text live inside the `"children"` list of their parent token. A link is always a child of a paragraph or heading — it never appears as a top-level token. To find links, you loop through the top-level tokens, then loop through each token's `"children"`.

**Code blocks are self-contained.** Token 8 has `"raw"` containing the entire code content and no `"children"`. This is why `mistune` doesn't confuse `# comments` inside code with headings — comments are part of a `"block_code"` token, not a `"heading"` token.

**Images have the same shape as links.** Token 14 contains an `"image"` child with `"attrs": {"url": ...}` and `"children"` holding the alt text. The only difference from a link is the `"type"` value.

**`mistune` doesn't understand Obsidian-specific syntax.** Token 16 shows a blockquote, but `mistune` doesn't recognize `[!tip]` as a callout marker — it splits the brackets into separate text nodes. Token 18 shows the Obsidian embed `![[quickstart_example.md]]` fragmented into five text nodes. For these Obsidian-specific patterns, regex on the raw file text is the better tool — `mistune` only understands standard Markdown.

> [!tip] 
> You can always inspect the full token list yourself by adding `import json` and printing `json.dumps(tokens, indent=2)` in your script. This is the fastest way to understand how `mistune` parses any Markdown structure you're unsure about.

#### Finding and processing tokens

Now that you can see the full structure of `tokens`, here is how to extract what you need. Every example below uses a simple `for` loop over the top-level list, checking `token["type"]` to find the tokens you care about.

**Finding all headings:**

```python
for token in tokens:
    if token["type"] == "heading":
        level = token["attrs"]["level"]
        text_parts = [child["raw"] for child in token["children"] if child["type"] == "text"]
        heading_text = "".join(text_parts)
        print(f"Level {level}: {heading_text}")
```

Applied to the example document, this prints:

```
Level 1: Installation Guide
Level 2: Quick Start
Level 2: Configuration
```

The `for` loop visits all 19 tokens, but the `if` check means only the three headings are processed. The rest — paragraphs, blank lines, the code block — are skipped.

**Extracting paragraph text:**

Paragraphs are the most common block-level token, and their `"children"` lists are where the mixed-type structure matters most. A paragraph's children can include `"text"`, `"link"`, `"codespan"`, and `"image"` nodes all interleaved. If you want the plain text content of a paragraph — stripping out the link URLs and image references — collect the `"raw"` value from every `"text"` child:

```python
for token in tokens:
    if token["type"] == "paragraph":
        text_parts = [child["raw"] for child in token["children"] if child["type"] == "text"]
        plain_text = "".join(text_parts)
        print(plain_text)
```

Applied to the example document, this prints:

```
The SDK requires Python 3.10 or later. Download it from .
Import the  class and create an instance:
See the  for the full method list.

For a working example, see ![[quickstart_example.md]].
```

Notice the gaps — the first line has a space before the period where `[python.org](https://python.org)` was, and the second line is missing "Client" where the inline code was. That's because links and codespans are their _own_ child types, not `"text"`. The blank fourth line is the image paragraph — its only child is an `"image"` token, so there are no `"text"` children to collect. If you want the full readable content including link text and inline code, you need to check each child's type and pull the text from the right place:

```python
for token in tokens:
    if token["type"] == "paragraph":
        parts = []
        for child in token["children"]:
            if child["type"] == "text":
                parts.append(child["raw"])
            elif child["type"] == "codespan":
                parts.append(child["raw"])
            elif child["type"] == "link":
                link_text = [c["raw"] for c in child["children"] if c["type"] == "text"]
                parts.append("".join(link_text))
        full_text = "".join(parts)
        print(full_text)
```

Output:

```
The SDK requires Python 3.10 or later. Download it from python.org.
Import the Client class and create an instance:
See the API reference for the full method list.

For a working example, see ![[quickstart_example.md]].
```

Now "python.org", "Client", and "API reference" appear in the output. Which approach you use depends on what you need — the first is simpler and works when you only care about the prose, while the second reconstructs the readable content.

**Finding all links:**

Links are children of paragraphs and headings, so you need a nested loop — the outer loop iterates the top-level tokens, the inner loop iterates each token's `"children"`:

```python
for token in tokens:
    if "children" in token:
        for child in token["children"]:
            if child["type"] == "link":
                url = child["attrs"]["url"]
                link_text_parts = [c["raw"] for c in child["children"] if c["type"] == "text"]
                link_text = "".join(link_text_parts)
                print(f"[{link_text}]({url})")
```

Output:

```
[python.org](https://python.org)
[API reference](https://docs.example.com/api)
```

The outer loop finds every token that has `"children"` (headings, paragraphs, blockquotes). The inner loop checks each child for `"type": "link"`. When it finds one, it reads the URL from `child["attrs"]["url"]` and builds the link text from the link's own `"children"`.

**Finding all images:**

Images work identically to links — same nesting pattern, just a different `"type"`:

```python
for token in tokens:
    if "children" in token:
        for child in token["children"]:
            if child["type"] == "image":
                url = child["attrs"]["url"]
                alt_parts = [c["raw"] for c in child["children"] if c["type"] == "text"]
                alt_text = "".join(alt_parts)
                print(f"Image: {alt_text} -> {url}")
```

Output:

```
Image: Settings panel -> ./images/settings.png
```

**Finding all fenced code blocks:**

Code blocks are top-level tokens with no `"children"`, so you only need the outer loop:

```python
for token in tokens:
    if token["type"] == "block_code":
        language = token["attrs"].get("info", "")
        code = token["raw"]
        print(f"Code block ({language}):")
        print(code)
```

The `.get("info", "")` call is `dict.get()` from Lesson 11 — it returns the value for `"info"` if the key exists, or `""` if it doesn't. A code fence without a language identifier (just ` ``` ` with no `python` or `bash` after it) would have no `"info"` key, so `.get()` prevents a `KeyError`.

Output:

```
Code block (python):
from example_sdk import Client
client = Client()
```

**Finding inline code spans:**

Inline code (backtick-wrapped text like `` `Client` ``) appears as `"codespan"` children inside paragraphs:

```python
for token in tokens:
    if "children" in token:
        for child in token["children"]:
            if child["type"] == "codespan":
                print(f"Inline code: {child['raw']}")
```

Output:

```
Inline code: Client
```

### Ordering results with `sorted()`

When processing multiple files, you'll often want results in a predictable order. Python's built-in `sorted()` function takes any iterable and returns a new list with the elements in sorted order:

```python
names = ["config.md", "install.md", "about.md"]
ordered = sorted(names)
# ordered is ["about.md", "config.md", "install.md"]
```

Strings sort alphabetically. `Path` objects sort the same way. Tuples sort by their first element, then by their second element to break ties — so a list of `(number, name)` tuples will sort numerically if the first element is an integer:

```python
items = [(3, "third"), (1, "first"), (2, "second")]
print(sorted(items))
# [(1, 'first'), (2, 'second'), (3, 'third')]
```

You can also pass a `key=` argument to control what value Python sorts by. The `key=` argument takes a function. Python calls that function on each element and sorts by the return values:

```python
# Sort a list of tuples by the second element
pairs = [("z", 1), ("a", 3), ("m", 2)]
print(sorted(pairs, key=lambda p: p[1]))
# [('z', 1), ('m', 2), ('a', 3)]
```

The `lambda p: p[1]` is a _lambda expression_ — a one-line anonymous function. `lambda p: p[1]` means "given an argument `p`, return `p[1]`." It's equivalent to writing a named function:

```python
def get_second(p):
    return p[1]
```

You'll see `lambda` used almost exclusively as an argument to `sorted()`, `min()`, and `max()`. You don't need to write lambdas from scratch for this curriculum — just recognize the pattern when you see it.

### Numbering items with `enumerate()`

When looping over a list, you sometimes need both the item _and_ its position. `enumerate()` wraps an iterable and yields `(index, item)` pairs:

```python
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# 0: apple
# 1: banana
# 2: cherry
```

By default the index starts at 0. You can change the start value with the `start=` argument:

```python
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
# 1. apple
# 2. banana
# 3. cherry
```

### List comprehensions

A list comprehension is a compact way to build a new list by transforming and/or filtering an existing iterable. Instead of writing a `for` loop with `append`:

```python
result = []
for child in token["children"]:
    if child["type"] == "text":
        result.append(child["raw"])
```

You can write the equivalent in a single expression:

```python
result = [child["raw"] for child in token["children"] if child["type"] == "text"]
```

The structure is `[expression for variable in iterable if condition]`. The `if` clause is optional. Read it left to right: "give me `child["raw"]` for each `child` in the list, but only if the type is `"text"`."

List comprehensions produce the same result as the loop-and-append pattern. Use whichever is clearer for the situation — comprehensions work well for simple transforms; loops are better when the body is complex.

### Using `re.sub()` with a function as the replacement

In Lesson 24 you used `re.sub(pattern, replacement_string, text)` where the replacement was a fixed string. You can also pass a _function_ as the replacement. When you do, Python calls that function for every match, passing it the match object, and uses the function's return value as the replacement text:

```python
import re

def add_hash(match):
    """Add one # to the front of a heading."""
    return "#" + match.group(0)

line = "## Installation"
result = re.sub(r"^#{1,6}", add_hash, line)
print(result)
# ### Installation
```

The function receives a match object (the same kind returned by `re.search()`), so you can call `.group()` on it to inspect what was matched. This pattern is useful whenever the replacement depends on the content of the match — you can't express "add one more `#` to however many were already there" with a static replacement string.

## Worked Examples

### Example 1: Extracting headings with regex (and the code-fence trap)

This example reads a Markdown file, extracts all headings using regex, and prints them. It works correctly for files without code fences.

```python
import re
from pathlib import Path

filepath = Path("example.md")
content = filepath.read_text(encoding="utf-8")

heading_pattern = r"^(#{1,6})\s+(.+)$"
matches = re.findall(heading_pattern, content, re.MULTILINE)

for hashes, text in matches:
    level = len(hashes)
    print(f"Level {level}: {text}")
```

Given this `example.md`:

````markdown
# Project Overview

Some introductory text.

## Installation

Run the following:

```bash
# Install dependencies
pip install requests
```

## Usage

Import the library and call the main function.
````

The output would be:

```
Level 1: Project Overview
Level 2: Installation
Level 1: Install dependencies
Level 2: Usage
```

Notice that the pattern _also_ matche `# Install dependencies`, because regex has no concept of "inside a code block," so any line starting with `#` and a space is a match. For controlled files you authored yourself, this may be acceptable. For arbitrary documentation files, it's a risk.

### Example 2: Extracting headings with `mistune` (code-fence safe)

This example uses `mistune` to parse the same file. Because `mistune` understands the document structure, it only identifies _real_ headings — content inside code fences is recognized as code and ignored.

```python
import mistune
from pathlib import Path

filepath = Path("example.md")
content = filepath.read_text(encoding="utf-8")

md = mistune.create_markdown(renderer=None)
tokens = md(content)

for token in tokens:
    if token["type"] == "heading":
        level = token["attrs"]["level"]
        text_parts = []
        for child in token["children"]:
            if child["type"] == "text":
                text_parts.append(child["raw"])
        heading_text = "".join(text_parts)
        print(f"Level {level}: {heading_text}")
```

Output:

```
Level 1: Project Overview
Level 2: Installation
Level 2: Usage
```

The Bash comment `# Install dependencies` does not appear, because `mistune` recognized it as part of a code block — not a heading.

### Example 3: Extracting front matter fields with regex

This example reads a Markdown file that has YAML front matter at the top and extracts the key-value pairs into a dictionary.

```python
import re
from pathlib import Path

filepath = Path("guide.md")
content = filepath.read_text(encoding="utf-8")

# Extract the front matter block
fm_match = re.search(r"\A---\n(.*?)\n---", content, re.DOTALL)
if fm_match:
    fm_block = fm_match.group(1)

    # Parse key: value pairs
    kv_pattern = r"^(\w[\w\s]*?):\s+(.+)$"
    pairs = re.findall(kv_pattern, fm_block, re.MULTILINE)

    metadata = {}
    for key, value in pairs:
        metadata[key.strip()] = value.strip()

    for key, value in metadata.items():
        print(f"{key}: {value}")
else:
    print("No front matter found.")
```

Given this `guide.md`:

```markdown
---
title: API Authentication Guide
sidebar_position: 3
tags: auth, tokens, security
---

# API Authentication Guide

This guide explains how to authenticate with the API.
```

Output:

```
title: API Authentication Guide
sidebar_position: 3
tags: auth, tokens, security
```

> [!tip] 
> This regex approach handles simple single-line `key: value` pairs, which covers the vast majority of front matter in documentation repos. It does not handle YAML lists or nested objects. For complex YAML, you would use a dedicated YAML parsing library — that is outside the scope of this curriculum.

## Quick Reference

```shellsession
# Match Markdown headings — group 1 is the hashes, group 2 is the text
$ python3 -c "import re; print(re.findall(r'^(#{1,6})\s+(.+)$', '## Setup\n### Details', re.MULTILINE))"
[('##', 'Setup'), ('###', 'Details')]

# Match inline links — group 1 is the link text, group 2 is the URL
$ python3 -c "import re; print(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', 'See [docs](https://example.com) and [help](/faq)'))"
[('docs', 'https://example.com'), ('help', '/faq')]

# Extract front matter from a string that starts with ---
$ python3 -c "import re; s='---\ntitle: Test\n---\n# Hi'; m=re.search(r'\A---\n(.*?)\n---', s, re.DOTALL); print(m.group(1) if m else 'None')"
title: Test

# Parse a front matter block into key-value pairs
$ python3 -c "import re; print(re.findall(r'^(\w[\w\s]*?):\s+(.+)$', 'title: Guide\ntags: api, sdk', re.MULTILINE))"
[('title', 'Guide'), ('tags', 'api, sdk')]

# Install mistune (run once)
$ pip install mistune
(no output on success — pip prints download/install progress)

# Parse Markdown into tokens with mistune (renderer=None returns raw tokens)
$ python3 -c "import mistune; md=mistune.create_markdown(renderer=None); tokens=md('# Hello\nWorld'); print(tokens[0]['type'], tokens[0]['attrs']['level'])"
heading 1

# Get heading text from a mistune token's children (list comprehension)
$ python3 -c "import mistune; md=mistune.create_markdown(renderer=None); t=md('## Setup')[0]; print([c['raw'] for c in t['children'] if c['type']=='text'])"
['Setup']

# Sort a list of strings alphabetically with sorted()
$ python3 -c "print(sorted(['config.md', 'install.md', 'about.md']))"
['about.md', 'config.md', 'install.md']

# Sort a list of tuples — sorts by first element, then second
$ python3 -c "print(sorted([(3, 'c'), (1, 'a'), (2, 'b')]))"
[(1, 'a'), (2, 'b'), (3, 'c')]

# Sort with key= and a lambda (sort by second element)
$ python3 -c "print(sorted([('z',1), ('a',3), ('m',2)], key=lambda p: p[1]))"
[('z', 1), ('m', 2), ('a', 3)]

# enumerate() — get (index, item) pairs, starting at 1
$ python3 -c "for i, x in enumerate(['a','b','c'], start=1): print(f'{i}. {x}')"
1. a
2. b
3. c

# re.sub with a function replacement — prepend '#' to a heading match
$ python3 -c "import re; print(re.sub(r'^#{1,6}', lambda m: '#' + m.group(0), '## Setup'))"
### Setup
```

## Exercises

### Setup

Create a directory called `lesson_27/docs/` and populate it with three Markdown files. Create these files by hand or with a short script — the content must match exactly so your output matches the expected output below.

> [!info] The file contents below are delimited by `---` lines instead of code fences, because these files contain internal code fences that would break the Markdown rendering. When creating each file, copy everything between the `---` delimiters — the delimiters themselves are not part of the file content.

**`lesson_27/docs/install.md`:**

````markdown
---
title: Installation Guide
sidebar_position: 1
tags: setup, quickstart
---

## title: Installation Guide 

# Installation Guide

Download the package from [the releases page](https://github.com/example/releases).

## Prerequisites

You need [Python 3.10+](https://python.org/) installed.

## Steps

Run the following command:

```bash
# Install the package globally
pip install example-sdk
```

Then verify:

```bash
# Check the version
example-sdk --version
```

## See the [usage guide](https://claude.ai/chat/usage.md) for next steps.
````


**`lesson_27/docs/usage.md`:**

````Markdown
---
title: Usage
sidebar_position: 2
tags: api, examples
---

## title: Usage Overview 

# Usage Overview

Import the SDK and initialize a client:

```python
# Create a client instance
from example_sdk import Client
client = Client(token="your-token")
```

## Fetching Data

Use the [fetch method](https://docs.example.com/fetch) to retrieve records:

```python
# Fetch all records
records = client.fetch_all()
```

## Error Handling

## Wrap calls in a try/except block. See the [error reference](https://claude.ai/chat/errors.md) for details.
````

**`lesson_27/docs/config.md`:**

````Markdown
---

---

## title: Configuration Reference sidebar_position: 5 tags: config, settings, advanced

# Configuration Reference

## Environment Variables

Set `EXAMPLE_TOKEN` before running. See [token setup](https://docs.example.com/auth) for details.

### Required Variables

The following are required:

- `EXAMPLE_TOKEN` — your API token
- `EXAMPLE_ENV` — set to `production` or `staging`

To set an environment variable, use the following code:

```bash
# This is a comment. It is not a heading, and it shouldn't be promoted.
export var="VAR_VALUE"
```

### Optional Variables

These are optional:

- `EXAMPLE_TIMEOUT` — request timeout in seconds
- `EXAMPLE_LOG_LEVEL` — one of `debug`, `info`, `warn`

## Config File

## You can also use a [YAML config file](https://docs.example.com/config-file) instead of environment variables. See the [advanced setup guide](https://claude.ai/chat/advanced.md).
````

### Part 1: Extract all links from all files

Write a script called `extract_links.py` that:

1. Accepts a directory path as a hardcoded variable (set it to `lesson_27/docs`).
2. Uses `pathlib` to find all `.md` files in that directory.
3. For each file, uses `mistune` to parse the content and extract every inline link.
4. Prints each link in the format shown below, grouped by file, with the filename as a header.

Sort the files alphabetically by filename. Print links in the order they appear in each file.

**Expected output:**

```
config.md
  [token setup](https://docs.example.com/auth)
  [YAML config file](https://docs.example.com/config-file)
  [advanced setup guide](./advanced.md)

install.md
  [the releases page](https://github.com/example/releases)
  [Python 3.10+](https://python.org)
  [usage guide](./usage.md)

usage.md
  [fetch method](https://docs.example.com/fetch)
  [error reference](./errors.md)
```

### Part 2: Rewrite heading levels

Write a script called `shift_headings.py` that:

1. Reads the file `lesson_27/docs/config.md`.
2. Splits the content into lines and processes each line individually.
3. Tracks whether the current line is inside a code fence by toggling a boolean flag for when the line enters or exits a code block.
4. For lines outside a code fence, uses `re.sub()` with a function as the replacement argument to increase every heading level by 1 (i.e., `#` becomes `##`, `##` becomes `###`, etc.). Lines inside a code fence are left unchanged.
5. Prints the full modified content to the terminal (do not write to the file).

**Expected output** (only the lines that change are highlighted here, but your script should print the _entire_ file content):

```markdown
---
title: Configuration Reference
sidebar_position: 5
tags: config, settings, advanced
---

## Configuration Reference

### Environment Variables

Set `EXAMPLE_TOKEN` before running. See [token setup](https://docs.example.com/auth) for details.

#### Required Variables

The following are required:

- `EXAMPLE_TOKEN` — your API token
- `EXAMPLE_ENV` — set to `production` or `staging`

#### Optional Variables

These are optional:

- `EXAMPLE_TIMEOUT` — request timeout in seconds
- `EXAMPLE_LOG_LEVEL` — one of `debug`, `info`, `warn`

### Config File

You can also use a [YAML config file](https://docs.example.com/config-file) instead of environment variables. See the [advanced setup guide](./advanced.md).
```

### Part 3: Front matter report across multiple files

Write a script called `fm_report.py` that:

1. Uses `pathlib` to find all `.md` files in `lesson_27/docs/`.
2. For each file, extracts the front matter block using regex.
3. From the front matter, extracts the `title` and `sidebar_position` fields.
4. Collects the results into a list of tuples: `(sidebar_position, title, filename)`.
5. Sorts the list by `sidebar_position` (numerically).
6. Prints a numbered report in the order shown below.

**Expected output:**

```
Documentation sidebar order:
  1. Installation Guide (install.md)
  2. Usage Overview (usage.md)
  5. Configuration Reference (config.md)
```

## Audit

|Exercise|Operations Required|Lesson Introduced|
|---|---|---|
|**Part 1**|`from pathlib import Path`|Lesson 23|
||`Path.iterdir()` or sorted file listing|Lesson 23|
||`Path.read_text(encoding=)`|Lesson 22|
||`import mistune`, `create_markdown(renderer=None)`|**Lesson 27 (current)**|
||Nested `for` loops over tokens and children|Lessons 9, 12, **Lesson 27 (current)**|
||List comprehension (optional, for building text from children)|**Lesson 27 (current)**|
||`for` loop, tuple unpacking|Lessons 9, 13|
||`if` conditional, string comparison|Lesson 10|
||`sorted()`|**Lesson 27 (current)**|
||f-strings|Lesson 6|
||`print()`|Lesson 1|
|**Part 2**|`from pathlib import Path`|Lesson 23|
||`Path.read_text(encoding=)`|Lesson 22|
||`str.split()` for line splitting|Lesson 5|
||`str.startswith()`|Lesson 5|
||`re.sub()` with function replacement|**Lesson 27 (current)**|
||`for` loop with boolean state tracking|Lessons 9, 10, 2|
||`print()`|Lesson 1|
|**Part 3**|`from pathlib import Path`|Lesson 23|
||`Path.iterdir()` with suffix filtering|Lesson 23|
||`Path.read_text(encoding=)`|Lesson 22|
||`import re`, `re.search()`, `re.findall()`|Lesson 24|
||`re.DOTALL` flag|Lesson 24|
||`.group()` on match objects|Lesson 24|
||`list.append()`|Lesson 7|
||Tuple creation and unpacking|Lesson 13|
||`sorted()` on list of tuples|**Lesson 27 (current)**|
||`int()` conversion|Lesson 2|
||`str.strip()`|Lesson 5|
||f-strings|Lesson 6|
||Conditionals|Lesson 10|
||`dict` creation and key access|Lesson 11|

All operations in every exercise are covered by the current lesson or prior lessons. No forward dependencies exist.