# Lesson 39 — Handling and debugging API responses

By the end of this lesson you will have written one function, `call()`, and every API script you write after this will be built on it. It sends a request, survives every way that request can go wrong, says something useful about what happened, and returns `None` when there is nothing worth returning. Its callers do exactly one thing: check for `None`.

You build it in five versions. Each version starts from the previous one, adds a single line, and is added because you have just watched the previous version fail. Nothing in the syntax section is introduced on its own — every piece of it is the fix for a failure on the page above it.

Lessons 37 and 38 taught you to send requests. This lesson is about what comes back.

It assumes two things Lesson 38b covers: what a dot does — why `response.raise_for_status()` binds no name and leaves `response` untouched — and what `raise` does. Read 38b first if either of those lines below reads like an overwrite.

Everything runs against the real [Zenmeter Management API](https://api.nalpeiron.io/docs/zenmeter.html) at `https://api.nalpeiron.io`. Every request in the lesson is a `GET`, and nothing here creates, changes, or deletes anything in your tenant.

> [!warning] Which output blocks I ran, and which you have to check
> Every block showing a `400`, a `403`, a `404`, a `503`, or a connection failure is copied from a real run against `api.nalpeiron.io` with deliberately wrong credentials. You can reproduce all of them right now, before you have a token.
> Blocks showing a successful `200` body, a `409`, or a `422` could not be run — those need a real tenant token, which I do not have. Each one is marked **(Not run — from the schema.)** in its lead-in sentence and is built from the API's published OpenAPI schema. Check them on your first real run and tell me if the API disagrees.

## Set up before you start

Zenmeter needs two values on every request, and neither belongs in the script. Export them, as Lesson 31 established.

```bash
export ZENMETER_ACCESS_TOKEN=<your access token>
export ZENMETER_TENANT_ID=<your tenant id>
```

The access token comes from the OAuth2 client-credentials exchange described in the API reference's Authentication section; the token endpoint, client id, and client secret are in the NGP administration site under "API Credentials". The tenant id is there too, and it looks like `t_KRwhRp1yl0_9gsZjE5Yjaw`. Tokens expire, so a run that worked yesterday and fails today with no code change is the first thing to re-check.

Read the base URL from an optional third variable so you can point a script somewhere else without editing it.

```python
import os

BASE = os.environ.get("ZENMETER_BASE_URL", "https://api.nalpeiron.io")
HEADERS = {"N-TenantId": os.environ.get("ZENMETER_TENANT_ID", ""),
           "Authorization": f"Bearer {os.environ.get('ZENMETER_ACCESS_TOKEN', '')}"}
```

You do not need a working token to follow this lesson. Set both variables to obvious nonsense and every example below still runs and still produces the output shown.

```bash
export ZENMETER_ACCESS_TOKEN=not-a-real-token
export ZENMETER_TENANT_ID=t_notarealtenant
```

### Use these three URLs as the lesson's fixture

Three paths on the one host produce three genuinely different failures, and every example in this lesson uses them. They are the fixture: no local server, no invented data.

| Path                | Who answers it              | What comes back without a valid token            |
| ------------------- | --------------------------- | ------------------------------------------------ |
| `/api/v1/customers` | the Zenmeter API itself     | `400` with a JSON `ApiError` body and a trace id |
| `/nosuchpath`       | nothing routes it           | `404` with a completely empty body               |
| `/docs/nope.html`   | the CDN in front of the API | `403` with an XML body and no trace id           |

Those three are the whole point. A script that handles only the first one crashes on the other two, and the other two are the ones you meet at three in the morning.

Confirm your setup with a single call that needs no credentials at all. A bare request with no headers is refused, and the refusal is informative.

```python
import requests

response = requests.get("https://api.nalpeiron.io/api/v1/customers", timeout=10)
print(response.status_code, response.reason)
print(response.json()["details"])
```

If you see this, `requests` works and the host is reachable, which is all this check is for.

```text
400 Bad Request
N-TenantId header is missing
```

## Terminology and theory

Three ideas run through the lesson: the three ways a call can end, the shape an API wraps its error messages in, and the id the server uses to name one request. The first decides the helper's structure; the other two decide what it prints when something goes wrong.

### Every call ends in one of three ways

Keeping these apart is what the whole lesson is built on, because the second and third look identical to a careless script and demand opposite responses.

- **It succeeded.** A `2xx` came back and the body is what you asked for.
- **It was refused.** A reply arrived and it says no — `400`, `404`, `500`, anything outside `2xx`. `requests` raises nothing here, because it did its job: it asked, and it got an answer.
- **No reply arrived at all.** The host is unreachable, the connection was refused, the deadline expired. This is the only case where `requests` raises on its own.

A refusal carries information — a status code, an error body, a trace id — and usually means you must change something. No reply carries none of that, and usually means you try again later.

### An error envelope is the shape an API wraps its error messages in

Zenmeter's is called `ApiError`, and knowing it is what lets you write one function that explains any failure the API produces instead of a special case per endpoint. It has exactly four fields. This is a real `400` body, from a real run:

```json
{
  "details": "Your request could not be processed. Please check your input and try again.",
  "error": "Bad Request",
  "errorCode": null,
  "validationErrors": null
}
```

`error` is the short name of the status, `details` is the sentence a human should read, and `errorCode` is very often `null` — so never build a message that depends on it alone. `validationErrors` is a list, and it is populated only when a `422` has field-level complaints. **(Not run — from the schema.)** Each entry has three fields, `message`, `propertyName`, and `code`:

```json
{
  "details": "One or more validation errors occurred.",
  "error": "Unprocessable Entity",
  "errorCode": null,
  "validationErrors": [
    {"message": "'Name' must not be empty.", "propertyName": "name", "code": "NotEmptyValidator"}
  ]
}
```

The useful sentence in a `422` is one level down, inside `validationErrors`. The top-level `details` only tells you that validation failed, not what failed.

### A trace id is the server's name for one request

Zenmeter returns a fresh one on every reply, success and failure alike, in a response header. It means nothing to you and everything to whoever reads the API's logs, so a script that logs it can be debugged by someone else and a script that discards it cannot. It differs on every request, so the ids printed in this lesson will never match yours.

Two details about it matter in practice. The header arrives on the wire as lowercase `n-trace-id`, but `response.headers` is case-insensitive, so `.get("N-Trace-Id")` finds it either way.

```python
print("N-Trace-Id ->", response.headers.get("N-Trace-Id"))
print("n-trace-id ->", response.headers.get("n-trace-id"))
```

Both spellings reach the same header:

```text
N-Trace-Id -> d5da85d8-c68d-4def-81d3-41d3406cb89d
n-trace-id -> d5da85d8-c68d-4def-81d3-41d3406cb89d
```

The second detail is more useful: the trace id is **absent** when something other than the API answered. The CDN in front of Zenmeter does not add one. So a reply with no trace id is a reply the API itself never saw, which narrows your search enormously before you have read a single line of the body.

## Syntax: build the helper one version at a time

Each heading below is one version of `call()`. Read them in order — every version is the previous version plus one line, and the line is there because you are about to watch the previous version fail.

### Send the request and report what came back

**Version 1.** It sends the request and hands back the `Response`. That is all it does.

`requests.request(method, url, ...)` takes the method as a string first argument and does the job of `get()`, `post()`, `put()`, `patch()`, and `delete()` — it is what all five are built on. Using it here means the helper handles any verb from the start.

```python
def call(method, path, params=None):
    """Send one request and hand back whatever came out of it."""
    return requests.request(method, f"{BASE}{path}", headers=HEADERS,
                            params=params, timeout=10)


response = call("GET", "/api/v1/customers", params={"pageSize": 3})
print("status:", response.status_code, response.reason, "| ok =", response.ok)
print("body  :", response.json())
```

Three attributes describe the reply, and none of them makes another request: `.status_code` is the number, `.reason` is its name, and `.ok` is `True` for anything below `400`.

```text
status: 400 Bad Request | ok = False
body  : {'details': 'Your request could not be processed. Please check your input and try again.', 'error': 'Bad Request', 'errorCode': None, 'validationErrors': None}
```

Here is the failure that forces Version 2. The call was refused, and `call()` returned a `Response` anyway. Nothing raised, nothing warned, and a caller that goes straight to `response.json()["items"]` gets a `KeyError` several lines away from the actual mistake — or worse, a caller that does `.get("items", [])` reports "0 customers" and exits cleanly, having never spoken to your tenant at all.

`.ok` is a convenience, not a full answer: it collapses `200`, `201`, and `204` into one `True`, and those three want different handling. Use `.ok` for "should I parse this at all", and `.status_code` when the specific code matters.

### Stop treating a refusal as data

**Version 2** adds one line: `raise_for_status()`. Call it on a `Response` and it raises `requests.exceptions.HTTPError` for any `4xx` or `5xx`, and returns `None` for anything else. It assigns nothing, and `response` is the same object on the line after it as on the line before — Lesson 38b is where that is worked through. It exists so a refusal reaches you through the same `try`/`except` machinery you already use for everything else, instead of an `if` after every call.

```python
def call(method, path, params=None):
    """Send one request. Raise on anything that is not a 2xx."""
    response = requests.request(method, f"{BASE}{path}", headers=HEADERS,
                                params=params, timeout=10)
    response.raise_for_status()
    return response


response = call("GET", "/api/v1/customers", params={"pageSize": 3})
print("body:", response.json())
```

The refusal now stops the script instead of being handed back as data:

```text
Traceback (most recent call last):
  File "/home/josh/call.py", line 16, in <module>
    response = call("GET", "/api/v1/customers", params={"pageSize": 3})
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/josh/call.py", line 12, in call
    response.raise_for_status()
  File "/usr/lib/python3/dist-packages/requests/models.py", line 1021, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 400 Client Error: Bad Request for url: https://api.nalpeiron.io/api/v1/customers?pageSize=3
```

The message names the status, the reason, and the full URL including the query string, which is often enough to spot the mistake without any further digging. Its wording changes with the range: a `4xx` produces `Client Error` and a `5xx` produces `Server Error`, so the message itself tells you whose fault it is.

That is progress — the script no longer lies to you — but the failure that forces Version 3 is now obvious. A helper whose whole job is to be reliable currently kills its caller with a traceback, and it has not yet met the third ending at all.

### Survive a host that never answers

**Version 3** wraps the whole thing in one `except` clause. `requests.exceptions.RequestException` is the parent of every exception `requests` raises — `HTTPError`, `ConnectionError`, `ReadTimeout`, and `JSONDecodeError` are all kinds of it — so one clause catches every failure the library can produce, and nothing escapes to the caller.

```python
def call(method, path, params=None):
    """Send one request. Return the Response, or None when it did not succeed."""
    try:
        response = requests.request(method, f"{BASE}{path}", headers=HEADERS,
                                    params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        print(f"{method} {path} failed: {exc}")
        return None
    return response


print("refused :", call("GET", "/api/v1/customers", params={"pageSize": 3}))
```

Against the live API, the refusal is now reported rather than raised, and the caller gets `None`:

```text
GET /api/v1/customers failed: 400 Client Error: Bad Request for url: https://api.nalpeiron.io/api/v1/customers?pageSize=3
refused : None
```

Point the same script at a port with nothing listening — `ZENMETER_BASE_URL=http://127.0.0.1:9999` — and the third ending arrives. The same clause catches it, and the caller still gets `None`:

```text
GET /api/v1/customers failed: HTTPConnectionPool(host='127.0.0.1', port=9999): Max retries exceeded with url: /api/v1/customers?pageSize=3 (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x79a1be22eb40>: Failed to establish a new connection: [Errno 111] Connection refused'))
refused : None
```

The hex number is a memory address and differs every run. That message is long, names a library you never imported, and buries `Connection refused` at the very end — which is exactly why it belongs in a log rather than in front of a person.

Here is the failure that forces Version 4. Compare those two messages. The first says `400 Client Error: Bad Request` and stops. The API sent a whole `ApiError` body explaining itself, and Version 3 threw it away — `raise_for_status()` produced the exception, and the helper printed only the exception.

> [!note] The response is still reachable from inside the handler
> `raise_for_status()` attaches the response to the exception it raises, so catching `HTTPError` does not cost you the body: `exc.response.status_code`, `exc.response.json()`, and `exc.response.headers` all work.
> `exc.response` is `None` when the exception is a `ConnectionError` or a `ReadTimeout`, because there was never a response to attach. That is the difference between the second and third endings of a call, expressed as an attribute — and it is why a handler that catches `RequestException` broadly must check before reaching for it.

### Say what the API actually said

**Version 4** splits the one `except` into two, so a refusal and a dead host get different treatment, and adds a helper that reads the error envelope.

The split matters: a refusal has a `Response` and a dead host does not, so they cannot share a message. The new `error_text()` function does the reading, and its first job is to never assume the body is JSON.

```python
def error_text(response):
    """Return the API's own error message, or the raw body when it is not JSON."""
    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        return f"non-JSON body: {response.text.strip()[:60]!r}"
    message = f"{body.get('error')}: {body.get('details')}"
    problems = body.get("validationErrors")
    if problems:
        for problem in problems:
            message += f" [{problem['propertyName']}: {problem['message']}]"
    return message


def call(method, path, params=None):
    """Send one request. Return the Response, or None when it did not succeed."""
    try:
        response = requests.request(method, f"{BASE}{path}", headers=HEADERS,
                                    params=params, timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"{method} {path} got no reply: {exc}")
        return None
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print(f"{method} {path} -> {response.status_code} {error_text(response)}")
        return None
    return response


print("refused :", call("GET", "/api/v1/customers", params={"pageSize": 3}))
print("not JSON:", call("GET", "/docs/nope.html"))
```

One function explains both fixture failures, and the second is unreadable in a useful way — it tells you at a glance that the API itself never generated this reply:

```text
GET /api/v1/customers -> 400 Bad Request: Your request could not be processed. Please check your input and try again.
refused : None
GET /docs/nope.html -> 403 non-JSON body: '<?xml version="1.0" encoding="UTF-8"?>\n<Error><Code>AccessDe'
not JSON: None
```

`body.get('error')` rather than `body['error']`, because a body that parsed as JSON is not necessarily an `ApiError` — a proxy can return well-formed JSON of its own shape, and `.get()` returns `None` there instead of raising `KeyError` inside your error handler.

The `validationErrors` check is the part worth slowing down on, because it is the one place a plain `if` beats the compressed idiom. `.get("validationErrors")` returns the list on a `422`, and `None` on every other status — Zenmeter sends the field as an explicit `null`. Looping over `None` raises `TypeError`, so the `if problems:` guard is what makes the same function safe on all six status codes. That is the Lesson 14 truthiness check doing real work: an empty list and a `None` are both falsy, and both should skip the loop.

Here is the failure that forces Version 5. Run this against a tenant that is misbehaving and you will have an accurate message and no way to ask anyone about it. You cannot tell support *which* request failed, and you cannot see the URL that actually went out.

### Log the trace id and the URL that went out

**Version 5** is the finished helper. It replaces `print()` with `logging` and records two things a message alone cannot carry.

`logging.basicConfig(level=logging.DEBUG)` sets the threshold for *every* logger in the process, and `requests` is built on a library called `urllib3` that logs at `DEBUG` too. Turning on your own debug output turns on its output as well, and the library is noisier than you are.

```python
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

response = requests.get(f"{BASE}/api/v1/customers", headers=HEADERS,
                        params={"pageSize": 3}, timeout=10)
logging.debug(f"GET {response.url}")
logging.debug(f"-> {response.status_code} {response.reason} "
              f"trace={response.headers.get('N-Trace-Id')}")
```

The first two lines are not yours:

```text
DEBUG: Starting new HTTPS connection (1): api.nalpeiron.io:443
DEBUG: https://api.nalpeiron.io:443 "GET /api/v1/customers?pageSize=3 HTTP/1.1" 400 None
DEBUG: GET https://api.nalpeiron.io/api/v1/customers?pageSize=3
DEBUG: -> 400 Bad Request trace=cdcf313a-9c1f-4659-9c33-41b488813ae9
```

`logging.getLogger(name)` returns the named logger, and `.setLevel()` sets its threshold independently of the root one. Name the library and it goes quiet while your own messages keep coming.

```python
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logging.getLogger("urllib3").setLevel(logging.WARNING)   # quiet the library
```

Only your two lines survive:

```text
DEBUG: GET https://api.nalpeiron.io/api/v1/customers?pageSize=3
DEBUG: -> 400 Bad Request trace=9f590645-355a-4b99-81a7-9fd4c9fc2ff6
```

Log `response.url` rather than the path you meant to request. It is the URL that actually went out, query string included, so it settles the "did my `params=` arrive" question that Lesson 37 raised — and it is the only line in your log that would show a parameter silently dropped for being `None`.

## Worked examples

The first example is Version 5 assembled into the file you keep. The next two are the two decisions the helper deliberately leaves to its caller: whether the body is JSON at all, and what a given status code means for this endpoint.

### Example 1: the finished helper

This is Version 5 assembled, and it introduces nothing you have not already seen — the two `logging` lines, the `trace` variable, and the `sending` line are the only additions to Version 4. Run it, then keep it; the rest of your API scripts start from this file.

```python
import logging
import os
import requests

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logging.getLogger("urllib3").setLevel(logging.WARNING)

BASE = os.environ.get("ZENMETER_BASE_URL", "https://api.nalpeiron.io")
HEADERS = {"N-TenantId": os.environ.get("ZENMETER_TENANT_ID", ""),
           "Authorization": f"Bearer {os.environ.get('ZENMETER_ACCESS_TOKEN', '')}"}


def error_text(response):
    """Return the API's own error message, or the raw body when it is not JSON."""
    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        return f"non-JSON body: {response.text.strip()[:60]!r}"
    message = f"{body.get('error')}: {body.get('details')}"
    problems = body.get("validationErrors")
    if problems:
        for problem in problems:
            message += f" [{problem['propertyName']}: {problem['message']}]"
    return message


def call(method, path, params=None, body=None):
    """Send one request. Return the Response, or None when it did not succeed."""
    logging.debug(f"sending {method} {path}")
    try:
        response = requests.request(method, f"{BASE}{path}", headers=HEADERS,
                                    params=params, json=body, timeout=10)
    except requests.exceptions.RequestException as exc:
        logging.error(f"{method} {path} got no reply: {exc}")
        return None

    trace = response.headers.get("N-Trace-Id", "none")
    logging.debug(f"{response.status_code} from {response.url} trace={trace}")
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logging.error(f"{method} {path} -> {response.status_code} "
                      f"{error_text(response)} (trace {trace})")
        return None
    return response


print("refused :", call("GET", "/api/v1/customers", params={"pageSize": 3}))
print("not JSON:", call("GET", "/docs/nope.html"))
```

Two calls, two different failures, and not one traceback. The `print()` lines interleave with the log because `logging` writes to standard error and `print()` writes to standard output, and a terminal shows you both:

```text
DEBUG: sending GET /api/v1/customers
DEBUG: 400 from https://api.nalpeiron.io/api/v1/customers?pageSize=3 trace=e62b9b5d-62ad-41db-a762-1414acd377b9
ERROR: GET /api/v1/customers -> 400 Bad Request: Your request could not be processed. Please check your input and try again. (trace e62b9b5d-62ad-41db-a762-1414acd377b9)
DEBUG: sending GET /docs/nope.html
DEBUG: 403 from https://api.nalpeiron.io/docs/nope.html trace=none
ERROR: GET /docs/nope.html -> 403 non-JSON body: '<?xml version="1.0" encoding="UTF-8"?>\n<Error><Code>AccessDe' (trace none)
refused : None
not JSON: None
```

Redirect one stream and the other survives on its own: `python3 example1.py 2>/dev/null` leaves you the two `print()` lines, and `None` is the whole vocabulary a caller needs to read them.

Run the same file with `ZENMETER_BASE_URL=http://127.0.0.1:9999` and the third ending appears instead, through the other `except` clause:

```text
DEBUG: sending GET /api/v1/customers
ERROR: GET /api/v1/customers got no reply: HTTPConnectionPool(host='127.0.0.1', port=9999): Max retries exceeded with url: /api/v1/customers?pageSize=3 (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x78c42119ec00>: Failed to establish a new connection: [Errno 111] Connection refused'))
```

Four details are doing the work here. The `sending` line is logged *before* the request, so a call that never returns still leaves evidence of having been attempted. The line after it logs `response.url`, which carries the query string the `sending` line could not know about. The `trace` appears on both the debug line and the error line, so grepping a log for one id gives you the whole story of one request. And `trace=none` on the second call is not a bug — it is the `"none"` default in `.get()` telling you the API never saw that request.

`logging.error()` rather than `logging.warning()` for a refusal, because the script did not do what it was asked. `logging.debug()` for the ordinary traffic, so a normal run is silent and `level=logging.DEBUG` is the switch that makes it talkative.

Once your credentials are real, the first call returns a `Response` instead of `None` and its `ERROR` line disappears. **(Not run — from the schema.)** A successful customer list is a paginated envelope, not a bare array:

```json
{
  "items": [
    {"id": "cust_n1bmaIvXnEW7DOl0w5EiHQ", "name": "Boeing Corporation", "type": "Prospect",
     "accountRefId": "account12395-32", "disabledDate": null, "status": "active",
     "description": null}
  ],
  "pageSize": 3,
  "pageNumber": 1,
  "elementsTotal": 1
}
```

`items` is the list, and `elementsTotal` is how many exist across all pages — so `len(body["items"])` and `body["elementsTotal"]` answer two different questions, and confusing them is how a script quietly reports one page as if it were the whole tenant.

### Example 2: never assume the body is JSON

The documented `ApiError` is what the API sends. A CDN, a proxy, or a load balancer in front of it has its own ideas, and those replies never reach the code that would have built an `ApiError`. This is why `error_text()` in the helper is written the way it is, and this example is the same logic slowed down so you can watch all three shapes arrive.

The ordering of the checks is the entire trick: empty body first, then JSON, then the envelope.

```python
import requests

BASE = "https://api.nalpeiron.io"
HEADERS = {"N-TenantId": "t_notarealtenant"}


def describe(label, path):
    """Print what came back, whatever shape the body turned out to be."""
    response = requests.get(f"{BASE}{path}", headers=HEADERS, timeout=10)
    trace = response.headers.get("N-Trace-Id", "none")
    print(f"{label}:")
    print(f"  {response.status_code} {response.reason}"
          f"  content-type={response.headers.get('Content-Type')}"
          f"  trace={trace}")
    if not response.text:
        print("  the body is empty; there is nothing to parse")
        return
    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        print(f"  not JSON ({exc}); first 60 characters:")
        print(f"  {response.text.strip()[:60]!r}")
        return
    print(f"  {body['error']}: {body['details']}")


describe("the API answered", "/api/v1/customers")
describe("a path the API never routes", "/nosuchpath")
describe("a path the CDN answers instead", "/docs/nope.html")
```

Three real replies from one host, and only the first one is the shape the documentation describes:

```text
the API answered:
  400 Bad Request  content-type=application/json; charset=utf-8  trace=04ef8cb8-a0d5-486c-a0f0-66a925e62345
  Bad Request: Your request could not be processed. Please check your input and try again.
a path the API never routes:
  404 Not Found  content-type=None  trace=79ca7c4a-d66c-4ac6-bdba-f6ecfcc8bd64
  the body is empty; there is nothing to parse
a path the CDN answers instead:
  403 Forbidden  content-type=application/xml  trace=none
  not JSON (Expecting value: line 1 column 1 (char 0)); first 60 characters:
  '<?xml version="1.0" encoding="UTF-8"?>\n<Error><Code>AccessDe'
```

Read the three `trace=` values together. The first two came from Zenmeter, which stamps every reply it generates. The third has none, because the CDN answered before the request ever reached the API — and that single missing field tells you where to look before you have read one character of the XML.

`{response.text.strip()[:60]!r}` uses the `!r` conversion from Lesson 25, and it earns its place twice here. It wraps the snippet in quotes, so a body that is empty prints as `''` rather than as nothing at all, and it escapes the newline inside the XML as `\n` so one truncated line stays one line in your log.

The `if not response.text:` check has to come first, because `.json()` on an empty body raises `JSONDecodeError` with the same "Expecting value: line 1 column 1 (char 0)" message that an HTML or XML body produces. Checking emptiness separately is what lets you say "there was no body" instead of "the body was not JSON", and those are different problems.

> [!warning] A `204` is a success with no body, and parsing it crashes
> Zenmeter answers a successful `PUT`, `disable`, `enable`, or `cancel` with `204` and no body at all. It is the *good* outcome, and `.json()` on it raises `requests.exceptions.JSONDecodeError` exactly as an empty `404` does.
> Never parse a body without checking the status first, or the calls that crash your script will be the ones that worked.
> This lesson sends only `GET` requests, so nothing here produces a `204` — but every write endpoint in the API does, and Lesson 38's `PUT` and `PATCH` calls are where you will meet it.

### Example 3: turn a status code into an instruction

A status code is only useful once it has become a sentence about what to do next. This is the same table you would put in the troubleshooting section of a doc page, expressed as a dict.

The keys come from Zenmeter's own OpenAPI schema, which documents exactly six codes for these endpoints: `400`, `402`, `404`, `409`, `422`, and `500`.

```python
import requests

BASE = "https://api.nalpeiron.io"
HEADERS = {"N-TenantId": "t_notarealtenant",
           "Authorization": "Bearer not-a-real-token"}

# Keyed on the six codes Zenmeter's OpenAPI schema documents for these endpoints.
ADVICE = {
    400: "Malformed request. Check the two headers, the path, and the query string.",
    402: "The account cannot be billed for this. Not a code problem.",
    404: "The path or the record id is wrong. Nothing was changed.",
    409: "The record is already in the state you asked for.",
    422: "The body parsed but failed validation. Read validationErrors.",
}


def advise(response):
    """Return what a person should do about this response."""
    if response.ok:
        return "Nothing to do."
    if response.status_code >= 500:
        return "The API failed, not your request. Retry, then quote the trace id."
    return ADVICE.get(response.status_code,
                      "Undocumented for this API. Read the body before assuming.")


probes = [
    ("the docs page", "/docs/zenmeter.html"),
    ("the API, bad tenant", "/api/v1/customers"),
    ("a path the CDN answers", "/docs/nope.html"),
    ("a path nothing routes", "/nosuchpath"),
]

for label, path in probes:
    response = requests.get(f"{BASE}{path}", headers=HEADERS, timeout=15)
    print(f"{label:24} {response.status_code}  {advise(response)}")
```

All four branches of `advise()` fire, and the interesting one is the third:

```text
the docs page            200  Nothing to do.
the API, bad tenant      400  Malformed request. Check the two headers, the path, and the query string.
a path the CDN answers   403  Undocumented for this API. Read the body before assuming.
a path nothing routes    503  The API failed, not your request. Retry, then quote the trace id.
```

That `403` is not in `ADVICE`, because the schema never documents a `403` — and it arrived anyway. `ADVICE.get(...)` with a default rather than `ADVICE[...]` is what keeps that from becoming a `KeyError` raised inside your error handler, which is the worst possible place for one.

The `>= 500` check comes before the dict lookup, because the `5xx` family is open-ended: `500`, `502`, `503`, and `504` all mean the same thing to your script, and enumerating them is a list you will forget to extend. The `4xx` codes each mean something different, so those get individual entries.

That `503` is also worth a note on retrying. On an earlier run, the very same path returned `404` rather than `503` — the difference was whether an `Authorization` header was sent. A `5xx` is the one family where sending the identical request again is a reasonable response, and it is the reason the advice for it is "retry" while the advice for every `4xx` is "change something".

## Check the code you get, not the code that is documented

Zenmeter's schema documents `400`, `402`, `404`, `409`, `422`, and `500` for these endpoints. It documents no `401` and no `403` anywhere — and you have already seen a `403` arrive in Example 3.

The gap runs the other way too. These two requests go to the live host with no credentials. They are read-only, unauthenticated, and safe to run.

```python
import requests

BASE = "https://api.nalpeiron.io"

for label, headers in [("no headers at all", {}),
                       ("a tenant id the platform does not know",
                        {"N-TenantId": "t_notarealtenant"})]:
    response = requests.get(f"{BASE}/api/v1/customers", headers=headers, timeout=10)
    print(f"{label}:")
    print(f"  {response.status_code} {response.reason}  "
          f"trace={response.headers.get('N-Trace-Id')}")
    print(f"  {response.json()['details']}")
```

Both are a `400`, and the second tells you almost nothing:

```text
no headers at all:
  400 Bad Request  trace=fcaa50b6-bc26-42fc-9e32-dc44c398b05d
  N-TenantId header is missing
a tenant id the platform does not know:
  400 Bad Request  trace=389c026e-9184-48bb-b92d-d8f0a26b55d2
  Your request could not be processed. Please check your input and try again.
```

The first message is precise and the second is deliberately not, which is the usual trade-off: naming the problem for an anonymous caller would tell them which tenant ids exist. Whatever the reason, that vagueness is what will cost you an hour, because a `400` with a generic message can mean a bad tenant id, a bad token, a bad query string, or a path that does not exist, and the response cannot tell you which.

Two habits follow, and both are why `call()` logs a trace id.

Classify on what you receive, not on what the table promises. `advise()` says something sensible about the `403` precisely because it is keyed on the code that came back and falls back to a default for anything else.

Quote the trace id when you ask for help. It is the one piece of a generic `400` that identifies your specific request in the API's own logs, and it is the difference between "the API returns 400" and a question someone can actually answer.

> [!note] This is worth writing down when you document an API
> A gap between the documented status code and the delivered one is a genuine finding, not a mistake on your part.
> Reproduce it, note the exact request that produces it, and keep the trace id.

## Lookup table

| Use when | Call | Result |
| --- | --- | --- |
| Check whether a reply is usable at all | `response.ok` | `True` below `400`, `False` from `400` up; makes no new request |
| Read the status as a number and a name | `response.status_code`, `response.reason` | `400` and `'Bad Request'` |
| Send any verb through one function | `requests.request(method, url, headers=..., timeout=10)` | Same `Response` as `get()`/`post()`; `params=None` and `json=None` send nothing |
| Stop the script on a refusal | `response.raise_for_status()` | `None` on `2xx`; raises `requests.exceptions.HTTPError` on `4xx` and `5xx` |
| Read the message that raise produces | the `HTTPError` text | `400 Client Error: Bad Request for url: ...`; `Server Error` instead for `5xx` |
| Catch every failure with one clause | `except requests.exceptions.RequestException` | Catches `HTTPError`, `ConnectionError`, `ReadTimeout`, and `JSONDecodeError` |
| Catch only a host that never answered | `except requests.exceptions.ConnectionError` | Raised when the connection is refused or the host is unreachable; nothing was sent to the API |
| Get the response back inside a handler | `exc.response` | The `Response` for an `HTTPError`; `None` for a `ConnectionError` or `ReadTimeout` |
| Read the API's own error message | `response.json()["details"]` | `'Your request could not be processed. Please check your input and try again.'` |
| Read the short status name from the body | `response.json()["error"]` | `'Bad Request'`, `'Not Found'`, `'Conflict'` |
| Read the envelope without risking a crash | `body.get("error")` | The value, or `None` when the JSON is not an `ApiError` at all |
| Read the machine-readable error code | `body.get("errorCode")` | Almost always `None`, even on a genuine error; never build a message that depends on it alone |
| Read per-field validation complaints | `body.get("validationErrors")` | A list of `{message, propertyName, code}` dicts on a `422`; `None` on every other status |
| Loop over a field that is `None` off a `422` | `if problems:` before the `for` | Skips the loop; looping over `None` directly raises `TypeError` |
| Survive an error body that is not JSON | `except requests.exceptions.JSONDecodeError` | `Expecting value: line 1 column 1 (char 0)` on an XML, HTML, or empty body |
| Tell an empty body from a malformed one | `if not response.text:` before `.json()` | `True` when the body is `''`; both cases otherwise raise the same `JSONDecodeError` |
| Parse a `204` by mistake | `response.json()` on a `204` | Raises `requests.exceptions.JSONDecodeError`; the body is `''` and the call succeeded |
| Identify one request in the API's logs | `response.headers.get("N-Trace-Id", "none")` | `'d5da85d8-c68d-4def-81d3-41d3406cb89d'`; the lookup is case-insensitive |
| Spot a reply the API never generated | the trace id is missing | `'none'` from the default; the CDN and proxies do not stamp one |
| Log the URL that actually went out | `response.url` | `'https://api.nalpeiron.io/api/v1/customers?pageSize=3'`, query string included |
| Treat every server-side failure alike | `response.status_code >= 500` | `True` for `500`, `502`, `503`, `504`; the one family worth retrying |
| Turn on your own debug logging | `logging.basicConfig(level=logging.DEBUG)` | Sets the threshold for *every* logger in the process, so `urllib3` starts logging each connection too |
| Stop `urllib3` flooding your debug log | `logging.getLogger("urllib3").setLevel(logging.WARNING)` | Your `DEBUG` lines survive; the library's connection lines stop |
| Check which codes this API can send | Zenmeter's OpenAPI schema | `400`, `402`, `404`, `409`, `422`, `500`; `402` means the account cannot be billed, and neither `401` nor `403` is documented |
| Handle a code the schema never documented | the default arm of `ADVICE.get()` | A `403` from the CDN arrives despite being undocumented; classify on what came back |
| Look up advice without risking a crash | `ADVICE.get(response.status_code, "Undocumented.")` | The sentence, or the default; `ADVICE[...]` would raise `KeyError` |
| Count one page against the whole set | `len(body["items"])` vs `body["elementsTotal"]` | Items on this page vs items in the tenant; they differ on every page but the last |

## Exercise: probe a live Zenmeter tenant

Write `zenmeter_probe.py`, a read-only diagnostic that runs a list of `GET` requests against a Zenmeter tenant, reports what each one did, and writes a Markdown summary.

Every request it sends is a `GET`, and nothing in the plan file below creates, changes, or removes anything. That is deliberate: this is the script you run first, against a tenant you do not want to disturb, to find out whether your credentials work and which endpoints answer.

### Save the plan file

Save this as `probe-plan.json`. Every entry is a `GET`, and none of them needs a record id from your tenant.

```json
[
  {
    "name": "customer list",
    "path": "/api/v1/customers",
    "params": {"pageSize": 3}
  },
  {
    "name": "product catalog",
    "path": "/api/v1/zenmeter/products"
  },
  {
    "name": "subscription list",
    "path": "/api/v1/zenmeter/subscriptions",
    "params": {"pageSize": 3}
  },
  {
    "name": "empty page",
    "path": "/api/v1/customers",
    "params": {"pageNumber": 99, "pageSize": 3}
  },
  {
    "name": "missing customer",
    "path": "/api/v1/customers/cust_000000000000000000000",
    "expect": 404
  }
]
```

The last two entries are what make the script worth running. `empty page` asks for a page far past the end of the list, and a healthy API answers `200` with an empty `items` list rather than failing. `missing customer` asks for an id that cannot exist, and declares through `expect` that a `404` is the correct answer — so a probe that gets its `404` passes, and one that gets anything else fails.

### Requirements

1. Take the plan file's path as a positional argument. Support `--out`, which names the Markdown report and defaults to `probe-report.md`, and `--verbose`. `--help` must explain all three.
2. Read `ZENMETER_ACCESS_TOKEN` and `ZENMETER_TENANT_ID` from the environment, checking the token first. If the token is unset or empty, print `ZENMETER_ACCESS_TOKEN is not set.` and send nothing at all. If the token is present but the tenant id is unset or empty, print `ZENMETER_TENANT_ID is not set.` and likewise send nothing.
3. Read the base URL from `ZENMETER_BASE_URL`, falling back to `https://api.nalpeiron.io` when it is not set.
4. Configure logging so that a plain run prints only errors and `--verbose` prints every request and response. Keep `urllib3` out of the output at both settings.
5. Send every request through one function that sets both headers and a timeout, logs the request before sending and the status, URL, and trace id after, and never lets an exception escape to its caller. A refusal and an unreachable host must both be handled there, and they must be distinguishable in what the function returns.
6. Read and parse the plan file. A plan file that does not exist must produce a message rather than a traceback.
7. Run every probe. An entry's `expect` defaults to `200` when the entry does not carry one.
8. Print one line per probe: `ok` or `FAIL`, the probe's name, the method and path, the status code, and a detail. On success, the detail is how many items came back out of how many exist in total. On a refusal, it is the API's own `error` and `details`, plus the trace id. When no reply arrived at all, there is no status code and no trace id, and the line must say so rather than inventing either.
9. A failing probe must not stop the run.
10. Finish with a count of how many probes did what was expected, out of how many were run.
11. Write a Markdown report to the `--out` path: a heading, the base URL that was probed, a table with one row per probe carrying the same five fields as the printed lines, and the same closing count.

### Expected output

All the blocks below are captured from real runs of my own solution. The first two send no request at all, the third goes to `https://api.nalpeiron.io`, and the fourth goes nowhere on purpose — so you can reproduce every one of them without a working token.

With no token set, nothing is sent:

```text
ZENMETER_ACCESS_TOKEN is not set.
```

With a token set but no tenant id, still nothing is sent:

```text
ZENMETER_TENANT_ID is not set.
```

Point it at a plan file that does not exist and it says so instead of raising:

```text
No plan file at nope.json.
```

Now set both credentials to deliberately wrong values and watch the script survive it. This sends five real requests to the live API, all of which are refused:

```bash
export ZENMETER_ACCESS_TOKEN=not-a-real-token
export ZENMETER_TENANT_ID=t_notarealtenant
python3 zenmeter_probe.py probe-plan.json
```

Every probe fails the same way, the run finishes, and the report is still written:

```text
FAIL  customer list      GET /api/v1/customers                             400  Bad Request: Your request could not be processed. Please check your input and try again.  (trace 4fab3043-d5c5-4127-802e-5d15e55eb8e3)
FAIL  product catalog    GET /api/v1/zenmeter/products                     400  Bad Request: Your request could not be processed. Please check your input and try again.  (trace e1b85812-7ec9-4979-adff-abcd5e8502c9)
FAIL  subscription list  GET /api/v1/zenmeter/subscriptions                400  Bad Request: Your request could not be processed. Please check your input and try again.  (trace 9b569cd2-3b27-4d49-a664-39e985dbb612)
FAIL  empty page         GET /api/v1/customers                             400  Bad Request: Your request could not be processed. Please check your input and try again.  (trace d7ec0331-dcef-40f9-ba7a-8fc15fdb7b73)
FAIL  missing customer   GET /api/v1/customers/cust_000000000000000000000  400  Bad Request: Your request could not be processed. Please check your input and try again.  (trace 8edd327a-322c-4a3c-a94a-cec397304b33)
0 of 5 probes as expected
Wrote probe-report.md
```

Your trace ids will differ — that is the point of them. The five status codes, the five messages, and the two summary lines should match exactly. Note that `missing customer` fails here even though it expected a `404`: it got a `400`, and a probe that fails for a different reason than the one you predicted is still a failure.

The report on disk carries the same five rows and the same count:

```markdown
# Zenmeter probe report

Base URL probed: `https://api.nalpeiron.io`

| Result | Probe | Request | Status | Detail |
| --- | --- | --- | --- | --- |
| FAIL | customer list | `GET /api/v1/customers` | 400 | Bad Request: Your request could not be processed. Please check your input and try again. (trace 4fab3043-d5c5-4127-802e-5d15e55eb8e3) |

0 of 5 probes as expected
```

Finally, point the script at a host with nothing listening, which exercises the other kind of failure:

```bash
ZENMETER_BASE_URL=http://127.0.0.1:9999 python3 zenmeter_probe.py probe-plan.json
```

Nothing replies, so there is no status code and no trace id for any of the five:

```text
FAIL  customer list      GET /api/v1/customers                             None  no reply from the API
FAIL  product catalog    GET /api/v1/zenmeter/products                     None  no reply from the API
FAIL  subscription list  GET /api/v1/zenmeter/subscriptions                None  no reply from the API
FAIL  empty page         GET /api/v1/customers                             None  no reply from the API
FAIL  missing customer   GET /api/v1/customers/cust_000000000000000000000  None  no reply from the API
0 of 5 probes as expected
Wrote probe-report.md
```

Each of those five also logs an `ERROR` line to standard error, without `--verbose`, of which this is the first:

```text
ERROR   GET /api/v1/customers got no reply: HTTPConnectionPool(host='127.0.0.1', port=9999): Max retries exceeded with url: /api/v1/customers?pageSize=3 (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x71d284a23c50>: Failed to establish a new connection: [Errno 111] Connection refused'))
```

That line's exact wording and its memory address are the library's and will vary. What must be true is that it appears without `--verbose`, that the run continues to the remaining probes, and that a probe with no reply reports differently from a probe that was refused. Column widths throughout are yours to choose; the field content is not.

Once your credentials are real, run it again. **(Not run — from the schema.)** A tenant in good health should answer `200` to the first four probes and `404` to the fifth, for a summary of `5 of 5 probes as expected` — but unlike the four runs above, I could not produce that run without a token, so treat it as the prediction the plan file encodes rather than as captured output. If your tenant answers differently, the probe is doing its job and the prediction was wrong.
