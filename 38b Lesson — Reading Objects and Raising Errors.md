# Lesson 38b — Reading objects and raising errors

Lesson 38 had you write `response.status_code` and `response.json()` without ever saying what the dot does, or why one of those needs parentheses and the other doesn't. This lesson settles both. You'll learn to read an object from the outside, tell an attribute from a method on sight, work out from a method's kind whether its line needs an `=`, and raise an error of your own as a second way out of a function. Then you'll meet `response.raise_for_status()`, which is all of that at once and which Lesson 39 builds on.

Classes stay out. Writing your own object is Lesson 43, and nothing here asks you to define one, only to use objects that already exist.

## The samples

Two samples cover every example, because one can't show both an object with data on it and an API that fails.

The following commands build the small docs tree the first two examples read, which has a nested directory so a path has a parent worth looking at:

```bash
mkdir -p docs/api
printf '# Authentication\n\nSend the token in the Authorization header.\n' > docs/api/auth.md
printf '# Rate limits\n\nSixty requests per hour without a token.\n' > docs/api/rate-limit.md
printf '# Documentation\n\n- [Authentication](api/auth.md)\n' > docs/index.md
```

The following list is the second sample, and the second record is deliberately missing its `user` field so that every example about raising has something real to reject:

```python
ISSUES = [
    {"number": 41, "title": "Broken link in install.md", "user": "kmp", "labels": ["docs"]},
    {"number": 42, "title": "Clarify rate-limit.md"},
]
```

The following imports and two URLs are assumed by every example below, so they aren't repeated in each block:

```python
import requests
from pathlib import Path

GOOD = "https://api.github.com/repos/PyGithub/PyGithub"
GONE = "https://api.github.com/repos/PyGithub/no-such-repo-xyz"
```

`GOOD` is a repository that exists and `GONE` is one that doesn't, so the same two lines of code can show a success and a failure. Both are public, so neither needs a token, and every request in this lesson is a `GET` that changes nothing.

## Terminology and theory

An **object** is one value that carries both data and the functions that work on that data. A string is an object, a list is an object, and so is the `Response` that `requests.get()` handed you in Lesson 37. You've been using objects since Lesson 2 without the word.

The **dot** reaches into one particular object. In `page.name`, the `page` on the left names which object, and the `name` on the right names what you want from it. That matters because the same name means different things on different objects: `page.name` on a path is a filename, and the `name` on some other object would be something else entirely. The dot isn't a general lookup; it asks this one object.

What follows the dot is either an attribute or a method, and the parentheses are how you tell them apart in code. An **attribute** is a piece of data sitting on the object, read with no parentheses, as in `response.status_code`. A **method** is a function belonging to the object, called with parentheses, as in `response.json()`. Getting it backwards fails in two different ways: parentheses on an attribute try to call a value that isn't a function, and a method without parentheses hands you the function itself instead of running it.

The second of those two mistakes is the dangerous one, because it isn't an error. Python lets you mention a method without calling it, so the line runs, nothing happens, and the script carries on as though the method had done its job. That's the whole reason this lesson exists ahead of Lesson 39.

Once a method is actually called, the question is whether its line needs an `=`, and the answer follows from which of three kinds of method it is. One kind **builds a new value** and hands it back, leaving the object alone, so the result is lost unless you assign it. One kind **changes the object in place** and hands back `None`, so assigning its result throws away the thing you wanted. One kind **checks something and raises** when it finds a problem, handing back `None` when it doesn't, so there's nothing to assign either way. Reading a method's kind off the documentation is how you know what its line should look like.

**Raising** is the second way out of a function. A `return` hands a value back to whoever called it, and the caller carries on with that value. A `raise` abandons the function without producing a value at all, and hands an exception to Python instead. The two are alternatives rather than companions: a line after a `raise` in the same branch never runs.

A raised exception doesn't stop at the function that raised it. It climbs out through every function in the chain that called it, and the first `except` clause matching its type catches it. Nothing in between has to mention it, which is what makes raising useful: a function three levels down can refuse to continue, and only the top level needs to decide what to do about that.

The curriculum's motivating case is `response.raise_for_status()`, a checking method on the response object. It inspects the status code you already hold, raises `requests.exceptions.HTTPError` when that code is a `4xx` or `5xx`, and returns `None` otherwise. The response doesn't vanish when it raises: it's attached to the exception as `exc.response`, so everything Lesson 37 taught you about reading a response still applies inside the `except` clause.

## Read the syntax

The parentheses are the whole difference between reading data and running code, and both wrong forms are worth seeing beside the right ones.

The following block pairs each correct form with the mistake it invites:

```python
page.name          # attribute: hands you the filename
page.name()        # a string cannot be called, so this is an error
page.exists()      # method: runs the check and hands back True or False
page.exists        # hands back the function itself, unrun, and raises nothing
```

The third and fourth lines are the pair to remember. Only one character separates them, and the fourth is legal Python that does nothing, so no traceback tells you about it.

Which of the three kinds a method is decides whether its line carries an `=`.

The following table is the rule, and every row is run further down:

| Kind of method | Hands back | Line looks like |
| --- | --- | --- |
| Builds a new value | the new value | `renamed = page.with_suffix(".txt")` |
| Changes the object in place | `None` | `labels.append("bug")` |
| Checks, and raises on a problem | `None` | `response.raise_for_status()` |

Assigning the result of the second kind is the trap, because the line looks ordinary and the damage is silent. `labels = labels.append("bug")` appends the label and then replaces your list with the `None` that `append` handed back, so the list you wanted is gone and no error is raised.

Raising takes one keyword and an exception you name yourself.

The following two functions differ only in how they refuse, and the difference is what the caller has to write:

```python
def summarize_or_none(issue):
    if "user" not in issue:
        return None                     # caller must remember to test for None
    return issue["user"]


def summarize_or_raise(issue):
    if "user" not in issue:
        raise KeyError(f"issue {issue['number']} has no user")
    return issue["user"]
```

Pick the exception type that describes the problem rather than always reaching for one: `ValueError` for a value that's the right type and unusable, `KeyError` for a missing key, `TypeError` for the wrong kind of thing entirely. The check above is for a missing key, so `summarize_or_raise` raises `KeyError`. Put the specific detail in the message, because the message is what you'll read in six months, and `issue 42 has no user` tells you which record while `missing field` doesn't.

Catching a raised exception uses the `try` and `except` from Lesson 19, with the exception's full name.

The following block is the shape every example at the end of this lesson takes:

```python
try:
    response.raise_for_status()
except requests.exceptions.HTTPError as exc:
    print(exc.response.status_code)     # the response is still here, on exc
```

The `as exc` part binds the exception to a name so you can read it, and `exc.response` is the response object the check rejected. The name `requests.exceptions.HTTPError` gets written out in full because it lives in the `requests.exceptions` module rather than being a built-in like `ValueError`.

## Work through the examples

Each example adds one thing to the one before it, starting from a path on disk and ending with a failed API call read through its exception. Every output block is from a real run.

### Example 1: Tell an attribute from a method by what the parentheses do

This first example establishes the base case, which is that the dot gives you either data or a function, and the parentheses decide which you get.

The following script reads three attributes, calls one method, and then makes both parenthesis mistakes:

```python
page = Path("docs/api/auth.md")

print("name     :", page.name)            # an attribute: no parentheses
print("suffix   :", page.suffix)
print("parent   :", page.parent.name)     # two attributes, one after the other
print("exists   :", page.exists())        # a method: parentheses required
print("unrun    :", page.exists)          # no parentheses, so nothing ran
try:
    page.name()
except TypeError as exc:
    print("name()   :", exc)
```

The following output shows the fifth line printing a function rather than running one, which is the failure with no traceback:

```output
name     : auth.md
suffix   : .md
parent   : api
exists   : True
unrun    : <bound method Path.exists of PosixPath('docs/api/auth.md')>
name()   : 'str' object is not callable
```

Compare the `exists` line with the `exists()` line above it. The call produced `True`, and the mention produced `<bound method …>`, which is Python telling you it handed back the function. *Bound* means attached to this one path, which is the dot doing its job: `page.exists` is a check against `docs/api/auth.md` and nothing else. The last line is the opposite mistake, and it does raise, because `page.name` is a string and a string can't be called.

### Example 2: Work out from a method's kind where the `=` goes

This example adds the three kinds of method call, so you can predict from a method's behavior whether its line should assign anything.

The following script uses one method of each kind, and then assigns the result of the one you shouldn't:

```python
page = Path("docs/api/auth.md")
labels = ["docs"]

renamed = page.with_suffix(".txt")        # builds a new value, so it needs the =
print("builds   :", renamed.name, "| original untouched:", page.name)

print("returns  :", labels.append("bug")) # changes labels in place, returns None
print("labels   :", labels)

lost = labels.append("api")               # the = captures the None, not the list
print("lost     :", lost, "| labels still changed:", labels)
```

The following output shows the building method leaving the original alone, and the in-place method handing back nothing at all:

```output
builds   : auth.txt | original untouched: auth.md
returns  : None
labels   : ['docs', 'bug']
lost     : None | labels still changed: ['docs', 'bug', 'api']
```

The `with_suffix()` call produced a second path and left `page` as it was, which is why dropping the `=` would lose the result. The `append()` call is the mirror image: it printed `None`, because changing the list is all it does, and the list itself changed anyway. The last line is the trap in action, and note what it costs you: `lost` is `None`, and had the name on the left been `labels` instead, the list would have been replaced by `None` while the append still happened.

### Example 3: Raise an error that names the record it rejected

This example adds `raise`, and uses it where returning `None` would have forced the caller to check.

The following script defines a function that refuses incomplete records and loops over both samples:

```python
def summarize(issue):
    if "user" not in issue:
        raise KeyError(f"issue {issue['number']} has no user")
    return f"#{issue['number']} {issue['title']} ({issue['user']})"


for issue in ISSUES:
    try:
        print(summarize(issue))
    except KeyError as exc:
        print("skipped:", exc)
```

The following output shows the complete record summarized and the incomplete one reported by number:

```output
#41 Broken link in install.md (kmp)
skipped: 'issue 42 has no user'
```

The `return` on the function's last line never runs for issue 42, because the `raise` above it left the function first. That's the contrast worth holding on to: `return` and `raise` are two exits from the same function, and whichever is reached first ends it. The message carries the issue number, so the caller's report says which record failed without the caller having to work it out.

The quotes around the message aren't in the string you passed to `KeyError`: printing a `KeyError` wraps its message in quotes, where printing a `ValueError` with the same message shows it bare. That's how `KeyError` displays itself, so expect the quotes whenever you print one, and don't take them for a mistake in your message.

### Example 4: Watch a raised exception climb past the function that called it

This example adds a second level of calls, to show that nothing in between needs to know an exception is passing through. Example 3's `summarize` is still in scope, and only the two definitions below are new.

The following script wraps `summarize` in a function with no `except` of its own:

```python
def report(issue):
    return f"[{summarize(issue)}]"        # no except here, so the raise passes through


try:
    for issue in ISSUES:
        print(report(issue))
except KeyError as exc:
    print("caught two levels up:", exc)
```

The following output shows the exception crossing `report` untouched and stopping at the only `except` in the chain:

```output
[#41 Broken link in install.md (kmp)]
caught two levels up: 'issue 42 has no user'
```

`report` doesn't mention `KeyError` anywhere, and it didn't have to. The `raise` in `summarize` abandoned `summarize`, then abandoned `report`, then found the `except` at the top. Note also that the loop stopped: issue 42 raised, the `except` ran, and no further record was reported, because the exception left the `for` loop along with everything else. That's the difference between catching inside the loop, as Example 3 did, and catching outside it.

### Example 5: Turn a failing status into an exception with `raise_for_status()`

This example adds the checking kind of method, against a real API, so you can see it do nothing on success and raise on failure.

The following script runs the identical two lines against a repository that exists and one that doesn't:

```python
for url in (GOOD, GONE):
    response = requests.get(url, timeout=10)
    print("status   :", response.status_code)
    print("returns  :", response.raise_for_status())   # None on success, exception on failure
```

The following output is everything the script printed, and the second iteration stops one line earlier than the first:

```output
status   : 200
returns  : None
status   : 404
```

The following is the last line of the traceback that ended the script, with the frames above it left out:

```output
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://api.github.com/repos/PyGithub/no-such-repo-xyz
```

On the successful request the method printed `None`, which is what the checking kind hands back when it finds nothing wrong, and that's why its line carries no `=`. On the `404` it raised, and since nothing caught the exception the traceback ends the script. Note that the request itself succeeded both times: a `404` is a response that arrived, exactly as Lesson 38 showed, and `raise_for_status()` is you choosing to treat it as an error.

### Example 6: Catch the exception, and see the check that never ran

This last example adds the `except` clause that reads the response back off the exception, and shows what the same check does when you forget its parentheses.

The following script mentions the method once without calling it, then calls it properly inside a `try`:

```python
response = requests.get(GONE, timeout=10)
response.raise_for_status                       # no parentheses, so no check happens
print("still running, nothing was checked")

try:
    response.raise_for_status()
except requests.exceptions.HTTPError as exc:
    print("code     :", exc.response.status_code)
    print("message  :", exc.response.json()["message"])
    print("url      :", exc.response.url)
```

The following output shows the second line passing silently, and then the real check raising into a clause that reads the failed response:

```output
still running, nothing was checked
code     : 404
message  : Not Found
url      : https://api.github.com/repos/PyGithub/no-such-repo-xyz
```

The second line of that script is the bug this lesson was inserted to prevent. It names a method, Python evaluates the name, the result is discarded, and the script continues as though the status had been checked. There's no traceback and no warning, and the `404` goes unnoticed until something downstream fails on data that was never there. The `except` clause shows the other half: `exc.response` is the same response object, so `status_code`, `json()`, and `url` all work on it, and the failure is as readable inside the clause as it was outside.

> [!warning] The check that isn't a syntax error
> `response.raise_for_status` on a line by itself is valid Python that checks nothing. Nothing in the language, and nothing in `requests`, will tell you about it. When a script seems to ignore a failing status, look at whether the check was called.

## Lookup table

The following table covers everything this lesson introduces, with every result taken from a real run against the local tree or `api.github.com`:

| Use when | Call | Result |
| --- | --- | --- |
| You want data that sits on an object | `page.name` | `'auth.md'`, with no parentheses anywhere |
| You put parentheses on an attribute | `page.name()` | Raises `TypeError: 'str' object is not callable` |
| You want to reach through one object to another | `page.parent.name` | `'api'`, two attribute reads in a row |
| You want to run a method and use its answer | `page.exists()` | `True` |
| You name a method and forget the parentheses | `page.exists` | `<bound method Path.exists of PosixPath('docs/api/auth.md')>`, and nothing ran |
| A method builds a new value from the object | `renamed = page.with_suffix(".txt")` | `renamed.name` is `'auth.txt'`; `page.name` is still `'auth.md'` |
| A method changes the object in place | `labels.append("bug")` | Returns `None`, and `labels` becomes `['docs', 'bug']` |
| You assign the result of an in-place method | `lost = labels.append("api")` | `lost` is `None`, and the append happened anyway |
| You want to refuse a missing key and say why | `raise KeyError(f"issue {n} has no user")` | Abandons the function; `print(exc)` shows `'issue 42 has no user'`, quotes included |
| You want to catch what you raised | `except KeyError as exc:` | Taken for the raise above, with `exc` bound to it |
| A raise happens two calls deep | `report()` calling `summarize()` with no `except` | Climbs past `report` to the nearest matching `except` |
| A raise happens inside a loop you catch outside | `try:` outside the `for` | The loop ends; no later item is processed |
| You want a bad status to become an exception | `response.raise_for_status()` | `None` on the `200`; raises `requests.exceptions.HTTPError` on the `404` |
| You name that check and forget the parentheses | `response.raise_for_status` | Nothing is checked, nothing is raised, and the script continues |
| You want to catch a failing status | `except requests.exceptions.HTTPError as exc:` | Taken for the `404`, with the response on `exc` |
| You want the failing code as a number | `exc.response.status_code` | `404`, an `int` you can compare |
| You want the API's explanation of the failure | `exc.response.json()["message"]` | `'Not Found'` |
| You want the URL that failed | `exc.response.url` | `'https://api.github.com/repos/PyGithub/no-such-repo-xyz'` |

## Exercise: Check a plan file before it reaches the API

Write `check_plan.py`, which reads a file of proposed issue changes, rejects the records that aren't complete enough to send, and confirms that the repository each remaining record names actually exists.

The following is `plan.json`, the input file to create, and between its three records it covers one that's ready, one that's missing a field, and one that names a repository GitHub doesn't have:

```json
[
  {"number": 41, "title": "Broken link in install.md", "user": "kmp", "repo": "PyGithub/PyGithub"},
  {"number": 42, "title": "Clarify rate-limit.md", "repo": "PyGithub/PyGithub"},
  {"number": 43, "title": "Document the version header", "user": "rivera", "repo": "PyGithub/no-such-repo-xyz"}
]
```

Your script must do all of the following:

1. Take the plan file's path as a required positional argument, and explain it under `--help`.
2. Require `title`, `user`, and `repo` on every record, and refuse a record missing any of them by raising an error that names both the record and the field that's absent. Send no request for such a record.
3. Ask GitHub about each remaining record's repository, and let a failing status become an exception rather than checking the code yourself.
4. Handle the two failures in two separate `except` clauses, so an incomplete record and a rejected repository produce different lines of output. For the rejected one, report the status code and the API's own `message`.
5. Print one line per record, and finish with a count of how many records are ready to send.

Everything you need from the earlier lessons is in the reference set, which is faster to search than the lesson files. The `Lookup` section of [[Exceptions]] has the `try` and `except` forms, [[JSON]] has the file reading, [[Command-line Arguments]] has the positional argument, and [[Making HTTP Requests]] has the request and the response. [[Objects and Methods]] covers the attribute-and-method material from this lesson, and [[Syntax Index]] maps a call to the page that owns it when you know the name but not where it lives.

### Expected output

The following is from a real run of my own solution, so it shows what a correct script produces rather than what one ought to:

```output
ok        : record 41 targets PyGithub/PyGithub
incomplete: record 42 has no user
rejected  : record 43 got 404 Not Found
1 of 3 records are ready to send
```

The following command produced it:

```bash
python3 check_plan.py plan.json
```
