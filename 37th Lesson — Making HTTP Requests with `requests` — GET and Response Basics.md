# Lesson 37 — GET requests with `requests`

Lesson 36 read API behavior with `curl`. This lesson does the same work from Python with the `requests` library: send a GET, get a `Response` object back, and pull the status code, headers, and body out of it. Every SDK you will document — PyGithub included — is doing this underneath, so the vocabulary here is the vocabulary you will use when you explain what an SDK method actually does.

## Setup — install `requests`, then start a local API to call

`requests` is not part of the standard library, so it has to be installed. Do it inside a virtual environment (lessons 32 and 33), not against system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

Confirm it imported, which also tells you which version's behavior you are seeing:

```bash
python3 -c "import requests; print(requests.__version__)"
```

On this machine that prints:

```output
2.33.1
```

The rest of the lesson calls a small API that runs on your own machine, so nothing here depends on a network account, an API token, or a rate limit. Save this as `docs_server.py`:

> [!note] You do not need to read this file
> Nothing in the lesson asks you to understand `docs_server.py`.
> It is built with `class`, `self`, and inheritance — lessons 43, 44, and 46 — plus `*args` from lesson 40. Python's standard library offers no way to run an HTTP server without them, and a local server is what lets every example below print real output instead of output you have to take on faith.
> Nothing in the syntax section, the worked examples, or the exercise requires understanding it. You start it once and then only send requests to it.

```python
"""A tiny local stand-in for a GitHub-shaped API. GET only.

Run it in its own terminal:  python3 docs_server.py
It answers on http://127.0.0.1:8073 and holds no state.
"""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PORT = 8073

REPO = {
    "full_name": "nalpeiron/docs",
    "description": "Product documentation sources",
    "default_branch": "main",
    "open_issues_count": 2,
    "private": False,
    "html_url": "https://example.invalid/nalpeiron/docs",
}

ISSUES = [
    {"number": 41, "title": "Rate limit page has no examples", "state": "open",
     "user": {"login": "jdoe"}, "labels": ["docs", "api"], "comments": 2},
    {"number": 38, "title": "Broken link in install.md", "state": "open",
     "comments": 0},
    {"number": 35, "title": "Clarify auth token scopes", "state": "closed",
     "user": {"login": "asmith"}, "labels": [], "comments": 5},
]

NOT_FOUND = {"message": "Not Found",
             "documentation_url": "https://example.invalid/docs/issues"}


class DocsAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        path = url.path.rstrip("/")

        if path == "/ping":
            self.send(200, b"pong", "text/plain; charset=utf-8")
        elif path == "/slow":
            time.sleep(5)
            self.send_json(200, {"message": "finally"})
        elif path == "/repos/nalpeiron/docs":
            self.send_json(200, REPO)
        elif path == "/repos/nalpeiron/docs/issues":
            state = query.get("state", ["open"])[0]
            per_page = int(query.get("per_page", ["30"])[0])
            picked = []
            for issue in ISSUES:
                if state == "all" or issue["state"] == state:
                    picked.append(issue)
            self.send_json(200, picked[:per_page])
        elif path.startswith("/repos/nalpeiron/docs/issues/"):
            wanted = path.rsplit("/", 1)[-1]
            for issue in ISSUES:
                if str(issue["number"]) == wanted:
                    self.send_json(200, issue)
                    return
            self.send_json(404, NOT_FOUND)
        elif path == "/boom":
            self.send_json(500, {"message": "Server Error"})
        else:
            self.send_json(404, NOT_FOUND)

    def send_json(self, code, payload):
        self.send(code, json.dumps(payload).encode("utf-8"), "application/json")

    def send(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-RateLimit-Limit", "60")
        self.send_header("X-RateLimit-Remaining", "58")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


print(f"docs_server listening on http://127.0.0.1:{PORT}  (Ctrl-C to stop)")
ThreadingHTTPServer(("127.0.0.1", PORT), DocsAPI).serve_forever()
```

Leave it running in a second terminal while you work through the lesson:

```bash
python3 docs_server.py
```

It reports the address it is listening on and then stays running:

```output
docs_server listening on http://127.0.0.1:8073  (Ctrl-C to stop)
```

It serves these paths, and the sample data behind them is what every example below uses:

| Path | What it returns |
| --- | --- |
| `/repos/nalpeiron/docs` | One repository object |
| `/repos/nalpeiron/docs/issues` | Three issues, filtered by `state` and capped by `per_page` |
| `/repos/nalpeiron/docs/issues/41` | One issue; any unknown number gives `404` |
| `/ping` | The plain text `pong`, not JSON |
| `/slow` | A reply after a five-second pause |
| `/boom` | A `500` with a JSON error body |

Two things in that sample data are deliberate, and the examples depend on both. Issue 38 has no `user` and no `labels` keys at all — real APIs omit fields rather than sending empty ones. Issue 35 has a `labels` key whose value is an empty list. Code that handles one of those but not the other will look correct until it meets the other.

If you forget to start the server, every request fails immediately with `requests.exceptions.ConnectionError` naming port 8073. That is the error to expect when nothing is listening.

## Terminology and theory — a response is data you inspect, not a body you receive

**`requests`** is an installed distribution whose import name happens to match: `pip install requests`, then `import requests`. It is the de facto standard HTTP client for Python and the library nearly every Python SDK uses internally.

**`Response`** is the object `requests.get()` hands back. It is not the body of the reply — it is the whole reply: the status code, the headers, and the body together, already downloaded. You get the parts you want out of it by reading attributes (`response.status_code`) and calling methods (`response.json()`).

**Query parameters** are the `?state=open&per_page=2` part of a URL. In `curl` you type that yourself; in `requests` you pass a dict and the library builds the string, including any escaping the values need.

**Parsing** here means turning the body — which arrives as characters — into Python objects you can index. `response.text` gives you the characters; `response.json()` gives you the dict or list they describe.

The one idea that governs everything else: **a request that failed is still a request that succeeded.** If the server answers `404`, `requests` has done its job — it asked, and it got a reply — so it returns a `Response` and raises nothing. Only a failure to obtain any reply at all, such as an unreachable host or an expired timeout, raises. So the status code is something you check, never something Python checks for you.

## Syntax

### `requests.get()` returns a `Response`, and the URL it actually sent

The call takes a URL and returns immediately with everything the server said. `timeout=` is covered further down, but it belongs in every call you write, so it appears from the start here.

```python
import requests

BASE = "http://127.0.0.1:8073"

response = requests.get(f"{BASE}/repos/nalpeiron/docs", timeout=5)

print(response.status_code)
print(response.url)
print(response.headers["Content-Type"])
```

That prints the three pieces you asked for:

```output
200
http://127.0.0.1:8073/repos/nalpeiron/docs
application/json
```

`response.url` is worth knowing early: it is the URL that was really sent, after `requests` assembled parameters and followed any redirect. When a request returns something you did not expect, printing it is the fastest way to find out whether you asked the question you thought you asked.

### `.text` is the body as characters, `.json()` is the body as Python objects

These two are easy to confuse because they show nearly the same content. The difference is type, and therefore what you can do next.

```python
import requests

BASE = "http://127.0.0.1:8073"
response = requests.get(f"{BASE}/repos/nalpeiron/docs", timeout=5)

body_text = response.text          # the bytes decoded to a string
body_data = response.json()        # the same body parsed into Python objects

print(type(body_text), type(body_data))
print(body_text[:38])
print(body_data["full_name"], body_data["open_issues_count"])
```

The two attributes hold the same content in different forms:

```output
<class 'str'> <class 'dict'>
{"full_name": "nalpeiron/docs", "descr
nalpeiron/docs 2
```

`response.json()` does the same work as `json.loads(response.text)` from lesson 28, so what comes back follows the same rules: a JSON object becomes a dict, a JSON array becomes a list. The issues endpoint returns an array, so `response.json()` there gives you a list you loop over, not a dict you index by key.

`.json()` parses whatever the body holds and raises `requests.exceptions.JSONDecodeError` when the body is not JSON at all. The `/ping` endpoint returns the plain text `pong`, so calling `.json()` on it fails. The full traceback shows the `json` module's own failure first and then re-raises; this is the tail, which is the part that names the exception you would catch:

```text
During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/tmp/lesson37/ping_check.py", line 6, in <module>
    print(response.json())
          ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/requests/models.py", line 982, in json
    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)
requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

"Expecting value: line 1 column 1" is the signature of a body that was never JSON — an HTML error page from a proxy, a plain-text health check, or an empty body. When you see it, print `response.text` and look at what actually arrived.

### `params=` builds the query string, and silently drops `None` values

Passing a dict to `params=` produces the same URL you would have typed by hand, without you having to escape anything:

```python
import requests

BASE = "http://127.0.0.1:8073"

# params= builds the query string for you
a = requests.get(f"{BASE}/repos/nalpeiron/docs/issues",
                 params={"state": "all", "per_page": 2}, timeout=5)

# the same request written out by hand
b = requests.get(f"{BASE}/repos/nalpeiron/docs/issues?state=all&per_page=2",
                 timeout=5)

print(a.url)
print(b.url)
print(len(a.json()), len(b.json()))
```

Both calls send the identical URL, and both come back with two issues:

```output
http://127.0.0.1:8073/repos/nalpeiron/docs/issues?state=all&per_page=2
http://127.0.0.1:8073/repos/nalpeiron/docs/issues?state=all&per_page=2
2 2
```

Note that `per_page` was passed as the integer `2` and arrived as `2` in the URL — `requests` converts values to strings for you.

Two behaviors of `params=` are worth knowing because neither announces itself. A value of `None` means the key is left out of the URL entirely, which is how you write one call that sometimes filters and sometimes does not. A value that is a list repeats the key once per element, which is how APIs that accept repeated parameters are fed:

```python
import requests

BASE = "http://127.0.0.1:8073"
r = requests.get(f"{BASE}/repos/nalpeiron/docs/issues",
                 params={"state": "all", "labels": None,
                         "assignee": ["jdoe", "asmith"]},
                 timeout=5)
print(r.url)
```

The URL that went out is not the one the dict suggests:

```output
http://127.0.0.1:8073/repos/nalpeiron/docs/issues?state=all&assignee=jdoe&assignee=asmith
```

`labels` is gone, and no error was raised. If a filter you passed seems to be ignored, its value being `None` is the first thing to check — and `response.url` is what proves it.

### `.headers` ignores case, and `.get()` on it avoids `KeyError`

Header names are case-insensitive in HTTP, and `response.headers` behaves accordingly: any capitalization finds the value. Values always come back as strings, even when they hold numbers.

```python
import requests

BASE = "http://127.0.0.1:8073"
response = requests.get(f"{BASE}/repos/nalpeiron/docs", timeout=5)

print(response.headers["X-RateLimit-Remaining"])
print(response.headers["x-ratelimit-remaining"])
print(response.headers.get("X-Poll-Interval", "not sent"))
```

The first two lookups find the same header:

```output
58
58
not sent
```

Bracket access on a header the server did not send raises `KeyError`, so the `.get()` habit from lesson 11 applies here for the same reason: optional headers are genuinely optional, and rate-limit headers in particular disappear on some endpoints. The `KeyError` message reports the name lowercased (`KeyError: 'x-poll-interval'`) even though you asked in title case, which can be momentarily confusing when you are searching your own code for the string.

### `timeout=` is the only thing that stops a request from waiting forever

Without `timeout=`, a request has no deadline. If the server accepts your connection and then never answers, the script waits indefinitely — no exception, no output, nothing to read in a log.

```python
import requests
requests.get("http://127.0.0.1:8073/slow", timeout=2)
```

The `/slow` endpoint waits five seconds, so a two-second deadline ends the call. Again the traceback is chained — urllib3's timeout comes first — and this is the tail:

```text
During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/tmp/lesson37/slow_check.py", line 2, in <module>
    requests.get("http://127.0.0.1:8073/slow", timeout=2)
  File "/usr/local/lib/python3.12/dist-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/usr/local/lib/python3.12/dist-packages/requests/adapters.py", line 691, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='127.0.0.1', port=8073): Read timed out. (read timeout=2)
```

The frames between the ones shown are all inside `requests` itself, which is normal for a library failure: the line of yours that started it is the first one in the tail, and the exception name and message are the last.

> [!warning] A hang is not a failure your tests will catch
> A script with no `timeout=` passes every test against a healthy server and hangs forever against a sick one.
> Set `timeout=` on every request you write, and catch `requests.exceptions.ReadTimeout` where a hang would matter.

## Worked examples

### Example 1 — check the status before you parse the body

The order here is the pattern to internalize: get the response, check the code, and only then parse. Parsing first works right up until the day the server answers `500` with an HTML error page.

```python
import requests

BASE = "http://127.0.0.1:8073"

response = requests.get(f"{BASE}/repos/nalpeiron/docs", timeout=5)

if response.status_code == 200:
    repo = response.json()
    print(f"Repository:  {repo['full_name']}")
    print(f"Description: {repo['description']}")
    print(f"Branch:      {repo['default_branch']}")
    print(f"Open issues: {repo['open_issues_count']}")
    print(f"Private:     {repo['private']}")
else:
    print(f"Could not read the repository (status {response.status_code}).")
```

The five fields come back as the repository object describes them:

```output
Repository:  nalpeiron/docs
Description: Product documentation sources
Branch:      main
Open issues: 2
Private:     False
```

Note the quoting inside the f-strings: the outer string uses double quotes, so the dict keys inside use single quotes. Mixing them up is the most common f-string error you will hit while pulling fields out of JSON.

### Example 2 — filter with `params=`, then survive the missing fields

This is what most SDK-shaped work looks like: ask for a filtered list, loop over it, and pull a few fields from each record. The guard clauses matter because the API omits fields it has no value for.

```python
import requests

BASE = "http://127.0.0.1:8073"

response = requests.get(
    f"{BASE}/repos/nalpeiron/docs/issues",
    params={"state": "all"},
    timeout=5,
)
print(f"Asked for: {response.url}")

issues = response.json()
print(f"Received {len(issues)} issues\n")

for issue in issues:
    user = issue.get("user")
    if user:
        author = user["login"]
    else:
        author = "unknown"

    labels = issue.get("labels")
    if labels:
        label_text = ", ".join(labels)
    else:
        label_text = "none"

    print(f"#{issue['number']} [{issue['state']}] {issue['title']}")
    print(f"    by {author} — labels: {label_text}")
```

The filter reached the server, and all three issues print:

```output
Asked for: http://127.0.0.1:8073/repos/nalpeiron/docs/issues?state=all
Received 3 issues

#41 [open] Rate limit page has no examples
    by jdoe — labels: docs, api
#38 [open] Broken link in install.md
    by unknown — labels: none
#35 [closed] Clarify auth token scopes
    by asmith — labels: none
```

Issue 38 and issue 35 both print `none`, and they get there by different routes. For 38, `issue.get("labels")` returns `None` because the key is absent; for 35, it returns `[]` because the key is present and empty. `if labels:` is false in both cases, which is exactly the behavior you want here, and it is why `if labels is None:` would have been wrong — it would catch 38 and let 35 through. Without the guards the loop raises: `issue["labels"]` on issue 38 raises `KeyError`, and `", ".join(None)` raises `TypeError: can only join an iterable`. The truthiness rules from lesson 14 are what keep both away.

Changing `params={"state": "all"}` to `{"state": "open"}` returns two issues instead of three. That the URL printed at the top matches what you asked for is how you confirm the filter reached the server rather than being quietly dropped.

### Example 3 — decide what the script should do next from the status code

Lesson 35 framed status codes as instructions for the caller. Here that framing becomes code: each class of code leads to a different action, and the body is only read where reading it makes sense.

```python
import requests

BASE = "http://127.0.0.1:8073"


def report(path):
    response = requests.get(f"{BASE}{path}", timeout=5)
    remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
    print(f"GET {path} -> {response.status_code} (calls left: {remaining})")

    if response.status_code == 200:
        print("    usable; parse the body")
    elif response.status_code == 404:
        detail = response.json()
        print(f"    the API said: {detail['message']}")
        print("    check the path; do not retry")
    elif response.status_code >= 500:
        print("    the server failed, not you; retrying later may work")
    else:
        print("    unhandled status; log it and stop")


report("/repos/nalpeiron/docs/issues/41")
report("/repos/nalpeiron/docs/issues/9999")
report("/boom")
```

Each call completes, and each status leads somewhere different:

```output
GET /repos/nalpeiron/docs/issues/41 -> 200 (calls left: 58)
    usable; parse the body
GET /repos/nalpeiron/docs/issues/9999 -> 404 (calls left: 58)
    the API said: Not Found
    check the path; do not retry
GET /boom -> 500 (calls left: 58)
    the server failed, not you; retrying later may work
```

All three calls completed. No exception was raised for the `404` or the `500`, and both of those responses had headers and a parseable JSON body just like the successful one — which is why `response.json()` works fine on the `404` and gives you the API's own explanation. Reading the message out of an error body is usually the difference between a script that says `404` and a script that says what was not found.

## Lookup table

| Use when                                      | Call                                                  | Result                                                                                    |
| --------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| You want to fetch a URL                       | `requests.get(url, timeout=5)`                        | A `Response`: `<class 'requests.models.Response'>`, holding status, headers, and body     |
| You need to know whether it worked            | `response.status_code`                                | `200`                                                                                     |
| You want a quick yes/no on success            | `response.ok`                                         | `True` for `200`, `False` for `404`                                                       |
| You want the body as characters               | `response.text`                                       | `'{"full_name": "nalpeiron/docs", ...}'` — a `str`                                        |
| You want the body as Python data              | `response.json()`                                     | `{'full_name': 'nalpeiron/docs', ...}`; a list for endpoints that return an array         |
| The body is not JSON                          | `requests.get(f"{BASE}/ping").json()`                 | Raises `requests.exceptions.JSONDecodeError`: `Expecting value: line 1 column 1 (char 0)` |
| You need the raw bytes (an image, a download) | `response.content[:20]`                               | `b'{"full_name": "nalpe'`                                                                 |
| You want the encoding used to decode `.text`  | `response.encoding`                                   | `'utf-8'`                                                                                 |
| You want to add query parameters              | `requests.get(url, params={"state": "all"})`          | The server receives `?state=all`                                                          |
| You want a parameter left out on some runs    | `params={"state": "all", "labels": None}`             | `labels` is omitted from the URL entirely, with no error                                  |
| You want to send one parameter twice          | `params={"assignee": ["jdoe", "asmith"]}`             | `?assignee=jdoe&assignee=asmith`                                                          |
| You want to see the URL actually sent         | `response.url`                                        | `'http://127.0.0.1:8073/repos/nalpeiron/docs/issues?state=all'`                           |
| You want to read a response header            | `response.headers["X-RateLimit-Remaining"]`           | `'58'` — a string, and the lookup ignores case                                            |
| The header may not be present                 | `response.headers.get("X-Poll-Interval", "not sent")` | `'not sent'`; bracket access instead raises `KeyError`: `'x-poll-interval'`               |
| You want to cap how long to wait              | `requests.get(url, timeout=2)`                        | Raises `requests.exceptions.ReadTimeout` when the server takes longer                     |
| Nothing is listening on the host or port      | `requests.get(url, timeout=5)`                        | Raises `requests.exceptions.ConnectionError` naming the host and port                     |
| You want the installed version                | `requests.__version__`                                | `'2.33.1'`                                                                                |

## Exercise

Write `issue_report.py`, a command-line tool that fetches issues from the local API and writes a Markdown report.

The script must:

1. Take the issue state as a required positional argument, and support two optional flags: one that sets the repository (defaulting to `nalpeiron/docs`) and one that sets the output file path (defaulting to `issue-report.md`). `--help` must explain all three.
2. Request `/repos/<repo>/issues` with the state sent as a query parameter, not spliced into the URL string, and with a timeout set.
3. Decide what to do from the status code before touching the body. On `404`, print a message that includes the API's own explanation taken from the error body, and write no file. On `500` or above, print a message saying it is a server problem and write no file. Only on `200` should a report be produced.
4. Write a Markdown file containing a heading naming the repository and the state, one bullet per issue giving its number, title, author, and labels, then a line giving the calls remaining from the response headers, and a final line showing the equivalent `curl` command for the request that was actually sent.
5. Use `unknown` as the author when the issue has no user, and `none` when it has no labels — including when the labels key is present but empty.
6. Print a single summary line to standard output saying how many issues were written and where.

Run it three ways: `open`, `all`, and once against a repository that does not exist.

Expected results — `python3 issue_report.py open` prints one line and produces `issue-report.md`:

```output
Wrote 2 issues to issue-report.md
```

The file it writes looks like this:

```markdown
# nalpeiron/docs — open issues

- #41 Rate limit page has no examples — jdoe (docs, api)
- #38 Broken link in install.md — unknown (none)

Calls remaining: 58
Equivalent curl: curl 'http://127.0.0.1:8073/repos/nalpeiron/docs/issues?state=open'
```

Asking for `all` adds the closed issue, and its empty labels list must produce `none` rather than an empty pair of parentheses:

```markdown
# nalpeiron/docs — all issues

- #41 Rate limit page has no examples — jdoe (docs, api)
- #38 Broken link in install.md — unknown (none)
- #35 Clarify auth token scopes — asmith (none)

Calls remaining: 58
Equivalent curl: curl 'http://127.0.0.1:8073/repos/nalpeiron/docs/issues?state=all'
```

A repository the server does not know about writes nothing and reports why, using the `message` field the API sent in the error body:

```output
Nothing written: the API said Not Found for nalpeiron/ghost
```

Your wording in the printed lines can differ from mine; the facts in them cannot. The counts, the file contents, and which runs produce a file are the parts to check.
