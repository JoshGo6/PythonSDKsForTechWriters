# Lesson 35: HTTP Essentials for SDK Users

## Terminology and Theory

Every Python SDK that talks to a web service — PyGithub, the Stripe SDK, the Anthropic SDK — is doing the same thing under the hood: sending **HTTP requests** to a server and reading **HTTP responses** back. Understanding this layer matters because when something goes wrong — a cryptic error, a missing field, a permission failure — the explanation almost always lives at the HTTP level, not the SDK level. You will also encounter raw HTTP concepts constantly in API documentation.

This lesson teaches the vocabulary and mechanics of HTTP so that when you see an SDK method like `repo.get_issues(state="open")`, you can picture the actual HTTP conversation happening beneath it.

**Request** — A message your code sends to a server. A request has four parts: a **method**, a **URL** (which includes the **endpoint**), **headers**, and an optional **body**.

**Response** — The message the server sends back. A response has three parts: a **status code**, **headers**, and an optional **body**.

**Endpoint** — The path portion of a URL that identifies a specific resource or action on the server. For example, in `https://api.github.com/repos/octocat/hello-world/issues`, the endpoint is `/repos/octocat/hello-world/issues`. The server uses the endpoint to decide what data to retrieve or what action to perform.

**Base URL** — The fixed prefix that all endpoints for an API share. For the GitHub API, the base URL is `https://api.github.com`. A full request URL is the base URL combined with an endpoint: `https://api.github.com` + `/repos/octocat/hello-world/issues`.

**HTTP method** — A verb that tells the server what kind of operation you want. The five methods you will encounter most often are:

- `GET` — Retrieve data. Does not change anything on the server. This is the most common method in SDK code.
- `POST` — Create a new resource. When an SDK method creates an issue, opens a pull request, or adds a comment, it sends a POST request.
- `PUT` — Replace a resource entirely with the data you send.
- `PATCH` — Update part of a resource, leaving the rest unchanged. Many "edit" operations in SDKs use PATCH.
- `DELETE` — Remove a resource.

> [!note]  
> `GET` and `DELETE` requests typically do not include a body. `POST`, `PUT`, and `PATCH` requests typically do.

**Status code** — A three-digit number in the response that tells you what happened. Status codes are grouped by their first digit:

- **2xx — Success.** The server did what you asked.
    - `200 OK` — The request succeeded and the response body contains the requested data.
    - `201 Created` — A new resource was created successfully. The response body usually contains the new resource.
    - `204 No Content` — The request succeeded but there is no body in the response. Common after a successful DELETE.
- **3xx — Redirection.** The resource has moved. SDKs and HTTP libraries usually follow redirects automatically, so you rarely deal with these directly.
    - `301 Moved Permanently` — The resource is now at a different URL.
- **4xx — Client error.** Something is wrong with your request.
    - `400 Bad Request` — The server could not understand your request. Often means malformed JSON or missing required fields.
    - `401 Unauthorized` — You did not provide valid credentials. Your token is missing, expired, or wrong.
    - `403 Forbidden` — Your credentials are valid, but you do not have permission to perform this action.
    - `404 Not Found` — The resource does not exist, or you do not have permission to see it. Some APIs return 404 instead of 403 to avoid revealing that a private resource exists.
    - `422 Unprocessable Entity` — The server understood your request but could not process it. Common when a field value is invalid (for example, assigning an issue to a user who does not exist in that repository).
- **5xx — Server error.** Something went wrong on the server's side, not yours.
    - `500 Internal Server Error` — A generic server failure.
    - `502 Bad Gateway` — The server received an invalid response from an upstream server.
    - `503 Service Unavailable` — The server is temporarily overloaded or down for maintenance.

**Header** — A key-value pair attached to a request or response that carries metadata. Headers are not part of the body — they describe the message itself. Common request headers include:

- `Authorization` — Carries your credentials (for example, `Authorization: Bearer ghp_abc123...`).
- `Content-Type` — Tells the server the format of your request body (for example, `Content-Type: application/json`).
- `Accept` — Tells the server what format you want the response in (for example, `Accept: application/json`).

Common response headers include:

- `Content-Type` — Tells you the format of the response body.
- `X-RateLimit-Remaining` — How many API requests you have left before being throttled (GitHub-specific, but many APIs have similar headers).

**Body** — The main content of a request or response. For APIs, the body is almost always JSON. In a `POST` request, the body contains the data you want to create (for example, the title and body text of a new issue). In a `GET` response, the body contains the data you requested.

**How this maps to SDKs:** When you call `repo.get_issues(state="open")` in PyGithub, the SDK internally builds an HTTP request like this:

```
GET /repos/octocat/hello-world/issues?state=open
Host: api.github.com
Authorization: Bearer ghp_abc123...
Accept: application/json
```

The server responds with something like:

```
200 OK
Content-Type: application/json
X-RateLimit-Remaining: 58

[{"id": 1, "title": "Fix typo in README", "state": "open", ...}, ...]
```

The SDK takes the response body (a JSON array of issue objects), parses it, wraps each item in a Python object with attributes and methods, and hands you the result. When something fails — a `401` because your token expired, a `404` because you misspelled the repo name — the SDK translates the status code into a Python exception. Understanding the HTTP layer helps you diagnose these failures and write accurate documentation about them.

---

## Syntax

This lesson does not introduce new Python syntax. Instead, it teaches the HTTP concepts that you will use when writing Python code that works with API response data. The code you write in this lesson uses skills you already have: dictionaries, JSON parsing, conditionals, functions, f-strings, and logging.

The patterns you will use to work with HTTP response data in Python look like this:

**Representing a response as a dictionary:**

```python
response = {
    "status_code": 200,
    "headers": {
        "Content-Type": "application/json",
        "X-RateLimit-Remaining": "58"
    },
    "body": '{"login": "octocat", "id": 1, "name": "The Octocat"}'
}
```

A response dictionary has three keys matching the three parts of an HTTP response: `status_code` (an integer), `headers` (a dictionary of strings), and `body` (a JSON string that you parse with `json.loads()`).

**Checking the status code to decide what to do:**

```python
status = response["status_code"]

if status == 200:
    data = json.loads(response["body"])
    # Process the data
elif status == 401:
    logging.error("Authentication failed — check your token")
elif status == 404:
    logging.warning("Resource not found")
else:
    logging.error(f"Unexpected status code: {status}")
```

**Reading a header value:**

```python
remaining = response["headers"].get("X-RateLimit-Remaining", "unknown")
```

Using `.get()` with a default avoids a `KeyError` if the header is not present.

**Parsing the body as JSON:**

```python
import json

body_text = response["body"]
data = json.loads(body_text)
```

After parsing, `data` is a normal Python dict or list that you work with using the same tools you already know.

---

## Worked Examples

### Example 1: Parse a successful GET response and extract data

This script receives a simulated response from a "get user" endpoint, checks the status code, parses the JSON body, and prints a summary.

```python
import json

response = {
    "status_code": 200,
    "headers": {
        "Content-Type": "application/json",
        "X-RateLimit-Remaining": "42"
    },
    "body": '{"login": "octocat", "id": 1, "name": "The Octocat", "public_repos": 8}'
}

status = response["status_code"]

if status == 200:
    user = json.loads(response["body"])
    print(f"User: {user['login']}")
    print(f"Name: {user['name']}")
    print(f"Public repos: {user['public_repos']}")
    remaining = response["headers"].get("X-RateLimit-Remaining", "unknown")
    print(f"API calls remaining: {remaining}")
else:
    print(f"Request failed with status {status}")
```

Output:

```
User: octocat
Name: The Octocat
Public repos: 8
API calls remaining: 42
```

This is the basic pattern: check the status, parse the body only if the request succeeded, and extract the fields you need. The rate-limit header is read with `.get()` because not every API includes it.

### Example 2: Handle multiple status codes with a branching function

This script defines a function that processes a response and takes different actions depending on the status code. This is the pattern you will use constantly when working with SDK code and when writing documentation about error handling.

```python
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def handle_response(response):
    """Process an HTTP response and return the parsed body or None."""
    status = response["status_code"]
    
    if status == 200:
        data = json.loads(response["body"])
        logging.info(f"Success — received {len(data)} items")
        return data
    elif status == 201:
        data = json.loads(response["body"])
        logging.info(f"Created — new resource id: {data.get('id', 'unknown')}")
        return data
    elif status == 204:
        logging.info("Success — no content returned")
        return None
    elif status == 401:
        logging.error("Authentication failed — check your API token")
        return None
    elif status == 403:
        logging.error("Permission denied — your token lacks the required scope")
        return None
    elif status == 404:
        logging.warning("Resource not found — check the endpoint path")
        return None
    elif status == 422:
        errors = json.loads(response["body"])
        logging.error(f"Validation failed: {errors.get('message', 'unknown error')}")
        return None
    elif status >= 500:
        logging.error(f"Server error ({status}) — retry later")
        return None
    else:
        logging.warning(f"Unexpected status code: {status}")
        return None

# Simulate a successful list response
success_response = {
    "status_code": 200,
    "headers": {"Content-Type": "application/json"},
    "body": '[{"id": 1, "title": "Bug report"}, {"id": 2, "title": "Feature request"}]'
}

# Simulate a 401 error
auth_error = {
    "status_code": 401,
    "headers": {"Content-Type": "application/json"},
    "body": '{"message": "Bad credentials"}'
}

print("--- Successful response ---")
items = handle_response(success_response)
if items:
    for item in items:
        print(f"  #{item['id']}: {item['title']}")

print()
print("--- Auth error response ---")
result = handle_response(auth_error)
```

Output:

```
INFO: Success — received 2 items
--- Successful response ---
  #1: Bug report
  #2: Feature request

--- Auth error response ---
ERROR: Authentication failed — check your API token
```

The `handle_response` function is a reusable pattern. It checks the status code, logs an appropriate message, and returns the parsed data when the request succeeds or `None` when it does not. The `status >= 500` check catches all server errors with a single condition.

### Example 3: Map an SDK-style operation to its HTTP equivalent

This script shows the mental model for connecting SDK calls to HTTP. It defines two functions: one that simulates what happens at the SDK level, and one that shows the HTTP request the SDK would build. This is the kind of thinking you do when documenting SDK behavior.

```python
import json

def describe_http_request(method, endpoint, headers, body=None):
    """Print what an HTTP request looks like on the wire."""
    print(f"{method} {endpoint}")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    if body:
        print(f"  Body: {json.dumps(body)}")
    print()

def describe_sdk_call(sdk_call, method, endpoint, headers, body=None):
    """Show how an SDK call maps to an HTTP request."""
    print(f"SDK call:    {sdk_call}")
    print(f"HTTP method: {method}")
    print(f"Endpoint:    {endpoint}")
    if body:
        print(f"Sends body:  yes")
    else:
        print(f"Sends body:  no")
    print()

# GET — listing issues
describe_sdk_call(
    sdk_call='repo.get_issues(state="open")',
    method="GET",
    endpoint="/repos/octocat/hello-world/issues?state=open",
    headers={"Authorization": "Bearer ghp_...", "Accept": "application/json"}
)

# POST — creating an issue
describe_sdk_call(
    sdk_call='repo.create_issue(title="Bug", body="Details here")',
    method="POST",
    endpoint="/repos/octocat/hello-world/issues",
    headers={"Authorization": "Bearer ghp_...", "Content-Type": "application/json"},
    body={"title": "Bug", "body": "Details here"}
)

# DELETE — deleting a comment
describe_sdk_call(
    sdk_call="comment.delete()",
    method="DELETE",
    endpoint="/repos/octocat/hello-world/issues/comments/42",
    headers={"Authorization": "Bearer ghp_..."}
)
```

Output:

```
SDK call:    repo.get_issues(state="open")
HTTP method: GET
Endpoint:    /repos/octocat/hello-world/issues?state=open
Sends body:  no

SDK call:    repo.create_issue(title="Bug", body="Details here")
HTTP method: POST
Endpoint:    /repos/octocat/hello-world/issues
Sends body:  yes

SDK call:    comment.delete()
HTTP method: DELETE
Endpoint:    /repos/octocat/hello-world/issues/comments/42
Sends body:  no
```

This example does not make real HTTP calls. It builds the mental model: every SDK method corresponds to a specific HTTP method, a specific endpoint, and possibly a JSON body. `GET` retrieves data without a body, `POST` creates data with a body, and `DELETE` removes data without a body. When you document SDK methods, you are ultimately describing these HTTP operations in a developer-friendly way.

---

## Quick Reference

```python
# HTTP status code families
# 2xx = success, 3xx = redirect, 4xx = client error, 5xx = server error

# Common success codes
# 200 OK — request succeeded, body contains data
# 201 Created — new resource created, body contains it
# 204 No Content — success, but no response body

# Common client error codes
# 400 Bad Request — malformed request
# 401 Unauthorized — missing or invalid credentials
# 403 Forbidden — valid credentials, insufficient permissions
# 404 Not Found — resource does not exist
# 422 Unprocessable Entity — valid syntax, invalid values

# Common server error codes
# 500 Internal Server Error — generic server failure
# 503 Service Unavailable — server temporarily overloaded

# HTTP methods and their purposes
# GET — retrieve data (no body sent)
# POST — create a resource (body contains new data)
# PUT — replace a resource entirely (body contains full replacement)
# PATCH — update part of a resource (body contains partial update)
# DELETE — remove a resource (no body sent)

# Representing an HTTP response as a Python dict
response = {
    "status_code": 200,
    "headers": {"Content-Type": "application/json", "X-RateLimit-Remaining": "58"},
    "body": '{"login": "octocat"}'
}

# Checking the status code
status = response["status_code"]

# Branching on status code families
if 200 <= status < 300:
    print("Success")
elif 400 <= status < 500:
    print("Client error")
elif status >= 500:
    print("Server error")

# Reading a header safely with .get()
remaining = response["headers"].get("X-RateLimit-Remaining", "unknown")

# Parsing a JSON body string into a Python dict
import json
data = json.loads(response["body"])

# Mapping SDK calls to HTTP — mental model
# repo.get_issues(state="open")    → GET  /repos/.../issues?state=open
# repo.create_issue(title="Bug")   → POST /repos/.../issues  (body: {"title": "Bug"})
# comment.delete()                 → DELETE /repos/.../issues/comments/42
```

---

## Exercise

Write a script called `response_router.py` that processes a list of simulated HTTP responses and prints a report showing what action to take for each one.

**Setup:** Create a file called `responses.json` with the following contents:

```json
[
    {
        "request_method": "GET",
        "endpoint": "/repos/acme-corp/docs/issues",
        "status_code": 200,
        "headers": {"Content-Type": "application/json", "X-RateLimit-Remaining": "15"},
        "body": "[{\"id\": 101, \"title\": \"Fix install guide\"}, {\"id\": 102, \"title\": \"Add troubleshooting page\"}]"
    },
    {
        "request_method": "POST",
        "endpoint": "/repos/acme-corp/docs/issues",
        "status_code": 201,
        "headers": {"Content-Type": "application/json", "X-RateLimit-Remaining": "14"},
        "body": "{\"id\": 103, \"title\": \"Draft API reference\"}"
    },
    {
        "request_method": "DELETE",
        "endpoint": "/repos/acme-corp/docs/issues/comments/77",
        "status_code": 204,
        "headers": {},
        "body": ""
    },
    {
        "request_method": "PATCH",
        "endpoint": "/repos/acme-corp/docs/issues/101",
        "status_code": 401,
        "headers": {"Content-Type": "application/json"},
        "body": "{\"message\": \"Bad credentials\"}"
    },
    {
        "request_method": "GET",
        "endpoint": "/repos/acme-corp/secret-repo/issues",
        "status_code": 404,
        "headers": {"Content-Type": "application/json"},
        "body": "{\"message\": \"Not Found\"}"
    },
    {
        "request_method": "POST",
        "endpoint": "/repos/acme-corp/docs/issues",
        "status_code": 422,
        "headers": {"Content-Type": "application/json"},
        "body": "{\"message\": \"Validation Failed\", \"errors\": [{\"field\": \"title\", \"code\": \"missing_field\"}]}"
    },
    {
        "request_method": "GET",
        "endpoint": "/repos/acme-corp/docs/pulls",
        "status_code": 500,
        "headers": {},
        "body": ""
    }
]
```

**Requirements:**

1. The script must accept two arguments using `argparse`:
    - A positional argument for the path to the JSON file.
    - An optional `--verbose` flag.
2. Load the JSON file and parse its contents.
3. Define a function called `classify_response` that accepts a single response dictionary and returns a string describing the outcome. The function must handle status codes 200, 201, 204, 401, 404, 422, and any code ≥ 500. For all other codes, return a generic "unexpected status" message.
4. For each response, print one line in this format: `METHOD ENDPOINT → STATUS_CODE: classification_message`
5. When `--verbose` is provided, also print the following for each response, indented with two spaces:
    - For status 200: print each item's `id` and `title` from the parsed body.
    - For status 201: print the new resource's `id` and `title` from the parsed body.
    - For status 422: print the `message` field from the parsed body.
    - For status 401: print the `message` field from the parsed body.
    - For other codes: print nothing extra.
6. After all responses are processed, print a summary line showing the count of successes (2xx) and failures (non-2xx).
7. Use `logging` at the `WARNING` level to log any response where `X-RateLimit-Remaining` is present in the headers and its integer value is below 20.

**Expected output without `--verbose`:**

```
GET /repos/acme-corp/docs/issues → 200: OK — received data
POST /repos/acme-corp/docs/issues → 201: Created — new resource
DELETE /repos/acme-corp/docs/issues/comments/77 → 204: No Content — success, no body
PATCH /repos/acme-corp/docs/issues/101 → 401: Unauthorized — check credentials
GET /repos/acme-corp/secret-repo/issues → 404: Not Found — resource does not exist
POST /repos/acme-corp/docs/issues → 422: Unprocessable — validation failed
GET /repos/acme-corp/docs/pulls → 500: Server Error — retry later
WARNING:root:Rate limit low (15 remaining) for GET /repos/acme-corp/docs/issues
WARNING:root:Rate limit low (14 remaining) for POST /repos/acme-corp/docs/issues
Summary: 3 succeeded, 4 failed
```

> [!note]  
> The `WARNING` log lines may appear interleaved with the print output depending on stream buffering. The exact position of these lines in your terminal output may differ from the expected output shown above. As long as all lines are present with the correct content, your solution is correct.

**Expected output with `--verbose`:**

```
GET /repos/acme-corp/docs/issues → 200: OK — received data
  #101: Fix install guide
  #102: Add troubleshooting page
POST /repos/acme-corp/docs/issues → 201: Created — new resource
  #103: Draft API reference
DELETE /repos/acme-corp/docs/issues/comments/77 → 204: No Content — success, no body
PATCH /repos/acme-corp/docs/issues/101 → 401: Unauthorized — check credentials
  Bad credentials
GET /repos/acme-corp/secret-repo/issues → 404: Not Found — resource does not exist
POST /repos/acme-corp/docs/issues → 422: Unprocessable — validation failed
  Validation Failed
GET /repos/acme-corp/docs/pulls → 500: Server Error — retry later
WARNING:root:Rate limit low (15 remaining) for GET /repos/acme-corp/docs/issues
WARNING:root:Rate limit low (14 remaining) for POST /repos/acme-corp/docs/issues
Summary: 3 succeeded, 4 failed
```

---

## Audit

|Requirement|Skill / Operation|Introduced In|
|---|---|---|
|Read and parse a JSON file|`json.load()`, `open()`, `with`|L28, L22|
|Parse JSON strings from response bodies|`json.loads()`|L28|
|Accept a file path argument with `argparse`|`argparse.ArgumentParser`, `add_argument()`|L30|
|Accept an optional `--verbose` flag|`add_argument("--verbose", action="store_true")`|L30|
|Define a function with a parameter and return value|`def`, `return`|L15|
|Use `if/elif/else` to branch on status codes|Conditionals, comparisons|L10|
|Iterate over a list of dicts|`for` loop, dict key access|L9, L11, L12|
|Format output with f-strings|f-strings|L6|
|Use `.get()` for safe header access|`dict.get()`|L11|
|Convert a string to `int`|`int()`|L2|
|Log warnings with `logging`|`logging.basicConfig()`, `logging.warning()`|L21|
|Count successes and failures|Integer variables, `+=`, conditionals|L2, L10|
|Print formatted output|`print()`|L1|
|HTTP status code interpretation|Current lesson (L35)|L35|
|HTTP method and endpoint concepts|Current lesson (L35)|L35|

All operations required by the exercise are covered in Lesson 35 or prior lessons. No forward dependencies exist.