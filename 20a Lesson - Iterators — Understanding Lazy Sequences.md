# Lesson 20: Iterators — Understanding Lazy Sequences

## Terminology and Theory

An **iterable** is anything you can loop over with a `for` loop. Lists, strings, tuples, and dictionaries are all iterables you already know. Each of these stores all of its elements in memory at once, and you can loop over them as many times as you want.

An **iterator** is a different kind of object. Instead of holding all its values in memory, an iterator **produces values on demand**, one at a time, as you ask for them. Once it has produced all of its values, it is **exhausted** — it has nothing left to give. If you try to loop over an exhausted iterator a second time, you get nothing. No error, no warning, just… nothing.

This "produce on demand" behavior is called **lazy evaluation**. The iterator does not compute or fetch the next value until something asks for it. This is the opposite of a list, which is **eager** — all its values exist the moment the list is created.

Why does this matter for SDK and script work? Three common Python patterns produce iterators instead of lists:

- **File handles**: When you open a file with `open()`, the resulting object is an iterator over the file's lines. Python reads one line at a time from disk instead of loading the entire file into memory at once.
- **`re.finditer()`**: When you search a string for all occurrences of a pattern, `finditer()` returns an iterator of match objects instead of building a complete list up front.
- **Paginated API results**: Many SDKs (including PyGithub) return iterators that fetch one page of results from the server at a time. You will encounter this pattern later in the curriculum.

The practical consequence is simple: if you need to loop over the same data twice, or if you need to check the length, or access items by index, you must **convert the iterator to a list first** using `list()`. If you forget, your second loop will silently produce zero iterations — one of the most common and confusing bugs in Python scripting.

The **iterator protocol** is the mechanism that makes this work. Every iterator has a `__next__()` method that Python calls internally each time it needs the next value. You can call this method yourself using the built-in `next()` function. When there are no more values, `next()` raises a `StopIteration` exception. You will rarely call `next()` directly in your own scripts — `for` loops handle it automatically — but knowing the mechanism exists helps you understand what is happening underneath.

> [!note] 
> Every iterator is also an iterable (you can use it in a `for` loop), but not every iterable is an iterator. A list is an iterable that is _not_ an iterator — it never gets exhausted, and it stores all its values eagerly.

## Syntax Section

### Creating an iterator from a list with `iter()`

You can turn any iterable into an iterator using the built-in `iter()` function:

```python
numbers = [10, 20, 30]
it = iter(numbers)
```

`it` is now an iterator. The original list `numbers` is unchanged and still holds all three values. The iterator `it` is a separate object that will walk through those values one at a time.

### Pulling values one at a time with `next()`

```python
print(next(it))   # 10
print(next(it))   # 20
print(next(it))   # 30
print(next(it))   # Raises StopIteration
```

Each call to `next()` advances the iterator by one position. After all values have been produced, any further call to `next()` raises `StopIteration`.

### Using `for` loops with iterators

A `for` loop consumes an iterator exactly the same way it consumes a list:

```python
it = iter([10, 20, 30])
for value in it:
    print(value)
```

The `for` loop calls `next()` internally and stops automatically when `StopIteration` is raised. After this loop, `it` is exhausted.

### Detecting an iterator with `type()`

```python
my_list = [1, 2, 3]
my_iter = iter(my_list)

print(type(my_list))   # <class 'list'>
print(type(my_iter))   # <class 'list_iterator'>
```

The type name tells you what you are working with. Different sources produce iterators with different type names (`list_iterator`, `callable_iterator`, `TextIOWrapper`, etc.), but the behavior is always the same: single-pass, lazy, exhaustible.

### Converting an iterator to a list with `list()`

```python
it = iter([10, 20, 30])
result = list(it)
print(result)   # [10, 20, 30]
```

`list()` drains every remaining value from the iterator and stores them in a new list. After this call, the iterator is exhausted, but the list is permanent and reusable. If the iterator was already exhausted, `list()` returns an empty list.

### Opening a file: the file handle as an iterator

```python
with open("example.txt") as f:
    for line in f:
        print(line)
```

`open()` returns a file object. When used in a `for` loop, this object behaves as an iterator: it yields one line at a time from the file. The `with` keyword ensures the file is properly closed when the indented block finishes, even if an error occurs. Lesson 22 covers file operations in depth — for now, treat `with open(...) as f:` as the safe pattern for opening a file to read its lines.

> [!tip]
> Each line yielded by a file handle includes the trailing newline character (`\n`). Use `.strip()` to remove it.

### Searching with `re.finditer()`

```python
import re

text = "Error at 10, error at 25, ERROR at 40"
matches = re.finditer(r"[Ee]rror", text)
```

`re.finditer(pattern, string)` searches `string` for every non-overlapping occurrence of `pattern` and returns an iterator of **match objects**. Each match object has methods you can call:

- `match.group()` — returns the actual text that matched.
- `match.start()` — returns the index position where the match begins.

> [!info]
> `re.finditer()` expects a **raw string** for the pattern (prefixed with `r`). You saw `r""` strings briefly in Lesson 17 when `re` was introduced. The `r` prefix tells Python not to interpret backslash sequences, which matters for regex patterns. For now, just remember to always prefix patterns with `r`.

## Worked Examples

### Example 1: Iterator Exhaustion with `iter()` and `next()`

This example creates an iterator from a list and demonstrates what happens when you pull every value out of it.

```python
colors = ["red", "green", "blue"]
color_iter = iter(colors)

print(f"Type of list:     {type(colors)}")
print(f"Type of iterator: {type(color_iter)}")
print()

# Pull values one at a time
print(next(color_iter))   # red
print(next(color_iter))   # green
print(next(color_iter))   # blue

# The iterator is now exhausted — this loop produces nothing
print("Attempting to loop over exhausted iterator:")
for c in color_iter:
    print(f"  Found: {c}")

print("Loop finished — nothing was printed because the iterator was empty.")
```

Output:

```
Type of list:     <class 'list'>
Type of iterator: <class 'list_iterator'>

red
green
blue
Attempting to loop over exhausted iterator:
Loop finished — nothing was printed because the iterator was empty.
```

There is no error when you loop over an exhausted iterator. The `for` loop simply executes zero iterations. This silence is what makes the bug so easy to miss — your script appears to work, but an entire section of logic quietly does nothing.

### Example 2: Reading a File Handle as an Iterator

This example reads a small text file line by line using the file handle as an iterator, then demonstrates that the handle is exhausted after one pass.

First, create a file called `fruits.txt` with this content:

```
apple
banana
cherry
```

Now run this script:

```python
with open("fruits.txt") as f:
    print(f"File object type: {type(f)}")
    print()

    # First pass — reads all lines
    print("First pass:")
    lines = []
    for line in f:
        cleaned = line.strip()
        lines.append(cleaned)
        print(f"  Read: {cleaned}")

    # Second pass — the file handle is exhausted
    print("\nSecond pass:")
    count = 0
    for line in f:
        count = count + 1
    print(f"  Lines read in second pass: {count}")

print(f"\nLines collected in list: {lines}")
print(f"List length: {len(lines)}")
```

Output:

```
File object type: <class '_io.TextIOWrapper'>

First pass:
  Read: apple
  Read: banana
  Read: cherry

Second pass:
  Lines read in second pass: 0

Lines collected in list: ['apple', 'banana', 'cherry']
List length: 3
```

The first pass reads all three lines. The second pass reads nothing because the file handle has already been consumed. But the `lines` list — built during the first pass — still holds all three values and can be used as many times as needed.

> [!warning] 
> The file handle is exhausted _within_ the `with` block. This is not the same as the file being _closed_ (which happens when the `with` block ends). Even inside the block, a second loop yields nothing. After the block ends, attempting to iterate the handle raises a `ValueError` because the file is closed.

### Example 3: Using `re.finditer()` and Converting to a List

This example searches a string for a pattern and shows how to work around iterator exhaustion by converting to a list.

```python
import re

log_text = "WARN: low disk. ERROR: disk full. INFO: cleared. ERROR: timeout."

# finditer returns an iterator of match objects
match_iter = re.finditer(r"ERROR", log_text)
print(f"finditer type: {type(match_iter)}")

# First loop — consumes the iterator
print("\nFirst loop:")
for m in match_iter:
    print(f"  '{m.group()}' at position {m.start()}")

# Second loop — iterator is exhausted
print("\nSecond loop (same variable):")
for m in match_iter:
    print(f"  '{m.group()}' at position {m.start()}")
print("  (nothing printed — iterator exhausted)")

# The fix: create a new iterator and convert to a list
match_list = list(re.finditer(r"ERROR", log_text))
print(f"\nConverted to list — type: {type(match_list)}")
print(f"Total matches: {len(match_list)}")

# Now you can loop as many times as you want
print("\nLoop 1 over the list:")
for m in match_list:
    print(f"  '{m.group()}' at position {m.start()}")

print("\nLoop 2 over the list:")
for m in match_list:
    print(f"  '{m.group()}' at position {m.start()}")
```

Output:

```
finditer type: <class 'callable_iterator'>

First loop:
  'ERROR' at position 16
  'ERROR' at position 50

Second loop (same variable):
  (nothing printed — iterator exhausted)

Converted to list — type: <class 'list'>
Total matches: 2

Loop 1 over the list:
  'ERROR' at position 16
  'ERROR' at position 50

Loop 2 over the list:
  'ERROR' at position 16
  'ERROR' at position 50
```

The pattern is: if you know you need the results more than once, call `list()` on the iterator immediately. The trade-off is that `list()` loads all results into memory at once, but for most scripting tasks this is perfectly fine.

## Quick Reference

```
# Create an iterator from a list
$ python3 -c "it = iter([1, 2, 3]); print(type(it))"
<class 'list_iterator'>

# Pull one value with next()
$ python3 -c "it = iter(['a', 'b']); print(next(it)); print(next(it))"
a
b

# Exhausted iterator in a for loop produces nothing
$ python3 -c "it = iter([1]); _ = next(it); [print(x) for x in it]"
(no output)

# next() on an exhausted iterator raises StopIteration
$ python3 -c "it = iter([]); next(it)"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
StopIteration

# Convert an iterator to a list
$ python3 -c "it = iter([10, 20]); result = list(it); print(result)"
[10, 20]

# list() on an exhausted iterator returns an empty list
$ python3 -c "it = iter([10, 20]); list(it); print(list(it))"
[]

# File handle type
$ python3 -c "f = open('fruits.txt'); print(type(f)); f.close()"
<class '_io.TextIOWrapper'>

# re.finditer() returns a callable_iterator
$ python3 -c "import re; print(type(re.finditer(r'x', 'xox')))"
<class 'callable_iterator'>

# Match object .group() and .start()
$ python3 -c "import re; m = list(re.finditer(r'cat', 'the cat sat'))[0]; print(m.group(), m.start())"
cat 4
```

## Exercise

### Iterator Lab

**Setup:** Create a file called `log_data.txt` in your working directory with the following exact content (six lines, no trailing blank line):

```
INFO: System started
ERROR: Disk full
INFO: User login
ERROR: Network timeout
INFO: Backup complete
ERROR: Permission denied
```

**Task:** Write a script called `iterator_lab.py` that does the following:

1. Defines a function `read_lines(filepath)` that reads a text file and returns a list of its lines with whitespace stripped from each line. If the file is not found, the function prints an error message in the format shown in the expected output and returns an empty list.
    
2. Calls `read_lines()` to load `log_data.txt`, then prints how many lines were read and from which file.
    
3. If lines were successfully read, joins them into a single string (with newline characters between them) and uses `re.finditer()` to locate every occurrence of `"ERROR"` in the joined text.
    
4. Prints the type of the `finditer` result, then loops over it, printing each match's text and starting position. Immediately loops over the same variable a second time and reports how many matches that second loop found.
    
5. Creates a fresh `finditer` result, converts it to a list, and prints the list's type and total match count.
    

**Expected output:**

```
Read 6 lines from log_data.txt
finditer type: <class 'callable_iterator'>
Match: 'ERROR' at position 21
Match: 'ERROR' at position 55
Match: 'ERROR' at position 100
Second loop found 0 matches
List type: <class 'list'>
Total matches (from list): 3
```

**Verify error handling:** Rename or delete `log_data.txt` and run the script again. It should print:

```
Error: File 'log_data.txt' not found
Read 0 lines from log_data.txt
```

---

## Audit

The following table lists every Python operation required by the exercise and the lesson where it was introduced.

|Operation / Concept|Lesson Introduced|
|---|---|
|`import re`|Lesson 17 (Modules and imports)|
|`def` with parameter, `return`|Lesson 15 (Functions I)|
|`with open(...) as f:` (file handle as iterator)|Lesson 20 (current)|
|`for line in f:` (iterating a file handle)|Lesson 20 (current), Lesson 9 (for loops)|
|`.strip()`|Lesson 5 (String methods)|
|`list.append()`|Lesson 7 (Lists I)|
|`try` / `except FileNotFoundError`|Lesson 19 (Exceptions II), Lesson 18 (Exceptions I)|
|`len()`|Lesson 7 (Lists I)|
|`print()` with f-strings|Lesson 3 (Printing), Lesson 6 (f-strings)|
|Truthiness check (`if lines:`)|Lesson 14 (Truthiness)|
|`"\n".join(lines)`|Lesson 5 (String methods)|
|`re.finditer(pattern, string)`|Lesson 20 (current)|
|`type()`|Lesson 2 (Variables and types)|
|`match.group()`, `match.start()`|Lesson 20 (current)|
|Iterator exhaustion (looping twice)|Lesson 20 (current)|
|`list()` to convert iterator|Lesson 20 (current)|
|Counter variable (`count = 0`, `count = count + 1`)|Lesson 2 (variables, assignment), basic integer arithmetic|

All operations are covered by the current lesson or prior lessons. No future-lesson dependencies exist.