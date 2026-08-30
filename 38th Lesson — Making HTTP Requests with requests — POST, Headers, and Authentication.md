# Lesson 38 - Sending Data and Authenticating with requests

Lesson 37 read data with `requests.get()`. This lesson writes it: creating records, changing them, removing them, and proving to the server that you are allowed to. The four calls are `requests.post()`, `requests.put()`, `requests.patch()`, and `requests.delete()`, and they differ from `get()` in two ways — they carry a body, and they almost always carry credentials.

## Setup — a local API that accepts writes

Every example below runs against a small API on your own machine. Save this as `docs_api.py` and leave it running in its own terminal while you work through the lesson.

Save it and run it — you do not need to read it. It is written with `class`, `self`, and inheritance, which Lessons 43-46 cover and this lesson does not use; Python's `http.server` cannot be used any other way. Nothing in the syntax section, the worked examples, or the exercise requires understanding any of it. The endpoint table below is the only part you need.

```python
"""A tiny local stand-in for a docs-issue API. Run it in its own terminal.

    python3 docs_api.py

It listens on http://127.0.0.1:8077.
"""
import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = "docs-token-123"
USER = "docs-bot"

ISSUES = {
    1: {"number": 1, "title": "auth.md is out of date", "body": "Rewrite the token section.",
        "state": "open", "labels": ["docs", "auth"], "user": "jdoe"},
    2: {"number": 2, "title": "rate-limit.md missing example", "body": "Add a 403 example.",
        "state": "open", "labels": [], "user": "jdoe"},
}
NEXT_NUMBER = 3


# class / self / inheritance: Lessons 43-46. Nothing below is needed for this lesson.
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # keep the server quiet

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length).decode("utf-8")

    def authorized(self):
        header = self.headers.get("Authorization", "")
        if header == f"Bearer {TOKEN}":
            return True
        if header.startswith("Basic "):
            decoded = base64.b64decode(header[6:]).decode("utf-8")
            return decoded == f"{USER}:{TOKEN}"
        return False

    def deny(self):
        self.send_json(401, {"error": "bad or missing credentials",
                             "hint": "send Authorization: Bearer <token>"})

    def issue_number(self):
        return int(self.path.rsplit("/", 1)[1])

    def do_GET(self):
        if self.path == "/issues":
            self.send_json(200, list(ISSUES.values()))
        elif self.path.startswith("/issues/"):
            n = self.issue_number()
            if n in ISSUES:
                self.send_json(200, ISSUES[n])
            else:
                self.send_json(404, {"error": f"no issue {n}"})
        else:
            self.send_json(404, {"error": "no such endpoint"})

    def do_POST(self):
        global NEXT_NUMBER
        raw = self.read_body()
        if self.path == "/echo":
            self.send_json(200, {"method": "POST",
                                 "content_type": self.headers.get("Content-Type"),
                                 "raw_body": raw})
            return
        if not self.authorized():
            self.deny()
            return
        if self.path != "/issues":
            self.send_json(404, {"error": "no such endpoint"})
            return
        record = json.loads(raw)
        record["number"] = NEXT_NUMBER
        record.setdefault("state", "open")
        ISSUES[NEXT_NUMBER] = record
        NEXT_NUMBER += 1
        self.send_json(201, record)

    def do_PUT(self):
        if not self.authorized():
            self.deny()
            return
        n = self.issue_number()
        if n not in ISSUES:
            self.send_json(404, {"error": f"no issue {n}"})
            return
        record = json.loads(self.read_body())
        record["number"] = n
        ISSUES[n] = record  # the whole record is replaced
        self.send_json(200, record)

    def do_PATCH(self):
        if not self.authorized():
            self.deny()
            return
        n = self.issue_number()
        if n not in ISSUES:
            self.send_json(404, {"error": f"no issue {n}"})
            return
        ISSUES[n].update(json.loads(self.read_body()))  # merged into the record
        self.send_json(200, ISSUES[n])

    def do_DELETE(self):
        if not self.authorized():
            self.deny()
            return
        n = self.issue_number()
        if n not in ISSUES:
            self.send_json(404, {"error": f"no issue {n}"})
            return
        del ISSUES[n]
        self.send_response(204)  # no content, no body at all
        self.end_headers()


if __name__ == "__main__":
    print("docs API listening on http://127.0.0.1:8077 -- Ctrl-C to stop")
    ThreadingHTTPServer(("127.0.0.1", 8077), Handler).serve_forever()
```

It must be `ThreadingHTTPServer` and not `HTTPServer`. `requests` keeps the connection open after a call, and a single-threaded server never gets around to accepting the second request — the script hangs with no error and no traceback.

The endpoints it understands:

| Endpoint | What it does | Token required |
| --- | --- | --- |
| `GET /issues` | Lists every issue | No |
| `GET /issues/<n>` | Reads one issue | No |
| `POST /issues` | Creates an issue and assigns it a number | Yes |
| `PUT /issues/<n>` | Replaces an issue with what you sent | Yes |
| `PATCH /issues/<n>` | Merges what you sent into the issue | Yes |
| `DELETE /issues/<n>` | Deletes an issue | Yes |
| `POST /echo` | Repeats the body and content type it received | No |

The token it accepts is `docs-token-123`. Export it before running any example:

```bash
export DOCS_API_TOKEN=docs-token-123
```

The server holds its data in memory, so restarting it resets the two starting issues. The examples in this lesson are written to run in order against a freshly started server, and the exercise assumes a fresh one too — restart it before you begin the exercise.

The endpoint names and behavior are deliberately ordinary. Point `BASE` at a real service and the same four calls work unchanged.

## Terminology — a body, a method, and credentials

**The request body is the data you send.** A GET request asks for something and carries no body; the four methods in this lesson carry one. The body is a block of text with a **content type** — a header naming the format the text is in, so the server knows how to parse it. `application/json` and `application/x-www-form-urlencoded` are the two you will meet, and `requests` sets the header for you based on which argument you used.

**The method is a verb, and the server decides what it means.** HTTP defines what each verb is *supposed* to do; nothing enforces it. The conventional meanings, which nearly every API follows:

- `POST` creates something new. The server assigns the identifier, so you do not know the issue number until the response comes back.
- `PUT` replaces a record wholesale with what you sent.
- `PATCH` changes only the fields you sent and leaves the rest alone.
- `DELETE` removes a record.

`PUT` and `PATCH` are the pair worth memorizing, because sending a `PUT` when you meant a `PATCH` destroys every field you did not include, and the response looks successful.

**Idempotent** means "doing it twice has the same effect as doing it once." `PUT` and `DELETE` are idempotent — replacing a record with the same content twice leaves the same record, and deleting something already deleted changes nothing further. `POST` is not: two identical `POST` calls create two records. This is why a retried `POST` is the one that produces duplicates.

**Credentials** are the proof that you are allowed to write. They travel in a header on every single request — HTTP has no concept of "logging in and staying logged in," so there is no session to establish and nothing to keep alive. Three shapes cover almost everything:

- An **API key** in a custom header, whose name the API picks: `X-API-Key: <key>`.
- A **Bearer token** in the standard `Authorization` header: `Authorization: Bearer <token>`. This is what GitHub uses.
- **Basic auth**, a username and password in the same header, encoded: `Authorization: Basic <encoded>`.

## Syntax — the four calls, and what changes between them

The shape is the same as `get()`: a URL, some keyword arguments, and a `Response` object comes back.

```python
import requests

BASE = "http://127.0.0.1:8077"
headers = {"Authorization": "Bearer docs-token-123"}
payload = {"title": "index.md 404s", "labels": ["docs"]}

requests.post(f"{BASE}/issues", json=payload, headers=headers)     # create
requests.put(f"{BASE}/issues/1", json=payload, headers=headers)    # replace
requests.patch(f"{BASE}/issues/1", json=payload, headers=headers)  # change some fields
requests.delete(f"{BASE}/issues/1", headers=headers)               # remove; no body to send
```

### `json=` builds a JSON body, `data=` builds a form body

Both arguments take a dict, and choosing the wrong one is a `400` that says nothing about encoding. Run them side by side and look at what actually left your machine:

```python
payload = {"title": "Docs typo"}

r = requests.post(f"{BASE}/echo", json=payload)
print(r.request.headers["Content-Type"], "|", r.request.body)

r = requests.post(f"{BASE}/echo", data=payload)
print(r.request.headers["Content-Type"], "|", r.request.body)
```

```
application/json | b'{"title": "Docs typo"}'
application/x-www-form-urlencoded | title=Docs+typo
```

`json=` serializes the dict to JSON and sets `Content-Type: application/json`. `data=` with a dict encodes it the way an HTML form does and sets `Content-Type: application/x-www-form-urlencoded`, a flat list of `key=value` pairs with no way to express nesting. Anything nested is mangled rather than rejected:

```python
r = requests.post(f"{BASE}/echo", data={"title": "t", "labels": ["docs", "bug"]})
print("list :", r.request.body)

r = requests.post(f"{BASE}/echo", data={"title": "t", "user": {"login": "jdoe"}})
print("dict :", r.request.body)
```

```
list : title=t&labels=docs&labels=bug
dict : title=t&user=login
```

The list survives only as a repeated key, and the nested dict is reduced to its *key* — `jdoe` never left your machine. APIs that document a JSON body want `json=`.

`response.request` is the request object that `requests` built and sent, so `.request.body` and `.request.headers` are how you check what you actually transmitted rather than what you meant to. This is the fastest way to settle "is the API wrong or am I?"

> [!warning] Passing both `json=` and `data=` silently drops the JSON
> `data=` wins, the JSON body never leaves your machine, and nothing warns you.
> ```python
> r = requests.post(f"{BASE}/echo", json={"title": "Docs typo"}, data={"state": "open"})
> print(r.request.headers["Content-Type"], "|", r.request.body)
> ```
> ```
> application/x-www-form-urlencoded | state=open
> ```

### `PATCH` merges, `PUT` replaces

The two calls look identical, and the responses are both `200`. The difference shows up in what the record holds afterwards:

```python
# Sends one field, changes one field. Everything else survives.
requests.patch(f"{BASE}/issues/1", json={"state": "closed"}, headers=headers)

# Sends one field, and the record is now only that field.
requests.put(f"{BASE}/issues/1", json={"title": "auth.md is out of date"}, headers=headers)
```

Worked Example 2 runs both against the same issue and prints the record after each.

### Three ways to send credentials

The first two are just headers you build yourself. The third has its own argument.

```python
payload = {"title": "Docs typo"}

r = requests.post(f"{BASE}/echo", json=payload, headers={"X-API-Key": "docs-token-123"})
print("api key:", r.request.headers["X-API-Key"])

r = requests.post(f"{BASE}/echo", json=payload,
                  headers={"Authorization": "Bearer docs-token-123"})
print("bearer :", r.request.headers["Authorization"])

r = requests.post(f"{BASE}/echo", json=payload, auth=("docs-bot", "docs-token-123"))
print("basic  :", r.request.headers["Authorization"])
```

```
api key: docs-token-123
bearer : Bearer docs-token-123
basic  : Basic ZG9jcy1ib3Q6ZG9jcy10b2tlbi0xMjM=
```

`auth=` takes a `(username, password)` tuple and builds the `Authorization` header for you. What it builds is Base64, which is an encoding and not encryption — `base64.b64decode("ZG9jcy1ib3Q6ZG9jcy10b2tlbi0xMjM=")` gives back `docs-bot:docs-token-123` for anyone who intercepts it. Basic auth is only safe over HTTPS, and the same is true of a Bearer token.

### The token comes from the environment, and a missing one is silent

Lesson 31 covered the two readers. Which one you pick changes how the failure looks:

```python
import os

token = os.getenv("DOCS_API_TOKEN")     # returns None when the variable is unset
token = os.environ["DOCS_API_TOKEN"]    # raises `KeyError` when the variable is unset
```

`os.getenv()` is the safer default only if you check the result. Interpolating an unset variable into an f-string produces a header that is well-formed and wrong:

```python
token = os.getenv("DOCS_API_TOKEN")   # unset
r = requests.post(f"{BASE}/issues", json=payload,
                  headers={"Authorization": f"Bearer {token}"})
print(r.status_code, "sent:", repr(r.request.headers["Authorization"]))
```

```
401 sent: 'Bearer None'
```

Passing the `None` on its own instead is no better — `requests` treats a header value of `None` as an instruction to remove that header, so the request goes out with no `Authorization` at all and gets the same `401`. Both failures are indistinguishable from a bad token in the server's reply, which is why the guard belongs at the top of the script:

```python
token = os.getenv("DOCS_API_TOKEN")
if not token:
    print("DOCS_API_TOKEN is not set; nothing was sent.")
```

`if not token:` rather than `if token is None:` because a variable exported as an empty string is set, and an empty string is falsy — Lesson 14's distinction, and this is where it bites.

> [!warning] A rejected write is still a delivered response
> `requests` raises nothing on a `401`, `403`, `404`, or `500`. The call returns normally and the status code is the only signal that your write did not happen.
> ```python
> r = requests.post(f"{BASE}/issues", json=payload)   # no credentials at all
> print(r.status_code, r.json())
> ```
> ```
> 401 {'error': 'bad or missing credentials', 'hint': 'send Authorization: Bearer <token>'}
> ```
> A script that never checks `r.status_code` reports success on every write it failed to make. Lesson 39 turns this into a repeatable pattern.

## Worked examples

Start the server fresh and run these in order.

### Example 1 — creating a record, and letting the server name it

`POST` sends the fields you know and the response tells you what the server made of them. The issue number is in the response and nowhere else.

```python
import os
import requests

BASE = "http://127.0.0.1:8077"

token = os.getenv("DOCS_API_TOKEN")
if not token:
    print("DOCS_API_TOKEN is not set; nothing was sent.")
else:
    headers = {"Authorization": f"Bearer {token}"}
    new_issue = {
        "title": "index.md 404s",
        "body": "The link to auth.md is broken.",
        "labels": ["docs", "bug"],
        "user": "jdoe",
    }

    response = requests.post(f"{BASE}/issues", json=new_issue, headers=headers)

    print("status:", response.status_code)
    print("sent  :", response.request.body)
    print("type  :", response.request.headers["Content-Type"])

    created = response.json()
    print(f"created #{created['number']}: {created['title']} ({created['state']})")
```

```
status: 201
sent  : b'{"title": "index.md 404s", "body": "The link to auth.md is broken.", "labels": ["docs", "bug"], "user": "jdoe"}'
type  : application/json
created #3: index.md 404s (open)
```

Three things to take from the output. The status is `201` and not `200` — the "created" status, which is what a well-behaved API returns from a successful `POST`. The body that went out is bytes, already serialized from your dict, and `Content-Type` was set for you by `json=`. And the response carries two fields you never sent: `number`, assigned by the server, and `state`, which the server defaulted. Reading the created record back out of the response is how you learn either one.

### Example 2 — `PUT` deletes the fields you did not send

Both calls target the same issue and both succeed. Watch the record.

```python
import os
import requests

BASE = "http://127.0.0.1:8077"
headers = {"Authorization": f"Bearer {os.environ['DOCS_API_TOKEN']}"}


def show(label):
    issue = requests.get(f"{BASE}/issues/1").json()
    print(f"{label:8} {issue}")


show("before")

# PATCH sends only the fields you want changed; everything else is left alone.
requests.patch(f"{BASE}/issues/1", json={"state": "closed"}, headers=headers)
show("patched")

# PUT sends the whole record. Fields you leave out are gone from the record.
requests.put(f"{BASE}/issues/1", json={"title": "auth.md is out of date"}, headers=headers)
show("put")
```

```
before   {'number': 1, 'title': 'auth.md is out of date', 'body': 'Rewrite the token section.', 'state': 'open', 'labels': ['docs', 'auth'], 'user': 'jdoe'}
patched  {'number': 1, 'title': 'auth.md is out of date', 'body': 'Rewrite the token section.', 'state': 'closed', 'labels': ['docs', 'auth'], 'user': 'jdoe'}
put      {'title': 'auth.md is out of date', 'number': 1}
```

The `PATCH` changed `state` and left `body`, `labels`, and `user` alone. The `PUT` sent a title that was already correct — an edit that changes nothing — and destroyed four fields doing it. Its response was `200` with a record that looks fine in isolation, which is exactly why this one is hard to catch by eye. When an API's documentation says a method "updates" a resource, check which of the two verbs it means before you send it.

This example reads the token with `os.environ[...]` rather than `os.getenv(...)`, which is the other reasonable choice: it raises `KeyError` immediately instead of letting an unset token reach the server as the string `None`.

### Example 3 — a `204` has no body to parse

`DELETE` sends no body and, on success, usually gets none back.

```python
import os
import requests

BASE = "http://127.0.0.1:8077"
credentials = ("docs-bot", os.environ["DOCS_API_TOKEN"])

response = requests.delete(f"{BASE}/issues/2", auth=credentials)
print("status      :", response.status_code)
print("sent header :", response.request.headers["Authorization"])
print("body        :", repr(response.text))

try:
    response.json()
except requests.exceptions.JSONDecodeError as exc:
    print("json()      :", exc)

# The second delete finds nothing to delete. requests does not treat that as a
# failure -- the response arrives normally and the status code is the only signal.
again = requests.delete(f"{BASE}/issues/2", auth=credentials)
print("second try  :", again.status_code, again.json())
```

```
status      : 204
sent header : Basic ZG9jcy1ib3Q6ZG9jcy10b2tlbi0xMjM=
body        : ''
json()      : Expecting value: line 1 column 1 (char 0)
second try  : 404 {'error': 'no issue 2'}
```

`204` means "done, and there is nothing to tell you." `response.text` is the empty string, and calling `.json()` on it raises `requests.exceptions.JSONDecodeError` with a message about column 1 that says nothing about the status code — so a script that parses every response the same way crashes on its successful deletes and not on its failed ones. Check the status before parsing.

The second delete returns `404` with a JSON error body, and no exception is raised. Notice that both outcomes — deleted, and never existed — leave the server in the same state, which is what idempotent means in practice.

## Lookup table

| Use when                         | Call                                                 | Result                                                                                       |
| -------------------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Create a record                  | `requests.post(url, json=payload, headers=headers)`  | `201`; response holds the record plus the number the server assigned                         |
| Replace a whole record           | `requests.put(url, json=payload, headers=headers)`   | `200`; every field not in `payload` is gone from the record                                  |
| Change some fields               | `requests.patch(url, json=payload, headers=headers)` | `200`; `payload` is merged in, other fields survive                                          |
| Remove a record                  | `requests.delete(url, headers=headers)`              | `204` with an empty body; the record is gone                                                 |
| Remove a record twice            | `requests.delete(url, headers=headers)`              | `404` with a JSON error body; no exception, server unchanged                                 |
| Send a JSON body                 | `json=payload`                                       | Body `b'{"title": "Docs typo"}'`, `Content-Type: application/json`                           |
| Send an HTML-form body           | `data=payload`                                       | Body `title=Docs+typo`, `Content-Type: application/x-www-form-urlencoded`                    |
| Pass both by mistake             | `requests.post(url, json=a, data=b)`                 | `data` wins; the JSON is dropped and nothing warns                                           |
| Send an API key                  | `headers={"X-API-Key": token}`                       | Header sent verbatim: `docs-token-123`                                                       |
| Send a Bearer token              | `headers={"Authorization": f"Bearer {token}"}`       | Header sent as `Bearer docs-token-123`                                                       |
| Send a username and password     | `auth=("docs-bot", token)`                           | Header built for you: `Basic ZG9jcy1ib3Q6ZG9jcy10b2tlbi0xMjM=`, decodable by anyone          |
| Check what you actually sent     | `response.request.body`, `response.request.headers`  | The serialized body and the full header dict of the outgoing request                         |
| Read a token, tolerating absence | `os.getenv("DOCS_API_TOKEN")`                        | The value, or `None` when unset — which reaches the server as `Bearer None` and gets a `401` |
| Read a token, failing loudly     | `os.environ["DOCS_API_TOKEN"]`                       | The value, or raises `KeyError` before any request is sent                                   |
| Unset a header on purpose        | `headers={"Authorization": None}`                    | The header is omitted from the request entirely; the server sees no credentials              |
| Parse a body that is not there   | `response.json()` on a `204`                         | Raises `requests.exceptions.JSONDecodeError`: `Expecting value: line 1 column 1 (char 0)`    |
| Detect a rejected write          | `response.status_code`                               | The only signal; `401`, `403`, `404`, and `500` all return normally                          |

## Exercise #1 — apply a plan file of issue changes

Write `sync_issues.py`, a script that reads a file describing changes to make and sends each one to the API.

Restart `docs_api.py` first so the data is back to its two starting issues, and save this as `issue-plan.json`:

```json
[
  {
    "action": "create",
    "title": "index.md 404s",
    "body": "The link to auth.md is broken.",
    "labels": ["docs", "bug"]
  },
  {
    "action": "create",
    "title": "notes.txt has stale paths",
    "body": "Paths still point at the old repo."
  },
  {
    "action": "update",
    "number": 2,
    "state": "closed"
  },
  {
    "action": "delete",
    "number": 99
  },
  {
    "action": "delete",
    "number": 1
  }
]
```

Requirements:

1. Take the plan file's path as a positional argument, and support a `--dry-run` flag.
2. Read the token from `DOCS_API_TOKEN`. If it is unset or empty, print `DOCS_API_TOKEN is not set.` and send nothing at all.
3. Read and parse the plan file.
4. Send each entry to the API with the method its `action` calls for, authenticated on every request. A `create` entry has no `number`, and the server assigns one. An `update` entry names the issue and carries the fields to change — treat every key other than `action` and `number` as a field to send, so the script keeps working when the plan changes a different field. Not every `create` entry carries every field.
5. Print one line per entry: the method, the path, the status code, and a detail. For a create, the detail is the new number, the title, and the labels the record ended up with. For an update, the number, title, and state. For a successful delete, the word `deleted`. For anything that came back `400` or higher, the error message the API sent.
6. A failed entry must not stop the run.
7. Finish with a count of what was sent and what failed.
8. `--dry-run` prints the method and path it would use for each entry and sends nothing, then reports how many were planned.

Expected output, with no token set:

```
DOCS_API_TOKEN is not set.
```

With the token set, `--dry-run`:

```
DRY RUN POST   /issues
DRY RUN POST   /issues
DRY RUN PATCH  /issues/2
DRY RUN DELETE /issues/99
DRY RUN DELETE /issues/1
5 planned, 0 sent
```

And the real run, against a freshly restarted server:

```
POST   /issues     201  #3 index.md 404s [docs, bug]
POST   /issues     201  #4 notes.txt has stale paths []
PATCH  /issues/2   200  #2 rate-limit.md missing example (closed)
DELETE /issues/99  404  no issue 99
DELETE /issues/1   204  deleted
4 sent, 1 failed
```

The field content must match; the column widths are yours to choose. Confirm the result with `curl -s http://127.0.0.1:8077/issues` — issue 1 should be gone, issue 2 closed, and issues 3 and 4 created.

## Exercise 2 — Sync a customer plan against the Zenmeter API

Lesson 38's `sync_issues.py` sent `POST`, `PUT`, `PATCH`, and `DELETE` at a stand-in API on your own machine. This exercise sends three of those four at a real one: your Zenmeter tenant. There's no local server to start — `BASE` points straight at Zenmeter, and every write actually happens.

Two things are different from the lesson's local API, and both come straight from the [Zenmeter Management API reference](https://api.nalpeiron.io/docs/zenmeter.html):

- Every request needs **two** credentials in `headers`, not one: your access token as a Bearer `Authorization` header, and your tenant ID as an `N-TenantId` header. Both are required on every call, not just the writes.
- Zenmeter has no `DELETE` operations at all. Removal is modeled as a lifecycle change — a customer is _disabled_, not deleted — so this exercise doesn't need `requests.delete()`. Worth remembering for when you go on to document this API: "delete" isn't a verb it uses.

## Setup — pointing the script at your tenant

Set `BASE` at the top of your script to your tenant's actual API host. The docs page lives at `api.nalpeiron.io/docs/`, but a docs site and the host that actually answers API calls aren't always the same machine — confirm the real one in the NGP administration site before assuming it matches the docs URL.

Export your credentials rather than writing them into the script:

```bash
export ZENMETER_ACCESS_TOKEN=<your access token>
export ZENMETER_TENANT_ID=<your tenant id>
```

> [!warning] This exercise writes to your real tenant There's no fixture to reset between runs. Point every entry in the plan file at test customers you're comfortable creating, updating, and disabling, and re-check IDs before you re-run — running the same `create` entry twice makes two customers, not one.

## The plan file

Save this as `customer-plan.json`. It has one entry of each kind this exercise covers:

```json
[
  {
    "action": "create",
    "name": "Fenwick Robotics",
    "type": "prospect",
    "accountRefId": "fenwick-2026",
    "subscriptionSku": "REPLACE-WITH-YOUR-SKU"
  },
  {
    "action": "create",
    "name": "Corvid Labs",
    "type": "customer",
    "accountRefId": "corvid-2019"
  },
  {
    "action": "update_contract",
    "customerId": "cust_REPLACE_WITH_A_REAL_TEST_CUSTOMER_ID",
    "contractValue": 250000,
    "contractRenewalDate": "2027-03-01T00:00:00Z"
  },
  {
    "action": "disable",
    "customerId": "cust_REPLACE_WITH_ANOTHER_REAL_TEST_CUSTOMER_ID"
  }
]
```

Before a real (non-dry-run) attempt, replace the placeholder strings: `GET /api/v1/customers` on your tenant will give you real customer IDs to update or disable, and the product catalog endpoints (`GET /api/v1/zenmeter/products` and the business-model endpoints under it) will give you a real SKU to subscribe the new customer to. Dry runs don't need any of that — the placeholders above are fine as they are.

## Requirements

Write `zenmeter_sync.py`.

1. Take the plan file's path as a positional argument, and support a `--dry-run` flag.
2. Read `ZENMETER_ACCESS_TOKEN` and `ZENMETER_TENANT_ID` from the environment. Check the token first. If it is unset or empty, print `ZENMETER_ACCESS_TOKEN is not set.` and send nothing at all. If the token is present but the tenant ID is unset or empty, print `ZENMETER_TENANT_ID is not set.` and likewise send nothing.
3. Send both credentials on every request: the token as a Bearer `Authorization` header, the tenant ID as an `N-TenantId` header.
4. Read and parse the plan file.
5. A `create` entry has a `name` and, optionally, `type`, `accountRefId`, and `subscriptionSku`. Create the customer first. Only if that succeeds, and only if the entry carries a `subscriptionSku`, create a subscription for the new customer using it. If the customer create fails, don't attempt the subscription create.
6. An `update_contract` entry names a `customerId` and carries the fields to change — treat every key other than `action` and `customerId` as a field to update. Zenmeter's customer-update endpoint replaces the whole record, so any field you don't explicitly carry forward must still hold whatever it held before the update. Check the OAD for what the customer record returns on a read versus what it accepts on a write — they're not the same shape.
7. A `disable` entry names a `customerId` and disables that customer.
8. Print one line per API request actually made — not one per plan entry; a `create` entry with a `subscriptionSku` makes two. Each line needs the method, the path, the status code, and a detail:
    - Customer create: the new customer's id and name.
    - Subscription create: the new subscription's id and the SKU you requested.
    - Update: the field or fields you changed, and the values you sent.
    - Disable: the word `disabled`.
    - Anything that comes back `400` or higher: the error message the API sent.
9. A failed request must not stop the run or prevent later entries from being attempted.
10. An entry counts as sent only if every request it made succeeded. If any request within an entry fails, the whole entry counts as failed.
11. Finish with a count of entries sent and entries failed.
12. `--dry-run` prints the method and path of every request the plan _would_ make, sends none of them, and finishes with a count of requests planned.

## Expected output

Two pieces below are real, captured output — I ran a solution locally against the plan file above. Neither needs your tenant: the missing-credential checks exit before any request goes out, and `--dry-run` never sends one.

With no token set:

```
ZENMETER_ACCESS_TOKEN is not set.
```

With `--dry-run`, using the plan file exactly as shown above:

```
DRY RUN POST   /api/v1/customers
DRY RUN POST   /api/v1/zenmeter/subscriptions
DRY RUN POST   /api/v1/customers
DRY RUN GET    /api/v1/customers/cust_REPLACE_WITH_A_REAL_TEST_CUSTOMER_ID
DRY RUN PUT    /api/v1/customers/cust_REPLACE_WITH_A_REAL_TEST_CUSTOMER_ID
DRY RUN PATCH  /api/v1/customers/cust_REPLACE_WITH_ANOTHER_REAL_TEST_CUSTOMER_ID/disable
6 planned, 0 sent
```

> [!note] The live run isn't verified I have no network access from this environment and no credentials to your tenant, so I can't run this exercise's actual writes the way the lesson's exercises are normally run and captured. Everything past this point is the _shape_ your output will have, with placeholders standing in for real values — not literal text to diff against, since your customer IDs, subscription IDs, and statuses will be whatever your tenant actually returns:
> 
> ```
> POST   /api/v1/customers                  201  <new customer id>  Fenwick Robotics
> POST   /api/v1/zenmeter/subscriptions     201  <new subscription id>  <sku>
> POST   /api/v1/customers                  201  <new customer id>  Corvid Labs
> PUT    /api/v1/customers/<id>              204  contractValue=250000, contractRenewalDate=2027-03-01T00:00:00Z
> PATCH  /api/v1/customers/<id>/disable      204  disabled
> 4 sent, 0 failed
> ```
> 
> If you'd like a second set of eyes once you've run it against your tenant, paste back what you got and I'll sanity-check it against the requirements above.