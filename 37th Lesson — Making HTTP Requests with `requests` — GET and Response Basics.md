# Lesson 37: Making HTTP Requests with `requests` — GET and Response Basics

## Terminology and Theory

In Lesson 35 you learned the structure of HTTP: requests go out, responses come back, status codes tell you what happened, and the body carries the data. In Lesson 36 you used `curl` to make raw requests and compared them to SDK abstractions. Now you're going to do the same thing from inside Python using the `requests` library.

**`requests` library** — A third-party Python package (`pip install requests`) that lets you make HTTP requests from Python code. It is the most widely used HTTP client library in the Python ecosystem. When SDK documentation tells developers to "call the API directly," the examples almost always use `requests`.

**`Response` object** — The object that `requests.get()` (and every other `requests` function) returns. It holds everything the server sent back: the status code, the headers, and the body. You interact with it through attributes and methods rather than parsing raw text yourself.

**Query parameters** — Key-value pairs appended to a URL after a `?` character that modify what the server returns. For example, in `https://api.github.com/search/repositories?q=python&per_page=5`, `q` and `per_page` are query parameters. The `requests` library lets you pass these as a dictionary via the `params=` argument instead of manually constructing the URL string.

**`response.json()`** — A method on the `Response` object that parses the response body as JSON and returns a Python dict or list. This is the bridge between the HTTP world (where everything is text on the wire) and the Python world (where you work with dicts and lists). It does the same thing as calling `json.loads(response.text)`, but it's shorter and handles encoding detection for you.

**`response.headers`** — A dictionary-like object containing the HTTP response headers. Headers carry metadata about the response: content type, rate-limit information, caching directives, and more. You access individual headers by key, and the keys are case-insensitive.

**Timeout** — The maximum number of seconds `requests` will wait for a server before giving up. There is no default: a request without a timeout can hang indefinitely if the server never answers. You set one with the `timeout=` argument on every request function.

> [!note]  
> The `requests` library is not part of the Python standard library. You must install it with `pip install requests` inside your virtual environment, the same way you installed `mdformat` in Lesson 34.

## Syntax

### Installing `requests`

```bash
pip install requests
```

### Making a GET request

```python
import requests

response = requests.get("https://httpbin.org/get")
```

`requests.get()` takes a URL string as its first argument. It sends an HTTP GET request to that URL and returns a `Response` object. The function blocks until the server responds — your script waits at this line until the response arrives.

### Reading the response status code

```python
print(response.status_code)  # 200
```

The `.status_code` attribute is an integer. You already know from Lesson 35 what the common codes mean: `200` is success, `404` is not found, `401` is unauthorized, and so on.

### Checking success without comparing numbers

```python
print(response.ok)      # True when the status code is below 400
print(response.reason)  # "OK", "Not Found", "Forbidden", and so on

if response:
    print("The request succeeded")
```

The `.ok` attribute is a boolean that is `True` for any status code below `400`. The `.reason` attribute is the short text phrase the server sends alongside the numeric code. A `Response` object is itself truthy when `.ok` is `True`, so `if response:` reads as "if the request succeeded" (Lesson 14). Use `.ok` when you only care whether the request worked, and compare `.status_code` directly when you need to tell `403` apart from `404`.

### Reading the response body as text

```python
print(response.text)
```

The `.text` attribute is a string containing the entire response body. For JSON APIs, this is the raw JSON string before parsing.

### Reading the body as bytes, and controlling encoding

```python
print(response.content)   # b'{"origin": "203.0.113.42"}'
print(response.encoding)  # "utf-8"
response.encoding = "utf-8"
```

The `.content` attribute is the body as raw bytes, and `.text` is `.content` decoded into a string using `.encoding`. The `requests` library derives the encoding from the response headers; when a server does not declare one, the guess can be wrong and `.text` comes back with mangled characters. Assigning to `.encoding` before you read `.text` corrects that. For JSON APIs you rarely need `.content`, but you do need it whenever the body is not text at all — an image, a PDF, or a zip archive.

### Parsing the response body as JSON

```python
data = response.json()
```

The `.json()` method parses the body and returns a Python dict or list. After this call, you work with `data` exactly the way you work with any dict — using key access, `.get()`, loops over `.items()`, and so on.

> [!warning]  
> Calling `.json()` on a response whose body is not valid JSON raises `requests.exceptions.JSONDecodeError`, which is a subclass of `ValueError`. If you are not certain the response is JSON, check `response.headers.get("Content-Type")` first or wrap the call in `try/except` (Lesson 19).

```python
try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    data = None
    print("Response body was not JSON")
```

### Reading response headers

```python
content_type = response.headers["Content-Type"]
```

Headers are accessed by key. The keys are case-insensitive, so `response.headers["content-type"]` and `response.headers["Content-Type"]` return the same value.

### Listing every header the server sent

```python
for name, value in response.headers.items():
    print(f"{name}: {value}")
```

The `response.headers` object supports `.items()` the same way a dict does (Lesson 12). Dumping all of the headers is how you find out what an API actually returns — rate-limit counters, request IDs, and caching directives are frequently undocumented, and you cannot write about them until you have seen them.

### Passing query parameters

```python
params = {"q": "python", "per_page": "5"}
response = requests.get("https://api.github.com/search/repositories", params=params)
```

The `params=` keyword argument accepts a dictionary. `requests` encodes the keys and values and appends them to the URL as a properly formatted query string. The resulting URL is `https://api.github.com/search/repositories?q=python&per_page=5`. You can verify this by printing `response.url` after the request.

> [!tip]  
> Always use `params=` instead of manually gluing `?key=value` strings onto URLs. The `requests` library handles URL encoding for you, which prevents bugs when values contain special characters like spaces or ampersands.

### Parameter values that are lists or `None`

```python
params = {"tag": ["docs", "python"], "sort": None}
response = requests.get("https://example.com/api", params=params)
```

A list value produces a repeated key — `?tag=docs&tag=python` — which is how many APIs accept several values for one filter. A value of `None` is dropped from the query string entirely, so you can build a single params dict that contains optional entries instead of assembling a different dict for every combination of options.

### Setting a timeout

```python
response = requests.get("https://httpbin.org/get", timeout=10)
```

The `timeout=` argument sets, in seconds, how long `requests` will wait for the server. Without it there is no limit, and a script that hits an unresponsive server hangs until you kill it. When the limit is exceeded, `requests` raises `requests.exceptions.Timeout` rather than returning a `Response`, so a timeout has to be caught rather than checked:

```python
try:
    response = requests.get("https://httpbin.org/delay/10", timeout=3)
except requests.exceptions.Timeout:
    print("The request timed out")
```

> [!tip]  
> Put a `timeout=` on every request you write, including throwaway scripts. Lesson 39 covers error handling systematically, but the timeout habit is worth forming now.

### Measuring how long a request took

```python
print(response.elapsed.total_seconds())  # 0.284
```

The `.elapsed` attribute holds the time between sending the request and finishing the parsing of the response headers. It is a `timedelta` object, and `.total_seconds()` converts it to a float. This is useful when you are documenting an API and want to say something concrete about which endpoints are slow.

### Checking before parsing

A reliable pattern is to check the status code before you attempt to parse the body:

```python
if response.status_code == 200:
    data = response.json()
else:
    print(f"Request failed: {response.status_code}")
```

This prevents your script from crashing on an error response that does not contain the JSON structure you expect.

## Worked Examples

### Example 1: Fetching your public IP address

This script makes a GET request to httpbin.org, a free service that echoes back information about your request. The `/ip` endpoint returns your public IP address as JSON.

```python
import requests

response = requests.get("https://httpbin.org/ip", timeout=10)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers['Content-Type']}")

if response.status_code == 200:
    data = response.json()
    print(f"Your public IP: {data['origin']}")
else:
    print(f"Request failed with status {response.status_code}")
```

Expected output (your IP will differ):

```
Status: 200
Content-Type: application/json
Your public IP: 203.0.113.42
```

What's happening here: `requests.get()` sends a GET request to the URL, waiting no longer than ten seconds for an answer. The response comes back with status `200`, and the body is a JSON object with a single key `origin` whose value is your IP address. After checking the status code, you call `.json()` to parse it into a dict and access the `origin` key the same way you have been accessing dict values since Lesson 11.

### Example 2: Searching GitHub repositories with query parameters

This script searches GitHub's public API for repositories matching a search term. It demonstrates passing query parameters as a dictionary and navigating the nested JSON response.

```python
import requests

params = {
    "q": "mkdocs",
    "sort": "stars",
    "per_page": "3"
}

response = requests.get(
    "https://api.github.com/search/repositories",
    params=params,
    timeout=10
)

print(f"Status: {response.status_code}")
print(f"Requested URL: {response.url}")

if response.status_code == 200:
    data = response.json()
    print(f"Total results: {data['total_count']}")
    print()
    for repo in data["items"]:
        name = repo["full_name"]
        stars = repo["stargazers_count"]
        description = repo.get("description") or "No description"
        print(f"  {name} ({stars} stars)")
        print(f"    {description}")
        print()
else:
    print(f"Request failed: {response.status_code}")
```

Expected output (star counts will change over time):

```
Status: 200
Requested URL: https://api.github.com/search/repositories?q=mkdocs&sort=stars&per_page=3
Total results: 4523

  mkdocs/mkdocs (20145 stars)
    Project documentation with Markdown.

  squidfunk/mkdocs-material (22300 stars)
    Documentation that simply works

  jimporter/mike (578 stars)
    Manage multiple versions of your MkDocs-powered documentation via Git
```

What's happening here: the `params` dictionary is encoded into the URL's query string automatically. The GitHub API returns a JSON object where `total_count` is an integer and `items` is a list of repository objects. Each repository object is a dict, so you access fields like `full_name`, `stargazers_count`, and `description` with key access. The `repo.get("description") or "No description"` pattern supplies a fallback for repositories without a description. Note that a default value on `.get()` alone would not work here: the key is present in the JSON, but its value is `null`, which `.json()` converts into Python's `None`. Because `.get()` only returns its default when the key is _missing_, you need the truthiness check from Lesson 14 to catch a key that exists with an empty value.

> [!note]  
> The GitHub API allows up to 60 requests per hour for unauthenticated requests. If you get status `403` while experimenting, wait a few minutes. Lesson 38 will cover authentication headers that raise this limit.

### Example 3: Inspecting response headers for API metadata

HTTP headers carry metadata you will need to document when writing about APIs. This script shows how to read rate-limit headers from the GitHub API, which tell users how many requests they have left.

```python
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

response = requests.get("https://api.github.com/rate_limit", timeout=10)

logging.info(f"Status: {response.status_code}")
logging.info(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")

rate_limit = response.headers.get("X-RateLimit-Limit", "not provided")
rate_remaining = response.headers.get("X-RateLimit-Remaining", "not provided")

logging.info(f"Rate limit: {rate_limit}")
logging.info(f"Remaining: {rate_remaining}")

if response.status_code == 200:
    data = response.json()
    core = data["resources"]["core"]
    print(f"Core API limit: {core['limit']}")
    print(f"Core API remaining: {core['remaining']}")
else:
    print(f"Request failed: {response.status_code}")
```

Expected output:

```
INFO: Status: 200
INFO: Content-Type: application/json; charset=utf-8
INFO: Rate limit: 60
INFO: Remaining: 58
Core API limit: 60
Core API remaining: 58
```

What's happening here: the script uses `logging` (Lesson 21) for diagnostic output and `print()` for the final report. The `response.headers` object works like a dict, so `.get()` with a default value prevents a `KeyError` if a header is missing. The body is a nested JSON structure — `data["resources"]["core"]` navigates two levels of dict nesting (Lesson 12) to reach the rate-limit details.

## Quick Reference

```python
# Install requests in your virtual environment
# pip install requests

# Import the library
import requests

# Make a basic GET request
response = requests.get("https://httpbin.org/get")

# Set a timeout in seconds so a silent server cannot hang your script
response = requests.get("https://httpbin.org/get", timeout=10)

# Catch a request that never completes
try:
    response = requests.get("https://httpbin.org/delay/10", timeout=3)
except requests.exceptions.Timeout:
    print("The request timed out")

# Read the HTTP status code (int)
print(response.status_code)

# Read the reason phrase that accompanies the status code
print(response.reason)

# Check for success without comparing numbers (True when status is below 400)
print(response.ok)

# A Response is truthy when .ok is True, so it can be tested directly
if response:
    print("The request succeeded")

# Read the response body as a decoded string
print(response.text)

# Read the response body as raw bytes (images, PDFs, archives)
print(response.content)

# Inspect or override the encoding used to decode .content into .text
print(response.encoding)
response.encoding = "utf-8"

# Parse the response body as JSON into a dict or list
data = response.json()

# Parse defensively when the body might not be JSON
try:
    data = response.json()
except requests.exceptions.JSONDecodeError:
    data = None

# Read a response header (case-insensitive key access)
content_type = response.headers["Content-Type"]

# Read a header safely with a default value
server = response.headers.get("Server", "unknown")

# Iterate over every header the server sent
for name, value in response.headers.items():
    print(f"{name}: {value}")

# Pass query parameters as a dictionary
params = {"q": "search term", "page": "1"}
response = requests.get("https://example.com/api", params=params)

# Repeat a parameter by giving it a list of values (?tag=docs&tag=python)
params = {"tag": ["docs", "python"]}
response = requests.get("https://example.com/api", params=params)

# A parameter whose value is None is left out of the query string
params = {"q": "python", "sort": None}
response = requests.get("https://example.com/api", params=params)

# Inspect the final URL that requests built (useful for debugging)
print(response.url)

# Measure the round trip as a timedelta, then convert it to seconds
print(response.elapsed.total_seconds())

# Check the status code before parsing
if response.status_code == 200:
    data = response.json()
else:
    print(f"Error: {response.status_code}")

# Supply a fallback when a JSON key exists but its value is null
description = data.get("description") or "No description provided"
```

## Exercise

### API Explorer Report

Write a script called `api_explorer.py` that accepts a search term as a positional command-line argument using `argparse`. The script must:

1. Use `requests.get()` to search the GitHub repository search API at `https://api.github.com/search/repositories`, passing the user's search term as the `q` parameter and limiting results to 5 items using the `per_page` parameter.
2. Check the response status code. If the request failed, log an error message using `logging` that includes the status code and exit the script.
3. If the request succeeded, parse the JSON response and print a report to stdout with the following format:

```
Search results for "MkDocs" (5 of 4523):
==========

1. mkdocs/mkdocs
   Stars: 20145
   URL: https://github.com/mkdocs/mkdocs
   Description: Project documentation with Markdown.

2. squidfunk/mkdocs-material
   Stars: 22300
   URL: https://github.com/squidfunk/mkdocs-material
   Description: Documentation that simply works

3. jimporter/mike
   Stars: 578
   URL: https://github.com/jimporter/mike
   Description: Manage multiple versions of your MkDocs-powered documentation via Git

4. mkdocs/catalog
   Stars: 950
   URL: https://github.com/mkdocs/catalog
   Description: No description provided

5. lukasgeiter/mkdocs-awesome-pages-plugin
   Stars: 512
   URL: https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin
   Description: An MkDocs plugin that simplifies configuring page titles and their order

==========
Rate limit remaining: 58/60
```

Requirements:

- The report header must include the search term (from the command-line argument), the number of items displayed, and the `total_count` from the API response.
- Each result must show the repo's `full_name`, `stargazers_count`, `html_url`, and `description`. If `description` is `None`, print `No description provided` instead.
- After the results, print the rate-limit information from the `X-RateLimit-Remaining` and `X-RateLimit-Limit` response headers.
- Use `logging` at the `INFO` level to log the request URL and the status code before printing the report. Set the logging format to `%(levelname)s: %(message)s`.
- Pass a `timeout=` argument to the request.

Example invocation:

```bash
python api_explorer.py "MkDocs"
```

Example output (star counts and totals will vary since this hits a live API):

```
INFO: Requesting: https://api.github.com/search/repositories?q=MkDocs&per_page=5
INFO: Response status: 200
Search results for "MkDocs" (5 of 4523):
==========

1. mkdocs/mkdocs
   Stars: 20145
   URL: https://github.com/mkdocs/mkdocs
   Description: Project documentation with Markdown.

2. squidfunk/mkdocs-material
   Stars: 22300
   URL: https://github.com/squidfunk/mkdocs-material
   Description: Documentation that simply works

3. jimporter/mike
   Stars: 578
   URL: https://github.com/jimporter/mike
   Description: Manage multiple versions of your MkDocs-powered documentation via Git

4. mkdocs/catalog
   Stars: 950
   URL: https://github.com/mkdocs/catalog
   Description: No description provided

5. lukasgeiter/mkdocs-awesome-pages-plugin
   Stars: 512
   URL: https://github.com/lukasgeiter/mkdocs-awesome-pages-plugin
   Description: An MkDocs plugin that simplifies configuring page titles and their order

==========
Rate limit remaining: 58/60
```

> [!note]  
> Because this exercise hits a live API, your exact numbers will differ from the example. The structure and format of the output are what matter. If you get a `403` status code, you have hit the unauthenticated rate limit — wait a minute and try again.

---

## Audit

|Operation / Concept|Required By|Introduced In|
|---|---|---|
|`import requests`|Lesson body, exercise|Lesson 37 (current)|
|`requests.get()`|Lesson body, exercise|Lesson 37 (current)|
|`response.status_code`|Lesson body, exercise|Lesson 37 (current)|
|`response.json()`|Lesson body, exercise|Lesson 37 (current)|
|`response.headers.get()`|Lesson body, exercise|Lesson 37 (current)|
|`response.url`|Exercise (logging the URL)|Lesson 37 (current)|
|`params=` keyword argument|Lesson body, exercise|Lesson 37 (current)|
|`timeout=` keyword argument|Lesson body, exercise|Lesson 37 (current)|
|`response.ok`, `response.reason`, Response truthiness|Lesson body|Lesson 37 (current)|
|`response.content`, `response.encoding`|Lesson body|Lesson 37 (current)|
|`response.headers.items()`|Lesson body|Lesson 37 (current)|
|`response.elapsed.total_seconds()`|Lesson body|Lesson 37 (current)|
|`requests.exceptions.Timeout`, `requests.exceptions.JSONDecodeError`|Lesson body|Lesson 37 (current)|
|`try/except` around a request|Lesson body|Lesson 19|
|Truthiness fallback (`x or "default"`)|Lesson body, exercise (null `description`)|Lesson 14|
|`argparse` (positional argument)|Exercise|Lesson 30|
|`logging.basicConfig()`, `logging.info()`, `logging.error()`|Exercise|Lesson 21|
|`for` loop over a list|Exercise (iterating `items`)|Lesson 9|
|`if/else` conditional|Exercise (status code check)|Lesson 10|
|Dict key access, `.get()` with default|Exercise (JSON fields, headers)|Lesson 11|
|f-strings|Exercise (formatted output)|Lesson 6|
|`print()`|Exercise|Lesson 1|
|`enumerate()`|Exercise (numbering results)|Not formally taught; optional (see note below)|
|`pip install` in a venv|Exercise setup|Lesson 32|

> [!note]  
> `enumerate()` has not been formally taught as a standalone topic, but it follows the same `for x in iterable` pattern from Lesson 9 and is a standard built-in. The exercise can be completed without it by using a counter variable incremented inside the loop (a pattern available since Lessons 2 and 9). The expected output uses sequential numbering, which the learner can achieve either way.

All operations required by the exercise have been introduced in the current lesson or in prior lessons. No future-lesson dependencies exist.