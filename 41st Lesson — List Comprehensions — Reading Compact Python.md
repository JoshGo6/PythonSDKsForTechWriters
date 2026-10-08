# Lesson 41: Read list comprehensions as the loops they replace

A list comprehension builds a new list in one line by evaluating an expression once for every item in an existing iterable, optionally skipping items that fail a test. This lesson teaches you to read one by mentally unpacking it into the `for` loop it replaces, and it has you write both the plain form and the filtered form yourself. It does not cover dict comprehensions, set comprehensions, nested comprehensions, or generator expressions — recognizing the two list forms below is enough for every SDK example ahead, and you will not meet the others in this curriculum.

Lesson 40 taught you to read a flexible signature. This lesson teaches you to read the compact line that usually builds the dict you spread into one: `repo.get_issues(**filters)` from the roadmap is easy to read once you can also read `{k: v for k, v in pairs}`'s list cousin, which is exactly what this lesson covers.

## The samples

Two samples run through this lesson, both carried over from Lesson 40. The first is the `issues` list, where the second issue is deliberately missing `user` and `labels`.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp",
     "labels": ["docs", "rate-limit"]},
    {"number": 42, "title": "Fix the auth example"},
]
```

The second is the same live GitHub REST endpoint Lesson 40 used, which answers without a token.

```python
ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
```

Run everything in the virtual environment you built in Lesson 33, with `requests` installed as Lesson 37 had you do.

```bash
mkdir ~/lesson41 && cd ~/lesson41
python3 -m venv venv
./venv/bin/pip install requests
```

> [!note] Unauthenticated GitHub allows 60 requests an hour
> Every request in this lesson is anonymous, so it shares a per-IP budget of 60 an hour. Nothing here comes close, but re-running the worked examples in a tight loop while experimenting will start returning `403` instead of `200`.

## Terminology and theory

Two ideas carry this lesson: the loop a comprehension always stands for, and the two different-looking uses of `if` that show up inside one.

### A list comprehension is a for loop and an append written as one expression

An **expression** is anything Python can evaluate down to a single value: `issue["title"]`, `len(issues)`, and `"labeled" if issue.get("labels") else "unlabeled"` are all expressions. A **list comprehension** is a single expression, written between square brackets, that produces a whole list by evaluating one expression once per item of an iterable.

Every list comprehension you will ever read can be unpacked into the same three lines: start with an empty list, loop over the iterable, and append the expression's result on each pass. That equivalence is the only thing you need to memorize — everything else in this lesson is a variation on it.

```python
titles = []
for issue in issues:
    titles.append(issue["title"])
```

The comprehension below produces the exact same list from the exact same fixture.

```python
titles = [issue["title"] for issue in issues]
```

Read the comprehension left to right and the pieces line up with the loop above: the expression before `for` is what got appended, `for issue in issues` is the loop line, and there is no visible `titles = []` or `.append()` because the brackets supply both.

### A trailing `if` filters; an `if`/`else` before `for` chooses a value

Two different-looking uses of `if` show up inside comprehensions, and confusing them produces a list of the wrong length instead of an error. A **filter clause** sits after the `for` and decides whether an item is skipped entirely — the resulting list can be shorter than the iterable it came from. A **conditional expression** sits before the `for`, as part of what gets evaluated, and it never skips anything — every item still produces one entry, just a different value depending on the test. Lesson 14's truthiness and Lesson 12's ternary `x if cond else y` are exactly the pieces each form is built from; this lesson only introduces where they sit relative to `for`.

## Syntax

The four patterns below cover every list comprehension you will meet in the lessons ahead. The first two teach the bracket shape itself; the third is the confusable pair from the theory section, made concrete; the fourth shows that the expression can be a function call rather than a bare lookup.

### Unpack the plain form into its equivalent loop

One expression, one `for`, no `if` at all: every item in the iterable produces exactly one entry in the new list.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp",
     "labels": ["docs", "rate-limit"]},
    {"number": 42, "title": "Fix the auth example"},
]

titles_loop = []
for issue in issues:                 # the for loop this comprehension replaces
    titles_loop.append(issue["title"])

titles_comp = [issue["title"] for issue in issues]   # the comprehension itself

print(titles_loop)
print(titles_comp)
print(titles_loop == titles_comp)
```

Both lists come out identical, because the comprehension is not a different operation — it is the loop above with the bracket syntax supplying the `[]` and the `.append()`.

```text
['Document the rate limit', 'Fix the auth example']
['Document the rate limit', 'Fix the auth example']
True
```

### Filter what enters the list with a trailing if

Adding `if condition` after the `for` reuses the same `.get()` truthiness check from Lesson 11 and Lesson 14, now deciding whether an item is appended at all.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp",
     "labels": ["docs", "rate-limit"]},
    {"number": 42, "title": "Fix the auth example"},
]

labeled_loop = []
for issue in issues:
    if issue.get("labels"):          # the filter this comprehension's trailing `if` replaces
        labeled_loop.append(issue["title"])

labeled_comp = [issue["title"] for issue in issues if issue.get("labels")]

print(labeled_loop)
print(labeled_comp)
print(len(issues), "issues in,", len(labeled_comp), "with labels")
```

Issue 42 has no `labels` key, `.get("labels")` returns `None`, and `None` is falsy — so it never reaches either list, and two issues in produce only one issue out.

```text
['Document the rate limit']
['Document the rate limit']
2 issues in, 1 with labels
```

### Distinguish the filter from a conditional expression

Put the filtered form beside a conditional-expression form built from the same test, and the difference the theory section named becomes visible in the counts: one form can shrink the list, and the other cannot.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp",
     "labels": ["docs", "rate-limit"]},
    {"number": 42, "title": "Fix the auth example"},
]

filtered = [issue["title"] for issue in issues if issue.get("labels")]                       # can shrink the list
labeled_or_not = ["labeled" if issue.get("labels") else "unlabeled" for issue in issues]      # cannot

print(len(issues), "issues total")
print(len(filtered), "kept by the trailing if:", filtered)
print(len(labeled_or_not), "kept by the conditional expression:", labeled_or_not)
```

`filtered` drops issue 42 the same way the previous example did. `labeled_or_not` keeps both issues and instead records which one lacked labels, so its length always matches `issues`.

```text
2 issues total
1 kept by the trailing if: ['Document the rate limit']
2 kept by the conditional expression: ['labeled', 'unlabeled']
```

> [!warning] A conditional expression with no `else` is not legal here
> `[x if cond for x in items]` raises `SyntaxError: expected 'else' after 'if' expression` — the conditional expression form always needs both branches. Only the filter clause after `for` is optional to omit the other side of.

### Call a function from inside the expression

The expression before `for` can be any expression, including a call to a function you wrote yourself — this is the shape behind `repo.get_issues(**filters)`-style SDK reads, where the comprehension's job is formatting, not just extracting a field.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp",
     "labels": ["docs", "rate-limit"]},
    {"number": 42, "title": "Fix the auth example"},
]


def report_line(issue, state="open"):
    """A default parameter, exactly as in Lesson 16."""
    return f"#{issue['number']} [{state}] {issue['title']}"


lines = [report_line(issue) for issue in issues]
for line in lines:
    print(line)
```

`report_line` runs once per issue, and every call still gets `state`'s default of `"open"` because the comprehension never passes one.

```text
#41 [open] Document the rate limit
#42 [open] Fix the auth example
```

## Worked examples

Three examples, each against the live GitHub endpoint from Lesson 37 onward. The first applies the plain form to real API data, the second uses a filter clause to solve a genuine problem in that data, and the third combines a filter with a function call to produce a docs-ready summary.

### Example 1: turn an API response into a report with one comprehension line

`requests.get` returns a list of dicts once you call `.json()` on the response, exactly the shape the `issues` fixture has been standing in for. One comprehension line replaces the report loop you would otherwise write by hand.

```python
import requests

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "sort": "created", "direction": "asc", "per_page": 5}

response = requests.get(ISSUES_URL, params=params, timeout=10)
response.raise_for_status()
issues = response.json()

lines = [f"#{issue['number']} [{issue['state']}] {issue['title']}" for issue in issues]

for line in lines:
    print(line)
```

Sorting `asc` by `created` asks for the oldest issues first, which is why this output reproduces on your machine exactly as shown — the repository's oldest history does not change.

```text
#1 [closed] Cookie support?
#2 [closed] a "40x" error my have content
#3 [closed] Eventlet Support
#4 [closed] Updates and Cleanup
#5 [closed] Case-Insensitive MultiDict for Headers
```

### Example 2: filter out pull requests hiding in the issues endpoint

GitHub's issues endpoint quietly mixes in pull requests along with actual issues — a pull request is also, in GitHub's data model, an issue. The one field that tells them apart is a `pull_request` key, present only on the entries that are really pull requests. Issue 4 above is one of them, which is exactly the kind of case a filter clause exists for.

```python
import requests

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "sort": "created", "direction": "asc", "per_page": 5}

response = requests.get(ISSUES_URL, params=params, timeout=10)
response.raise_for_status()
issues = response.json()

issues_only = [issue for issue in issues if "pull_request" not in issue]

print(len(issues), "entries returned by the issues endpoint")
print(len(issues_only), "are actually issues")
for issue in issues_only:
    print(f"#{issue['number']} {issue['title']}")
```

Five entries come back and only four survive the filter — issue 4 is missing, because it is the pull request the `not in` test caught.

```text
5 entries returned by the issues endpoint
4 are actually issues
#1 Cookie support?
#2 a "40x" error my have content
#3 Eventlet Support
#5 Case-Insensitive MultiDict for Headers
```

### Example 3: combine a filter with a function that has a default parameter

A docs report usually needs titles kept to a consistent width as well as the pull requests filtered out. `format_issue` supplies that with a default parameter exactly as Lesson 16 taught, and the comprehension calls it once per surviving issue.

```python
import requests

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "sort": "created", "direction": "asc", "per_page": 5}


def format_issue(issue, max_len=30):
    """A default parameter, exactly as in Lesson 16: most callers take it as is."""
    title = issue["title"]
    if len(title) > max_len:
        title = title[:max_len].rstrip() + "..."
    return f"#{issue['number']} {title}"


response = requests.get(ISSUES_URL, params=params, timeout=10)
response.raise_for_status()
issues = response.json()

summary = [format_issue(issue) for issue in issues if "pull_request" not in issue]

print(len(summary), "of", len(issues), "results were real issues")
for line in summary:
    print(line)
```

Issue 5's title is 38 characters, longer than the 30-character default, so it alone comes back cut short with `...` — proof that the default parameter is doing real work rather than being silently ignored.

```text
4 of 5 results were real issues
#1 Cookie support?
#2 a "40x" error my have content
#3 Eventlet Support
#5 Case-Insensitive MultiDict for...
```

## Lookup table

| Use when | Call | Result |
| --- | --- | --- |
| Build a new list from an iterable | `[issue["title"] for issue in issues]` | `['Document the rate limit', 'Fix the auth example']` |
| Filter which items enter the list | `[issue["title"] for issue in issues if issue.get("labels")]` | `['Document the rate limit']` — one issue in has no `labels` |
| Keep every item but choose its value | `["labeled" if issue.get("labels") else "unlabeled" for issue in issues]` | `['labeled', 'unlabeled']` — same length as `issues` |
| Test whether a dict is missing a key, as the filter | `[issue for issue in issues if "pull_request" not in issue]` | four of five entries kept; the pull request is dropped |
| Call a function inside the expression | `[report_line(issue) for issue in issues]` | `['#41 [open] Document the rate limit', '#42 [open] Fix the auth example']` |
| Rely on a function's default inside a comprehension | `[format_issue(issue) for issue in issues]` | titles over 30 characters come back truncated with `...` |
| Write a conditional expression with no filter | `[x if cond for x in items]` | raises `SyntaxError: expected 'else' after 'if' expression` |

## Exercise: turn a mixed API response into a clean issue report

Write `repo_report.py`, which fetches issues from a real repository, separates the pull requests out from the real issues, and prints a formatted report.

Your script must do all of the following.

1. Send a GET request to `https://api.github.com/repos/psf/requests/issues` with `params={"state": "closed", "sort": "created", "direction": "asc", "per_page": 8}` and `timeout=10`, then call `raise_for_status()` on the response before reading anything else.
2. Parse the JSON body into a variable named `issues`.
3. The entries returned mix real issues with pull requests, told apart by a `pull_request` key that appears only on the latter. The following loop builds the entries that are not pull requests:

   ```python
   real_issues = []
   for issue in issues:
       if "pull_request" not in issue:
           real_issues.append(issue)
   ```

   Rewrite it as a single list comprehension, assigned to the same name.
4. Write `format_issue(issue, max_len=40)`, a function with a default parameter, that returns `f"#{issue['number']} {title}"` and truncates `title` to `max_len` characters followed by `"..."` when the title is longer than that.
5. Build `lines`, a list comprehension over `real_issues` that calls `format_issue` on each entry.
6. Build `flags`, a list comprehension over the full `issues` list — not `real_issues` — using a conditional expression rather than a filter clause: each entry becomes `"PR"` when it carries a `pull_request` key and `"issue"` otherwise. Every entry in `issues` must produce one entry in `flags`.
7. Print, in this order: a line stating how many entries came back and how many were real issues; every line from `lines`, one per line; and a final line joining `flags` with `", "`.

### Expected output

Your wording may differ, but the counts and the report lines must match.

```text
8 entries returned, 6 were real issues
#1 Cookie support?
#2 a "40x" error my have content
#3 Eventlet Support
#5 Case-Insensitive MultiDict for Headers
#6 parse url parameter and set params
#7 POST + file + auth
issue, issue, issue, PR, issue, issue, issue, PR
```
