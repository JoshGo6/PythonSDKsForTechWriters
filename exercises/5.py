'''
## 5. Exercises

### Exercise 1: Clean and transform a raw commit message

You receive this raw commit message string from a script:
```
raw = "   fix: update broken links in API docs   "
```

Using only the string methods from this lesson and prior lessons, do the following in a script file named `lesson5_ex1.py`:

1. Strip the leading and trailing whitespace from `raw` and save the result to a variable named `cleaned`.
2. Print `cleaned`.
3. Replace `"fix: "` with `"FIXED: "` in `cleaned` and save the result to a variable named `labeled`.
4. Print `labeled`.
5. Split `labeled` on `" "` (a single space) and save the result to a variable named `words`.
6. Print `words`.
7. Print the first word in `words` using indexing.

Expected output (based on the input above):
```
fix: update broken links in API docs
FIXED: update broken links in API docs
['FIXED:', 'update', 'broken', 'links', 'in', 'API', 'docs']
FIXED:
```
'''

raw = "   fix: update broken links in API docs   "
cleaned = raw.strip()
labeled = cleaned.replace("fix", "FIXED")
print(labeled)
words = labeled.split()
print(words)
print(words[-2])

'''
---

### Exercise 2: Analyze a file path string

You have this string representing a file path returned from the API:
```
path = "  /DOCS/Reference/Authentication.MD  "
```

In a script named `lesson5_ex2.py`, do the following using only string methods from this lesson and prior lessons:

1. Strip whitespace from `path` and save it to `clean_path`.
2. Convert `clean_path` to lowercase and save it to `lower_path`. Print `lower_path`.
3. Check whether `lower_path` ends with `".md"` and print the result.
4. Check whether `lower_path` starts with `"/"` and print the result.
5. Find the index where `"authentication"` begins in `lower_path` and print the result.
6. Split `lower_path` on `"/"` and save the result to `parts`. Print `parts`.
7. Join `parts` using `" > "` as the separator and print the result. (This mimics a breadcrumb trail you might write in a doc.)
'''

path = "  /DOCS/Reference/Authentication.MD  "
clean_path = path.strip()
lower_path = clean_path.lower()
print(lower_path)
print(lower_path.startswith("/"))
first_appearance = lower_path.find("authentication")
print(first_appearance)
path_segments = lower_path.split("/")
print(path_segments)
path_segments = path_segments[1:]
print(path_segments)
breadcrumbs = ">".join(path_segments)
print(breadcrumbs)
breadcrumbs = "/" + breadcrumbs
print(breadcrumbs)
'''
Expected output:
```
/docs/reference/authentication.md
True
True
16
['', 'docs', 'reference', 'authentication.md']
 > docs > reference > authentication.mdDocstring for Untitled-2
'''
