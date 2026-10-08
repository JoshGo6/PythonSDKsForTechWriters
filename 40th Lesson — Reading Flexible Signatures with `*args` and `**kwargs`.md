# Lesson 40: Read flexible signatures written with `*args` and `**kwargs`

`def get(url, params=None, **kwargs)` is the real signature of `requests.get`, and its last parameter says "and anything else you care to pass." A star can appear in a `def` line or in a call, singly or doubled, and those four positions decide what a function will accept and what a call actually sends. This lesson teaches you to read all four.

You have depended on one of them since Lesson 1. `print("a", "b", "c")` takes three values and `print("a")` takes one, because `print`'s own signature is `print(*args, sep=' ', end='\n', file=None, flush=False)`. The star in front of `args` is what makes the count flexible.

This lesson is about reading and calling flexible signatures rather than designing them. SDK reference pages are full of lines like `def create_issue(self, *args, **kwargs)`, and by the end of this lesson every part of that line reads except `self`, which belongs to Lesson 43. Nothing here needs a `class`, and nothing here writes one.

## The samples

Two samples run through the whole lesson. The first is the `issues` list you have used since Lesson 11, where the second issue is deliberately missing `user` and `labels`.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp",
     "labels": ["docs", "rate-limit"]},
    {"number": 42, "title": "Fix the auth example"},
]
```

The second is one live GitHub REST endpoint, which answers without a token.

```python
ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
```

Every request below asks that endpoint for the *oldest* issues on the repository, so the results are historic and the output on this page reproduces on your machine. Run everything in the virtual environment you built in Lesson 33, with `requests` installed as Lesson 37 had you do.

```bash
mkdir ~/lesson40 && cd ~/lesson40
python3 -m venv venv
./venv/bin/pip install requests
```

> [!note] Unauthenticated GitHub allows 60 requests an hour
> Every request in this lesson is anonymous, so you share a per-IP budget of 60 an hour. Nothing here comes close, but if you loop over the endpoint while experimenting you will start seeing `403` instead of `200`.

## Terminology and theory

Three ideas carry this lesson: the difference between the two kinds of argument, the difference between a star in a definition and a star in a call, and what type each star hands you inside the function.

### A positional argument is matched by place, a keyword argument by name

A **positional argument** is matched to a parameter by where it sits in the call. A **keyword argument** is matched by name, written `name=value`, and its position does not matter. Every call you have written since Lesson 15 used one or the other, and most used both.

```python
def report_line(number, title, state="open"):
    """Two required parameters and one with a default, as in Lesson 16."""
    return f"#{number} {title} [{state}]"


print(report_line(41, "Document the rate limit"))
print(report_line(number=42, title="Fix the auth example"))
print(report_line(42, state="closed", title="Fix the auth example"))
```

The third call passes `state` before `title` and still works, because both are matched by name rather than by place.

```text
#41 Document the rate limit [open]
#42 Fix the auth example [open]
#42 Fix the auth example [closed]
```

That distinction is the whole reason there are two stars instead of one. One star handles the arguments matched by place; two stars handle the arguments matched by name.

### A star in a definition collects, and a star in a call spreads

Keep this sentence and the rest of the lesson follows from it. The same punctuation does opposite things depending on which side of the call it sits on.

| Where the star sits | What it does |
| --- | --- |
| In a `def` line | Collects the arguments the named parameters did not take, into one value |
| In a call | Spreads one value out into separate arguments |

`def show(*args)` collects: a call passing three strings arrives inside the function as one tuple of three strings. `show(*labels)` spreads: one list sitting in a variable arrives inside the function as separate arguments. Reading a line wrongly in this direction is the single most common mistake with this syntax, and it produces a wrong answer rather than an error.

### `args` collects into a tuple and `kwargs` collects into a dict

The names `args` and `kwargs` are convention rather than syntax — the stars do the work, and `*things` behaves identically. What the stars produce is fixed, though.

`*args` gives you a **tuple**, the immutable sequence from Lesson 13. `**kwargs` gives you a **dict**, so you read it with the `.get()` and `.items()` you learned in Lessons 11 and 12. Both are ordinary values once inside the function, which is why the next section can just print them.

## Syntax

The first three sections below are about the stars in a `def` line, and answer "what did this function receive?" The last four are about the stars in a call, and answer "what did I actually send?"

### Collect extra positional arguments with `*args`

One star in front of a parameter name collects every positional argument the earlier parameters did not take. Print it and its type to see what arrived.

```python
def show(*args):
    print(f"{len(args)} positional argument(s), collected as {args} of {type(args)}")


show()
show("docs")
show("docs", "rate-limit")
```

A call with no arguments at all is legal and produces the empty tuple, which matters because your code then has to survive it.

```text
0 positional argument(s), collected as () of <class 'tuple'>
1 positional argument(s), collected as ('docs',) of <class 'tuple'>
2 positional argument(s), collected as ('docs', 'rate-limit') of <class 'tuple'>
```

The single-item tuple prints as `('docs',)` with a trailing comma, which is the "comma makes a tuple" notation from Lesson 13 rather than a typo in the output.

### Collect extra keyword arguments with `**kwargs`

Two stars collect every keyword argument no named parameter claimed, and hand them over as a dict keyed by the names the caller used.

```python
def show_options(**kwargs):
    print(f"{len(kwargs)} keyword argument(s), collected as {kwargs} of {type(kwargs)}")


show_options()
show_options(state="closed")
show_options(state="closed", per_page=3)
```

The keys are strings even though the caller wrote them as bare names, so `kwargs["state"]` and `kwargs.get("state")` are how you read them back.

```text
0 keyword argument(s), collected as {} of <class 'dict'>
1 keyword argument(s), collected as {'state': 'closed'} of <class 'dict'>
2 keyword argument(s), collected as {'state': 'closed', 'per_page': 3} of <class 'dict'>
```

### Put required parameters first, then `*args`, then `**kwargs`

The order is fixed: ordinary parameters, then the one-star parameter, then the two-star parameter. Reading a signature left to right therefore tells you exactly which arguments are required and which are optional overflow.

Here all three appear together, run against the `issues` sample. The second issue has no `labels` key, so `.get("labels", [])` from Lesson 11 supplies an empty list and the spread sends nothing.

```python
issues = [
    {"number": 41, "title": "Document the rate limit", "user": "kmp",
     "labels": ["docs", "rate-limit"]},
    {"number": 42, "title": "Fix the auth example"},
]


def label_line(number, *labels, **options):
    """`number` is required, `labels` takes the rest, `options` takes any names."""
    prefix = options.get("prefix", "#")
    joined = ", ".join(labels) or "(none)"
    return f"{prefix}{number} labels: {joined}"


for issue in issues:
    print(label_line(issue["number"], *issue.get("labels", [])))

print(label_line(41, "docs", prefix="issue "))
```

Issue 42 reaches `label_line` with an empty `labels` tuple, `", ".join(())` is the empty string, and the truthiness check from Lesson 14 turns that into `(none)`.

```text
#41 labels: docs, rate-limit
#42 labels: (none)
issue 41 labels: docs
```

A parameter written after `*args` can only be passed by name, because every positional argument has already been swallowed by the star. That is exactly why `print("a", "b", sep=" | ")` has to write `sep=`.

```python
def line(*parts, sep=" - "):
    """`sep` sits after `*parts`, so it can only be passed by name."""
    return sep.join(parts)


print(line("#41", "Document the rate limit"))
print(line("#41", "Document the rate limit", sep=" | "))
print(line("#41", "Document the rate limit", " | "))
```

The third call is the trap. Passing the separator positionally raises nothing at all — the string is simply collected into `parts` as a third thing to join.

```text
#41 - Document the rate limit
#41 | Document the rate limit
#41 - Document the rate limit -  |
```

> [!warning] A missing `=` on a keyword-only argument fails silently
> `line("a", "b", " | ")` is valid Python that runs, returns a string, and gets the separator wrong. Nothing warns you, so when output from a `*args` function looks subtly wrong, check whether an option went in positionally.

### Spread a list into positional arguments with one star

A star in a *call* takes one list or tuple apart and passes its items as separate arguments. Without the star, the list itself is one argument. Both forms are legal, so put them side by side against the same `show` from above.

```python
def show(*args):
    print(f"{len(args)} positional argument(s), collected as {args} of {type(args)}")


labels = ["docs", "rate-limit"]

show(labels)      # one argument: the list itself
show(*labels)     # two arguments: the strings inside it
```

The first call sends a tuple containing a list. The second sends a tuple containing two strings, and only the second is what a function expecting separate values wants.

```text
1 positional argument(s), collected as (['docs', 'rate-limit'],) of <class 'tuple'>
2 positional argument(s), collected as ('docs', 'rate-limit') of <class 'tuple'>
```

### Spread a dict into keyword arguments with two stars

Two stars in a call turn each key of a dict into a keyword argument. This is the form that appears everywhere in SDK examples, because it lets you build a call's options as data and then send them in one line.

```python
def show_options(**kwargs):
    print(f"{len(kwargs)} keyword argument(s), collected as {kwargs} of {type(kwargs)}")


filters = {"state": "closed", "per_page": 3}

show_options(**filters)   # two keyword arguments: state= and per_page=
show_options(filters)     # one positional argument, which this function refuses
```

The starred call works. The unstarred call sends the dict as a single positional argument, and `show_options` has no positional parameters to put it in, so it raises `TypeError`.

```text
2 keyword argument(s), collected as {'state': 'closed', 'per_page': 3} of <class 'dict'>
Traceback (most recent call last):
  File "/Users/joshgoldstein/lesson40/s8.py", line 8, in <module>
    show_options(filters)     # one positional argument, which this function refuses
    ~~~~~~~~~~~~^^^^^^^^^
TypeError: show_options() takes 0 positional arguments but 1 was given
```

The same spread works on a real call. Here every keyword argument to `requests.get` lives in a dict first, including the nested `params` dict from Lesson 37.

```python
import requests

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
filters = {"state": "closed", "sort": "created", "direction": "asc", "per_page": 3}
options = {"params": filters, "timeout": 10}

response = requests.get(ISSUES_URL, **options)
print(response.status_code, response.url)
```

The URL that went out shows all four filter values, so `params=filters` really did arrive as a keyword argument rather than as part of the URL string.

```text
200 https://api.github.com/repos/psf/requests/issues?state=closed&sort=created&direction=asc&per_page=3
```

### Expect `TypeError` when a spread dict names something the function refuses

A dict you build by hand is checked only when you spread it, and the check happens wherever the name finally has to be matched. Add one key `requests` does not know about.

```python
import requests

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
options = {"timeout": 10, "retries": 3}

requests.get(ISSUES_URL, **options)
```

Read the traceback as a route rather than as an error. `retries` was accepted by `requests.get`, forwarded to `request`, forwarded again to `session.request`, and refused there — three frames deep, in a function you never called by name.

```text
Traceback (most recent call last):
  File "/Users/joshgoldstein/lesson40/s10.py", line 6, in <module>
    requests.get(ISSUES_URL, **options)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/joshgoldstein/lesson40/venv/lib/python3.14/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/Users/joshgoldstein/lesson40/venv/lib/python3.14/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Session.request() got an unexpected keyword argument 'retries'
```

That distance between where you wrote the name and where it was rejected is the cost of `**kwargs`, and it is why Worked Example 3 checks the names before the call.

### Read the pass-through signature in `requests`'s own source

`help()` from Lesson 32 shows you the signature of any installed function, and it is the fastest way to find out whether the thing you are documenting takes overflow arguments.

```python
import requests

help(requests.get)
```

The signature line names two parameters and then admits everything else, and the docstring's `**kwargs` entry points at the function it forwards to rather than listing the names.

```text
Help on function get in module requests.api:

get(url, params=None, **kwargs)
    Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :return: :class:`Response <Response>` object
    :rtype: requests.Response
```

The source explains the traceback above. Both lines here are copied from `requests/api.py` in version 2.32.5, with each function's docstring left out; the definitions collect with `**kwargs` and then immediately spread with `**kwargs`.

```python
def request(method, url, **kwargs):
    with sessions.Session() as session:
        return session.request(method=method, url=url, **kwargs)


def get(url, params=None, **kwargs):
    return request("get", url, params=params, **kwargs)
```

This is the **pass-through signature**: a function that names the arguments it cares about, collects the rest, and hands them on unread. It is why `requests.get` needed no change when `Session.request` gained new options, and it is why the error for `retries` named `Session.request` rather than `get`.

> [!note] A newer `requests` annotates the same signature
> Release 2.34 writes `get` as `def get(url: _t.UriType, params: _t.ParamsType = None, **kwargs: Unpack[_t.GetKwargs]) -> Response:`. The stars mean exactly what they mean above; the added type annotations are Lesson 59's subject, and nothing on this page depends on reading them.

## Worked examples

Three examples, in the order you will meet them at work. The first builds a call's options as data, the second forwards arguments it never looks at, and the third refuses a bad option before the library gets a chance to.

### Example 1: build the keyword arguments as data, then spread them

This is the shape the roadmap's `repo.get_issues(**filters)` refers to. A function decides which options belong in the call, returns them as a dict, and one call site spreads whatever it got.

```python
import requests

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"


def issue_request(state=None, per_page=None):
    """Return the keyword arguments for one call, built only from what was asked."""
    filters = {"sort": "created", "direction": "asc"}
    if state:
        filters["state"] = state
    if per_page:
        filters["per_page"] = per_page
    return {"params": filters, "timeout": 10}


for options in (issue_request(), issue_request(state="closed", per_page=2)):
    response = requests.get(ISSUES_URL, **options)
    print(len(response.json()), "issues |", response.url)
```

The `if state:` and `if per_page:` guards from Lesson 14 keep unset options out of the dict entirely, so the first call sends no `state` and no `per_page` and GitHub applies its own defaults — open issues, 30 per page.

```text
30 issues | https://api.github.com/repos/psf/requests/issues?sort=created&direction=asc
2 issues | https://api.github.com/repos/psf/requests/issues?sort=created&direction=asc&state=closed&per_page=2
```

Building the options as a dict is what makes those two calls one line of code instead of two branches. The alternative — an `if` that calls `requests.get` twice with different arguments — duplicates the call site, and the duplicate is where the logging, the timeout, and the error handling drift apart.

### Example 2: wrap a call without naming any of its arguments

Every script from Lesson 39 onward wants one place that logs what went out. A pass-through wrapper gives you that without repeating `requests.get`'s parameter list, and it keeps working when you start passing `headers=` or `json=`.

```python
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"


def logged_get(*args, **kwargs):
    """Forward every argument to requests.get, and record what went out."""
    logging.info(f"GET positional={args} keyword={kwargs}")
    response = requests.get(*args, **kwargs)
    response.raise_for_status()
    return response.json()


oldest = {"state": "closed", "sort": "created", "direction": "asc", "per_page": 2}

for issue in logged_get(ISSUES_URL, params=oldest, timeout=10):
    print(f"#{issue['number']} [{issue['state']}] {issue['title']}")
```

The `INFO` line proves the wrapper saw the arguments without knowing anything about them: the URL arrived in `args` as a one-item tuple, and `params` and `timeout` arrived in `kwargs` as a dict. Log lines go to standard error and the report lines to standard output.

```text
INFO GET positional=('https://api.github.com/repos/psf/requests/issues',) keyword={'params': {'state': 'closed', 'sort': 'created', 'direction': 'asc', 'per_page': 2}, 'timeout': 10}
#1 [closed] Cookie support?
#2 [closed] a "40x" error my have content
```

`response.raise_for_status()` sits inside the wrapper, so every caller gets the Lesson 38b behavior for free: a refusal raises `requests.exceptions.HTTPError` instead of being parsed as data.

### Example 3: refuse an unknown option before the call reaches the library

The `retries` traceback above named a function three frames down, which is a poor error message to hand a colleague running your script. Checking the names yourself turns it into a `ValueError` you wrote, raised at the call the person actually made.

```python
import requests

ISSUES_URL = "https://api.github.com/repos/psf/requests/issues"
ALLOWED = ("params", "headers", "timeout")


def checked_get(url, **kwargs):
    """Refuse names requests.get does not take, and say which ones they were."""
    unknown = []
    for name in kwargs:
        if name not in ALLOWED:
            unknown.append(name)
    if unknown:
        raise ValueError(f"unsupported options: {', '.join(sorted(unknown))}")
    return requests.get(url, **kwargs)


plans = [
    {"params": {"per_page": 1}, "timeout": 10},
    {"params": {"per_page": 1}, "timeout": 10, "retries": 3, "cache": True},
]

for options in plans:
    try:
        response = checked_get(ISSUES_URL, **options)
        print("OK  ", response.status_code, response.url)
    except ValueError as exc:
        print("SKIP", exc)
```

Looping over `kwargs` iterates its keys, exactly as looping over any dict does. Both bad names are reported together and `sorted()` keeps their order stable between runs.

```text
OK   200 https://api.github.com/repos/psf/requests/issues?per_page=1
SKIP unsupported options: cache, retries
```

The check costs you a hard-coded list of allowed names that goes stale when the library adds an option, so use it where a plan file or a colleague supplies the names, and skip it where your own code does.

## Lookup table

| Use when | Call | Result |
| --- | --- | --- |
| Accept any number of positional arguments | `def show(*args):` | `show("docs", "rate-limit")` binds `args` to `('docs', 'rate-limit')` |
| Check what the one star collected | `type(args)` | `<class 'tuple'>` — always a tuple, even for one argument |
| Handle a call that passed nothing | `show()` | binds `args` to `()`, the empty tuple |
| Accept any number of keyword arguments | `def show_options(**kwargs):` | `show_options(state="closed")` binds `kwargs` to `{'state': 'closed'}` |
| Check what the two stars collected | `type(kwargs)` | `<class 'dict'>`, keyed by the names the caller used |
| Require one argument and collect the rest | `def label_line(number, *labels, **options):` | `label_line(41, "docs")` gives `number` `41` and `labels` `('docs',)` |
| Read an option out of the collected dict | `options.get("prefix", "#")` | `'#'` when the caller passed no `prefix` |
| Force an option to be passed by name | `def line(*parts, sep=" - "):` | `line("#41", "x", "; ")` returns `'#41 - x - ; '` — the separator became a part |
| Spread a list into separate positional arguments | `show(*labels)` | two arguments; without the star it is one argument holding the list |
| Spread a dict into keyword arguments | `requests.get(url, **options)` | each key becomes a keyword argument, so `{"timeout": 10}` sends `timeout=10` |
| Pass a dict where keywords are expected, unstarred | `show_options(filters)` | raises `TypeError`: `show_options() takes 0 positional arguments but 1 was given` |
| Spread a dict holding a name the callee refuses | `requests.get(url, **{"retries": 3})` | raises `TypeError`: `Session.request() got an unexpected keyword argument 'retries'` |
| Forward every argument to another function | `def logged_get(*args, **kwargs): return requests.get(*args, **kwargs)` | the wrapper needs no knowledge of the arguments it passes on |
| Reject an unknown option in your own code first | `raise ValueError(f"unsupported options: {', '.join(sorted(unknown))}")` | raises `ValueError`: `unsupported options: cache, retries` |
| Find out whether an installed function takes overflow | `help(requests.get)` | `get(url, params=None, **kwargs)` |

## Exercise: run a plan of API calls through one wrapper

Write `run_plan.py`, which reads a plan of API calls from a file, sends each one through a single logging wrapper, and reports what came back — including the two ways an entry can fail.

### Save the plan file

Save this as `plan.json` beside your script. The second entry names a repository that does not exist, and the third entry's request holds an option `requests.get` does not accept.

```json
[
  {"repo": "psf/requests", "request": {"params": {"state": "closed", "sort": "created", "direction": "asc", "per_page": 2}, "timeout": 10}},
  {"repo": "python/no-such-repository-here", "request": {"timeout": 10}},
  {"repo": "python/cpython", "request": {"params": {"per_page": 1}, "retries": 3}}
]
```

### Requirements

Your script must do all of the following.

1. Load `plan.json` from disk and parse it.
2. Configure logging so that `INFO` messages appear.
3. Write one wrapper function that accepts any positional and any keyword arguments, logs both of them at `INFO` before doing anything else, forwards all of them to `requests.get`, calls `raise_for_status()`, and returns the parsed body. It must not name any of `requests.get`'s own parameters.
4. Write a second function that accepts any number of already-formatted strings plus a separator that can only be passed by name, and returns them joined.
5. Loop over the plan. For each entry, build the issues URL from its `repo` value and send the entry's `request` dict to the wrapper as keyword arguments. Print one line per issue returned, built with the function from step 4, carrying the repository, the issue number, its state, and its title.
6. Handle the two failures in two separate `except` clauses, and build those lines with the same function from step 4. A refused option must report the repository and the message Python produced. An HTTP failure must report the repository plus the status code and the reason phrase, both read off the exception.
7. Finish with a count of how many entries were fetched and how many failed.

### Expected output

Your line format may differ, but the three verdicts and the counts must match. The `INFO` lines go to standard error, so they interleave with the report lines as shown when you run the script in a terminal.

```text
INFO GET positional=('https://api.github.com/repos/psf/requests/issues',) keyword={'params': {'state': 'closed', 'sort': 'created', 'direction': 'asc', 'per_page': 2}, 'timeout': 10}
psf/requests | #1 | closed | Cookie support?
psf/requests | #2 | closed | a "40x" error my have content
INFO GET positional=('https://api.github.com/repos/python/no-such-repository-here/issues',) keyword={'timeout': 10}
python/no-such-repository-here | HTTP error | 404 Not Found
INFO GET positional=('https://api.github.com/repos/python/cpython/issues',) keyword={'params': {'per_page': 1}, 'retries': 3}
python/cpython | plan error | Session.request() got an unexpected keyword argument 'retries'

1 fetched, 2 failed
```
