# Lesson 9: Loops I — `for` Loops Over Lists and Strings

## Terminology and Theory

**Iteration** is the act of moving through a sequence one element at a time and doing something with each element. When you have a list of repository names or a block of text, you rarely want to handle items one by one with hard-coded index numbers. Instead, you write a loop that walks through the sequence for you.

**`for` loop** is Python's primary tool for iteration. It takes each element from a sequence, assigns it to a temporary variable, and runs a block of code once per element. When the sequence is exhausted, the loop ends and execution continues with the next line after the loop body.

**Iterable** is any object Python can walk through element by element. For now, the iterables you know are lists and strings. A list yields its items; a string yields its individual characters.

**`range()`** is a built-in that produces a sequence of integers. It does not produce a list — it generates each number on demand — but you can loop over it exactly like a list. You will use `range()` when you need to repeat an action a specific number of times or when you need a numeric counter.

**Loop variable** is the name that receives each element during iteration. It exists as a normal variable and is overwritten on every pass through the loop. After the loop ends, it still holds the last value it was assigned.

**Loop body** is the indented block of code beneath the `for` line. Every line indented one level deeper than the `for` statement is part of the body and runs once per iteration.

> [!note]
> Python uses indentation — not braces or keywords — to define the loop body. Every line in the body must be indented by the same amount (conventionally four spaces).

## Syntax Section

### Basic `for` loop

```python
for variable in iterable:
    # body — runs once per element
```

`variable` is a name you choose. `iterable` is the sequence to walk through. The colon at the end of the `for` line is required. The body must be indented.

### Looping over a list

```python
for item in some_list:
    print(item)
```

On each pass, `item` is bound to the next element of `some_list`. The loop runs `len(some_list)` times total.

### Looping over a string

```python
for char in some_string:
    print(char)
```

On each pass, `char` is bound to the next single character of `some_string`.

### `range()` with one argument

```python
for i in range(5):
    print(i)
```

`range(5)` produces the integers `0, 1, 2, 3, 4` — five values starting from `0`. The stop value (`5`) is excluded.

### `range()` with two arguments

```python
for i in range(2, 6):
    print(i)
```

`range(2, 6)` produces `2, 3, 4, 5` — starting at `2` and stopping before `6`.

### `range()` with three arguments

```python
for i in range(0, 10, 3):
    print(i)
```

The third argument is the step. This produces `0, 3, 6, 9`.

### Accumulating a result across iterations

A common pattern is to create a variable before the loop and update it inside the loop body:

```python
total = 0
for num in number_list:
    total = total + num
print(total)
```

This works for building strings, too:

```python
result = ""
for word in word_list:
    result = result + word + " "
print(result.strip())
```

> [!tip] 
> Printing inside the loop body is the fastest way to verify that your loop is doing what you expect. When something goes wrong, add a `print()` inside the body as your first debugging step.

## Worked Examples

### Example 1 — Printing each item from a list of repo names

Suppose you pulled a list of repository names from an SDK and want to print each one with a numbered label.

```python
repos = ["docs-site", "api-client", "sdk-python", "changelog-tool"]

count = 1
for name in repos:
    print(f"{count}. {name}")
    count = count + 1
```

Output:

```
1. docs-site
2. api-client
3. sdk-python
4. changelog-tool
```

**What is happening:** The loop walks through `repos` one element at a time. On the first pass, `name` is `"docs-site"` and `count` is `1`. The f-string formats the output, and then `count` is incremented. On the next pass, `name` is `"api-client"` and `count` is `2`, and so on. After the loop ends, `count` holds `5` and `name` holds `"changelog-tool"`.

### Example 2 — Using `range()` to walk a list by index

Sometimes you need the index position itself, not just the element. You can use `range()` with the length of the list to get each valid index.

```python
labels = ["Title", "Author", "Version"]
values = ["SDK Guide", "Josh", "2.1"]

for i in range(3):
    print(f"{labels[i]}: {values[i]}")
```

Output:

```
Title: SDK Guide
Author: Josh
Version: 2.1
```

**What is happening:** `range(3)` produces `0, 1, 2`. On each pass, `i` is an integer index used to pull the matching element from both `labels` and `values`. This pattern is useful when you need to access the same position in two or more parallel lists simultaneously.

> [!note] 
> You could also write `range(len(labels))` instead of `range(3)`. `len()` returns the number of elements in a list, so this avoids hard-coding the length. `len()` has not been formally taught yet, but it is a simple built-in that takes a list (or string) and returns its length as an integer.

### Example 3 — Iterating over characters in a string

Looping over a string is useful when you need to inspect or transform text character by character.

```python
header = "README"

spaced = ""
for char in header:
    spaced = spaced + char + " "

print(spaced.strip())
```

Output:

```
R E A D M E
```

**What is happening:** The loop walks through the string `"README"` one character at a time. On each pass, it appends the current character followed by a space to the accumulator variable `spaced`. After the loop, `.strip()` removes the trailing space added after the final character.

## Quick Reference

```
# Loop over a list
$ python3 -c "for x in [1, 2, 3]: print(x)"
1
2
3

# Loop over a string
$ python3 -c "for ch in 'SDK': print(ch)"
S
D
K

# range() with one argument (stop)
$ python3 -c "for i in range(4): print(i)"
0
1
2
3

# range() with two arguments (start, stop)
$ python3 -c "for i in range(2, 5): print(i)"
2
3
4

# range() with three arguments (start, stop, step)
$ python3 -c "for i in range(0, 10, 2): print(i)"
0
2
4
6
8

# Accumulate a sum across a list
$ python3 -c "
total = 0
for n in [10, 20, 30]: total = total + n
print(total)"
60

# Loop variable persists after the loop ends
$ python3 -c "
for x in ['a', 'b', 'c']: pass
print(x)"
c
```

## Exercise

You are given the following nested list, which represents three SDK methods. Each inner list contains three strings: the method name, the HTTP verb, and the endpoint path.

```python
methods = [
    ["get_repo", "GET", "/repos/{owner}/{repo}"],
    ["create_issue", "POST", "/repos/{owner}/{repo}/issues"],
    ["update_pull", "PATCH", "/repos/{owner}/{repo}/pulls/{pull_number}"],
]
```

Write a script that:

1. Loops over `methods` and prints a formatted summary line for each method, using this exact format:

```
[1] get_repo — GET /repos/{owner}/{repo}
[2] create_issue — POST /repos/{owner}/{repo}/issues
[3] update_pull — PATCH /repos/{owner}/{repo}/pulls/{pull_number}
```

2. After the loop, prints a blank line, then prints a header `"Endpoint paths:"`, then loops over `methods` a second time and prints only the endpoint path from each inner list, lowercased, one per line:

```
/repos/{owner}/{repo}
/repos/{owner}/{repo}/issues
/repos/{owner}/{repo}/pulls/{pull_number}
```

3. After the second loop, prints a blank line, then prints the total number of characters across all three method names (the first element of each inner list). Use the following format:

```
Total characters in method names: 36
```

The complete expected output is:

```
[1] get_repo — GET /repos/{owner}/{repo}
[2] create_issue — POST /repos/{owner}/{repo}/issues
[3] update_pull — PATCH /repos/{owner}/{repo}/pulls/{pull_number}

Endpoint paths:
/repos/{owner}/{repo}
/repos/{owner}/{repo}/issues
/repos/{owner}/{repo}/pulls/{pull_number}

Total characters in method names: 36
```

---

## Audit

|Requirement|Introduced in|
|---|---|
|`print()`|Lesson 1|
|Variables and assignment|Lesson 2|
|`str`, `int` types|Lesson 2|
|String concatenation|Lesson 4|
|`.lower()`|Lesson 5|
|f-strings (`f"..."`)|Lesson 6|
|List literals, indexing|Lesson 7|
|Nested lists, chained indexing (`list[i][j]`)|Lesson 8|
|`for` loop over a list|Lesson 9 (current)|
|Accumulator pattern (variable before loop, update inside)|Lesson 9 (current)|
|`len()`|Introduced informally in Example 2 of Lesson 9; used here only on a string, which is a straightforward application of "a string is a sequence with a length"|

**Forward-dependency check:** The exercise does not require conditionals, dictionaries, functions, `range()`, file I/O, imports, or any other concept from Lesson 10 or later. All operations are `for` loops over a list, chained list indexing, f-strings, string methods, accumulation, and `print()`.

**Prior-lesson reinforcement:** The exercise reinforces Lesson 6 (f-strings for formatted output), Lesson 7 (list indexing), Lesson 8 (nested lists and chained indexing), and Lesson 5 (`.lower()`). It also reinforces Lesson 2 (variable assignment and integer arithmetic) and Lesson 4 (string concatenation via the accumulator pattern).