# Lesson 17: Modules and Imports (Standard Library First)

---

## Terminology and Theory

A **module** is a single `.py` file that contains Python code — variables, functions, classes, or all three. Every script you have written so far is technically a module. When someone else writes a useful `.py` file and makes it available, you can pull its contents into your own script using the `import` statement.

The **standard library** is the collection of modules that ships with Python itself — you don't need to install anything extra. It covers a huge range of functionality: math operations, file-path handling, JSON parsing, regular expressions, date/time processing, random number generation, and much more. Later lessons will use several of these modules in depth. This lesson focuses on the mechanics of importing and calling code from them.

An **import statement** tells Python: "go find this module, load it, and make its contents available to me under a name I can use." Until you import a module, its functions and variables don't exist in your script's namespace.

A **namespace** is the mapping of names to objects that Python maintains at any given point. When you write `import math`, Python creates a name `math` in your script's namespace that points to the math module object. You then reach inside it with dot notation: `math.sqrt(16)`. This is conceptually similar to how you reach into a dictionary by key — the module is the container, and the function name is the key.

**Dot notation** (`module.name`) is how you access something inside a module. You have already seen dot notation with string methods (`"hello".upper()`) and list methods (`my_list.append(5)`). Module access works the same way: the module name on the left, a dot, and the name of the thing you want on the right.

A quick word on **reading module documentation**: Python's official docs list every module in the standard library. For any module, the docs tell you what functions and constants it provides, what arguments each function accepts, and what it returns. You don't need to memorize modules — you need to know how to import one and how to look up what it offers. The built-in `help()` function is useful here: calling `help(math.sqrt)` in the REPL prints the function's docstring so you can see what it does without leaving your terminal.

---

## Syntax Section

### `import module`

The most common form. Loads the entire module and gives you access through the module name:

```python
import math

result = math.sqrt(25)
print(result)  # 5.0
```

After `import math`, every function and constant inside `math` is reachable via `math.name`.

### `from module import name`

Pulls a specific name directly into your script's namespace so you can use it without the module prefix:

```python
from math import sqrt

result = sqrt(25)
print(result)  # 5.0
```

You can import multiple names in one line by separating them with commas:

```python
from math import sqrt, ceil, floor
```

### `import module as alias`

Creates a shorter alias for the module name. This is common when a module name is long or when a community convention exists:

```python
import random as rng

print(rng.randint(1, 10))
```

You can also alias individual imports:

```python
from math import factorial as fact

print(fact(5))  # 120
```

### When to use which form

- Use `import module` when you call many things from a module — the prefix makes it clear where each function comes from, which helps readability.
- Use `from module import name` when you only need one or two specific functions and repeating the module prefix would clutter the code.
- Use `import module as alias` when the module name is long or the alias is an accepted convention.

There is no performance difference between these forms. The choice is purely about readability.

### Where imports go

By convention, all `import` statements go at the top of your script, before any other code. This makes it immediately obvious what your script depends on.

```python
import math
import random

# rest of your script below
```

### Previewing modules you will use later

You don't need to learn these in depth right now, but you should know they exist because they appear in later lessons:

- **`pathlib`** — Working with file and directory paths. You will use it heavily in file-processing scripts. (Lesson 22)
- **`json`** — Reading and writing JSON data, the format almost every API and SDK uses for structured data. (Lesson 26)
- **`re`** — Regular expressions for pattern matching and text substitution. (Lesson 23)

For now, just recognize that these are standard library modules you will import the same way you import `math` or `random`.

---

## Worked Examples

### Example 1: Importing `math` to transform a list of numbers

This example imports the `math` module and uses two of its functions to process a list of values — something you would do when summarizing numeric data returned by an SDK.

```python
import math

download_counts = [850, 3_200, 47, 12_500, 999]

for count in download_counts:
    log_value = math.log10(count)
    rounded = math.ceil(log_value)
    print(f"{count:>8} downloads → log10 = {log_value:.2f} → magnitude bucket: {rounded}")
```

Output:

```
     850 downloads → log10 = 2.93 → magnitude bucket: 3
    3200 downloads → log10 = 3.51 → magnitude bucket: 4
      47 downloads → log10 = 1.67 → magnitude bucket: 2
   12500 downloads → log10 = 4.10 → magnitude bucket: 5
     999 downloads → log10 = 3.00 → magnitude bucket: 3
```

What is happening:

- `import math` loads the module. Every call uses dot notation: `math.log10()`, `math.ceil()`.
- `math.log10(count)` returns the base-10 logarithm of a number. This is a quick way to figure out the "order of magnitude" — whether a number is in the hundreds, thousands, or ten-thousands.
- `math.ceil()` rounds a float up to the nearest integer.
- The f-string uses `:>8` to right-align the count in an 8-character-wide field, and `:.2f` to show exactly two decimal places. Both of these are f-string formatting features from Lesson 6.
- The underscore in `3_200` and `12_500` is a visual separator Python allows in numeric literals. It has no effect on the value — `3_200` is identical to `3200`. It just makes large numbers easier to read in your source code.

### Example 2: Using `from ... import` and `random` to select items

This example shows the `from module import name` form and uses the `random` module to simulate picking a random item from a list — a pattern useful for sampling SDK results during testing.

```python
from random import choice, randint

repo_names = ["docs-api", "sdk-python", "cli-tools", "web-dashboard", "data-pipeline"]

featured = choice(repo_names)
print(f"Featured repo: {featured}")

random_issue_count = randint(1, 50)
print(f"Simulated open issues: {random_issue_count}")
```

Possible output (values will vary each run):

```
Featured repo: cli-tools
Simulated open issues: 23
```

What is happening:

- `from random import choice, randint` pulls two specific functions directly into the script's namespace. No `random.` prefix is needed when calling them.
- `choice(repo_names)` picks one random element from the list.
- `randint(1, 50)` returns a random integer between 1 and 50, inclusive on both ends.
- Because these are random, re-running the script produces different output each time.

### Example 3: Using `help()` and an alias to explore a module

This example demonstrates how to inspect a module from the REPL using `help()`, and how to use an alias.

```python
import math as m

# Check what pi looks like
print(f"Pi to 4 decimal places: {m.pi:.4f}")

# Get help on a specific function
help(m.factorial)
```

Output:

```
Pi to 4 decimal places: 3.1416
Help on built-in function factorial in module math:

factorial(n, /)
    Find n!.

    Raise a ValueError if x is negative or non-integral.
```

What is happening:

- `import math as m` loads the module but binds it to the shorter name `m`. Every access uses `m.` instead of `math.`.
- `m.pi` is a constant (not a function), so no parentheses are needed. It holds the value of π.
- `help(m.factorial)` prints the docstring for the `factorial` function. This is how you quickly check what a function does, what arguments it takes, and what errors it can raise — without leaving your terminal.
- The `:.4f` inside the f-string formats the float to four decimal places.

---

## Quick Reference

```
# Import an entire module
$ python3 -c "import math; print(math.sqrt(64))"
8.0

# Import a specific function from a module
$ python3 -c "from math import floor; print(floor(3.7))"
3

# Import multiple names from a module
$ python3 -c "from math import pi, tau; print(pi, tau)"
3.141592653589793 6.283185307179586

# Import a module with an alias
$ python3 -c "import random as rng; print(rng.randint(1, 100))"
(random integer between 1 and 100)

# Use help() to read a function's docstring
$ python3 -c "import math; help(math.pow)"
Help on built-in function pow in module math:
pow(x, y, /)
    Return x**y (x to the power of y).

# Access a module constant (no parentheses)
$ python3 -c "import math; print(math.e)"
2.718281828459045

# Combine an import with a loop
$ python3 -c "
import math
for n in [1, 10, 100, 1000]:
    print(f'{n} -> {math.log10(n):.1f}')
"
1 -> 0.0
10 -> 1.0
100 -> 2.0
1000 -> 3.0
```

---

## Audit

The exercise below requires the following operations. Each one is verified against the lesson where it was introduced:

|Operation|Introduced in|
|---|---|
|`import module`|Lesson 17 (current)|
|`from module import name`|Lesson 17 (current)|
|`help()` on a module function|Lesson 17 (current)|
|`print()` with f-strings|Lesson 6|
|List creation and indexing|Lesson 7|
|List of dictionaries|Lessons 7, 11|
|`for` loop over a list|Lesson 9|
|`if/elif/else`|Lesson 10|
|Dictionary key access and `.get()`|Lesson 11|
|Tuple unpacking in a loop|Lesson 13|
|Truthiness check on a value|Lesson 14|
|Defining and calling a function with default parameter|Lessons 15, 16|

All operations have been introduced in the current lesson or a prior lesson. No future-lesson dependencies exist.

---

## Exercise

### SDK Module Report Generator

You are building a utility that summarizes download statistics for a set of packages. Write a single script that does all of the following:

**Setup data** — Define the following list of dictionaries at the top of your script (after your imports):

```python
packages = [
    {"name": "pygithub", "downloads": 54000, "description": "GitHub API wrapper"},
    {"name": "requests", "downloads": 890000, "description": ""},
    {"name": "flask", "downloads": 312000, "description": "Micro web framework"},
    {"name": "obscure-tool", "downloads": 15, "description": "An obscure utility"},
    {"name": "numpy", "downloads": 1450000, "description": "Numerical computing"},
]
```

**Requirements:**

1. Import the `math` module using the standard `import math` form. Import `choice` directly from the `random` module using the `from ... import` form.
    
2. Define a function called `classify_popularity` that accepts a download count and an optional threshold parameter with a default value of `1000`. The function must return a two-element tuple: the first element is the result of `math.log10()` on the download count, and the second element is a string — `"popular"` if the count is greater than or equal to the threshold, or `"niche"` if it is below.
    
3. Loop through the `packages` list. For each package, call `classify_popularity` and unpack the returned tuple into two variables. Then print a line in this exact format:
    
    ```
    pygithub       |   54000 downloads | log10: 4.73 | popular
    ```
    
    The name field should be left-aligned and 15 characters wide. The download count should be right-aligned and 7 characters wide. The `log10` value should be displayed to 2 decimal places. If a package's `description` is falsy (empty string), print a second line immediately after it that says `(no description provided)`.
    
4. After the loop, use `choice` to pick one random package dictionary from the list. Print a blank line, then print:
    
    ```
    Random spotlight: <name> — <description>
    ```
    
    If the chosen package's description is falsy, print `No description` in place of the description.
    

**Expected output** (the spotlight line will vary):

```
pygithub        |   54000 downloads | log10: 4.73 | popular
requests        |  890000 downloads | log10: 5.95 | popular
  (no description provided)
flask           |  312000 downloads | log10: 5.49 | popular
obscure-tool    |      15 downloads | log10: 1.18 | niche
numpy           | 1450000 downloads | log10: 6.16 | popular

Random spotlight: flask — Micro web framework
```