# Lesson 39: API Response Handling and Debugging

## Terminology and Theory

**Status code checking before parsing.** Every HTTP response carries a status code that tells you whether the request succeeded. A common mistake is to call `.json()` on a response without first checking whether the server actually returned JSON. A `500 Internal Server Error` response might return an HTML error page, and calling `.json()` on that raises a `json.JSONDecodeError`. The discipline is: always check the status code _before_ you try to parse the body.

**`response.raise_for_status()`.** The `requests` library provides a built-in method that inspects the status code and raises an `HTTPError` exception if the code indicates failure (any 4xx or 5xx status). Calling this immediately after a request means you don't need to write your own `if response.status_code >= 400` logic every time. The exception it raises is `requests.exceptions.HTTPError`, which is a subclass of `requests.exceptions.RequestException`.

**The `requests.exceptions` hierarchy.** The `requests` library defines several exception classes, all inheriting from `requests.exceptions.RequestException`:

- `ConnectionError` — the request could not reach the server at all (DNS failure, refused connection, network down).
- `Timeout` — the server did not respond within the allowed time.
- `HTTPError` — raised by `raise_for_status()` when the server returns a 4xx or 5xx status code.

Catching `RequestException` catches all of these. Catching a specific subclass lets you handle each failure differently.

**Common HTTP error codes you'll encounter in API work:**

- `400 Bad Request` — the server rejected your request because something in it was malformed or invalid (wrong field name, bad JSON, missing required parameter).
- `401 Unauthorized` — you didn't provide credentials, or the credentials were not recognized.
- `403 Forbidden` — your credentials were recognized, but you don't have permission to access this resource.
- `404 Not Found` — the resource you requested doesn't exist at that URL.
- `422 Unprocessable Entity` — the request was well-formed, but the server couldn't process it due to semantic errors (common in APIs that validate input fields).
- `500 Internal Server Error` — something went wrong on the server's side.

**Logging request and response details.** When a script makes API calls, logging what you sent and what you got back is essential for debugging. At minimum, log the HTTP method, URL, status code, and (for failures) the response body. Use the `logging` module rather than `print()` so you can control verbosity with log levels.

**The `timeout` parameter.** Every `requests.get()` or `requests.post()` call should include a `timeout` parameter (in seconds). Without it, a request to an unresponsive server will hang indefinitely, and your script will appear frozen. A timeout of 10–30 seconds is typical for API calls.

**Reusable request functions.** Once you've written status-checking, error-handling, and logging logic, you don't want to repeat it for every API call. Wrapping this logic in a function that accepts a method, URL, and optional parameters gives you a single place to maintain your error-handling strategy.

---

## Syntax Section

### Checking the status code before parsing

```python
response = requests.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
else:
    print(f"Request failed: {response.status_code}")
```

`response.status_code` is an integer. You compare it directly against known codes. Only parse the body when you know the response is what you expected.

### Using `raise_for_status()`

```python
response = requests.get(url, timeout=10)
response.raise_for_status()  # Raises HTTPError if status is 4xx or 5xx
data = response.json()
```

If the status code is 200–299, `raise_for_status()` does nothing and execution continues. If it's 4xx or 5xx, it raises `requests.exceptions.HTTPError`. You wrap this in a `try/except` to handle the failure.

### Catching specific request exceptions

```python
import requests

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.ConnectionError:
    print("Could not connect to the server.")
except requests.exceptions.Timeout:
    print("The request timed out.")
except requests.exceptions.HTTPError as exc:
    print(f"HTTP error: {exc.response.status_code}")
except requests.exceptions.RequestException as exc:
    print(f"Unexpected request error: {exc}")
```

The order matters. `RequestException` is the parent class, so it goes last — it catches anything the more specific handlers above it didn't already catch. Each `except` block receives the exception object as `exc`. For `HTTPError`, the original response is available as `exc.response`, so you can inspect `exc.response.status_code` and `exc.response.text`.

### Accessing the response body on errors

```python
except requests.exceptions.HTTPError as exc:
    print(f"Status: {exc.response.status_code}")
    print(f"Body: {exc.response.text}")
```

API error responses often include a JSON body with details about what went wrong. You can inspect `exc.response.text` (the raw string) or, if you know the error response is JSON, call `exc.response.json()` inside the `except` block.

### Logging request and response details

```python
import logging
import requests

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

response = requests.get(url, timeout=10)
logging.debug("GET %s → %d", url, response.status_code)

if response.status_code != 200:
    logging.error("Response body: %s", response.text[:500])
```

Use `logging.debug()` for routine information (what was sent, what came back) and `logging.error()` for failures. Truncating the response body (e.g., `[:500]`) prevents flooding your log with an entire HTML error page.

### The `timeout` parameter

```python
# Timeout after 10 seconds
response = requests.get(url, timeout=10)

# Separate connect and read timeouts: 5s to connect, 15s to read
response = requests.get(url, timeout=(5, 15))
```

A single number sets both the connect timeout and the read timeout. A tuple sets them independently. If the timeout is exceeded, `requests` raises `requests.exceptions.Timeout`.

### Building a reusable request function

```python
def api_request(method, url, **kwargs):
    """Make an HTTP request with logging and error handling."""
    kwargs.setdefault("timeout", 10)
    logging.debug("%s %s", method.upper(), url)

    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        logging.debug("Response: %d", response.status_code)
        return response
    except requests.exceptions.HTTPError as exc:
        logging.error("HTTP %d: %s", exc.response.status_code, exc.response.text[:300])
        return None
    except requests.exceptions.RequestException as exc:
        logging.error("Request failed: %s", exc)
        return None
```

`requests.request(method, url, **kwargs)` is the general-purpose function underlying `requests.get()`, `requests.post()`, and so on. The first argument is the HTTP method as a string (`"get"`, `"post"`, etc.). Using this in a wrapper function means you don't need separate wrappers for each method.

`kwargs.setdefault("timeout", 10)` sets a default timeout only if the caller didn't pass one. This ensures every request gets a timeout without forcing callers to specify one.

The function returns the `response` object on success and `None` on failure. The caller checks the return value before proceeding.

---

## Worked Examples

### Example 1: Checking status before parsing

This script fetches a user from the GitHub API and handles the case where the user doesn't exist.

```python
import requests

username = "octocat"
url = f"https://api.github.com/users/{username}"

response = requests.get(url, timeout=10)

if response.status_code == 200:
    user = response.json()
    print(f"Login: {user['login']}")
    print(f"Name: {user.get('name', 'N/A')}")
    print(f"Public repos: {user['public_repos']}")
elif response.status_code == 404:
    print(f"User '{username}' not found.")
else:
    print(f"Unexpected status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
```

The script checks `response.status_code` before calling `.json()`. If the status is `404`, it prints a clear message instead of crashing on invalid JSON. The `else` branch catches any other unexpected status and prints a truncated response body so you can debug the issue.

### Example 2: Using `raise_for_status()` with exception handling

This script wraps the same request in a `try/except` block, using `raise_for_status()` to convert error codes into exceptions.

```python
import logging
import requests

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

url = "https://api.github.com/users/octocat"

try:
    response = requests.get(url, timeout=10)
    logging.debug("GET %s → %d", url, response.status_code)
    response.raise_for_status()
    user = response.json()
    logging.info("Fetched user: %s", user["login"])
    print(f"Login: {user['login']}")
    print(f"Public repos: {user['public_repos']}")
except requests.exceptions.HTTPError as exc:
    logging.error("HTTP error %d for %s", exc.response.status_code, url)
    logging.error("Body: %s", exc.response.text[:300])
except requests.exceptions.ConnectionError:
    logging.error("Could not connect to %s", url)
except requests.exceptions.Timeout:
    logging.error("Request to %s timed out", url)
except requests.exceptions.RequestException as exc:
    logging.error("Unexpected error: %s", exc)
```

Every branch produces a clear log message describing what went wrong and where. The `logging.debug()` call after the request records the status code regardless of whether it's a success or failure — if `raise_for_status()` raises an exception, the debug line has already executed, so the log still shows what status code the server returned.

### Example 3: A reusable request function

This script defines a wrapper function and uses it to make two different API calls.

```python
import logging
import requests

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def api_request(method, url, **kwargs):
    """Make an HTTP request with standard logging and error handling."""
    kwargs.setdefault("timeout", 10)
    logging.debug("%s %s", method.upper(), url)

    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        logging.debug("Response: %d", response.status_code)
        return response
    except requests.exceptions.HTTPError as exc:
        logging.error(
            "HTTP %d: %s", exc.response.status_code, exc.response.text[:300]
        )
        return None
    except requests.exceptions.RequestException as exc:
        logging.error("Request failed: %s", exc)
        return None


# --- Use the wrapper ---

# Fetch a valid user
response = api_request("get", "https://api.github.com/users/octocat")
if response is not None:
    user = response.json()
    print(f"User: {user['login']} — {user['public_repos']} public repos")

# Fetch a nonexistent user (will log an HTTP 404 error)
response = api_request("get", "https://api.github.com/users/this-user-does-not-exist-xyz")
if response is not None:
    user = response.json()
    print(f"User: {user['login']}")
else:
    print("Could not fetch the second user. Check the log for details.")
```

The `api_request` function handles all the error logic. The calling code only needs to check whether the return value is `None`. This pattern keeps the main script clean and puts all error handling in one place.

The function uses `**kwargs` to pass through any extra arguments (like `headers=`, `json=`, `params=`) to `requests.request()` without listing them individually. You saw `**kwargs` in functions from earlier lessons — here it's doing practical work, forwarding whatever the caller provides.

---

## Quick Reference

```python
# Check status code before parsing the response body
if response.status_code == 200:
    data = response.json()

# Raise an exception automatically for 4xx/5xx status codes
response.raise_for_status()

# Catch an HTTP error and inspect the failed response
except requests.exceptions.HTTPError as exc:
    print(exc.response.status_code)
    print(exc.response.text[:300])

# Catch a connection error (server unreachable)
except requests.exceptions.ConnectionError:
    print("Could not connect")

# Catch a timeout (server didn't respond in time)
except requests.exceptions.Timeout:
    print("Request timed out")

# Catch any request-related exception (parent class)
except requests.exceptions.RequestException as exc:
    print(f"Error: {exc}")

# Set a timeout on every request (seconds)
response = requests.get(url, timeout=10)

# Set separate connect and read timeouts
response = requests.get(url, timeout=(5, 15))

# Log the request method, URL, and status code
logging.debug("GET %s → %d", url, response.status_code)

# Log the response body on errors (truncated)
logging.error("Body: %s", response.text[:500])

# Use requests.request() for a method-agnostic call
response = requests.request("get", url, timeout=10)

# Set a default value in kwargs without overriding the caller
kwargs.setdefault("timeout", 10)
```

---

## Exercise

### API Response Handler Script

Write a script called `api_checker.py` that accepts command-line arguments and makes API requests with full error handling and logging.

**Requirements:**

1. Use `argparse` to accept the following arguments:
    
    - A required positional argument: the GitHub username to look up.
    - An optional `--output` flag that accepts a file path. If provided, write the results to that file instead of printing to stdout.
    - An optional `--verbose` flag (no value, just a flag). If present, set the logging level to `DEBUG`. If absent, set it to `WARNING`.
2. Load a GitHub token from the environment variable `GITHUB_TOKEN` using `os.getenv()`. If the variable is not set, log a warning that requests will be unauthenticated (do not exit — unauthenticated requests to the GitHub API still work, just with lower rate limits).
    
3. Define a function called `api_request` that:
    
    - Accepts a URL and an optional `headers` dictionary (with a default of `None`).
    - Sets a timeout of 10 seconds.
    - Logs the URL at the `DEBUG` level before making the request.
    - Calls `requests.get()` and then `raise_for_status()`.
    - On success, logs the status code at `DEBUG` and returns the response.
    - Catches `HTTPError`, `ConnectionError`, `Timeout`, and `RequestException` separately, logs an appropriate error message for each, and returns `None`.
4. Use `api_request` to make two requests:
    
    - `https://api.github.com/users/{username}` — fetch the user's profile.
    - `https://api.github.com/users/{username}/repos?per_page=5&sort=updated` — fetch their five most recently updated repositories.
5. If either request returns `None`, print an error message and exit without processing further.
    
6. Build a report as a list of strings, containing:
    
    - The user's `login`, `name` (or `"N/A"` if `null`), and `public_repos` count.
    - A blank line.
    - A line reading `Recent repositories:`.
    - For each repository: `- {repo_name}: {description}` (use `"No description"` if the description is `null`).
7. If `--output` was provided, write the report lines to that file (one line per entry). If not, print them to stdout. Log an `INFO` message indicating where the output went.
    

**Test it using these invocations:**

```
python3 api_checker.py octocat --verbose
python3 api_checker.py octocat --output octocat_report.txt --verbose
python3 api_checker.py nonexistent-user-xyz-12345 --verbose
```

**Expected output for `python3 api_checker.py octocat --verbose`:**

The exact `DEBUG` log lines will vary (they include timestamps, URLs, and status codes), but the printed report should match this structure:

```
Login: octocat
Name: The Octocat
Public repos: 8

Recent repositories:
  - test-repo1: No description
  - boysenern: Testing
  - git-consortium: This repo is for testing
  - hello-worId: My first repository on GitHub!
  - Spoon-Knife: This repo is for demonstration purposes.
```

> [!note] The exact repository names, descriptions, and counts may differ because the `octocat` account's repositories can change over time. What matters is that the structure matches: user info on top, a blank line, then an indented list of repos with descriptions.

**Expected output for `python3 api_checker.py nonexistent-user-xyz-12345 --verbose`:**

```
DEBUG: https://api.github.com/users/nonexistent-user-xyz-12345
ERROR: HTTP 404: {"message":"Not Found", ...}
Error: Could not fetch user profile. Check the log for details.
```

The `DEBUG` and `ERROR` lines come from your logging calls. The final line is your script's own printed message.

---

## Audit

|Requirement|Operations Used|Introduced In|
|---|---|---|
|`argparse` with positional arg, `--output`, `--verbose`|`argparse.ArgumentParser`, `add_argument`, `parse_args`|Lesson 30|
|`os.getenv()` for token loading|`os.getenv`|Lesson 31|
|`logging.basicConfig()` with dynamic level|`logging` module, `logging.basicConfig`, `logging.DEBUG`, `logging.WARNING`|Lesson 21|
|`logging.debug()`, `logging.error()`, `logging.info()`, `logging.warning()`|`logging` log-level methods|Lesson 21|
|`requests.get()` with `timeout` and `headers`|`requests.get`, `timeout` param, `headers` param|Lessons 37–38|
|`response.raise_for_status()`|`raise_for_status()`|Lesson 39 (this lesson)|
|`requests.exceptions.HTTPError`, `ConnectionError`, `Timeout`, `RequestException`|Exception hierarchy and `except ... as exc`|Lesson 39 (this lesson), `try/except` from Lesson 19|
|`exc.response.status_code`, `exc.response.text`|Accessing response from exception object|Lesson 39 (this lesson)|
|`response.json()` → dict access with `[]` and `.get()`|Dict access, `.get()` with default|Lessons 11–12, JSON from Lesson 28|
|Defining a function with default parameter (`headers=None`)|`def`, default parameters, `None`|Lessons 15–16|
|Building a list of strings, iterating, joining|Lists, `for` loops, `append`|Lessons 7, 9|
|Writing to a file with `open()` and `with`|File I/O, context managers|Lesson 22|
|`f`-strings for formatted output|f-strings|Lesson 6|
|`if`/`else` conditionals|Conditionals|Lesson 10|
|`import requests`, `import os`, `import logging`, `import argparse`|Module imports|Lesson 17|

All operations are covered by the current lesson or prior lessons. No future-lesson dependencies.