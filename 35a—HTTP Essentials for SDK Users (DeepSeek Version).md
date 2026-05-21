## Audit for Lesson 35: HTTP essentials for SDK users

## Exercise: Process an HTTP response file and print next-step message

| Required operation / syntax      | Introduced in |
| -------------------------------- | ------------- |
| `import json`                    | Lesson 28     |
| `import logging`                 | Lesson 21     |
| `import argparse`                | Lesson 30     |
| `logging.basicConfig()`          | Lesson 21     |
| `logging.debug()`                | Lesson 21     |
| `argparse.ArgumentParser()`      | Lesson 30     |
| `parser.add_argument()`          | Lesson 30     |
| `args = parser.parse_args()`     | Lesson 30     |
| `with open(…) as f:`             | Lesson 22     |
| `json.load(f)`                   | Lesson 28     |
| Dictionary subscript access      | Lesson 11     |
| `if…elif…else`                   | Lesson 10     |
| Comparison operators (`==`, `<`) | Lesson 10     |
| f‑string formatting              | Lesson 6      |
| `print()`                        | Lesson 3      |

All operations are drawn from lessons completed before Lesson 35. The exercise passes the audit.

---

# Lesson 35: HTTP essentials for SDK users

## Terminology and Theory

Every interaction between an SDK (or a script) and a remote API happens over **HTTP**—the Hypertext Transfer Protocol. At a high level:

- A **client** (your Python script or the SDK) sends an **HTTP request** to a **server** (e.g., `https://api.github.com`).
- The server processes the request and returns an **HTTP response**.

All the SDK method calls you’ll see—`g.get_user()`, `repo.get_issues()`—are translated into HTTP requests under the hood. Understanding HTTP helps you read raw API behaviour, debug SDK errors, and write scripts when no SDK exists.

When I am typing. This is what it sounds like.
### Key concepts

| Term                     | Explanation                                                                                                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Endpoint (URL)**       | The address the request is sent to. It includes a protocol (`https://`), a host, and a path: `https://api.github.com/repos/octocat/Spoon‑Knife`.                                      |
| **HTTP method**          | The action the request wants to perform. Common methods: `GET` (read data), `POST` (create new), `PUT`/`PATCH` (update), `DELETE` (remove).                                           |
| **Request headers**      | Key-value pairs sent with the request. Examples: `Authorization` (token), `Content‑Type` (format of the body), `Accept` (desired response format).                                    |
| **Request body**         | Optional data sent with `POST`/`PUT` methods. Often a JSON string when working with APIs.                                                                                             |
| **Response status code** | A three‑digit number indicating the result. Categories: **2xx** success, **3xx** redirect, **4xx** client error, **5xx** server error. See the table below for the most common codes. |
| **Response headers**     | Key-value pairs from the server. They often include `Content‑Type` (e.g., `application/json`) and rate‑limit information.                                                             |
| **Response body**        | The data returned by the server. With REST APIs, this is almost always JSON text that Python can parse into a dictionary.                                                             |

### Common status codes

| Code | Meaning                  | Typical SDK behaviour                                       |
|------|--------------------------|-------------------------------------------------------------|
| 200  | OK                       | Request succeeded; body contains the data you asked for.     |
| 201  | Created                  | A new resource was created (e.g., a new issue).              |
| 204  | No Content               | Request succeeded but there is no body to return.            |
| 301  | Moved Permanently        | The resource has a new URL; the SDK may follow it automatically. |
| 400  | Bad Request              | The server cannot understand the request (e.g., malformed JSON). |
| 401  | Unauthorized             | Authentication is missing or invalid. Check your token.      |
| 403  | Forbidden                | Authenticated but not allowed to access the resource.         |
| 404  | Not Found                | The requested resource does not exist.                       |
| 422  | Unprocessable Entity     | The request was valid, but the data failed validation (e.g., duplicate issue). |
| 500  | Internal Server Error    | Something went wrong on the server side.                     |

> [!tip]  
> When an SDK encounters a non‑2xx response, it typically raises an exception. In Lesson 39 we’ll learn to catch those exceptions gracefully.

### How SDK methods map to HTTP

Consider this PyGithub call:

```python
repo = g.get_repo("octocat/Spoon‑Knife")
```

Behind the scenes the SDK:
1. Constructs a `GET` request to `https://api.github.com/repos/octocat/Spoon‑Knife`.
2. Adds an `Authorization: token <your_token>` header.
3. Sends the request.
4. Checks the status code. If it’s 200, it parses the JSON body into a Python object. If it’s 404, it raises a `github.GithubException` with the error details.

When you work at the HTTP level—for example, using `curl` or the `requests` library—you see all of these steps explicitly. This lesson teaches you how to work with **simulated HTTP responses** so you can practice decision‑making based on status codes and bodies before making real API calls in Lesson 37.

## Syntax Section

There are no new Python keywords or syntax to learn in this lesson. Instead, you will use previously‑taught tools—dictionaries, `json.loads()`, conditionals, and f‑strings—to handle response data that comes as a dictionary or a JSON string.

A typical pattern for processing a simulated response looks like this:

```python
import json

# Response as a JSON string (as it would arrive from a real API call)
response_text = '''
{
    "status_code": 200,
    "headers": {"Content-Type": "application/json"},
    "body": {"login": "octocat", "id": 1}
}
'''

data = json.loads(response_text)
status = data["status_code"]
body = data["body"]

if 200 <= status < 300:
    print(f"Success: user {body['login']} has id {body['id']}")
elif status == 404:
    print("Error: resource not found")
else:
    print(f"Unexpected status: {status}")
```

- `json.loads()` turns the JSON string into a nested dictionary.
- `data["status_code"]` retrieves the integer status code.
- `data["body"]` gives the inner dictionary (or list, or scalar) that the API returned.
- Conditionals decide what to do next based on the status.

When the response body is expected to contain a list, you can iterate with `for` loops, just as you would with any list of dictionaries.

## Worked Examples

Assume each example is run inside a script. The pattern of importing `json` and parsing a string is the same throughout.

### Example 1: A successful GET response

```python
import json

response = '''
{
    "status_code": 200,
    "headers": {"Content-Type": "application/json"},
    "body": {
        "login": "octocat",
        "public_repos": 8,
        "followers": 5432
    }
}
'''

data = json.loads(response)
status = data["status_code"]
body = data["body"]

if 200 <= status < 300:
    print(f"User {body['login']} has {body['public_repos']} public repos.")
else:
    print(f"Request failed with status {status}")
```

**What’s happening:**  
The status falls in the 2xx range, so the `if` branch runs, and we extract values from the body dictionary to produce a human‑readable message. If the status were anything else, we’d simply report it.

### Example 2: A 404 “Not Found” response

```python
import json

response = '''
{
    "status_code": 404,
    "headers": {"Content-Type": "application/json"},
    "body": {
        "message": "Not Found",
        "documentation_url": "https://docs.github.com/rest"
    }
}
'''

data = json.loads(response)
status = data["status_code"]

if status == 404:
    print("Error: The requested resource was not found.")
    print(f"GitHub message: {data['body']['message']}")
else:
    print(f"Status {status}: something else happened.")
```

**What’s happening:**  
We only expect two branches here. The status is 404, so we print a clear error message along with the server’s own `message` field. In real code you’d often want to include the documentation URL for the user to investigate.

### Example 3: A 401 “Unauthorized” response — suggest checking credentials

```python
import json

response = '''
{
    "status_code": 401,
    "headers": {"Content-Type": "application/json"},
    "body": {
        "message": "Bad credentials",
        "documentation_url": "https://docs.github.com/rest"
    }
}
'''

data = json.loads(response)
status = data["status_code"]

if status == 401:
    print("Authentication failed: bad credentials.")
    print("Check that your token is set correctly and has not expired.")
else:
    print(f"Received status {status}")
```

**What’s happening:**  
The status 401 branch fires, printing a user‑friendly suggestion. The body’s `message` often contains the phrase “Bad credentials,” which you can relay to the user. In an automated script, you might then abort or prompt for a new token.

## Quick Reference

```python
# Loading a JSON string into a dict
import json
response_str = '{"status_code": 200, "body": {"key": "value"}}'
data = json.loads(response_str)

# Accessing status and body
status = data["status_code"]
body = data["body"]

# Checking status categories
if 200 <= status < 300:
    print("Success")
elif status in (401, 403):
    print("Authentication / access problem")
elif status == 404:
    print("Not found")
elif status >= 500:
    print("Server error")

# Extracting a header value
headers = data.get("headers", {})
content_type = headers.get("Content-Type", "unknown")
print(f"Content-Type: {content_type}")

# Iterating over a body that is a list of dicts
for item in body:
    if isinstance(item, dict):
        print(item.get("name", "unnamed"))
```

## Exercises

### Exercise: Process an HTTP response file and print the next step

**Goal:** Use `argparse` to accept a file path, load a simulated HTTP response from that file with `json.load()`, log debug information, and print a decision message based on the status code and body contents.

**Step 1 – Create the response file**

Copy the content below into a file named `response.json` in the same directory as your script. The file represents a successful `GET /users/octocat` response.

```json
{
    "status_code": 200,
    "headers": {
        "Content-Type": "application/json",
        "X-RateLimit-Remaining": "4999"
    },
    "body": {
        "login": "octocat",
        "id": 1,
        "public_repos": 8,
        "followers": 5432,
        "following": 9,
        "created_at": "2011-01-25T18:44:36Z"
    }
}
```

**Step 2 – Write the script**

Write a Python script named `process_response.py` that:

1. Uses `argparse` to accept an optional `--file` argument. If not provided, the program should default to `"response.json"`.
2. Configures `logging` at `DEBUG` level so that debug messages appear in the terminal.
3. Logs a debug message containing the status code and the `Content-Type` header value as soon as they are read from the file.
4. Reads the JSON file using `open()` and `json.load()`.
5. Checks the `status_code`:
   - If the status is 200, print exactly:  
     `Success: user <login> has <public_repos> public repos.`  
     Replace `<login>` and `<public_repos>` with the values from the response body.
   - If the status is 404, print:  
     `Error: resource not found.`
   - For any other status, print:  
     `Unexpected status: <code>`  
     replacing `<code>` with the actual status code.
6. Prints the appropriate message to standard output.

**Desired output**  
When you run `python process_response.py --file response.json`, the output should be:

```
DEBUG:root:Status: 200, Content-Type: application/json
Success: user octocat has 8 public repos.
```

(The exact format of the DEBUG line may include additional information like timestamps; that’s fine.)

> [!note]  
> Remember that `logging.basicConfig(level=logging.DEBUG)` must be called once at the start of your script for debug messages to appear.