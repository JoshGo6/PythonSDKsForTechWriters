'''
Docstring for 10a
Write a script that accepts a hard-coded list of strings (representing lines from a changelog or release note) and scans them for lines that contain **any** of the following keywords: `"fix"`, `"patch"`, `"security"`. The scan should be case-insensitive.

Use this list:

'''

lines = [
    "Added dark mode support",
    "Fixed crash on startup",
    "Security patch for token handling",
    "Improved pagination performance",
    "Patch applied to rate limiter",
    "Updated contributor guidelines",
    "Hotfix for null pointer exception",
    ]

count = 0
for line in lines:
    val = line.lower()
    if "fix" in val or "patch" in val or "security" in val:
        count +=1
        print(f"MATCH: {line}")
print (f"{count} line(s) matched.")

'''
Your script must:

1. Loop over all lines.
2. For each line, check whether it contains `"fix"`, `"patch"`, or `"security"` (case-insensitive).
3. Print only the matching lines, each preceded by `"[MATCH]"`.
4. After the loop, print a final count: `"X line(s) matched."`, where `X` is the number of matches found.

**Expected output:**

```
[MATCH] Fixed crash on startup
[MATCH] Security patch for token handling
[MATCH] Patch applied to rate limiter
[MATCH] Hotfix for null pointer exception
4 line(s) matched.
```

'''
