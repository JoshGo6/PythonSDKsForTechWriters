# Lesson 38: Making HTTP Requests with `requests` — POST, Headers, and Authentication

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