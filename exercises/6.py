
filename = "  contributing.md  "
status   = "modified"
editor   = "jsmith"
line_count = 312

filename = filename.strip().lower()
status = status.upper()
editor = editor.upper()

print(f"[{status}] {filename} ― {line_count} lines — editor: {editor}")

'''
Your f-string must:

1. Strip the whitespace from `filename` and display it in lowercase.
2. Display `status` in uppercase.
3. Display `editor` in uppercase.
4. Include `line_count` as a number.

Expected output (exactly):
```
[MODIFIED] contributing.md — 312 lines — editor: JSMITH
'''

