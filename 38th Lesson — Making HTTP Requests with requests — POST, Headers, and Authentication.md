# Lesson 38 — `requests`: POST, Headers, and Authentication

**Phase 3 — HTTP and API mental models (SDK user edition)**

In Lesson 37 you asked servers for data. This lesson covers sending data _to_ a server, attaching headers, and proving who you are. These three things are what every SDK does under the hood on your behalf.

---

## 1. Terminology and Theory

### Request body (payload)

The **body** is the data you send to the server. A `GET` request normally has no body — everything it needs is in the URL. A `POST` or `PUT` almost always has one.

Think of it this way:

|Part of the request|What it carries|Example|
|---|---|---|
|URL|_Which_ resource|`https://api.github.com/repos/octocat/hello/issues`|
|Method|_What kind_ of operation|`POST`|
|Headers|Metadata about the request|`Authorization`, `Content-Type`|
|Body|The data itself|`{"title": "Docs typo"}`|

### Serialization

Your payload starts as a Python dict. It has to travel over the network as text. Converting the dict to JSON text is called **serialization**. You already did this manually in Lesson 28 with `json.dumps()`. The `requests` library can do it for you.

### `json=` versus `data=`

These two keyword arguments look interchangeable. They are not.

- `json=payload` — serializes the dict to JSON and sets the header `Content-Type: application/json` automatically. This is what you want for modern REST APIs.
- `data=payload` — when given a dict, encodes it as an HTML form (`Content-Type: application/x-www-form-urlencoded`). When given a string, sends that string as-is and sets no content type.

> [!tip] If an API returns `400 Bad Request` on a POST that "looks right," check whether you used `data=` when the API expected `json=`. This is one of the most common beginner mistakes, and it is worth a troubleshooting entry in any API doc you write.

### Headers

A **header** is a key/value pair of metadata attached to the request. You pass them as a dict. Four you will meet constantly:

- `Authorization` — your credentials.
- `Content-Type` — describes the format of the body you are **sending**.
- `Accept` — describes the format you want **back**.
- `User-Agent` — identifies the client software. `requests` sets this to something like `python-requests/2.32.3` unless you override it.

`Content-Type` and `Accept` point in opposite directions. Getting them confused is a classic source of confusing 415 and 406 responses.

### Authentication versus authorization

- **Authentication** answers "who are you?" A failure here is `401 Unauthorized`.
- **Authorization** answers "are you allowed to do this?" A failure here is `403 Forbidden`.

The distinction matters when you write troubleshooting docs: a 401 means fix your token, a 403 means fix your permissions or scopes. They are not the same problem.

### Three authentication patterns

|Pattern|What it looks like on the wire|Used by|
|---|---|---|
|Bearer token|`Authorization: Bearer ghp_abc123`|GitHub, most modern REST APIs|
|API key header|`X-API-Key: abc123`|Many vendor APIs; the header name varies|
|Basic auth|`Authorization: Basic am9zaDpwYXNz`|Older APIs, internal services|

Basic auth is a username and password joined by a colon and Base64-encoded. Base64 is **encoding, not encryption** — anyone who sees the header can decode it instantly. It is only safe over HTTPS.

There is no universal rule for API key header names. `X-API-Key`, `api-key`, and `X-Auth-Token` are all common. Always read the API's own documentation.

### Why the method matters when you write docs

`GET`, `PUT`, and `DELETE` are meant to be **idempotent**: sending the same request twice produces the same end state. `POST` usually is not — POST twice and you often create two issues, two comments, two records.

This is exactly the detail that belongs in your documentation, because it determines whether a user can safely retry a failed call.

### Status codes you will see on writes

|Code|Meaning|What your script should do|
|---|---|---|
|200|OK, response has a body|Parse it|
|201|Created — often includes a `Location` header pointing at the new resource|Parse it; report the new resource|
|204|No Content — success, empty body|Do **not** parse it|
|400|Malformed request|Fix the body or parameters|
|401|Not authenticated|Fix the token|
|403|Authenticated but not permitted|Fix the scopes or permissions|
|404|No such resource — or you lack permission to know it exists|Check the path|
|422|Well-formed but semantically invalid|Fix the field values|

> [!warning] Calling `.json()` on a `204 No Content` response raises an exception, because there is no body to parse. Check the status code before parsing. Lesson 39 turns this habit into a reusable pattern.

### Where the token lives

Never put a token in your source code. Read it from an environment variable with `os.getenv()` (Lesson 31), and fail immediately with a clear message when it is missing. A token pasted into a script eventually gets committed, and a committed token has to be revoked.

### The test server for this lesson

`httpbin.org` echoes your request back to you as JSON. When you POST to `https://httpbin.org/post`, the response tells you exactly what the server received — body, headers, and all. That makes it the ideal place to _see_ what `requests` did on your behalf.

---

## 2. Syntax

### POST with a JSON body

```python
import requests

payload = {"title": "Docs typo", "body": "Fix the heading."}
response = requests.post("https://httpbin.org/post", json=payload, timeout=10)
```

- `requests.post(url, ...)` — sends a POST request.
- `json=payload` — serializes `payload` to JSON and sets `Content-Type: application/json`.
- `timeout=10` — give up after 10 seconds instead of hanging forever.

> [!note] `timeout` is optional but you should always pass it. Without it, a stalled server can freeze your script indefinitely. Ten to thirty seconds is a reasonable default for API work.

### POST form-encoded data

```python
form_fields = {"username": "josh", "role": "writer"}
response = requests.post("https://httpbin.org/post", data=form_fields, timeout=10)
```

Same method, different encoding. Use this only when the API asks for form data.

### Custom headers

```python
headers = {
    "Authorization": "Bearer my-secret-token",
    "Accept": "application/json",
    "X-Docs-Client": "zenmeter-notes/1.0",
}

response = requests.post(
    "https://httpbin.org/post",
    json=payload,
    headers=headers,
    timeout=10,
)
```

- `headers` is a plain dict of strings.
- Header names are case-insensitive on the wire, but write them in the conventional capitalization anyway.
- Anything you put in this dict is added to (or overrides) what `requests` sends by default.

### Bearer token from an environment variable

```python
import os

token = os.getenv("DOCS_API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
```

The literal word `Bearer`, then a single space, then the token. The space is required.

### Basic authentication

```python
response = requests.get(
    "https://httpbin.org/basic-auth/user/passwd",
    auth=("user", "passwd"),
    timeout=10,
)
```

- `auth=(username, password)` — a two-item tuple (Lesson 13). `requests` builds and encodes the `Authorization: Basic ...` header for you.

An equivalent, more explicit form you will see in SDK source:

```python
from requests.auth import HTTPBasicAuth

response = requests.get(url, auth=HTTPBasicAuth("user", "passwd"), timeout=10)
```

### PUT and DELETE

```python
response = requests.put("https://httpbin.org/put", json={"state": "closed"}, timeout=10)
response = requests.delete("https://httpbin.org/delete", timeout=10)
```

The signatures match `post()`. `delete()` usually has no body.

### Reading the response

Everything from Lesson 37 still applies:

```python
print(response.status_code)      # 200
print(response.headers["Content-Type"])
data = response.json()           # dict, when the body is JSON
```

### Recognition only: `requests.Session()`

You do not need to write this yet, but you will see it in SDK source code:

```python
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})
response = session.get("https://api.github.com/user", timeout=10)
```

A `Session` holds headers and connection state so every call reuses them. When you read PyGithub's source later and see a session object being passed around, this is what it is doing: setting your auth header once instead of on every request.

---

## 3. Worked Examples

### Example 1 — POST a JSON body and read the echo

```python
"""Send a JSON body to httpbin and inspect what the server received."""

import requests

payload = {
    "title": "Zenmeter usage export",
    "labels": ["docs", "metering"],
    "draft": True,
}

response = requests.post("https://httpbin.org/post", json=payload, timeout=10)

print(f"Status: {response.status_code}")

echo = response.json()

print(f"Content-Type requests set: {echo['headers']['Content-Type']}")
print(f"Title the server received: {echo['json']['title']}")
print(f"First label received: {echo['json']['labels'][0]}")
print(f"Raw body as text: {echo['data']}")
```

Expected output:

```
Status: 200
Content-Type requests set: application/json
Title the server received: Zenmeter usage export
First label received: docs
Raw body as text: {"title": "Zenmeter usage export", "labels": ["docs", "metering"], "draft": true}
```

What to notice:

- You never called `json.dumps()`. `json=` serialized the dict for you.
- You never set `Content-Type`. `json=` set it for you.
- Python's `True` became JSON's `true` in the raw body. Serialization translates between the two languages' conventions.
- `echo['json']` is httpbin's parsed copy of your body; `echo['data']` is the raw text that came across the wire.

### Example 2 — Bearer token from the environment

First set the token in your shell:

```bash
export DEMO_TOKEN="test-token-9f2c"
```

```python
"""Authenticate with a Bearer token read from the environment."""

import os

import requests

token = os.getenv("DEMO_TOKEN")

if token is None:
    print("DEMO_TOKEN is not set. Nothing to send.")
else:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    response = requests.get("https://httpbin.org/bearer", headers=headers, timeout=10)

    if response.status_code == 200:
        result = response.json()
        print(f"Authenticated: {result['authenticated']}")
        print(f"Token the server saw: {result['token']}")
    elif response.status_code == 401:
        print("401 Unauthorized: the token was missing or malformed.")
    else:
        print(f"Unexpected status: {response.status_code}")
```

Expected output:

```
Authenticated: True
Token the server saw: test-token-9f2c
```

Now prove the failure path. Temporarily change the scheme in the header to `Token`, which some older APIs use and this endpoint does not accept:

```python
"Authorization": f"Token {token}",
```

The credentials are fine, but the scheme is wrong, so the endpoint rejects the request:

```
401 Unauthorized: the token was missing or malformed.
```

Change it back to `Bearer` when you are done.

What to notice:

- The guard clause runs before any network call. Failing fast on a missing token costs nothing and produces a clear message instead of a confusing 401.
- A 401 does not always mean a bad token. Here the token was perfectly valid and the _scheme_ was wrong. This is why "check the exact header your client sends" belongs in every API troubleshooting section.
- The `if / elif / else` on `status_code` is the shape of nearly every real API script.
- `/bearer` is a free 401 generator. Being able to trigger an error on demand is how you verify error handling actually works.

### Example 3 — PUT, DELETE, and basic auth in one tour

```python
"""Compare PUT, DELETE, and basic auth against httpbin."""

import requests


def describe(label, response):
    """Print a one-line summary of a response."""
    print(f"{label}: {response.status_code} {response.request.method}")


put_response = requests.put(
    "https://httpbin.org/put",
    json={"state": "closed"},
    timeout=10,
)
describe("PUT   ", put_response)
print(f"  server received state = {put_response.json()['json']['state']}")

delete_response = requests.delete("https://httpbin.org/delete", timeout=10)
describe("DELETE", delete_response)

basic_response = requests.get(
    "https://httpbin.org/basic-auth/josh/hunter2",
    auth=("josh", "hunter2"),
    timeout=10,
)
describe("BASIC ", basic_response)
print(f"  authenticated as {basic_response.json()['user']}")
```

Expected output:

```
PUT   : 200 PUT
  server received state = closed
DELETE: 200 DELETE
BASIC : 200 GET
  authenticated as josh
```

What to notice:

- `describe()` is an ordinary function (Lesson 15) that takes a response object as an argument. Lesson 39 grows this idea into a full request-and-handle-errors helper.
- `auth=("josh", "hunter2")` produced a valid `Authorization: Basic ...` header without you encoding anything.
- `response.request.method` reads back the method actually sent — useful when a redirect quietly changes it.

> [!info] `httpbin.org` is a public service and is occasionally slow or down. If a call hangs or fails to connect, wait a minute and retry, or point the same scripts at `https://postman-echo.com/post`, which echoes requests in a similar (not identical) shape.

---

## 4. Quick Reference

```python
# Send a dict as a JSON body; sets Content-Type: application/json automatically
response = requests.post("https://httpbin.org/post", json={"title": "Docs typo"})

# Send a dict as HTML form data; sets Content-Type: application/x-www-form-urlencoded
response = requests.post("https://httpbin.org/post", data={"title": "Docs typo"})

# Always set a timeout in seconds so a stalled server cannot hang the script
response = requests.post("https://httpbin.org/post", json={"a": 1}, timeout=10)

# Attach custom headers as a plain dict of strings
headers = {"Accept": "application/json", "X-Docs-Client": "zenmeter-notes/1.0"}
response = requests.post("https://httpbin.org/post", json={"a": 1}, headers=headers)

# Bearer token authentication: the word Bearer, a space, then the token
token = os.getenv("DOCS_API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

# API key authentication: header name varies by API, so check its docs
headers = {"X-API-Key": os.getenv("DOCS_API_TOKEN")}

# Basic authentication as a (username, password) tuple; requests encodes it
response = requests.get("https://httpbin.org/basic-auth/josh/hunter2", auth=("josh", "hunter2"))

# Basic authentication, explicit form seen in SDK source
from requests.auth import HTTPBasicAuth
response = requests.get(url, auth=HTTPBasicAuth("josh", "hunter2"))

# PUT sends a body like POST; DELETE usually sends none
response = requests.put("https://httpbin.org/put", json={"state": "closed"}, timeout=10)
response = requests.delete("https://httpbin.org/delete", timeout=10)

# Read back the method actually sent
print(response.request.method)

# A Session reuses headers across calls (recognition only, common in SDK source)
session = requests.Session()
session.headers.update({"Authorization": f"Bearer {token}"})
response = session.get("https://api.github.com/user", timeout=10)

# Check the status before parsing: 204 has no body and .json() will fail on it
if response.status_code == 200:
    data = response.json()
```

---

## 5. Exercise

### Scenario

Your team has an internal "docs publishing" API. Before it exists, you are writing the client script against `httpbin.org` so the request shape can be reviewed.

Write a script named `publish_note.py` that reads a Markdown release note, sends it as an authenticated JSON POST, and prints a summary a reviewer could paste into a ticket.

### Setup

1. Work inside your virtual environment with `requests` installed.
    
2. Create `release-note.md` with exactly this content:
    

```markdown
# Zenmeter 3.2 Release Notes

Metering data now exports to CSV.
Fixed a bug in the usage rollup job.
```

3. Set the token in your shell:

```bash
export DOCS_API_TOKEN="demo-token-12345"
```

### Requirements

1. The script accepts a required positional argument: the path to the Markdown file. It also accepts an optional `--url` argument that defaults to `https://httpbin.org/post`. Both must appear in `--help`.
2. The token is read from the `DOCS_API_TOKEN` environment variable. If it is not set, the script prints the message shown below and stops without sending a request and without a traceback.
3. The script reads the Markdown file and builds this payload:
    - `title` — the first line of the file with the leading `#` removed.
    - `body` — every remaining non-empty line, joined with a single space.
    - `line_count` — the number of non-empty lines in the file, counting the heading.
4. The script sends a POST to the URL with the payload as a JSON body and these three headers:
    - `Authorization: Bearer <token>`
    - `Accept: application/json`
    - `X-Docs-Client: zenmeter-notes/1.0`
5. If the status code is 200, the script prints the success output below, reading the values back out of the response body. If it is anything else, it prints the failure output and stops.
6. The `Auth header sent` line shows the authentication scheme, four asterisks, and only the last four characters of the token. The full token must never appear in the output.
7. The `Equivalent curl` line reproduces the request as a `curl` command, with the token redacted the same way.

### Expected output

Run it:

```bash
python publish_note.py release-note.md
```

```
POST https://httpbin.org/post -> 200
Title sent: Zenmeter 3.2 Release Notes
Lines counted: 3
Content-Type set by requests: application/json
Client header echoed: zenmeter-notes/1.0
Auth header sent: Bearer ****2345
Equivalent curl:
curl -X POST -H "Authorization: Bearer ****2345" -H "Accept: application/json" -H "X-Docs-Client: zenmeter-notes/1.0" https://httpbin.org/post
```

Now force a failure:

```bash
python publish_note.py release-note.md --url https://httpbin.org/status/401
```

```
POST https://httpbin.org/status/401 -> 401
Request failed. Nothing was published.
```

Now unset the token and run it again:

```bash
unset DOCS_API_TOKEN
python publish_note.py release-note.md
```

```
DOCS_API_TOKEN is not set. Export it and try again.
```

All three runs must produce exactly the output shown.

## Terminology and Theory

In Lesson 37, you used `requests.get()` to retrieve data from an API. GET requests ask the server for information without changing anything. This lesson covers the other side of HTTP: sending data to a server and authenticating yourself so the server knows who you are.

**POST request:** An HTTP request that sends data to a server, typically to create a new resource. When you submit a form on a website, file a support ticket, or create a GitHub issue, a POST request is what carries your data to the server.

**PUT request:** An HTTP request that sends data to replace an existing resource entirely. If you wanted to update an issue's title and body, a PUT request would replace the entire issue object with the new version you provide.

**DELETE request:** An HTTP request that asks the server to remove a resource. Deleting a comment, removing a label, or closing an account — all of these translate to DELETE requests at the HTTP level.

**Request body:** The data payload attached to a POST or PUT request. In API work, the body is almost always a JSON object. The `requests` library provides a `json=` parameter that handles serialization and sets the correct `Content-Type` header automatically.

**Request headers:** Key-value metadata sent alongside a request. Headers carry information the server needs to process your request — what format your data is in, who you are, what response format you accept. You already saw response headers in Lesson 37 (`.headers`). Now you will send custom headers of your own.

**Authentication:** The process of proving your identity to an API. APIs need to know who is making a request so they can enforce permissions and rate limits. Three common patterns exist:

- **API key in a header:** The server expects a specific header (often `X-API-Key`) containing a secret key. This is the simplest pattern.
- **Bearer token:** The server expects an `Authorization` header whose value is the word `Bearer` followed by a space and then the token string. This is the pattern GitHub, most cloud APIs, and OAuth-based services use.
- **Basic authentication:** The server expects an `Authorization` header containing a base64-encoded `username:password` pair. The `requests` library handles the encoding for you through its `auth=` parameter.

> [!note] All three authentication patterns use headers to transmit credentials. The differences are in which header name the server expects and how the credential value is formatted. You already learned in Lesson 31 that tokens and keys should be loaded from environment variables, never hardcoded in your script.

**`response.raise_for_status()`:** A method on the `Response` object that checks the status code and raises an `HTTPError` exception if the request failed (status code 400 or above). This is a shortcut for writing your own `if response.status_code >= 400` check. You will use this method in exercises, and Lesson 39 will cover response handling and debugging in full depth.

## Syntax

### Sending a POST request with a JSON body

```python
import requests

payload = {"title": "Bug report", "body": "Login fails on mobile"}
response = requests.post("https://httpbin.org/post", json=payload)
```

The `json=` parameter does three things at once: it converts the Python dictionary to a JSON string, attaches it as the request body, and sets the `Content-Type` header to `application/json`. You do not need to call `json.dumps()` yourself when using this parameter.

### Sending a PUT request

```python
updated_data = {"title": "Updated title", "body": "Revised description"}
response = requests.put("https://httpbin.org/put", json=updated_data)
```

The syntax is identical to `requests.post()`. The difference is semantic — PUT tells the server you are replacing an existing resource rather than creating a new one.

### Sending a DELETE request

```python
response = requests.delete("https://httpbin.org/delete")
```

DELETE requests typically do not include a body. You are telling the server to remove the resource at that URL.

### Custom headers with `headers=`

```python
custom_headers = {
    "Accept": "application/json",
    "X-Custom-Header": "my-value"
}
response = requests.get("https://httpbin.org/headers", headers=custom_headers)
```

The `headers=` parameter accepts a dictionary of header names and values. These are merged with the default headers that `requests` sends automatically (like `User-Agent`).

### Authentication: API key in a header

```python
import os

api_key = os.getenv("MY_API_KEY")
headers = {"X-API-Key": api_key}
response = requests.get("https://api.example.com/data", headers=headers)
```

The server documentation tells you which header name to use. You load the key from an environment variable (Lesson 31) and pass it in the `headers=` dictionary.

### Authentication: Bearer token

```python
import os

token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.github.com/user", headers=headers)
```

The `Authorization` header value must be the literal string `Bearer`, followed by a space, followed by the token. The f-string builds this formatted value from the variable.

### Authentication: Basic auth with `auth=`

```python
response = requests.get(
    "https://httpbin.org/basic-auth/myuser/mypass",
    auth=("myuser", "mypass")
)
```

The `auth=` parameter accepts a tuple of `(username, password)`. The `requests` library handles the base64 encoding and header formatting internally. You never need to construct the `Authorization: Basic ...` header yourself.

### Combining body, headers, and auth

```python
import os

token = os.getenv("API_TOKEN")
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}
payload = {"name": "new-repo", "private": True}
response = requests.post(
    "https://api.example.com/repos",
    json=payload,
    headers=headers
)
```

All parameters can be used together in the same call. This is the most common real-world pattern: an authenticated POST with a JSON body and explicit headers.

## Worked Examples

### Example 1: POST a JSON payload and inspect what the server received

httpbin.org echoes back everything you send it, which makes it ideal for learning. This script sends a POST request with a JSON body and prints the server's view of what it received.

```python
import requests

payload = {
    "title": "Improve error messages",
    "priority": "high",
    "labels": ["ux", "error-handling"]
}

response = requests.post("https://httpbin.org/post", json=payload)
result = response.json()

print(f"Status: {response.status_code}")
print(f"Content-Type sent: {result['headers']['Content-Type']}")
print(f"Body received by server: {result['json']}")
```

**What is happening:** `requests.post()` sends the dictionary as a JSON-encoded body. The httpbin.org `/post` endpoint mirrors the request back as JSON, so `result['json']` contains exactly the dictionary you sent. The `result['headers']` dictionary shows the headers the server received, confirming that `Content-Type` was set to `application/json` automatically.

**Expected output:**

```
Status: 200
Content-Type sent: application/json
Body received by server: {'title': 'Improve error messages', 'priority': 'high', 'labels': ['ux', 'error-handling']}
```

### Example 2: Sending custom headers and verifying them

This script sends custom headers to httpbin.org's `/headers` endpoint, which echoes back all headers it received. This pattern is useful when you need to verify that your headers are reaching the server correctly.

```python
import requests

headers = {
    "X-API-Key": "demo-key-12345",
    "Accept": "application/json",
    "X-Request-Source": "lesson-38-script"
}

response = requests.get("https://httpbin.org/headers", headers=headers)
received = response.json()["headers"]

print("Headers the server received:")
for name, value in received.items():
    print(f"  {name}: {value}")
```

**What is happening:** The `headers=` dictionary is merged with the default headers that `requests` sends (like `Host` and `User-Agent`). The httpbin `/headers` endpoint returns all of them. Iterating over `received.items()` (Lesson 12) and printing each pair lets you verify that your custom headers arrived intact. This is a useful debugging technique when an API rejects your request — you can send the same headers to httpbin first to confirm they look correct.

**Expected output** (your `User-Agent` version may differ):

```
Headers the server received:
  Accept: application/json
  Host: httpbin.org
  User-Agent: python-requests/2.31.0
  X-Api-Key: demo-key-12345
  X-Request-Source: lesson-38-script
```

### Example 3: Bearer token authentication with environment variables

This script loads a GitHub token from an environment variable and uses Bearer authentication to fetch your own GitHub user profile. It combines environment variable loading (Lesson 31), GET with headers, and JSON response parsing (Lesson 37).

> [!tip] To run this example, you need a GitHub personal access token. Set it in your shell before running the script: `export GITHUB_TOKEN="ghp_your_token_here"`.

```python
import os
import sys
import requests

token = os.getenv("GITHUB_TOKEN")
if not token:
    print("Error: GITHUB_TOKEN environment variable is not set.")
    print("Set it with: export GITHUB_TOKEN=\"ghp_your_token_here\"")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

response = requests.get("https://api.github.com/user", headers=headers)

if response.status_code == 200:
    user = response.json()
    print(f"Authenticated as: {user['login']}")
    print(f"Name: {user.get('name', 'Not set')}")
    print(f"Public repos: {user['public_repos']}")
else:
    print(f"Authentication failed: {response.status_code}")
    print(f"Response: {response.text}")
```

**What is happening:** The script follows a pattern you will repeat constantly in API work. First, it loads the token from the environment and fails fast with a helpful message if the token is missing (Lesson 31). Then it constructs the `Authorization` header using the Bearer pattern. The `Accept` header tells GitHub which response format version to use — this is a GitHub-specific convention, but many APIs have similar versioning headers. After making the request, it checks the status code before attempting to parse the response as JSON. The `.get('name', 'Not set')` call (Lesson 11) provides a safe fallback because the `name` field is optional on GitHub profiles.

**Expected output** (with a valid token):

```
Authenticated as: your-username
Name: Your Name
Public repos: 12
```

## Quick Reference

```python
# Send a POST request with a JSON body
response = requests.post("https://httpbin.org/post", json={"key": "value"})

# Send a PUT request with a JSON body
response = requests.put("https://httpbin.org/put", json={"key": "new_value"})

# Send a DELETE request
response = requests.delete("https://httpbin.org/delete")

# Attach custom headers to any request
headers = {"Accept": "application/json", "X-Custom": "value"}
response = requests.get("https://httpbin.org/headers", headers=headers)

# Authenticate with an API key in a custom header
headers = {"X-API-Key": os.getenv("MY_API_KEY")}
response = requests.get("https://api.example.com/data", headers=headers)

# Authenticate with a Bearer token
headers = {"Authorization": f"Bearer {os.getenv('API_TOKEN')}"}
response = requests.get("https://api.example.com/user", headers=headers)

# Authenticate with basic auth using the auth= parameter
response = requests.get("https://httpbin.org/basic-auth/user/pass", auth=("user", "pass"))

# Combine POST body, custom headers, and Bearer auth in one call
headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
response = requests.post("https://api.example.com/items", json=payload, headers=headers)

# Check for HTTP errors and raise an exception if the request failed
response.raise_for_status()
```

## Exercise

Write a script called `api_methods.py` that demonstrates POST, PUT, and DELETE requests with authentication. The script must do the following:

1. Load a token from an environment variable called `API_TOKEN`. If the variable is not set, print an error message and exit. For this exercise, the token value can be any non-empty string — httpbin.org does not validate tokens, but your script must still load it from the environment and include it in headers.
    
2. Define a function called `make_request` that accepts three parameters: `method` (a string — `"POST"`, `"PUT"`, or `"DELETE"`), `url` (a string), and `data` (a dictionary, with a default value of `None`). The function must:
    
    - Build an `Authorization` header using the Bearer token pattern with the token loaded in step 1.
    - Also include an `Accept: application/json` header.
    - If `method` is `"POST"`, call `requests.post()` with the `json=` parameter set to `data`.
    - If `method` is `"PUT"`, call `requests.put()` with the `json=` parameter set to `data`.
    - If `method` is `"DELETE"`, call `requests.delete()` (no body).
    - If `method` is anything else, print `Unknown method: <method>` and return `None`.
    - Return the response object.
3. Use `make_request` to perform the following three calls, in order:
    
    - POST to `https://httpbin.org/post` with the body `{"action": "create", "item": "issue", "title": "Fix login bug"}`
    - PUT to `https://httpbin.org/put` with the body `{"action": "update", "item": "issue", "title": "Fix login bug (updated)"}`
    - DELETE to `https://httpbin.org/delete` with no body
4. After each call, print a summary in the following exact format (one summary per call, no blank lines between them):
    

```
--- POST https://httpbin.org/post ---
Status: 200
Auth header sent: Bearer <your token value here>
Body sent: {"action": "create", "item": "issue", "title": "Fix login bug"}
--- PUT https://httpbin.org/put ---
Status: 200
Auth header sent: Bearer <your token value here>
Body sent: {"action": "update", "item": "issue", "title": "Fix login bug (updated)"}
--- DELETE https://httpbin.org/delete ---
Status: 200
Auth header sent: Bearer <your token value here>
Body sent: None
```

> [!tip] To get the `Auth header sent` and `Body sent` values, parse the httpbin response JSON. httpbin echoes back the headers it received in `response.json()["headers"]` and the parsed JSON body in `response.json()["json"]`. For DELETE (which sends no body), `response.json()["json"]` will be `None`.

Run the script by setting the environment variable inline:

```bash
API_TOKEN="my-test-token-123" python3 api_methods.py
```

**Expected output** (with `API_TOKEN="my-test-token-123"`):

```
--- POST https://httpbin.org/post ---
Status: 200
Auth header sent: Bearer my-test-token-123
Body sent: {"action": "create", "item": "issue", "title": "Fix login bug"}
--- PUT https://httpbin.org/put ---
Status: 200
Auth header sent: Bearer my-test-token-123
Body sent: {"action": "update", "item": "issue", "title": "Fix login bug (updated)"}
--- DELETE https://httpbin.org/delete ---
Status: 200
Auth header sent: Bearer my-test-token-123
Body sent: None
```

---

## Audit

|Requirement|Introduced in|
|---|---|
|`import requests`|Lesson 37|
|`import os`|Lesson 31|
|`import sys`|Lesson 29|
|`import json` (for `json.dumps`)|Lesson 28|
|`os.getenv()`|Lesson 31|
|`sys.exit()`|Lesson 29|
|`requests.post()`, `requests.put()`, `requests.delete()`|Lesson 38 (this lesson)|
|`json=` parameter|Lesson 38 (this lesson)|
|`headers=` parameter|Lesson 38 (this lesson)|
|Bearer token in `Authorization` header|Lesson 38 (this lesson)|
|`response.status_code`|Lesson 37|
|`response.json()`|Lesson 37|
|Dictionary access with `[]`|Lesson 11|
|`def` with parameters and default values|Lessons 15–16|
|`if/elif/else`|Lesson 10|
|`return`|Lesson 15|
|f-strings|Lesson 6|
|`print()`|Lesson 1|
|`json.dumps()` for formatting dict as string|Lesson 28|
|String comparison (`method == "POST"`)|Lesson 10|

All operations required by the exercise are covered in this lesson or in prior lessons. No future-lesson material is required.