# Lesson 38b: Read objects and raise your own errors

Lesson 39 opens with two lines that look like they fight each other:

```python
response = requests.request(method, url, headers=HEADERS, timeout=10)
response.raise_for_status()
```

The second line looks like it overwrites the first. It does not. Nothing on that line binds a name, nothing changes `response`, and the line can stop your script dead without ever producing a value. This lesson explains why, because two pieces of Python that Lesson 39 assumes have never actually been taught: what a dot does, and what `raise` does.

It sits between Lessons 38 and 39 and introduces nothing else. Lessons 44 through 47 teach how objects are *built* — `class`, `__init__`, `self`, inheritance. You need none of that here. You only need to read objects other people built, which is what every SDK asks of you.

## The samples

Two samples run through the whole lesson. The first is the `issues` list you have used since Lesson 11, where the second issue is deliberately missing `user` and `labels`.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp", "labels": ["docs"]},
    {"number": 42, "title": "Fix the auth example"},
]
```

The second is the live GitHub REST API, which answers without a token. One URL exists and one does not, so every example can show both the success and the failure.

```python
GOOD = "https://api.github.com/repos/python/cpython"
BAD = "https://api.github.com/repos/python/no-such-repository-here"
```

> [!note] Unauthenticated GitHub allows 60 requests an hour
> Every request in this lesson is anonymous, so you share a per-IP budget of 60 an hour. Nothing here comes close, but if you loop over these URLs while experimenting you will start seeing `403` instead of `200`.

## Terminology and theory

Three words carry this lesson: object, method, and raise. The first two are about reading; the third is about control flow.

### An object carries data and functions together

An **object** is one value that holds data *and* the functions that work on it, bundled into a single thing you can pass around. `response` is one object. Inside it are the status code, the headers, the raw body — and also `json`, `raise_for_status`, and a dozen other functions that came attached.

The dot is how you reach inside. `response.status_code` means "the `status_code` that belongs to this particular response." Not to responses in general — to this one.

You have been using objects since Lesson 4 without the word. `"Rate Limit"` is a string object, and `.lower()` is one of the functions attached to it. `[1, 2, 3]` is a list object, and `.append()` is one of the functions attached to it. Nothing new is happening in `response.json()`; it is the same shape you already read.

### An attribute is data, a method is an action

An **attribute** is data stored on the object. You read it and no code runs: `response.status_code` is the number `200` sitting there.

A **method** is a function stored on the object. You call it with parentheses and code runs: `response.json()` parses the body and hands back a dict.

The parentheses are the entire difference, and they are not optional decoration. `response.json` without them does not parse anything — it hands you the function itself, unrun.

### Raising is the other way out of a function

A function can end in exactly two ways.

**`return`** hands a value back to whoever called it, and the caller carries on with that value in hand. This is the ending you know.

**`raise`** hands nothing back. It abandons the function mid-line and throws an exception object *upward* — to the caller, and to the caller's caller, and onward — until something catches it. If nothing does, Python gives up and prints the traceback.

You have only ever been on the catching side. `try`/`except` from Lesson 19 is the catcher's mitt. `raise` is the throw, and until now nothing in this curriculum has shown you how to make one. Every exception you have caught — `ValueError`, `KeyError`, `FileNotFoundError` — was thrown by a `raise` statement inside somebody else's function.

## Syntax

The first three sections below are about the dot, and answer the question "what did that line change?" The last three are about `raise`, and answer "where did control go?"

### Look for the `=` to see what a line changes

The `=` is the only thing in Python that rebinds a name. A line without one cannot make `response` mean something different, however many dots it has.

That is not the same as saying the line does nothing. Compare a method that changes a list against an assignment that replaces it, watched through a second name pointing at the same list — the two-names-one-list situation from Lesson 2.

```python
numbers = [1, 2, 3]
same_list = numbers          # two names, one list

numbers.append(4)            # no =, and the list itself changes
print("after .append(4)  — same_list:", same_list, "| numbers:", numbers)

numbers = numbers + [5]      # an =, so this is a NEW list bound to the old name
print("after = numbers+[5] — same_list:", same_list, "| numbers:", numbers)
```

After the `append`, both names show the change because there is still only one list. After the assignment, they disagree, because `numbers` now points at something else entirely.

```text
after .append(4)  — same_list: [1, 2, 3, 4] | numbers: [1, 2, 3, 4]
after = numbers+[5] — same_list: [1, 2, 3, 4] | numbers: [1, 2, 3, 4, 5]
```

Now the opposite case. `.lower()` builds a new string and hands it back; it cannot change the original, because strings are immutable (Lesson 5). Call it without an `=` and the result is thrown on the floor.

```python
title = "Rate Limit"

title.lower()                # the new string is created and immediately discarded
print("after the bare call:", title)

title = title.lower()        # the = is what keeps it
print("after the assignment:", title)
```

The first call is a real Python statement that really ran, and it accomplished nothing.

```text
after the bare call: Rate Limit
after the assignment: rate limit
```
/
### Expect one of three things from a method call

Those two blocks show two different behaviors, and there is a third. Every method call you meet does one of these, and knowing which tells you immediately whether the line needs an `=`.

| The method                                     | Needs an `=`                          | Example                            |
| ---------------------------------------------- | ------------------------------------- | ---------------------------------- |
| Builds a new value and returns it              | Yes, or the value is lost             | `title.lower()`, `response.json()` |
| Changes the object in place and returns `None` | No, and adding one destroys your data | `numbers.append(4)`                |
| Checks something and raises when it is wrong   | No, and there is nothing to assign    | `response.raise_for_status()`      |

`response.raise_for_status()` is the third kind. It looks at the status code, and either it raises `requests.exceptions.HTTPError` or it does nothing at all. On success it returns `None` — literally nothing worth keeping, which is exactly why the line has no `=` on it.

Here is that claim run against both URLs. Notice what the successful call returns.

```python
import requests

GOOD = "https://api.github.com/repos/python/cpython"
BAD = "https://api.github.com/repos/python/no-such-repository-here"

good = requests.get(GOOD, timeout=10)
print("good status :", good.status_code)
print("returns     :", good.raise_for_status())
print("after it, the script is still running")

bad = requests.get(BAD, timeout=10)
print("bad status  :", bad.status_code)
bad.raise_for_status()
print("this line never runs")
```

The `200` produces `None` and execution continues. The `404` produces no value at all, because control leaves the script at that line.

```text
good status : 200
returns     : None
after it, the script is still running
bad status  : 404
Traceback (most recent call last):
  File "/tmp/lesson38b/check.py", line 13, in <module>
    bad.raise_for_status()
  File "/usr/lib/python3/dist-packages/requests/models.py", line 1021, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://api.github.com/repos/python/no-such-repository-here
```

Read the middle frame of that traceback. It points into `requests`'s own source at a line that says `raise HTTPError(...)`. `raise_for_status` is an ordinary function with an ordinary `raise` statement inside it, and the traceback is showing you the exact line.

### Add the parentheses or nothing happens

An attribute is read without parentheses and a method is called with them, and swapping the two produces two different failures.

```python
import requests

response = requests.get("https://api.github.com/repos/python/cpython", timeout=10)

print("attribute, no parens:", response.status_code)
print("method, with parens :", response.json()["full_name"])
print("method, no parens   :", response.json)
```

The third line is the one to look at. Python is perfectly happy to hand you a function you did not call, and it prints as a `bound method` — bound meaning it is attached to this response and remembers which one.

```text
attribute, no parens: 200
method, with parens : python/cpython
method, no parens   : <bound method Response.json of <Response [200]>>
```

Calling an attribute fails loudly, because a number is not a function.

```python
response.status_code()
```

The message names the type it tried to call, which is usually enough to spot the stray parentheses.

```text
TypeError: 'int' object is not callable
```

> [!warning] A check you forget to call is a check that never runs
> `response.raise_for_status` without parentheses is not a syntax error and produces no warning. Python evaluates the method, discards it, and moves on. Your error handling is silently gone.

The failure is invisible, which is what makes it worth showing. Below, a genuine `404` sails straight past.

```python
import requests

response = requests.get("https://api.github.com/repos/python/no-such-repository-here",
                        timeout=10)
response.raise_for_status
print("nothing raised, and the script carried on:", response.status_code)
```

Nothing raised, nothing printed a warning, and the script reported the failure as though it were fine.

```text
nothing raised, and the script carried on: 404
```

### Return hands a value back, raise abandons the call

Now write a `raise` yourself. The syntax is the keyword, an exception type, and a message: `raise ValueError("what went wrong")`.

Issue 42 in the samples has no `user`. Nothing about it is illegal Python — it is a perfectly good dict that happens to be unusable for your purpose — so reading it raises nothing on its own. Here are the two ways a function can respond to that, side by side against the same data.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp", "labels": ["docs"]},
    {"number": 42, "title": "Fix the auth example"},
]


def user_or_none(issue):
    """Hand back the user, or None when the issue has no user."""
    if "user" not in issue:
        return None
    return issue["user"]


def user_or_raise(issue):
    """Hand back the user. Refuse to return at all when the issue has no user."""
    if "user" not in issue:
        raise ValueError(f"issue #{issue['number']} has no user")
    return issue["user"]


print("returned:", user_or_none(issues[1]))
print("still running")
print("raised  :", user_or_raise(issues[1]))
print("this line never runs")
```

The first call comes back with `None` and the script continues. The second never comes back at all, so the `print()` wrapped around it never gets a value to print.

```text
returned: None
still running
Traceback (most recent call last):
  File "/tmp/lesson38b/issues.py", line 23, in <module>
    print("raised  :", user_or_raise(issues[1]))
                       ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/lesson38b/issues.py", line 17, in user_or_raise
    raise ValueError(f"issue #{issue['number']} has no user")
ValueError: issue #42 has no user
```

Pick the exception type that describes the problem: `ValueError` for content you cannot use, `TypeError` for the wrong kind of thing, `FileNotFoundError` for a missing path. A caller then catches yours the same way they catch the library's.

### Watch a raised exception climb until something catches it

A `raise` does not stop at the function that made it. It climbs through every caller in turn, and the first `except` clause that matches the type wins. Put a middle function between the raise and the loop, one that catches nothing.

```python
def line_for(issue):
    """Nothing here catches anything. The exception passes straight through."""
    return f"#{issue['number']} {issue['title']} ({user_or_raise(issue)})"


for issue in issues:
    print(line_for(issue))
```

Issue 41 formats fine. Issue 42 raises `ValueError` two calls deep, and because nothing catches it, the traceback records the whole climb — bottom frame is where it was raised, top frame is the loop it escaped to.

```text
#41 Document the rate limit (kmp)
Traceback (most recent call last):
  File "/tmp/lesson38b/report.py", line 19, in <module>
    print(line_for(issue))
          ^^^^^^^^^^^^^^^
  File "/tmp/lesson38b/report.py", line 15, in line_for
    return f"#{issue['number']} {issue['title']} ({user_or_raise(issue)})"
                                                   ^^^^^^^^^^^^^^^^^^^^
  File "/tmp/lesson38b/report.py", line 9, in user_or_raise
    raise ValueError(f"issue #{issue['number']} has no user")
ValueError: issue #42 has no user
```

Wrap the loop body in the `try`/`except` you already know and the climb stops there instead. `line_for` is unchanged; it still does not catch anything.

```python
for issue in issues:
    try:
        print(line_for(issue))
    except ValueError as exc:
        print("skipped:", exc)
```

The `as exc` binds the exception object that was raised, and printing it prints the message you wrote into it. This is the payoff of raising rather than returning `None`: the bad record announces itself by number instead of vanishing.

```text
#41 Document the rate limit (kmp)
skipped: issue #42 has no user
```

### Read `response.raise_for_status()` as a check that can raise

Everything in Lesson 39 now reads. `raise_for_status` is a method attached to the response, it checks the status code, and it raises `requests.exceptions.HTTPError` when the code is a refusal.

Written with only what you have met — as a plain function taking the response as a parameter — it is about this long.

```python
import requests


def my_raise_for_status(response):
    """The same check, written with only what you have already met."""
    if response.status_code >= 400:
        raise requests.exceptions.HTTPError(
            f"{response.status_code} {response.reason} for url: {response.url}")
    return None


bad = requests.get(BAD, timeout=10)
print("my version returns:", my_raise_for_status(requests.get(GOOD, timeout=10)))
my_raise_for_status(bad)
```

It behaves the way the real one did — `None` on the `200`, an `HTTPError` on the `404`.

```text
my version returns: None
Traceback (most recent call last):
  File "/tmp/lesson38b/mine.py", line 17, in <module>
    my_raise_for_status(bad)
  File "/tmp/lesson38b/mine.py", line 10, in my_raise_for_status
    raise requests.exceptions.HTTPError(
requests.exceptions.HTTPError: 404 Not Found for url: https://api.github.com/repos/python/no-such-repository-here
```

The real one differs in two ways that do not change the idea. It is attached to the response rather than taking it as a parameter, so its source says `self` where mine says `response` — Lesson 44 covers that keyword and you do not need it yet. And it separates `4xx` from `5xx` so the message can say `Client Error` or `Server Error`, where mine prints the reason phrase alone.

## Worked examples

Three examples, each one a pattern you will reuse. The first two raise from your own code; the third catches one raised by `requests`.

### Example 1: name the record in every message you raise

The message is the part that matters. `raise ValueError("bad data")` inside a loop over 400 records tells you nothing about which record, and you will be reading that message at the worst possible moment.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp", "labels": ["docs"]},
    {"number": 42, "title": "Fix the auth example"},
]


def field(issue, name):
    """Return one field, or raise a message that identifies the record."""
    if name not in issue:
        raise ValueError(f"issue #{issue['number']} has no {name}")
    return issue[name]


for issue in issues:
    for name in ("title", "user", "labels"):
        try:
            print(f"#{issue['number']} {name}: {field(issue, name)}")
        except ValueError as exc:
            print("  missing:", exc)
```

Two fields are missing from issue 42, and each reports itself by number and by field name.

```text
#41 title: Document the rate limit
#41 user: kmp
#41 labels: ['docs']
#42 title: Fix the auth example
  missing: issue #42 has no user
  missing: issue #42 has no labels
```

### Example 2: choose between raising and returning None

Both endings are legitimate, and the choice is about who is responsible for noticing. Return `None` when the absence is ordinary and the caller will obviously check for it. Raise when carrying on would produce a wrong answer quietly.

Here is the quiet wrong answer, which is the failure mode that costs you an afternoon.

```python
def user_or_none(issue):
    if "user" not in issue:
        return None
    return issue["user"]


owners = []
for issue in issues:
    owners.append(user_or_none(issue))

print("owners:", owners)
print("count of owned issues:", len(owners))
```

The count is wrong and nothing anywhere said so. `None` went into the list as though it were a username.

```text
owners: ['kmp', None]
count of owned issues: 2
```

Raising instead forces the caller to decide what to do, at the moment the bad record is read rather than five steps downstream.

```python
owners = []
for issue in issues:
    try:
        owners.append(user_or_raise(issue))
    except ValueError as exc:
        print("excluded:", exc)

print("owners:", owners)
print("count of owned issues:", len(owners))
```

The bad record is named, excluded, and the count is right.

```text
excluded: issue #42 has no user
owners: ['kmp']
count of owned issues: 1
```

### Example 3: catch the exception and read the response off it

`raise_for_status()` raises `requests.exceptions.HTTPError`, and it attaches the response to the exception before throwing it. Catching the exception therefore does not cost you the reply — `exc.response` is the same `Response` object you would have had.

```python
import requests

for url in (GOOD, BAD):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print("OK  ", response.json()["full_name"])
    except requests.exceptions.HTTPError as exc:
        print("FAIL", exc.response.status_code, exc.response.reason)
        print("     body:", exc.response.json()["message"])
```

The successful URL never enters the handler. The failing one does, and the handler still reaches the status, the reason phrase, and GitHub's own explanation in the body.

```text
OK   python/cpython
FAIL 404 Not Found
     body: Not Found
```

> [!note] `exc.response` is `None` when nothing ever replied
> A `404` is a reply, so there is a response to attach. A connection refused or a timeout is not a reply, and those exceptions carry `exc.response` as `None`. Lesson 39 handles that case; here, every exception you catch is an `HTTPError` and always has one.

## Lookup table

| Use when | Call | Result |
| --- | --- | --- |
| Read data stored on an object | `response.status_code` | `200` — no code runs, no parentheses |
| Run a function stored on an object | `response.json()` | `{'id': 81598961, 'node_id': …, 'name': 'cpython', 'full_name': 'python/cpython', …}` — the parsed body |
| See what a method is without running it | `response.json` | `<bound method Response.json of <Response [200]>>` |
| Call something that is not a function | `response.status_code()` | raises `TypeError`: `'int' object is not callable` |
| Change a list without rebinding its name | `numbers.append(4)` | returns `None`; the list itself now ends in `4` |
| Keep the result of a method that builds a new value | `title = title.lower()` | `'rate limit'`; without the `=` the new string is discarded |
| Stop a function and report unusable data | `raise ValueError(f"issue #{n} has no user")` | raises `ValueError`; the function never returns |
| Stop the script on an HTTP refusal | `response.raise_for_status()` | `None` on `2xx`; raises `requests.exceptions.HTTPError` on `4xx` and `5xx` |
| Forget the parentheses on that check | `response.raise_for_status` | returns the method, unrun — the check silently never happens |
| Catch a refusal raised by `requests` | `except requests.exceptions.HTTPError as exc:` | binds the exception; `str(exc)` is `404 Client Error: Not Found for url: …` |
| Reach the reply from inside the handler | `exc.response.status_code` | `404` — the same `Response` the call produced |
| Read the API's own error text after catching | `exc.response.json()` | `{'message': 'Not Found', 'documentation_url': …, 'status': '404'}` — GitHub's error body |

## Exercise: check a repository plan against the GitHub API

Write `check_plan.py`, which reads a plan file of repositories, checks each one against the GitHub REST API, and reports every entry that fails — whether the plan is bad or the API refused.

### Save the plan file

Save this as `plan.json` beside your script. The third entry is deliberately incomplete and the second names a repository that does not exist.

```json
[
  {"repo": "python/cpython", "owner": "kmp"},
  {"repo": "python/no-such-repository-here", "owner": "rivera"},
  {"repo": "psf/requests"}
]
```

### Requirements

Your script must do all of the following.

1. Load `plan.json` from disk and parse it.
2. Write a function that returns an entry's `owner`, and raises `ValueError` with a message naming the repository when the entry has no `owner`.
3. Write a function that takes a `full_name` like `python/cpython`, requests `https://api.github.com/repos/{full_name}`, calls `raise_for_status()`, and returns the parsed body. It must not catch anything.
4. Loop over the plan. For each entry, print one line: `OK` with the repository's `full_name`, `default_branch`, `language`, and the owner from the plan; or `FAIL` with the reason.
5. Handle the two failures separately, in two `except` clauses. A plan error must report the message you raised. An HTTP failure must report the status code and reason phrase read off the exception.
6. Finish with a count of how many succeeded and how many failed.

### Expected output

Your line format may differ, but the three verdicts and the counts must match.

```text
OK    python/cpython — main, Python, owner kmp
FAIL  python/no-such-repository-here: 404 Not Found
FAIL  plan error: psf/requests has no owner in the plan

1 checked, 2 failed
```
