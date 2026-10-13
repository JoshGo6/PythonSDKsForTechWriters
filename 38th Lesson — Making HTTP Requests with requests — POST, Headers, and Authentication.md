# Lesson 38 — Sending data and authenticating with `requests`

Lesson 37 covered the half of `requests` that only reads, which is a `GET` with query parameters and the response object it hands back. This lesson covers the half that writes. You'll send a JSON body with `requests.post()`, replace a record with `requests.put()`, amend one with `requests.patch()`, remove one with `requests.delete()`, set request headers of your own, and attach a credential so GitHub accepts the call instead of refusing it.

Two things stay out, and both arrive shortly. Turning a failing status code into an exception is Lesson 38b, so every check in this lesson uses an `if` on the response you already hold. Wrapping all of it in one reusable function that handles errors is Lesson 39.

## Set up the examples

The following imports and four constants have already run in every example below, so they aren't repeated in each block:

```python
import os
import sys
import requests

API = "https://api.github.com"
REPO = f"{API}/repos/PyGithub/PyGithub"
ISSUES = f"{API}/repos/JoshGo6/ThrowAway/issues"
STUB = "http://127.0.0.1:8038/records/1"
```

Examples 1, 2, 5, and 6 go to real GitHub. Examples 1, 2, and 5 need no credential, so you can run them as they stand; Example 6 writes to your own `JoshGo6/ThrowAway` and needs a token. Examples 3 and 4 go to a small server on your own machine, for a reason worth stating plainly: GitHub has no endpoint that accepts both a `PUT` and a `PATCH` against one record, and no endpoint at all that deletes an issue, so the two behaviors this lesson most needs to show can't be shown against it.

> [!warning] The anonymous rate limit is 60 requests per hour
> Unauthenticated requests are counted against your IP address rather than an account, and the ceiling is 60 per hour. Running the GitHub examples repeatedly will exhaust it, and GitHub then answers `403` until the hour rolls over.

You don't need to read the next block, and nothing in this lesson asks you to understand it. It's a server that holds one record in memory and answers `GET`, `PUT`, `PATCH`, and `DELETE` for it, written the way Python's standard library wants such a server written: with a `class`, with `self`, and by inheriting from `BaseHTTPRequestHandler`. Classes arrive in Lesson 43, methods and attributes in Lesson 44, and inheritance in Lesson 46, so all three are ahead of you here. There's no way around it, because the standard library offers no non-class way to serve HTTP, and the alternative would be to describe the two behaviors instead of letting you watch them. Treat it as equipment: you start it, you send requests to it, and the syntax section, the worked examples, and the exercise all work without your ever reading a line of it.

The following file is that server, saved as `stub.py`:

```python
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PAGE = {
    "path": "docs/api/auth.md",
    "title": "Authentication",
    "owner": "josh",
    "state": "published",
}
STORE = {"1": dict(PAGE)}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # keep the server quiet so only the example's own output shows

    def reply(self, code, payload=None):
        body = b"" if payload is None else json.dumps(payload, indent=2).encode()
        self.send_response(code)
        if body:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def sent_body(self):
        size = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(size)
        try:
            return json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return None

    def missing(self):
        self.reply(404, {
            "message": "Not Found",
            "documentation_url": "https://example.invalid/docs/records",
            "status": "404",
        })

    def do_GET(self):
        if self.path == "/records/1" and "1" in STORE:
            self.reply(200, STORE["1"])
        else:
            self.missing()

    def do_PUT(self):
        if self.path != "/records/1":
            self.missing()
            return
        body = self.sent_body()
        if body is None:
            self.reply(400, {"message": "Body was not JSON", "status": "400"})
            return
        STORE["1"] = body  # replaces the record, so omitted keys are gone
        self.reply(200, STORE["1"])

    def do_PATCH(self):
        if self.path != "/records/1" or "1" not in STORE:
            self.missing()
            return
        body = self.sent_body()
        if body is None:
            self.reply(400, {"message": "Body was not JSON", "status": "400"})
            return
        STORE["1"].update(body)  # merges, so omitted keys survive
        self.reply(200, STORE["1"])

    def do_DELETE(self):
        if self.path == "/records/1" and "1" in STORE:
            del STORE["1"]
            self.reply(204)
        else:
            self.missing()

    def do_POST(self):
        self.reply(405, {"message": "Use PUT to create this record", "status": "405"})


ThreadingHTTPServer(("127.0.0.1", 8038), Handler).serve_forever()
```

The following command starts it, and it prints nothing and keeps running until you stop it with Ctrl-C, so give it a terminal of its own and run the examples in another:

```bash
python3 stub.py
```

Example 6 and the exercise write to a repository of yours, which takes two things you set up once. Create a repository named `ThrowAway` under your own account, and create a fine-grained personal access token whose repository permissions include **Issues: read and write** for it. Then export the token as `GITHUB_TOKEN` in the shell you run the examples from, which is the pattern Lesson 31 established and the only place a token belongs. Nothing in this lesson prints a token, and a token never belongs in a script's source.

## Terminology and theory

A **request body** is the data you send with a request, carried separately from the URL. A `GET` puts everything it has to say in the path and the query string, which is why Lesson 37 needed only `params=`. A write has more to say than a URL can hold, so the fields go in the body, and the request's headers tell the server how to interpret the bytes that arrive.

The four write methods differ in what they claim to do to the record, and the server, not `requests`, decides what that claim means. `POST` creates something new and lets the server name it, so sending the same `POST` twice creates two records. `PUT` replaces a record with exactly what you sent, so a field you leave out is gone. `PATCH` amends a record with just the fields you sent, so a field you leave out survives. `DELETE` removes it. The difference between `PUT` and `PATCH` is the one that costs people data, because a partial `PUT` is a successful request: it answers `200`, and the fields you didn't mention are simply no longer there.

This is where **idempotent** earns its place, because it's the word APIs use for the distinction. An idempotent request leaves the same state behind however many times you send it, which `PUT` and `DELETE` both do, and which `POST` doesn't. It matters practically rather than theoretically: a `POST` you retry after a timeout may well create a second record, and a `DELETE` you retry is safe.

A **header** is one name-and-value pair of metadata attached to a request or a response, and `requests` sets several on your behalf before you set any of your own. Two headers matter to GitHub specifically. `Accept` asks for a particular response format, and GitHub's current one is `application/vnd.github+json`. `X-GitHub-Api-Version` pins the API version, and `2022-11-28` is the value to pin: it's what GitHub uses when you send no version header at all, so pinning it means your script keeps behaving the same way on the day GitHub changes its default.

A **credential** is whatever proves the request is allowed, and it travels in a header too. There are three shapes you'll meet, and GitHub uses the first. A **bearer token** goes in the `Authorization` header as the word `Bearer` and a space and the token. An **API key** goes in a header the service names itself, often something like `X-API-Key`, and differs from a bearer token only in which header carries it. **Basic auth** puts a username and a password in the same `Authorization` header, as the word `Basic` and a space and the pair joined by a colon and encoded as base64.

Base64 is worth one sentence of its own, because its appearance invites a wrong conclusion. It's an encoding and not encryption, so anyone holding the header can reverse it to the original username and password in a second, which is why basic auth is only ever as safe as the HTTPS connection carrying it.

Two failures round this out, and they look alike until you read the body. A request whose credential is absent or unreadable gets `401`, which means GitHub doesn't know who you are. A request whose credential is fine but insufficient gets `403`, which means GitHub knows who's asking and is refusing anyway, and with a fine-grained token that usually means a permission you didn't grant. Both are plain responses, not exceptions, so nothing in Python raises and your script carries on unless you check.

## Read the syntax

The four write calls take the same shape as the `GET` from Lesson 37, differing only in the function name and in whether they carry a body.

The following block shows all four against one URL, with a comment on each saying what the server does with it:

```python
requests.post(url, json=payload, timeout=10)    # create; the server names the result
requests.put(url, json=payload, timeout=10)     # replace; omitted fields are gone
requests.patch(url, json=payload, timeout=10)   # amend; omitted fields survive
requests.delete(url, timeout=10)                # remove; usually no body either way
```

Keep `timeout=10` on every one of them for the reason Lesson 37 gave, which is that a request without a timeout can hang forever. It matters more here than it did for a `GET`, because a write that hangs leaves you unsure whether the change landed.

The body goes in one of two keyword arguments, and choosing the wrong one is the commonest mistake in this lesson.

The following two calls send the same dictionary and produce entirely different requests:

```python
payload = {"title": "Document the rate limit", "labels": ["docs"]}
requests.post(url, json=payload, timeout=10)    # JSON: Content-Type set for you
requests.post(url, data=payload, timeout=10)    # a web form, and the list collapses
```

Use `json=` for an API. It serializes the dictionary to JSON, sets `Content-Type: application/json` without being asked, and preserves the structure, so a nested dictionary or a list of strings arrives intact. Use `data=` for an HTML form, which is what it builds: it encodes the pairs the way a browser's form submission does, under `Content-Type: application/x-www-form-urlencoded`, and that format has no way to express a list or a nested object. Passing both at once is the trap worth knowing about, because `data=` wins silently and the JSON you thought you were sending never leaves.

Your own headers go in `headers=`, as a dictionary that `requests` merges with the ones it already sets.

The following block sets two headers, and then removes one that `requests` would otherwise send:

```python
head = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
requests.get(url, headers=head, timeout=10)             # adds both to the request
requests.get(url, headers={"User-Agent": None}, timeout=10)   # drops a default header
```

A header you set replaces the default of the same name, and a header whose value is `None` is removed from the request rather than sent as empty. That last form is the only way to drop something `requests` adds for you.

Credentials reach the server through either `headers=` or the dedicated `auth=` argument, depending on their shape.

The following block shows all three credential forms, with the token read from the environment rather than written down:

```python
token = os.environ["GITHUB_TOKEN"]
requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)  # GitHub's
requests.get(url, headers={"X-API-Key": token}, timeout=10)      # an API key header
requests.get(url, auth=("josh", "s3cret"), timeout=10)           # basic auth
```

The first two are the same mechanism with different header names, and you build the header value yourself. The third is different in that `requests` does the work: you hand `auth=` a two-item tuple of username and password, and it builds the `Authorization: Basic …` header, base64 included. Reading the token with `os.environ["GITHUB_TOKEN"]` raises `KeyError` when the variable is unset, which Lesson 31 preferred over `os.getenv()` for exactly this case, since a write that proceeds without a credential is worse than one that stops.

## Work through the examples

Each example adds one thing to the one before it. The first five run without a token and their output is from a real run; the last one writes to a repository, so its output came from running it on my own machine.

### Example 1: Send a JSON body, and see what `data=` sends instead

This first example establishes the base case, which is what each of the two body arguments actually puts on the wire.

The following script sends one dictionary twice, once each way, and reads back what `requests` built:

```python
payload = {"title": "Document the rate limit", "labels": ["docs"]}

as_json = requests.post(ISSUES, json=payload, timeout=10)     # JSON body
print("json=", as_json.request.headers["Content-Type"])
print("     ", as_json.request.body)

as_form = requests.post(ISSUES, data=payload, timeout=10)     # form body
print("data=", as_form.request.headers["Content-Type"])
print("     ", as_form.request.body)
print("refused:", as_json.status_code, as_json.json()["message"])
```

The following output shows both bodies, and the refusal that both requests got for having no credential:

```output
json= application/json
      b'{"title": "Document the rate limit", "labels": ["docs"]}'
data= application/x-www-form-urlencoded
      title=Document+the+rate+limit&labels=docs
refused: 401 Requires authentication
```

The `b` in front of the JSON body marks it as bytes rather than characters, which is what finally goes over the connection. Compare the two bodies and the loss in the second one is plain: `labels` went from a list containing `"docs"` to the string `docs`, and nothing in the request records that it was ever a list. Both calls answered `401 Requires authentication`, because neither carried a token, and neither raised an exception on the way.

### Example 2: Set your own headers, and watch one get rejected

This example adds headers of your own, and shows that the server reads them rather than ignoring them.

The following script pins the version GitHub documents, then pins one that no longer exists:

```python
pinned = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
asked = requests.get(REPO, headers=pinned, timeout=10)
print("accept  :", asked.request.headers["Accept"])
print("version :", asked.request.headers["X-GitHub-Api-Version"])
print("default :", requests.get(f"{API}/zen", timeout=10).request.headers["Accept"])

dead = requests.get(f"{REPO}/issues", params={"per_page": 1}, timeout=10,
                    headers={"X-GitHub-Api-Version": "2019-01-01"})
print("dead    :", dead.status_code, dead.json()["errors"])
```

The following output confirms both headers went out, names the `Accept` that `requests` sends when you set none, and shows what an unsupported version costs you:

```output
accept  : application/vnd.github+json
version : 2022-11-28
default : */*
dead    : 400 The version you specified in the "X-GitHub-API-Version" request header, "2019-01-01", is not a supported version. The following versions are currently supported: "2026-03-10" (most recent) and "2022-11-28".
```

The default `Accept` is `*/*`, meaning no preference at all, which is why pinning the GitHub media type is worth doing rather than relying on the default. A dead version answers `400 Bad Request` and names the versions that work, so this is one failure that tells you how to fix it. Setting a header's value to `None` instead of a string removes it from the request, and a `requests.get(url, headers={"User-Agent": None})` sends no `User-Agent` at all rather than an empty one.

The dead-version request deliberately asks for the issues list rather than the repository the two lines above it just fetched, and the reason is a caching behavior worth knowing about. GitHub checks the version header only on a request that reaches the API: when it answers a URL from its cache, the response comes back without the header being looked at. Sending the retired version to a URL you have already fetched successfully therefore answers `200` and hides the error, which is exactly what happened the first time I wrote this example.

> [!note] Confirming the caching behavior yourself
> Fetch one URL with `X-GitHub-Api-Version` set to `2022-11-28`, then fetch the identical URL with it set to `2019-01-01`. The second call answers `200`. Change one character of the query string so the URL is new and the same retired version answers `400`.

### Example 3: Replace a record with `PUT`, and amend one with `PATCH`

This example is the one worth slowing down for, because it puts the two methods against the same record and the same partial body, so the only variable left is the method name.

The following script seeds a four-field record, sends one field by each method, and prints what the record holds afterward:

```python
whole = {"path": "docs/api/auth.md", "title": "Authentication",
         "owner": "josh", "state": "published"}
rename = {"title": "Authentication and tokens"}

requests.put(STUB, json=whole, timeout=10)                 # seed the record
replaced = requests.put(STUB, json=rename, timeout=10)
print("PUT  ", replaced.status_code, replaced.json())

requests.put(STUB, json=whole, timeout=10)                 # seed it again
amended = requests.patch(STUB, json=rename, timeout=10)
print("PATCH", amended.status_code, amended.json())
```

The following output is the whole lesson of this example, and the status code is the same on both lines:

```output
PUT   200 {'title': 'Authentication and tokens'}
PATCH 200 {'path': 'docs/api/auth.md', 'title': 'Authentication and tokens', 'owner': 'josh', 'state': 'published'}
```

The `PUT` took the record from four fields to one. The `path`, `owner`, and `state` fields weren't changed and weren't rejected; they were replaced along with everything else, by a body that didn't mention them. The `PATCH` sent the identical body and kept all four. Both answered `200`, so there's no signal in the status code, in the headers, or in any exception to tell you which of the two just happened, and a script that reaches for `PUT` when it means `PATCH` destroys data and reports success. Reach for `PATCH` whenever you're changing part of something that already exists, and use `PUT` only when you genuinely hold the entire record.

### Example 4: Remove a record, and read a response with no body

This example adds `DELETE`, whose response is shaped unlike any other in this lesson, and it runs directly after Example 3, which left the record in place.

The following script deletes the record, deletes it again, and then tries the same thing against a GitHub issue:

```python
first = requests.delete(STUB, timeout=10)
print("first :", first.status_code, first.ok, "body length", len(first.text))

second = requests.delete(STUB, timeout=10)
print("second:", second.status_code, second.json()["message"])

absent = requests.delete(f"{API}/repos/JoshGo6/ThrowAway/issues/4", timeout=10)
print("GitHub:", absent.status_code, absent.json()["message"])
```

The following output shows a success with nothing in it, and two different roads to the same `404`:

```output
first : 204 True body length 0
second: 404 Not Found
GitHub: 404 Not Found
```

A `204 No Content` is a success with an empty body, and `response.ok` is `True` for it. Calling `response.json()` on that response raises `requests.exceptions.JSONDecodeError`, because an empty string isn't JSON, so a `DELETE` is the one call where parsing the body unconditionally breaks a working script. The second delete found nothing left and answered `404`, which is the normal outcome of repeating a `DELETE` rather than a problem. GitHub's `404` on the last line has a different cause worth knowing: there's no endpoint that deletes an issue at all, so that `404` reports the absence of the route rather than the absence of the issue. An issue's life ends at a `PATCH` that sets its `state` to `closed`, which is what Example 6 does.

### Example 5: Let `auth=` build a basic-auth header

This example adds the one credential form you don't build yourself, and shows what `requests` puts in the header on your behalf.

The following script sends two different username-and-password pairs and prints the header each one produced:

```python
josh = requests.get(f"{API}/user", auth=("josh", "not-a-real-token"), timeout=10)
print("josh  :", josh.request.headers["Authorization"])

ada = requests.get(f"{API}/user", auth=("ada", "not-a-real-token"), timeout=10)
print("ada   :", ada.request.headers["Authorization"])
print("basic :", josh.status_code, josh.json()["message"])

bearer = requests.get(f"{API}/user", timeout=10,
                      headers={"Authorization": "Bearer ghp_notarealtoken"})
print("bearer:", bearer.status_code, bearer.json()["message"])
```

The following output shows the two basic-auth headers, then the two different ways GitHub says no:

```output
josh  : Basic am9zaDpub3QtYS1yZWFsLXRva2Vu
ada   : Basic YWRhOm5vdC1hLXJlYWwtdG9rZW4=
basic : 401 Requires authentication
bearer: 401 Bad credentials
```

Both headers are the word `Basic` and a base64 encoding of `username:password`, and the two values differ only because the usernames do, which is as much obfuscation as basic auth provides. The credentials here are invented, so both requests failed, but the failure messages differ and the difference is informative: a malformed bearer token gets `Bad credentials`, because GitHub recognized a token and rejected it, while the basic-auth attempt gets `Requires authentication`, because nothing GitHub could use as a credential arrived. Reading that message is quicker than guessing which of your two credential mechanisms is wrong.

### Example 6: Create and close a real issue with your token

This last example puts a working credential on a real write, and it's the only example here that changes anything.

The following script creates an issue in your throwaway repository and immediately closes it:

```python
head = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28"}
made = requests.post(ISSUES, json={"title": "Document the rate limit"},
                     headers=head, timeout=10)
print("POST ", made.status_code, made.reason)
if not made.ok:
    print("gave up:", made.json()["message"], file=sys.stderr)
    sys.exit(1)
shut = requests.patch(f"{ISSUES}/{made.json()['number']}", headers=head, timeout=10,
                      json={"state": "closed", "state_reason": "completed"})
print("PATCH", shut.status_code, shut.json()["state"], shut.json()["state_reason"])
```

The following output came from running that script on my own machine, against my own repository:

```output
POST  201 Created
PATCH 200 closed completed
```

A successful create answers `201 Created` rather than `200`, and its body is the new issue, which is where `made.json()["number"]` comes from — the server named the record, and a `POST` is the only method here that leaves you to find out what the name turned out to be. The `if not made.ok` guard between the two calls is doing real work rather than ceremony: without it, a refused create still returns a response, `made.json()["number"]` raises `KeyError` against the error body, and the traceback names the missing key instead of GitHub's explanation. I hit exactly that while writing this lesson, and the `403` underneath it said `Resource not accessible by personal access token`, which is the message a fine-grained token produces when it can read the repository but wasn't granted **Issues: write**.

## Lookup table

The following table covers everything this lesson introduces, with every result taken from a real run against either GitHub or the local server:

| Use when | Call | Result |
| --- | --- | --- |
| You want to create something and let the server name it | `requests.post(url, json=payload, timeout=10)` | `201 Created`, with the new record as the body |
| You want to send a dictionary as a JSON body | `json=payload` | Body `b'{"title": "…", "labels": ["docs"]}'`, `Content-Type: application/json` |
| You want to send a dictionary as an HTML form | `data=payload` | Body `title=Document+the+rate+limit&labels=docs`; the list collapsed to one value |
| You passed both body arguments by mistake | `requests.post(url, json=a, data=b)` | `data` wins silently; the body is form-encoded and `a` never leaves |
| You want to replace a record with what you sent | `requests.put(url, json=payload, timeout=10)` | `200`, and the record is now only `{'title': 'Authentication and tokens'}` |
| You want to change part of a record and keep the rest | `requests.patch(url, json=payload, timeout=10)` | `200`, and all four fields survive with `title` changed |
| You sent a `PUT` with no body at all | `requests.put(url, timeout=10)` | `200`, request body `None`, and the record is now `{}` |
| You want to remove a record | `requests.delete(url, timeout=10)` | `204`, `response.ok` is `True`, `len(response.text)` is `0` |
| You parsed a `204` without checking for a body | `response.json()` on a `204` | Raises `requests.exceptions.JSONDecodeError` |
| You repeated a `DELETE` that already succeeded | `requests.delete(url, timeout=10)` | `404 Not Found`, which is the expected second outcome |
| You want to delete a GitHub issue | `requests.delete(f"{API}/repos/…/issues/4")` | `404 Not Found`; no such endpoint exists, so close it instead |
| You want to close a GitHub issue | `json={"state": "closed", "state_reason": "completed"}` | `200`, with `state` `closed` and `state_reason` `completed` |
| You want to add headers to a request | `requests.get(url, headers=head, timeout=10)` | Both headers appear in `response.request.headers` |
| You want to drop a header `requests` sets for you | `headers={"User-Agent": None}` | The header is absent from the request rather than empty |
| You want to know the `Accept` sent when you set none | `response.request.headers["Accept"]` | `'*/*'`, meaning no preference |
| You want to pin GitHub's API version | `{"X-GitHub-Api-Version": "2022-11-28"}` | Accepted; it's also what an omitted header selects |
| You pinned a version GitHub no longer supports | `{"X-GitHub-Api-Version": "2019-01-01"}` | `400` on a URL GitHub answers freshly, and `errors` names `"2026-03-10"` and `"2022-11-28"` |
| You sent a retired version to a URL you just fetched | `{"X-GitHub-Api-Version": "2019-01-01"}` | `200` from the cache, with the header never checked |
| You want to send a bearer token | `headers={"Authorization": f"Bearer {token}"}` | Accepted; `201` on the create in Example 6 |
| You want to send an API key in a header | `headers={"X-API-Key": key}` | The same mechanism as a bearer token, under a name the service picks |
| You want `requests` to build basic auth for you | `auth=("josh", "not-a-real-token")` | Header `Basic am9zaDpub3QtYS1yZWFsLXRva2Vu` |
| You sent a token GitHub can read but not accept | `headers={"Authorization": "Bearer ghp_notarealtoken"}` | `401`, message `Bad credentials` |
| You sent no credential on a write | `requests.post(ISSUES, json=payload)` | `401`, message `Requires authentication` |
| You sent a token missing the permission it needs | A fine-grained token without **Issues: write** | `403`, message `Resource not accessible by personal access token` |
| You want the body `requests` actually built | `response.request.body` | `b'{"title": "Document the rate limit", "labels": ["docs"]}'` |
| You want the token without writing it in the script | `os.environ["GITHUB_TOKEN"]` | The token's value, or `KeyError` when the variable is unset |

## Exercise: Open, amend, and close an issue from the command line

Write `issue_run.py`, which opens one issue in your throwaway repository, changes it twice, reads it back, closes it, and leaves a Markdown record of every call it made.

Your script must do all of the following:

1. Take the issue's title as a required positional argument, and accept two optional flags: one that sets the repository, defaulting to your own `JoshGo6/ThrowAway`, and one that sets the output file, defaulting to `issue-log.md`. Running it with `--help` must explain all three.
2. Read the token from the environment and stop with a message naming the variable before sending any request, when the variable is unset or empty.
3. Make every request carry the token and pin the API version.
4. Make four calls in this order: create the issue, add a body to it, read it back, and close it with a reason. Stop as soon as a call answers outside the `2xx` range, and log that call's status code together with GitHub's own `message` field at `ERROR`.
5. Write a Markdown table to the output file, with one row for every call that was made, giving the method, the path the request went to, the status code, and the issue's state after that call. Write the table even on the runs that stop early.
6. Print the issue's number and its browser URL as the last line.

Everything you need from the earlier lessons is in the reference set, which is faster to search than the lesson files. The `Lookup` section of [[Command-line Arguments]] has the `argparse` patterns, [[Environment Variables]] has the token reading, [[Logging]] has the configuration calls, and [[Reading and Writing Files]] has the write. [[Making HTTP Requests]] covers the calls from this lesson and Lesson 37. [[Syntax Index]] maps a call to the page that owns it when you know the name but not where it lives.

### Expected output

Both blocks below came from a real run of my own solution on my own machine, so they show what a correct script produces rather than what one ought to.

The following two lines are what the script prints, and your issue number will differ because GitHub assigns the next one in the repository:

```output
INFO wrote issue-log.md with 4 rows
issue 4: https://github.com/JoshGo6/ThrowAway/issues/4
```

The following is the file the script wrote, where the fourth row is the only one whose state has changed and the first row's path has no issue number in it because the number didn't exist yet:

```markdown
# Issue run log

| Method | Path | Status | State after |
| --- | --- | --- | --- |
| `POST` | `/repos/JoshGo6/ThrowAway/issues` | 201 | open |
| `PATCH` | `/repos/JoshGo6/ThrowAway/issues/4` | 200 | open |
| `GET` | `/repos/JoshGo6/ThrowAway/issues/4` | 200 | open |
| `PATCH` | `/repos/JoshGo6/ThrowAway/issues/4` | 200 | closed |
```

The following command produced both blocks:

```bash
python3 issue_run.py "Exercise run: document the rate limit"
```
