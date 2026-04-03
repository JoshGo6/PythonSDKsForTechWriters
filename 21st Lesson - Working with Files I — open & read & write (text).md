# Lesson 21: Working with Files I — open/read/write (text)

## Terminology and Theory

**File handle (file object)** When you call `open()`, Python returns a file object (also called a file handle). This object is your connection to the file on disk. You read from it or write to it through this object, and you close it when you're done.

**Context manager (`with` statement)** A `with` block automatically closes the file when the block ends, even if an error occurs inside the block. This is the standard way to work with files in Python. You will almost never see production code that opens a file without `with`.

**Mode string** The second argument to `open()` controls what you can do with the file:

- `"r"` — Read (default). The file must already exist.
- `"w"` — Write. Creates the file if it doesn't exist. **Overwrites the file if it does exist.**
- `"a"` — Append. Creates the file if it doesn't exist. Adds to the end if it does.

There are other modes, but these three cover the vast majority of scripting work.

> [!important]
> There is no "edit" mode in Python's `open()`. Files on disk are not like a document in a word processor. They are a linear sequence of bytes. You cannot insert or delete bytes in the middle. You can only overwrite bytes at specific positions. True "editing" requires restructuring the entire file.

**Encoding** Text files store bytes, not characters. The encoding tells Python how to translate between bytes and characters. Always pass `encoding="utf-8"` explicitly. If you don't, Python uses whatever your operating system's default is, which can differ between machines and cause subtle bugs — files that look fine on your computer but contain garbled characters on someone else's.

**Newlines** Different operating systems historically use different characters to mark the end of a line:

- Linux/macOS: `\n`
- Windows: `\r\n`

By default, Python's text mode performs **universal newline translation**: it converts all line endings to `\n` when reading and converts `\n` to your OS's native ending when writing. This is usually what you want for scripting. If you ever need to suppress this behavior (rare), you pass `newline=""` to `open()`.

**Reading strategies** There are two main approaches to reading a file:

- **Read the entire file at once** with `.read()`. This gives you one big string. Good for small files.
- **Read line by line** by iterating over the file object in a `for` loop. Each iteration gives you one line as a string, including its trailing `\n`. Good for large files or when you want to process each line individually.

There is also `.readlines()`, which reads the entire file and returns a list of lines (each line includes its trailing `\n`). It combines the downsides of both approaches — it loads everything into memory like `.read()` but gives you a list you still have to iterate. Prefer `.read()` or a `for` loop instead.

**The trailing newline problem** When you read lines from a file, each line includes its `\n` at the end. If you print a line that already has `\n`, `print()` adds another one, and you get double-spaced output. You have two options:

- Strip the newline with `.rstrip("\n")` (you learned `.strip()` in Lesson 5 — `.rstrip()` strips only from the right side).
- Pass `end=""` to `print()` so it doesn't add its own newline.

**Writing** When writing with `"w"` mode, you are responsible for including `\n` at the end of each line. Unlike `print()`, the `.write()` method does not add a newline automatically.

## Syntax Section

### Opening and reading an entire file

```python
with open("input.txt", "r", encoding="utf-8") as f:
    contents = f.read()
```

- `open(...)` returns a file object assigned to `f`.
- `"r"` is the mode (read). You can omit it since `"r"` is the default, but being explicit is clearer.
- `encoding="utf-8"` prevents encoding surprises across machines.
- `f.read()` returns the entire file as a single string.
- When the `with` block ends, the file is automatically closed.

### Reading line by line

```python
with open("input.txt", "r", encoding="utf-8") as f:
    for line in f:
        clean = line.rstrip("\n")
        print(clean)
```

- Iterating over `f` yields one line per iteration.
- Each `line` includes a trailing `\n`, so `.rstrip("\n")` removes it.

### Writing to a file

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("First line\n")
    f.write("Second line\n")
```

- `"w"` mode creates the file or overwrites it if it already exists.
- `.write()` does not add `\n` for you — you must include it yourself.

### Appending to a file

```python
with open("log.txt", "a", encoding="utf-8") as f:
    f.write("New entry\n")
```

- `"a"` mode adds to the end of the file without destroying existing content.

### Reading and writing in sequence

```python
with open("source.txt", "r", encoding="utf-8") as src:
    data = src.read()

with open("destination.txt", "w", encoding="utf-8") as dst:
    dst.write(data.upper())
```

- You can use separate `with` blocks for reading and writing. Each block opens and closes its own file.

> [!warning] 
>Never open the same file for reading and writing at the same time in a script. Read first, close, then write. Trying to read and overwrite the same file simultaneously will destroy your data.

## Worked Examples

### Example 1: Read a file and print each line with a line number

Suppose you have a file called `servers.txt` with the following content:

```
web-01.example.com
web-02.example.com
db-01.example.com
```

This script reads the file and prints each line with a number in front of it:

```python
line_number = 1

with open("servers.txt", "r", encoding="utf-8") as f:
    for line in f:
        hostname = line.rstrip("\n")
        print(f"{line_number}: {hostname}")
        line_number = line_number + 1
```

Output:

```
1: web-01.example.com
2: web-02.example.com
3: db-01.example.com
```

What's happening:

- The file is opened for reading. The `for` loop iterates one line at a time.
- `.rstrip("\n")` removes the trailing newline from each line so it doesn't double-space when printed.
- An f-string (Lesson 6) formats the output.
- A counter variable tracks the line number manually. (You haven't learned `enumerate()` yet, so a manual counter is the right approach.)

### Example 2: Read a config file, filter lines, and write matches to a new file

Suppose `config.txt` contains:

```
# Database settings
DB_HOST=localhost
DB_PORT=5432
# Cache settings
CACHE_ENABLED=true
CACHE_TTL=300
```

This script reads the file, skips comment lines (lines starting with `#`), and writes only the key-value lines to a new file:

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

kept = 0
skipped = 0

with open("config.txt", "r", encoding="utf-8") as src:
    lines = src.read().splitlines()

with open("clean_config.txt", "w", encoding="utf-8") as dst:
    for line in lines:
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            skipped = skipped + 1
            logging.debug(f"Skipped: {stripped}")
        else:
            dst.write(line + "\n")
            kept = kept + 1
            logging.info(f"Kept: {line}")

logging.info(f"Done. Kept {kept} lines, skipped {skipped}.")
```

Output (at INFO level):

```
INFO: Kept: DB_HOST=localhost
INFO: Kept: DB_PORT=5432
INFO: Kept: CACHE_ENABLED=true
INFO: Kept: CACHE_TTL=300
INFO: Done. Kept 4 lines, skipped 2.
```

And `clean_config.txt` will contain:

```
DB_HOST=localhost
DB_PORT=5432
CACHE_ENABLED=true
CACHE_TTL=300
```

What's happening:

- The source file is read entirely with `.read()`, then split into a list of lines with `.splitlines()`. Unlike iterating the file object directly, `.splitlines()` strips the trailing newlines for you automatically.
- Each line is checked: if it's empty or starts with `#`, it's skipped. Otherwise, it's written to the output file.
- `.write()` needs `\n` added explicitly because `.splitlines()` removed the original newlines.
- `logging` (Lesson 20) replaces `print()` for status messages. The `DEBUG`-level message for skipped lines won't appear because the threshold is set to `INFO`.

> [!tip] 
> `.splitlines()` is a string method that splits on line boundaries and strips the newline characters from each resulting string. It's a convenient alternative to reading line by line and calling `.rstrip("\n")` on every line. The tradeoff is that it loads the entire file into memory at once, which is fine for small configuration files and scripts but not ideal for very large files.

### Example 3: Read a text file, transform each line, and write a report

Suppose `endpoints.txt` contains a list of API endpoint paths:

```
/api/v1/repos
/api/v1/issues
/api/v1/users
/api/v1/pulls
```

This script reads the file, extracts the resource name from each path, and writes a simple Markdown summary to a new file:

```python
def extract_resource(path):
    """Return the last segment of a URL path."""
    parts = path.split("/")
    return parts[-1]

def format_entry(resource):
    """Return a Markdown list item for a resource."""
    title = resource.replace("_", " ").upper()
    return f"- **{title}**: `/api/v1/{resource}`"

with open("endpoints.txt", "r", encoding="utf-8") as f:
    paths = f.read().splitlines()

with open("endpoint_summary.md", "w", encoding="utf-8") as out:
    out.write("# API Endpoints\n\n")
    for path in paths:
        if path.strip() == "":
            continue
        resource = extract_resource(path)
        entry = format_entry(resource)
        out.write(entry + "\n")

print("Wrote endpoint_summary.md")
```

Output to terminal:

```
Wrote endpoint_summary.md
```

Content of `endpoint_summary.md`:

```markdown
# API Endpoints

- **REPOS**: `/api/v1/repos`
- **ISSUES**: `/api/v1/issues`
- **USERS**: `/api/v1/users`
- **PULLS**: `/api/v1/pulls`
```

What's happening:

- Two helper functions (Lesson 15) handle the transformation logic. `extract_resource` uses `.split("/")` (Lesson 5) and negative indexing (Lesson 4) to grab the last segment. `format_entry` uses `.replace()` (Lesson 5), `.upper()` (Lesson 5), and an f-string (Lesson 6).
- The input file is read and split into lines. Empty lines are skipped using a truthiness check on the stripped string (Lesson 14) with `continue` to skip to the next iteration.
- The output file is opened in write mode. Each formatted entry is written with an explicit `\n`.

> [!note]
> The `continue` keyword skips the rest of the current loop iteration and jumps to the next one. You saw loops in Lesson 9. `continue` is a natural companion — when a line doesn't meet your criteria, `continue` lets you skip it cleanly without nesting the rest of the loop body inside an `else` block.

## Quick Reference

```
# Open a file for reading (entire contents as one string)
$ python3 -c "
with open('demo.txt', 'w', encoding='utf-8') as f:
    f.write('hello\nworld\n')
with open('demo.txt', 'r', encoding='utf-8') as f:
    print(repr(f.read()))
"
'hello\nworld\n'

# Read a file line by line (each line includes trailing \n)
$ python3 -c "
with open('demo.txt', 'w', encoding='utf-8') as f:
    f.write('alpha\nbeta\n')
with open('demo.txt', 'r', encoding='utf-8') as f:
    for line in f:
        print(repr(line))
"
'alpha\n'
'beta\n'

# Strip trailing newline from each line
$ python3 -c "
with open('demo.txt', 'w', encoding='utf-8') as f:
    f.write('alpha\nbeta\n')
with open('demo.txt', 'r', encoding='utf-8') as f:
    for line in f:
        print(line.rstrip('\n'))
"
alpha
beta

# Use .splitlines() to read all lines without trailing newlines
$ python3 -c "
with open('demo.txt', 'w', encoding='utf-8') as f:
    f.write('one\ntwo\nthree\n')
with open('demo.txt', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()
print(lines)
"
['one', 'two', 'three']

# Write to a file (overwrites existing content)
$ python3 -c "
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write('line one\n')
    f.write('line two\n')
with open('output.txt', 'r', encoding='utf-8') as f:
    print(f.read())
"
line one
line two

# Append to an existing file
$ python3 -c "
with open('log.txt', 'w', encoding='utf-8') as f:
    f.write('entry 1\n')
with open('log.txt', 'a', encoding='utf-8') as f:
    f.write('entry 2\n')
with open('log.txt', 'r', encoding='utf-8') as f:
    print(f.read())
"
entry 1
entry 2

# Write mode destroys existing content — be careful
$ python3 -c "
with open('danger.txt', 'w', encoding='utf-8') as f:
    f.write('original content\n')
with open('danger.txt', 'w', encoding='utf-8') as f:
    f.write('replaced\n')
with open('danger.txt', 'r', encoding='utf-8') as f:
    print(f.read())
"
replaced
```

## Exercises

### Exercise 1: Server log filter

You manage a list of server log entries. Create a file called `access_log.txt` with the following content (copy and paste it exactly):

```
2024-06-01 08:14:22 INFO  GET /api/v1/repos 200
2024-06-01 08:14:25 ERROR GET /api/v1/repos/999 404
2024-06-01 08:15:01 INFO  POST /api/v1/issues 201
2024-06-01 08:15:44 ERROR DELETE /api/v1/repos/5 403
2024-06-01 08:16:02 INFO  GET /api/v1/users 200
2024-06-01 08:16:30 WARNING GET /api/v1/pulls 429
2024-06-01 08:17:11 ERROR POST /api/v1/issues 500
```

Write a script called `log_filter.py` that does the following:

1. Define a function called `parse_log_line` that accepts a single log line string and returns a dictionary with the following keys: `"timestamp"`, `"level"`, `"method"`, `"path"`, and `"status"`. The timestamp should be the first two space-separated tokens joined back together (e.g., `"2024-06-01 08:14:22"`). The remaining tokens map to the remaining keys in order.
    
2. Read `access_log.txt` line by line. For each non-empty line, call `parse_log_line` to get a dictionary.
    
3. Use a conditional check: if the value associated with `"level"` is `"ERROR"`, write a formatted summary line to a new file called `error_report.txt`. The format for each line is: `[TIMESTAMP] STATUS PATH`
    
4. Use logging at the `INFO` level to print a message to the terminal for every line processed (whether or not it was an error), showing the level and path. Use logging at the `WARNING` level to print a final count of how many error lines were written.
    
5. After writing, open `error_report.txt` and print its contents to the terminal to verify.
    

Expected terminal output:

```
INFO:root:Processed: INFO /api/v1/repos
INFO:root:Processed: ERROR /api/v1/repos/999
INFO:root:Processed: INFO /api/v1/issues
INFO:root:Processed: ERROR /api/v1/repos/5
INFO:root:Processed: INFO /api/v1/users
INFO:root:Processed: WARNING /api/v1/pulls
INFO:root:Processed: ERROR /api/v1/issues
WARNING:root:Wrote 3 error(s) to error_report.txt
[2024-06-01 08:14:25] 404 /api/v1/repos/999
[2024-06-01 08:15:44] 403 /api/v1/repos/5
[2024-06-01 08:17:11] 500 /api/v1/issues
```

Expected content of `error_report.txt`:

```
[2024-06-01 08:14:25] 404 /api/v1/repos/999
[2024-06-01 08:15:44] 403 /api/v1/repos/5
[2024-06-01 08:17:11] 500 /api/v1/issues
```

---

## Audit

|Requirement|Introduced In|
|---|---|
|`print()`|Lesson 1|
|Variables and assignment|Lesson 2|
|String methods (`.split()`, `.strip()`, `.rstrip()`, `.join()`)|Lesson 5|
|f-strings|Lesson 6|
|List indexing (including negative indexing)|Lesson 7|
|`for` loops|Lesson 9|
|Conditionals (`if`/`elif`/`else`), comparison with `==`|Lesson 10|
|Dictionary creation (literal `{}` syntax with keys)|Lesson 11|
|Truthiness checks (empty string check)|Lesson 14|
|Defining and calling functions, `return`|Lesson 15|
|`import logging`, `logging.basicConfig()`, `logging.info()`, `logging.warning()`|Lesson 20|
|`open()`, `with`, `"r"`/`"w"` mode, `encoding="utf-8"`, `.read()`, `.write()`, line-by-line iteration, `.rstrip("\n")`|Lesson 21 (current)|

No operations from future lessons are required. All syntax and patterns used in the exercise have been taught in Lessons 1–21.