## Audit

| Exercise | Operations Required | Introduced In |
|----------|---------------------|---------------|
| Exercise 1 | Assign dict literal; access dict values by key; `if`/`elif`/`else`; comparison operators; implicit truthiness; `print` with f-strings; nested dict access; `json.loads`; string lowercasing with `.lower()`; indexing; `len` function. | L2 (variables, dict literal creation, `type()` – but `type()` not needed, dict literals are used); L11 (dictionaries – key access, `.get()` optionally, though we use direct key access); L10 (conditionals, comparisons); L6 (f-strings); L5 (`.lower()`); L7 (lists – `len`); L28 (JSON loading). All within scope. |

No future concepts required.

---

# Lesson 35: HTTP Essentials for SDK Users

## Terminology and Theory

When you call a method on an SDK object – for example, `repo.get_issues()` in PyGithub – the SDK is not performing magic. It constructs an **HTTP request** and sends it over the network to a remote server. The server replies with an **HTTP response**, and the SDK converts that response back into Python objects for you.

Understanding the HTTP conversation underneath an SDK call is essential for:
- reading **error messages** that bubble up from network problems,
- interpreting **rate‑limit headers**,
- debugging why a “valid” call did not return what you expected, and
- writing accurate API documentation.

> [!info]  
> An SDK is a wrapper around raw HTTP requests. Every SDK method call corresponds to one or more HTTP requests.

### The request / response cycle

1. The **client** (your script) sends an **HTTP request** to a **server** at a specific **URL** (also called an **endpoint**).
2. The request includes:
   - an **HTTP method** (the *verb* of the action), such as `GET`, `POST`, `PUT`, or `DELETE`.
   - optional **headers** that provide metadata (e.g., `Authorization`, `Content-Type`).
   - an optional **body** (for `POST` and `PUT`), often a JSON payload.
3. The server processes the request and sends back an **HTTP response** containing:
   - a **status code** (a three‑digit number telling you what happened).
   - **response headers** (metadata about the response).
   - a **response body**, which for modern REST APIs is almost always JSON.

### Status codes in practice

| Status code range | Meaning                  | Common codes you’ll see         |
|-------------------|--------------------------|---------------------------------|
| 2xx               | Success                  | 200 OK, 201 Created, 204 No Content |
| 3xx               | Redirection              | 301 Moved Permanently, 304 Not Modified |
| 4xx               | Client error (your fault)| 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity |
| 5xx               | Server error (their fault)| 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable |

A robust script always checks the status code before parsing the body. A successful status does not guarantee the body matches your expectation, but an error status always means the body contains error information, not the data you asked for.

### Headers

Headers are key‑value pairs that convey extra information. Important headers for SDK users:

- **`Content-Type`** – tells you the format of the response body (e.g., `application/json`).
- **`Authorization`** – carries your token (the SDK handles this for you).
- **`X-RateLimit-Remaining`** – how many requests you have left (GitHub‑specific).

### The body

For REST APIs, the response body is typically a JSON string. When you call `response.json()` in a library like `requests` (or when the SDK does it for you), the JSON string is parsed into Python dictionaries, lists, strings, numbers, Booleans, and `None`. We already know how to work with those.

### How all of this maps to SDK calls

Consider a PyGithub call like:
```python
repo = g.get_repo("owner/repo")
issues = repo.get_issues(state="open")
```
Under the hood, PyGithub sends a `GET` request to something like:
```
GET /repos/owner/repo/issues?state=open
```
with an `Authorization` header that contains your token.  
It receives a JSON array of issue objects, parses it, and wraps each one in a `GithubIssue` instance.  
If the request fails (e.g., 404 “repo not found”), PyGithub raises a `GithubException` that contains the status code and error body.

By the end of this lesson, you will be able to look at a raw HTTP response (represented as a Python dictionary) and write script logic that decides what to do next based on the status code and body.

---

## Syntax Section

There is no new Python syntax in this lesson – we will use skills you already have. However, it is useful to establish a pattern for working with simulated HTTP responses.

### Representing an HTTP response in Python

We will model a response as a dictionary with at least these keys:

```python
response = {
    "status_code": 200,           # integer
    "headers": {                  # dict of string -> string
        "Content-Type": "application/json",
        "X-RateLimit-Remaining": "57"
    },
    "body": '{"items": [1, 2, 3]}'  # the raw response body as a string
}
```

If the body is JSON, you can parse it with `json.loads()` to get back the Python data structure.

### Pattern for processing a response

```python
import json

# 1. Inspect the status code
if response["status_code"] == 200:
    # 2. Parse the body and use it
    data = json.loads(response["body"])
    count = len(data.get("items", []))
    print(f"Success – found {count} items.")
elif response["status_code"] == 404:
    print("Resource not found.")
elif response["status_code"] == 401:
    print("Authorization required – check your token.")
else:
    print(f"Unexpected status code: {response['status_code']}")
```

> [!tip]  
> Always check the status code **before** attempting to parse the body. An error response might contain HTML or a plain‑text message, not valid JSON.

### Reading headers

```python
content_type = response["headers"].get("Content-Type", "unknown")
if "json" not in content_type:
    print(f"Warning: unexpected content type {content_type}")
```

All of these operations – dictionary lookups (`[]`), `.get()`, `json.loads()`, conditionals, f‑strings – were taught in earlier lessons.

---

## Worked Examples

### Example 1: A successful response

Assume we received this response from a “list items” endpoint:

```python
response = {
    "status_code": 200,
    "headers": {"Content-Type": "application/json"},
    "body": '{"items": ["apple", "banana", "cherry"]}'
}
```

Our script should print how many items were returned.

```python
import json

response = {
    "status_code": 200,
    "headers": {"Content-Type": "application/json"},
    "body": '{"items": ["apple", "banana", "cherry"]}'
}

if response["status_code"] == 200:
    data = json.loads(response["body"])
    items = data.get("items", [])
    print(f"Found {len(items)} items: {', '.join(items)}")
else:
    print(f"Request failed with status {response['status_code']}")
```

**Output:**
```
Found 3 items: apple, banana, cherry
```

### Example 2: Dealing with a 404

The same endpoint, but the resource does not exist:

```python
response = {
    "status_code": 404,
    "headers": {"Content-Type": "application/json"},
    "body": '{"message": "Not Found"}'
}

if response["status_code"] == 200:
    data = json.loads(response["body"])
    print("Success, data:", data)
elif response["status_code"] == 404:
    error_msg = json.loads(response["body"]).get("message", "No additional info")
    print(f"Resource not found: {error_msg}")
else:
    print(f"Unhandled status: {response['status_code']}")
```

**Output:**
```
Resource not found: Not Found
```

### Example 3: Interpreting a 401 (Unauthorized)

```python
response = {
    "status_code": 401,
    "headers": {"Content-Type": "application/json"},
    "body": '{"message": "Bad credentials"}'
}

if response["status_code"] == 401:
    error_msg = json.loads(response["body"]).get("message", "")
    print("Authentication failed. Check your token.")
    print(f"Server says: {error_msg}")
elif response["status_code"] == 200:
    print("OK – you are authenticated.")
else:
    print(f"Status {response['status_code']}")
```

**Output:**
```
Authentication failed. Check your token.
Server says: Bad credentials
```

> [!note]  
> When you see a 401 from a real API, the body is often a JSON object with a `message` field. Always show it to the user – it helps them fix the problem.

---
## Quick Reference

```python
# Represent an HTTP response as a dictionary
response = {
    "status_code": 200,
    "headers": {"Content-Type": "application/json", "X-Request-Id": "abc-123"},
    "body": '{"data": ["apple", "banana", "cherry"]}'
}

# Check for a successful status code
if response["status_code"] == 200:
    # proceed to parse body – safe path

# Parse a JSON body
import json
data = json.loads(response["body"])

# Extract a header value safely
request_id = response["headers"].get("X-Request-Id", "N/A")

# Branch on status codes – cover 200, 404, 401, and a fallback
if response["status_code"] == 200:
    items = json.loads(response["body"]).get("data", [])
    print(f"Success: {len(items)} items")
elif response["status_code"] == 404:
    print("Not found")
elif response["status_code"] == 401:
    msg = json.loads(response["body"]).get("message", "Unauthorized")
    print(f"Unauthorized – {msg}")
    print(f"Request ID: {request_id}")
else:
    print(f"Unexpected status: {response['status_code']}")
```

---

## Exercises

### Exercise 1: Status‑Based Decision Maker

Write a Python script that processes a simulated HTTP response.  
The response is provided below as a Python dictionary. Your script must examine the status code and the parsed body, then print exactly the expected output.

**The response to process:**

```python
response = {
    "status_code": 401,
    "headers": {
        "Content-Type": "application/json",
        "X-Request-Id": "abc-123"
    },
    "body": '{"message": "Requires authentication"}'
}
```

**Requirements:**

- If the status code is `200`, the script should:
  - Parse the JSON body,
  - Extract a key named `"data"` from the parsed body (a list of strings),
  - Print `Success: N items` where `N` is the length of that list.  
    If the key `"data"` is missing, print `Success: empty data`.

- If the status code is `401`, the script should:
  - Parse the JSON body,
  - Extract the `"message"` field from the parsed body,
  - Print `Unauthorized – <message>` where `<message>` is the extracted text.
  - Additionally, print the value of the `X-Request-Id` header on the next line in the format `Request ID: <value>`. (If the header is missing, use `N/A`).

- If the status code is `404`, the script should print `Not found`.

- For any other status code, print `Unexpected status: <code>`.

**Expected output for the provided response:**

```
Unauthorized – Requires authentication
Request ID: abc-123
```

**Hint:**  
Use `json.loads()` to parse the body. Use `.get()` to safely access dictionary keys that might be missing.

Write your script and run it. Verify that the printed output matches the expected lines exactly.