# Lesson 39 — Handling and debugging API responses

Lesson 38b taught you `raise_for_status()` and showed you one failure caught in one `except` clause. This lesson covers the rest of the job: deciding whether to check a status code or raise on it, catching the failures that never produce a response at all, reading the detail GitHub puts in an error body, logging enough to debug a call you can't watch, and folding all of it into one function your later scripts will call instead of calling `requests` directly.

Everything here runs against real GitHub at `https://api.github.com`, and every request is a `GET` that needs no token. Nothing in this lesson creates, changes, or deletes anything, and nothing needs the repository you set up for later lessons.

## Set up the examples

Every example below assumes three lines have already run, so they aren't repeated each time.

The following imports and base URL are those three lines:

```python
import logging
import requests

BASE = "https://api.github.com"
```

The examples use two repositories, and the second one is the interesting case. `PyGithub/PyGithub` is public, so an unauthenticated request succeeds. `JoshGo6/ThrowAway` is your own private repository, which exists, and an unauthenticated request for it answers `404 Not Found` rather than `403 Forbidden`. GitHub does this deliberately: a repository you can't see and a repository that doesn't exist answer identically, so an outsider can't use the API to discover that a private repository is there. It means a `404` in your own scripts has two causes, and the token is as likely to be the problem as the URL.

> [!warning] The anonymous rate limit is 60 requests per hour
> Unauthenticated requests are counted against your IP address, not an account, and the ceiling is 60 per hour. Running every example on this page a few times will exhaust it, and GitHub then answers `403` until the hour rolls over. Example 5 prints how many calls you have left.

## Terminology and theory

An API call has three distinct failure modes, and they need different handling because they carry different amounts of information.

A **response that reports a failure** is still a response. GitHub answered, and the answer has a status code, headers, and a JSON body explaining the problem. Nothing has gone wrong at the Python level, so no exception is raised unless you ask for one. The `requests` library treats a `404` exactly as it treats a `200`.

A **failure to get any response** is different. A timeout, a DNS failure, or a refused connection means nothing came back, so there's no status code and no body to read. These raise immediately, and the exception carries no response.

An **exception you asked for** sits between the two. The `raise_for_status()` method inspects a response you already hold and converts a failing status code into a `requests.exceptions.HTTPError`, so you can handle a bad status in an `except` clause instead of an `if`. The response is still there, attached to the exception.

These three are why the `except` clauses in this lesson have an order. Every exception `requests` defines inherits from `requests.exceptions.RequestException`, so catching that one catches every failure the library can produce, which makes it the right last clause and the wrong first one. An `except RequestException` written above `except Timeout` catches the timeout too, and the `Timeout` clause below it never runs.

Two terms from the response itself appear throughout. The **error body** is the JSON GitHub returns with a failure, and it always carries the same three fields: `message`, a short human-readable summary; `documentation_url`, pointing at the endpoint's reference page; and `status`, the status code repeated. The **request ID** is the value of the `X-GitHub-Request-Id` header, which GitHub sets on every response and which identifies that one call in GitHub's own logs. It's the single most useful thing to log, because it's the only identifier you and GitHub both hold.

## Read the syntax

Checking a status code and raising on one are two forms of the same decision, and which one you reach for depends on what the caller does next.

The following block shows both forms against the same request, so the only difference between them is how the failure surfaces:

```python
# Form 1: branch on the response, no exception involved.
response = requests.get(url, timeout=10)
if response.ok:                      # True for any 2xx code
    data = response.json()

# Form 2: convert a failing code into an exception.
response = requests.get(url, timeout=10)
response.raise_for_status()          # raises `HTTPError` on 4xx and 5xx
data = response.json()
```

Use the first form when a failure is an expected outcome you want to handle inline, such as a missing repository in a list you're iterating over. Use the second when a failure means the current operation can't continue, because the exception stops the code that follows it without a further `if`.

The `except` clauses run from specific to general, because a broad clause placed above a narrow one takes the exception first and the narrow one never runs.

The following order is the one to copy, and each comment says what that clause has to work with:

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.Timeout:          # no response at all
    print("gave up waiting")
except requests.exceptions.ConnectionError:  # no response at all
    print("never reached the host")
except requests.exceptions.HTTPError as exc: # a response, with a bad code
    print("answered", exc.response.status_code)
except requests.exceptions.RequestException: # anything else requests raises
    print("something else went wrong")
```

Inside the `HTTPError` clause, `exc.response` is the response object, so everything you learned about a response in Lesson 37 is still available: `exc.response.status_code`, `exc.response.json()`, `exc.response.headers`, and `exc.response.text`. In the `Timeout` and `ConnectionError` clauses there's no response, and reaching for one gets you `None`.

Logging a request takes one new habit, which is handing the values to `logging` rather than formatting them yourself.

The following two calls log the same message, but only the second is the correct form:

```python
logging.error(f"{path} gave {code}")     # f-string: formatted even when not logged
logging.error("%s gave %s", path, code)  # arguments: formatted only if logged
```

Pass the values as arguments after the format string rather than building an f-string. The `logging` module then formats the message only if that level is actually being emitted, and a `logging.debug()` call in a script running at `INFO` costs nothing.

One more line belongs in any script that logs at `DEBUG`, and leaving it out is why debug output is often unreadable.

The following call silences the HTTP library underneath `requests`:

```python
logging.getLogger("urllib3").setLevel(logging.WARNING)
```

Without it, `logging.basicConfig(level=logging.DEBUG)` turns on `urllib3`'s own debug output as well, and your messages are buried in connection-pool chatter.

## Work through the examples

Each example below adds one thing to the one before it, starting from a bare status check and ending with the function you'll reuse for the rest of the curriculum. Every output block is from a real run against `api.github.com`.

### Example 1: Check the status before parsing

This first example establishes the base case, which is that a failing response is a normal response and its body is JSON you can read.

The following script asks for your private repository without a token and branches on the result:

```python
response = requests.get(f"{BASE}/repos/JoshGo6/ThrowAway", timeout=10)
if response.ok:
    print("name:", response.json()["full_name"])
else:
    print("failed:", response.status_code)
    print("message:", response.json()["message"])
```

The following output shows the `else` branch running, with no exception raised anywhere:

```output
failed: 404
message: Not Found
```

Note that `response.json()` worked on a failure. The error body is JSON like any other, which is why the `if` form can report a useful reason without doing anything special.

### Example 2: Raise on the status instead of checking it

This example adds the exception form, against the identical request, so the only thing that changes is how the failure reaches you.

The following script replaces the `if` with `raise_for_status()`:

```python
response = requests.get(f"{BASE}/repos/JoshGo6/ThrowAway", timeout=10)
try:
    response.raise_for_status()
    print("name:", response.json()["full_name"])
except requests.exceptions.HTTPError as exc:
    print("raised:", type(exc).__name__)
    print("str:", exc)
```

The following output shows the exception type and the message `requests` builds for it:

```output
raised: HTTPError
str: 404 Client Error: Not Found for url: https://api.github.com/repos/JoshGo6/ThrowAway
```

The `requests` library assembles that message from the status code and the reason phrase, and it includes the full URL. The URL is why this form is worth using even when you'd have checked the code anyway: the exception reports which call failed, which an `if` branch has to state for itself.

### Example 3: Catch the failures that return no response

This example adds the two failure modes that produce no response at all, which neither of the first two examples could show.

The following script sends three requests: one that answers `404`, one that times out, and one to a port where nothing is listening:

```python
for url, limit in [(f"{BASE}/repos/JoshGo6/ThrowAway", 10),
                   (f"{BASE}/user/repos", 0.001),
                   ("http://127.0.0.1:9999/repos", 10)]:
    try:
        requests.get(url, timeout=limit).raise_for_status()
    except requests.exceptions.Timeout:
        print("timeout: nothing came back")
    except requests.exceptions.ConnectionError:
        print("connection: nothing answered")
    except requests.exceptions.HTTPError as exc:
        print("http:", exc.response.status_code)
```

The following output shows each request taking a different clause, in request order:

```output
http: 404
timeout: nothing came back
connection: nothing answered
```

The `timeout=0.001` is what forces the second case, since no round trip to GitHub finishes in a millisecond. The third case needs no network at all, because nothing is listening on port 9999 and the connection is refused locally. Neither of those two clauses can report a status code, since there's no response to take one from.

### Example 4: Read GitHub's explanation off the exception

This example adds the error body, which the earlier examples caught but never looked inside.

The following script reaches through the exception to the response and prints all three of its fields:

```python
try:
    requests.get(f"{BASE}/repos/JoshGo6/ThrowAway", timeout=10).raise_for_status()
except requests.exceptions.HTTPError as exc:
    body = exc.response.json()
    print("code:", exc.response.status_code)
    print("message:", body["message"])
    print("docs:", body["documentation_url"])
    print("status field:", body["status"], type(body["status"]).__name__)
    print("equal to 404?", body["status"] == 404)
```

The following output shows the three fields, and a trap in the third:

```output
code: 404
message: Not Found
docs: https://docs.github.com/rest/repos/repos#get-a-repository
status field: 404 str
equal to 404? False
```

The `status` field holds the string `"404"`, not the integer `404`, so comparing it to a number is always `False` and never raises. Use `exc.response.status_code`, which is a real `int`, whenever you need to compare. Read the `status` field only to confirm that the body came from GitHub rather than from a proxy in between.

### Example 5: Log what went out and what came back

This example adds the debugging layer, which none of the previous four produce: a record of the call that survives after the script exits.

The following script configures logging, silences `urllib3`, then logs the URL, the status, the request ID, and the calls you have left:

```python
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
logging.getLogger("urllib3").setLevel(logging.WARNING)

response = requests.get(f"{BASE}/repos/JoshGo6/ThrowAway", timeout=10)
logging.debug("GET %s", response.url)
logging.debug("status %s request-id %s", response.status_code,
              response.headers.get("X-GitHub-Request-Id"))
logging.debug("calls left %s", response.headers.get("x-ratelimit-remaining"))
```

The following output is from one run, and your request ID and remaining count will differ:

```output
DEBUG GET https://api.github.com/repos/JoshGo6/ThrowAway
DEBUG status 404 request-id A638:2CCCD7:277F84:8261DC:6AC706A9
DEBUG calls left 56
```

The header names are read with `.get()` rather than square brackets, so a header GitHub omits gives `None` instead of raising `KeyError`. The lowercase spelling of `x-ratelimit-remaining` is deliberate: HTTP/2 lowercases every header name, and `requests` matches them case-insensitively, so either spelling works and the lowercase one is what the wire actually carries.

### Example 6: Fold it into one function

This last example assembles the previous five into the reusable function the rest of the curriculum will use.

The following script defines `fetch()`, which returns parsed JSON, or returns `None` after logging why it couldn't:

```python
def fetch(path):
    try:
        response = requests.get(f"{BASE}{path}", timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        logging.error("%s failed: %s", path, exc)
        return None
    return response.json()


print(fetch("/repos/PyGithub/PyGithub")["full_name"])
print(fetch("/repos/JoshGo6/ThrowAway"))
```

The following output shows the successful call, the failed one, and the `ERROR` line arriving before both:

```output
ERROR /repos/JoshGo6/ThrowAway failed: 404 Client Error: Not Found for url: https://api.github.com/repos/JoshGo6/ThrowAway
PyGithub/PyGithub
None
```

The `ERROR` line appears first because `logging` writes to standard error while `print()` writes to standard output, and the two streams are flushed independently. That ordering isn't a bug in your script, and it disappears the moment you send either stream to a file.

This version catches `RequestException` alone, which is the right trade for a helper whose callers only need to know whether they got data. A single clause can't say *why* the call failed, so the `exc` value goes into the log message to preserve it. When a caller does need to branch on the reason, the function keeps the specific clauses from Example 3 instead.

## Lookup table

The following table covers everything this lesson introduces, with every result taken from a run against `api.github.com`:

| Use when | Call | Result |
| --- | --- | --- |
| You want to know whether a request succeeded at all | `response.ok` | `False` for the `404` on `ThrowAway`; `True` for any `2xx` |
| You want a bad status code to stop the script | `response.raise_for_status()` | Raises `requests.exceptions.HTTPError`; returns `None` on a `2xx` |
| You want the exception's own description | `str(exc)` | `'404 Client Error: Not Found for url: https://api.github.com/repos/JoshGo6/ThrowAway'` |
| You want the exception's class name | `type(exc).__name__` | `'HTTPError'` |
| You want the response that caused an `HTTPError` | `exc.response` | The `Response` object; `None` when nothing ever replied |
| You want the failing code as a number | `exc.response.status_code` | `404`, an `int` you can compare |
| You want GitHub's explanation of the failure | `exc.response.json()["message"]` | `'Not Found'` |
| You want the reference page for the failing endpoint | `exc.response.json()["documentation_url"]` | `'https://docs.github.com/rest/repos/repos#get-a-repository'` |
| You want the status code out of the error body | `exc.response.json()["status"]` | `'404'`, a `str`, so `== 404` is `False` |
| You want the raw error body as characters | `exc.response.text` | `'{\n  "message": "Not Found",\n  …\n}'` |
| You want to catch a request that never came back | `except requests.exceptions.Timeout:` | Taken when `timeout=0.001` expires before GitHub answers |
| You want to catch a host that refused or vanished | `except requests.exceptions.ConnectionError:` | Taken for `http://127.0.0.1:9999`, where nothing listens |
| You want to catch a bad status you raised on | `except requests.exceptions.HTTPError as exc:` | Taken for the `404`, with the response on `exc` |
| You want one clause for every failure `requests` raises | `except requests.exceptions.RequestException:` | Taken for all three of the above, so it must come last |
| You want the call GitHub can look up in its logs | `response.headers.get("X-GitHub-Request-Id")` | `'A638:2CCCD7:277F84:8261DC:6AC706A9'`, different every call |
| You want to know how many calls are left this hour | `response.headers.get("x-ratelimit-remaining")` | `'56'`, a string, and `60` is the unauthenticated ceiling |
| You want a log message built only when it's emitted | `logging.error("%s gave %s", path, code)` | `ERROR /repos/… gave 404` |
| You want `DEBUG` logging without connection noise | `logging.getLogger("urllib3").setLevel(logging.WARNING)` | Suppresses `urllib3`'s own debug lines; returns `None` |

## Exercise: Report on a list of repositories

Write `repo_report.py`, which reads a list of repositories from a text file, asks GitHub about each one, and writes a Markdown table summarizing what it found.

The following four lines are the input file to create, and between them they cover a public repository, a private one, one that doesn't exist, and a line that isn't a repository path at all:

```text
PyGithub/PyGithub
JoshGo6/ThrowAway
PyGithub/no-such-repo-xyz
requests
```

Your script must do all of the following:

1. Take the input file's path as a required positional argument, and accept an optional flag that sets the output file, defaulting to `repo-report.md`. Running it with `--help` must explain both.
2. Skip blank lines, and reject any line that isn't exactly one owner and one name separated by a single slash, logging it at `ERROR` and recording it in the report as malformed. Send no request for such a line.
3. Fetch each valid repository through one function that handles a timeout, a connection failure, and a bad status code in three separate `except` clauses, and that returns `None` on any of them. Log each failure at `ERROR`, and include the status code and the request ID for the failures that have them.
4. Write a Markdown table to the output file with one row per input line, giving the repository's default branch and open issue count when the call succeeded, and an em dash with the word `failed` or `malformed` when it didn't.
5. Configure logging so your own messages appear and `urllib3`'s don't.

Everything you need from earlier lessons is in the reference set, which is faster to search than the lesson files. The `Lookup` section of [[Logging]] has the configuration calls, [[Command-line Arguments]] has the `argparse` patterns, and [[Reading and Writing Files]] and [[Path Objects]] have the file reading and writing. [[Syntax Index]] maps a call to the page that owns it when you know the name but not where it lives.

### Expected output

Both blocks below are from a real run of my own solution, so they show what a correct script produces rather than what one ought to.

The following is what the script prints, and your request IDs will differ because GitHub issues a new one for every call:

```output
ERROR /repos/JoshGo6/ThrowAway gave 404 (request D8A2:2A589B:5361CD:1134ED0:6AC70711)
ERROR /repos/PyGithub/no-such-repo-xyz gave 404 (request D8AA:1DB00C:5860ED:12336AD:6AC70711)
ERROR requests is not owner/name
INFO wrote report.md with 4 rows
```

The following is the Markdown the script writes, and `open_issues_count` includes pull requests, so the number for `PyGithub/PyGithub` is larger than its issue list alone and will have moved by the time you run it:

```output
# Repository report

| Repo | Default branch | Open issues |
| --- | --- | --- |
| PyGithub/PyGithub | main | 411 |
| JoshGo6/ThrowAway | — | failed |
| PyGithub/no-such-repo-xyz | — | failed |
| requests | — | malformed |
```

The following command is the one that produced both blocks:

```bash
python3 repo_report.py repos.txt --out report.md
```
