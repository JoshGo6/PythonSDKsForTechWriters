'''
Your script must:

1. Extract the first tag from `tag_string` using `.split()` and indexing.
2. Calculate and display the ratio of open issues to total as a percentage with one decimal place.
3. Print all four lines shown below, aligned so the values start in the same column.

Expected output (values must match, spacing may vary slightly):
```
Repo        : sdk-reference
Primary tag : docs
Open issues : 9 of 25
Open rate   : 36.0%
'''

repo       = "sdk-reference"
tag_string = "docs,sdk,python,reference"
open_count = 9
total      = 25

print(f"{"repo":<12}: {repo}")
print(f"{"Primary tag":<12}: {tag_string.split(",")[0]}")
print(f"{"Open issues":<12}: {open_count} of {total}")
print(f"{"Open rate":<12}: {open_count/total:.1%}")
