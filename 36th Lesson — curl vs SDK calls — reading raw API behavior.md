# Lesson 36: curl vs SDK calls — reading raw API behavior

## Terminology and Theory

**curl** is a command-line tool for making HTTP requests. When API documentation says "try this endpoint," the example is almost always a `curl` command. As a technical writer documenting SDKs, you need to read `curl` examples fluently — not because you will write `curl` all day, but because `curl` shows you the raw HTTP conversation that an SDK hides behind a method call. Understanding that raw conversation is how you explain what an SDK method actually does.

**A curl command** maps directly onto the HTTP concepts you learned in Lesson 35. A `curl` invocation specifies a URL (the endpoint), an HTTP method, headers, and optionally a body. The output is the raw response: status line, headers, and a JSON body. Every piece of this was covered in Lesson 35 — `curl` is just the tool that lets you perform those requests from a terminal.

**An SDK call** wraps that same HTTP conversation inside a method. When you write `repo.get_issues()` in PyGithub, the SDK is building an HTTP GET request, attaching your authentication token as a header, sending it to `https://api.github.com/repos/owner/name/issues`, receiving the JSON response, checking the status code, and converting the JSON into Python objects. The SDK does all of this in one line. That is convenient, but it hides information you need to understand in order to document the SDK accurately.

**What SDKs preserve vs. what they hide:**

The SDK **preserves** the data — the fields in the JSON response become attributes on objects. If the API returns `"title": "Fix login bug"`, the SDK gives you `issue.title` with the value `"Fix login bug"`.

The SDK **hides** the mechanics: the URL that was called, the HTTP method used, the headers sent (including authentication), the status code of the response, pagination details (how the API signals "there are more results"), and rate-limit headers. When you document an SDK, you often need to explain these hidden details so users understand what is happening and what can go wrong.

**Authentication in curl** is done with headers. The most common pattern for token-based APIs is the `Authorization` header with a Bearer token:

```
curl -H "Authorization: Bearer ghp_abc123..." https://api.github.com/user
```

The `-H` flag adds a header to the request. The SDK equivalent loads this token once during setup and attaches it to every request automatically. As a documentor, you need to explain both: what the user provides (a token) and what the SDK does with it (sends it as a Bearer header on every request).

**Pagination in REST APIs** is how an API delivers large result sets in chunks rather than all at once. A common pattern is the `Link` header, which contains URLs for the next, previous, first, and last pages of results. Another common pattern is query parameters like `?page=2&per_page=30`. The SDK handles this transparently — when you loop over `repo.get_issues()`, the SDK follows those `Link` headers behind the scenes. But if you are reading raw API output or writing documentation, you need to recognize these pagination signals.

> [!note] This lesson does not make live HTTP requests. You will parse curl output that is provided as strings. Lesson 37 introduces the `requests` library for making actual HTTP calls from Python.

## Syntax Section

### Reading a curl command

A typical `curl` command has this structure:

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/octocat/Hello-World/issues?state=open&per_page=5"
```

Breaking this down piece by piece:

- `curl` — the command itself.
- `-X GET` — the HTTP method. `-X` stands for "request method." If omitted, `curl` defaults to GET.
- `-H "Header-Name: value"` — adds a request header. You can use `-H` multiple times for multiple headers.
- The URL in quotes — the endpoint, including query parameters after the `?`.

The query string `?state=open&per_page=5` contains two parameters separated by `&`. This is how the client tells the API "only return open issues, five per page."

### Reading curl output with verbose mode

When `curl` is run with the `-i` flag (include response headers) or `-v` flag (verbose), you see the full HTTP conversation. The `-i` flag is more common in documentation examples because it shows response headers alongside the body:

```
HTTP/2 200
content-type: application/json; charset=utf-8
link: <https://api.github.com/repos/octocat/Hello-World/issues?state=open&per_page=5&page=2>; rel="next", <https://api.github.com/repos/octocat/Hello-World/issues?state=open&per_page=5&page=7>; rel="last"
x-ratelimit-limit: 5000
x-ratelimit-remaining: 4990
x-ratelimit-reset: 1716700000

[{"id":1,"title":"Found a bug", ...}, ...]
```

The blank line separates headers from body. The `link` header contains pagination URLs. The `x-ratelimit-*` headers tell you how many requests you can make before the API starts rejecting you. None of this appears when you use an SDK — the SDK reads it internally.

### Parsing curl JSON output in Python

Since `curl` output bodies are JSON, you parse them with the `json` module you already know:

```python
import json

curl_output = '{"login": "octocat", "id": 1, "type": "User"}'
data = json.loads(curl_output)
print(data["login"])
```

For multi-object responses (like a list of issues), the JSON is an array:

```python
import json

curl_output = '[{"id": 1, "title": "Bug"}, {"id": 2, "title": "Feature request"}]'
issues = json.loads(curl_output)
for issue in issues:
    print(f"#{issue['id']}: {issue['title']}")
```

### Parsing the Link header for pagination

The `Link` header is a string with a specific format. Each link is a URL in angle brackets followed by `; rel="relationship"`. Multiple links are separated by commas. You can extract these with string methods and regex you already know:

```python
import re

link_header = '<https://api.github.com/repos/octocat/Hello-World/issues?page=2>; rel="next", <https://api.github.com/repos/octocat/Hello-World/issues?page=5>; rel="last"'

links = re.findall(r'<([^>]+)>;\s*rel="([^"]+)"', link_header)
for url, rel in links:
    print(f"{rel}: {url}")
```

The regex `<([^>]+)>;\s*rel="([^"]+)"` captures two groups: the URL inside angle brackets and the relationship name inside quotes. The `findall` call returns a list of tuples, which you unpack in the loop — all patterns from prior lessons.

## Worked Examples

### Example 1: Parsing a curl user response and producing a doc summary

Imagine you ran `curl -H "Authorization: Bearer TOKEN" https://api.github.com/user` and captured the JSON body. Your task is to parse it and produce a documentation-style summary of what the endpoint returns.

```python
import json

# Simulated curl output — the JSON body from GET /user
curl_body = '''{
    "login": "octocat",
    "id": 1,
    "type": "User",
    "name": "The Octocat",
    "company": "GitHub",
    "blog": "https://github.blog",
    "location": "San Francisco",
    "email": null,
    "bio": "I love coding",
    "public_repos": 8,
    "followers": 12400,
    "following": 9
}'''

user = json.loads(curl_body)

print("## GET /user — Response Fields\n")
print(f"The authenticated user endpoint returns a JSON object with "
      f"{len(user)} fields.\n")
print("| Field | Type | Example Value |")
print("|---|---|---|")
for key, value in user.items():
    if value is None:
        val_type = "null"
        display = "`null`"
    elif isinstance(value, int):
        val_type = "integer"
        display = str(value)
    elif isinstance(value, str):
        val_type = "string"
        display = f'`"{value}"`'
    else:
        val_type = type(value).__name__
        display = str(value)
    print(f"| `{key}` | {val_type} | {display} |")
```

Output:

```
## GET /user — Response Fields

The authenticated user endpoint returns a JSON object with 12 fields.

| Field | Type | Example Value |
|---|---|---|
| `login` | string | `"octocat"` |
| `id` | integer | 1 |
| `type` | string | `"User"` |
| `name` | string | `"The Octocat"` |
| `company` | string | `"GitHub"` |
| `blog` | string | `"https://github.blog"` |
| `location` | string | `"San Francisco"` |
| `email` | null | `null` |
| `bio` | string | `"I love coding"` |
| `public_repos` | integer | 8 |
| `followers` | integer | 12400 |
| `following` | integer | 9 |
```

This script does what a technical writer does: it takes raw API output and turns it into structured documentation. Notice how it handles `None` (JSON `null`) separately — this matters in documentation because a nullable field needs to be called out.

> [!tip] The `isinstance()` function checks whether a value is a particular type. You have not had a formal lesson on `isinstance()` yet, but the pattern `isinstance(value, int)` reads naturally as "is this value an integer?" You will encounter `isinstance()` frequently when working with SDK objects.

### Example 2: Comparing a curl command to its SDK equivalent

This example places a raw curl command side by side with what the equivalent SDK call would look like, and then parses the curl output to show what the SDK would give you versus what it would hide.

```python
import json

# The curl command (as documentation)
curl_command = '''curl -X GET \\
  -H "Authorization: Bearer ghp_abc123" \\
  -H "Accept: application/vnd.github+json" \\
  "https://api.github.com/repos/octocat/Hello-World/issues?state=open&per_page=2"'''

# Simulated response headers
response_headers = {
    "status": "200 OK",
    "content-type": "application/json; charset=utf-8",
    "x-ratelimit-limit": "5000",
    "x-ratelimit-remaining": "4985",
    "x-ratelimit-reset": "1716700000",
    "link": '<https://api.github.com/repos/octocat/Hello-World/issues?state=open&per_page=2&page=2>; rel="next", <https://api.github.com/repos/octocat/Hello-World/issues?state=open&per_page=2&page=4>; rel="last"'
}

# Simulated response body
response_body = '''[
    {"number": 42, "title": "Login fails on Safari", "state": "open",
     "user": {"login": "alice"}, "labels": [{"name": "bug"}]},
    {"number": 38, "title": "Add dark mode", "state": "open",
     "user": {"login": "bob"}, "labels": [{"name": "enhancement"}]}
]'''

issues = json.loads(response_body)

# What the SDK preserves — the data
print("=== What the SDK gives you ===")
for issue in issues:
    labels = ", ".join(label["name"] for label in issue["labels"])
    print(f"  Issue #{issue['number']}: {issue['title']}")
    print(f"    Author: {issue['user']['login']}")
    print(f"    Labels: {labels}")
    print()

# What the SDK hides — the mechanics
print("=== What the SDK hides ===")
print(f"  HTTP method: GET")
print(f"  Endpoint: /repos/octocat/Hello-World/issues")
print(f"  Auth: Bearer token sent in Authorization header")
print(f"  Status code: {response_headers['status']}")
print(f"  Rate limit: {response_headers['x-ratelimit-remaining']} "
      f"of {response_headers['x-ratelimit-limit']} requests remaining")
print(f"  Pagination: Link header present — more pages exist")
```

Output:

```
=== What the SDK gives you ===
  Issue #42: Login fails on Safari
    Author: alice
    Labels: bug

  Issue #38: Add dark mode
    Author: bob
    Labels: enhancement

=== What the SDK hides ===
  HTTP method: GET
  Endpoint: /repos/octocat/Hello-World/issues
  Auth: Bearer token sent in Authorization header
  Status code: 200 OK
  Rate limit: 4985 of 5000 requests remaining
  Pagination: Link header present — more pages exist
```

> [!note] The expression `", ".join(label["name"] for label in issue["labels"])` uses a generator expression inside `.join()`. This is similar to a list comprehension but without the square brackets. It produces items one at a time instead of building a whole list. You can read it the same way: "for each label in the labels list, give me the name." This is a pattern you will see frequently in Python code.

### Example 3: Extracting pagination links from a Link header

This example parses a realistic `Link` header and builds a dictionary mapping relationship names to URLs — a pattern you would use to explain pagination in documentation.

```python
import json
import re

link_header = (
    '<https://api.github.com/repos/octocat/Hello-World/issues?page=2&per_page=5>; rel="next", '
    '<https://api.github.com/repos/octocat/Hello-World/issues?page=1&per_page=5>; rel="prev", '
    '<https://api.github.com/repos/octocat/Hello-World/issues?page=7&per_page=5>; rel="last", '
    '<https://api.github.com/repos/octocat/Hello-World/issues?page=1&per_page=5>; rel="first"'
)

# Parse into a dict of {rel: url}
pagination = {}
matches = re.findall(r'<([^>]+)>;\s*rel="([^"]+)"', link_header)
for url, rel in matches:
    pagination[rel] = url

# Produce a doc-style explanation
print("## Pagination\n")
print(f"This response includes {len(pagination)} pagination links:\n")
for rel, url in pagination.items():
    print(f"- **{rel}**: `{url}`")

print()

if "next" in pagination:
    print("To fetch the next page, send a GET request to the `next` URL.")
    print("Continue following `next` links until the response no longer "
          "includes a `next` link.")
else:
    print("No `next` link is present — this is the last page of results.")

# Extract page numbers to show total extent
if "last" in pagination:
    last_url = pagination["last"]
    page_match = re.search(r'page=(\d+)', last_url)
    if page_match:
        total_pages = page_match.group(1)
        print(f"\nTotal pages available: {total_pages}")
```

Output:

```
## Pagination

This response includes 4 pagination links:

- **next**: `https://api.github.com/repos/octocat/Hello-World/issues?page=2&per_page=5`
- **prev**: `https://api.github.com/repos/octocat/Hello-World/issues?page=1&per_page=5`
- **last**: `https://api.github.com/repos/octocat/Hello-World/issues?page=7&per_page=5`
- **first**: `https://api.github.com/repos/octocat/Hello-World/issues?page=1&per_page=5`

To fetch the next page, send a GET request to the `next` URL.
Continue following `next` links until the response no longer includes a `next` link.

Total pages available: 7
```

This is exactly the kind of output a technical writer produces: take a raw header that most users will never see, and turn it into a clear explanation of how to paginate through results.

## Quick Reference

```python
# Reading a curl command: -X sets the method, -H adds a header, URL comes last
# curl -X GET -H "Authorization: Bearer TOKEN" "https://api.example.com/items"

# The -H flag can appear multiple times for multiple headers
# curl -H "Authorization: Bearer TOKEN" -H "Accept: application/json" URL

# Query parameters appear after ? in the URL, separated by &
# curl "https://api.example.com/items?state=open&per_page=10"

# Parse a JSON response body with json.loads (from Lesson 28)
import json
body = '{"login": "octocat", "id": 1}'
data = json.loads(body)

# Access nested JSON fields with chained key lookups
issue_json = '{"user": {"login": "alice"}, "title": "Bug"}'
issue = json.loads(issue_json)
author = issue["user"]["login"]

# Parse a Link header with re.findall to extract pagination URLs
import re
link = '<https://api.example.com/items?page=2>; rel="next"'
matches = re.findall(r'<([^>]+)>;\s*rel="([^"]+)"', link)

# Build a dict from parsed pagination links using a loop
pagination = {}
for url, rel in matches:
    pagination[rel] = url

# Check whether more pages exist by testing for a "next" key
if "next" in pagination:
    print(f"Next page: {pagination['next']}")

# Extract a page number from a URL using re.search and .group()
page_match = re.search(r'page=(\d+)', pagination.get("last", ""))
if page_match:
    total_pages = page_match.group(1)

# Identify what an SDK hides: method, URL, headers, status, rate limits, pagination
# Identify what an SDK preserves: the data fields from the JSON body

# isinstance() checks the type of a value — useful when JSON has mixed types
value = 42
if isinstance(value, int):
    print("integer")
elif isinstance(value, str):
    print("string")
```

## Exercise

Write a Python script called `api_doc_generator.py` that takes a simulated API response (provided below as a multi-line string in your script) and produces a documentation-style analysis of the endpoint.

Your script must:

1. Accept a single command-line argument using `argparse`: `--verbose`, a flag (no value needed) that controls whether the script prints hidden HTTP details in addition to the data summary.
    
2. Define the following three multi-line strings in your script to simulate a curl response:
    

The endpoint description:

```
GET /repos/{owner}/{repo}/pulls?state=closed&per_page=3
```

The response headers (as a JSON string — not a raw HTTP header block):

```json
{"status": "200 OK", "content-type": "application/json", "x-ratelimit-limit": "5000", "x-ratelimit-remaining": "4200", "x-ratelimit-reset": "1716700000", "link": "<https://api.github.com/repos/octocat/Hello-World/pulls?state=closed&per_page=3&page=2>; rel=\"next\", <https://api.github.com/repos/octocat/Hello-World/pulls?state=closed&per_page=3&page=12>; rel=\"last\""}
```

The response body:

```json
[
    {"number": 101, "title": "Refactor auth module", "state": "closed", "user": {"login": "carol"}, "merged_at": "2025-05-10T14:30:00Z", "labels": [{"name": "refactor"}, {"name": "backend"}]},
    {"number": 98, "title": "Fix typo in README", "state": "closed", "user": {"login": "dave"}, "merged_at": null, "labels": []},
    {"number": 95, "title": "Add rate limit docs", "state": "closed", "user": {"login": "eve"}, "merged_at": "2025-05-08T09:15:00Z", "labels": [{"name": "documentation"}]}
]
```

3. Parse the response body and print a summary of each pull request. For each PR, print the number, title, author, whether it was merged or closed without merging (check whether `merged_at` is `null` or has a value), and the labels (joined with commas, or "none" if the list is empty).
    
4. After the PR list, print a count: how many of the PRs were merged and how many were closed without merging.
    
5. If `--verbose` is provided, also parse the response headers and print: the status code, the rate limit remaining out of the total, and the pagination links with their `rel` values. If `--verbose` is not provided, do not print any header information.
    
6. Use `logging` at the `INFO` level to log when the script starts, when it finishes parsing the body, and when it finishes parsing headers (if `--verbose`). Set the log level to `DEBUG` if `--verbose` is provided, otherwise `INFO`.
    

**Expected output without `--verbose`:**

```
## Closed Pull Requests for octocat/Hello-World

PR #101: Refactor auth module
  Author: carol
  Status: merged (2025-05-10T14:30:00Z)
  Labels: refactor, backend

PR #98: Fix typo in README
  Author: dave
  Status: closed without merge
  Labels: none

PR #95: Add rate limit docs
  Author: eve
  Status: merged (2025-05-08T09:15:00Z)
  Labels: documentation

Summary: 2 merged, 1 closed without merge
```

**Expected output with `--verbose`:**

```
## Closed Pull Requests for octocat/Hello-World

PR #101: Refactor auth module
  Author: carol
  Status: merged (2025-05-10T14:30:00Z)
  Labels: refactor, backend

PR #98: Fix typo in README
  Author: dave
  Status: closed without merge
  Labels: none

PR #95: Add rate limit docs
  Author: eve
  Status: merged (2025-05-08T09:15:00Z)
  Labels: documentation

Summary: 2 merged, 1 closed without merge

## HTTP Details (hidden by SDK)

Status: 200 OK
Rate limit: 4200 of 5000 remaining
Pagination:
  next: https://api.github.com/repos/octocat/Hello-World/pulls?state=closed&per_page=3&page=2
  last: https://api.github.com/repos/octocat/Hello-World/pulls?state=closed&per_page=3&page=12
```

## Audit

|Requirement|Introduced In|
|---|---|
|`print()`, f-strings|Lessons 1, 6|
|String methods (`.join()`)|Lesson 5|
|Lists, indexing|Lesson 7|
|`for` loops|Lesson 9|
|Conditionals (`if/elif/else`)|Lesson 10|
|Dict access, `.items()`, `.get()`|Lessons 11, 12|
|Tuple unpacking in loops|Lesson 13|
|Truthiness checks (empty list as falsy)|Lesson 14|
|Functions (`def`)|Lesson 15|
|`import`|Lesson 17|
|`json.loads()`|Lesson 28|
|`argparse` (`--verbose` flag)|Lesson 30|
|`logging`, `logging.basicConfig()`, `logging.info()`|Lesson 21|
|`re.findall()`, `re.search()`, `.group()`|Lesson 24|
|`isinstance()`|Introduced in this lesson (Example 1)|
|HTTP concepts (status codes, headers, methods)|Lesson 35|
|curl command reading, pagination, Link header|This lesson (36)|

All operations required by the exercise have been taught in this lesson or prior lessons. No future-lesson dependencies exist.