## Lesson 40: `*args` and `**kwargs` — reading flexible signatures

### Terminology and Theory

When reading SDK code or documentation, you’ll often see function signatures that look like this:

```python
def create_issue(self, *args, **kwargs): ...
def get_issues(**filters): ...
```

These stars aren’t special operators — they’re a way to make a function accept a flexible number of arguments. Understanding them is essential for navigating real-world Python SDKs, where methods are often thin wrappers around HTTP requests and may forward arbitrary parameters.

- **`*args`** (collecting positional arguments)  
  The single `*` in `*args` collects any remaining positional arguments into a **tuple**. Inside the function, `args` is a tuple containing all the extra arguments passed without a keyword. The name `args` is convention; you can use any valid name like `*things`.  
  In an SDK signature, something like `*args` signals: *“this function can accept extra values after the required ones.”*

- **`**kwargs`** (collecting keyword arguments)  
  The double `**` in `**kwargs` collects any extra keyword arguments into a **dict**. Inside the function, `kwargs` is a dictionary mapping argument names to their values. The name `kwargs` is convention.  
  In an SDK signature, `**kwargs` often represents optional parameters or filters: *“pass any additional named parameters you like, and we’ll forward them as query params or request body fields.”*

- **Argument packing** is what happens when you define `*` and `**` in the parameter list — the extra values “pack” into a tuple or dict.  
- **Argument unpacking** is the reverse: when you **call** a function, you can unpack a list/tuple into positional arguments with `*` or a dict into keyword arguments with `**`. For example: `some_func(*my_list)` passes the list elements as separate arguments, and `some_func(**my_dict)` passes the dict’s key–value pairs as keyword arguments.

> [!tip]  
> You don’t need to write functions that use `*args`/`**kwargs` to be a good technical writer.  
> You **must** be able to look at a function signature that uses them and understand what arguments it expects.

> [!note]  
> The order of parameters matters: inside a function definition, normal parameters come first, then `*args`, then keyword-only parameters, then `**kwargs`.  
> Example: `def f(a, b, *args, c=10, **kwargs):`.  
> This lesson does not require you to write such complex signatures; we only need to recognise them.

### Syntax Section

#### Packing: defining a function that accepts extra arguments

```python
def func(*args):
    # args is a tuple of all extra positional arguments
    print(args)

func(1, 2, 3)          # prints (1, 2, 3)

def func(**kwargs):
    # kwargs is a dict of all extra keyword arguments
    print(kwargs)

func(a=1, b=2)         # prints {'a': 1, 'b': 2}
```

You can combine both:

```python
def report(prefix, *items, **options):
    print(prefix, "-> items:", items, "| options:", options)

report("LOG", "apple", "banana", show_time=True, level=3)
# prints: LOG -> items: ('apple', 'banana') | options: {'show_time': True, 'level': 3}
```

#### Unpacking: using `*` and `**` when you call a function

```python
# Unpacking a list/tuple into positional arguments
def add(a, b):
    return a + b

numbers = [3, 5]
result = add(*numbers)   # equivalent to add(3, 5)

# Unpacking a dict into keyword arguments
def greet(name, greeting):
    return f"{greeting}, {name}"

info = {"name": "Josh", "greeting": "Hello"}
message = greet(**info)  # equivalent to greet(name="Josh", greeting="Hello")
```

> [!note]  
> You can also unpack iterables and dicts with `*` and `**` when **building** lists, tuples, or dicts, but that’s beyond today’s scope. We’ll stick to function signatures and calls.

### Worked Examples

#### Example 1: Inspecting what a function receives

This small script illustrates how `*args` and `**kwargs` collect values. No external libraries needed.

```python
def show_args(*args, **kwargs):
    print("Positional arguments (tuple):", args)
    print("Keyword arguments (dict):", kwargs)
    print("---")

show_args(1, "hello", name="Josh", active=True)
# Positional arguments (tuple): (1, 'hello')
# Keyword arguments (dict): {'name': 'Josh', 'active': True}
# ---

show_args(42)
# Positional arguments (tuple): (42,)
# Keyword arguments (dict): {}
```

When you read an SDK method like `repo.get_issues(**filters)`, think of `filters` as a dictionary that gets unpacked into keyword arguments (e.g. `state="open", labels=["bug"]`). The method definition will probably have `**kwargs` to accept them.

#### Example 2: Simulating an SDK‑style function that forwards arguments

Here’s a function that builds a request dictionary, mimicking how an SDK might collect parameters before sending them to an API endpoint.

```python
def build_request(endpoint, *path_segments, **options):
    """Simulate constructing an API request."""
    # Join path segments into a full URL path
    path = "/".join(path_segments)
    url = f"{endpoint}/{path}"
    # options might contain query params or headers
    print("Final URL:", url)
    print("Options:", options)

build_request("https://api.example.com", "v1", "issues", state="open", per_page=30)
# Final URL: https://api.example.com/v1/issues
# Options: {'state': 'open', 'per_page': 30}
```

Notice how the positional arguments `"v1"` and `"issues"` become `path_segments`, and the keyword arguments go into `options`. This pattern is very common in SDK wrappers.

#### Example 3: Unpacking a dictionary to call a function dynamically

Often you’ll build a dictionary of parameters first and then pass it to an SDK method:

```python
def print_issue(title, body, labels=None, milestone=None):
    print(f"Title: {title}\nBody: {body}")
    print(f"Labels: {labels}\nMilestone: {milestone}")

issue_data = {
    "title": "Fix login bug",
    "body": "The login page returns 500 when the password is empty.",
    "labels": ["bug", "priority-high"],
}

# Unpack the dict; milestone will use its default (None)
print_issue(**issue_data)
```

This is exactly how you’ll see code like `repo.create_issue(**issue_data)`.

### Quick Reference

```python
# Packing extra positional arguments into a tuple
def list_items(*items):
    print(type(items))          # <class 'tuple'>
    for item in items:
        print("-", item)

list_items("doc", "test", "src")   # prints each item

# Packing extra keyword arguments into a dictionary
def configure(**settings):
    print(type(settings))       # <class 'dict'>
    for key, value in settings.items():
        print(f"{key}={value}")

configure(debug=True, verbose=2)


# A function that accepts both normal, *args, and **kwargs
def log_event(event_type, *details, **metadata):
    print("Event:", event_type)
    print("Details:", details)
    print("Metadata:", metadata)


log_event("page_load", "home", "mobile", user="josh", domain="example.com")

# Unpacking a list into positional arguments with *
def multiply(a, b):
    return a * b

values = [4, 5]
print(multiply(*values))       # 20

# Unpacking a dictionary into keyword arguments with **
def say_hello(name, greeting="Hello"):
    return f"{greeting}, {name}"

person = {"name": "Josh"}
print(say_hello(**person))     # "Hello, Josh"
```

### Exercises

Write a **single** Python script that does the following:

1. Imports `requests` and `logging`.  
2. Configures logging so that messages at level `INFO` and above are shown.  
3. Defines a function `call_api(base_url, *path_parts, **params)` that:  
   - builds the full URL by joining `path_parts` onto `base_url` with slashes (e.g., `https://httpbin.org/get/anything`).  
   - makes a **GET** request to that URL using `requests.get()`, passing `params` as the query parameters.  
   - logs the final URL (including any appended query string) at `INFO` level.  
   - uses `response.raise_for_status()` to raise an `HTTPError` if the status code indicates an error.  
   - if the request succeeds, logs the status code at `INFO` level and **returns** the decoded JSON (`response.json()`).  
   - if an `HTTPError` occurs, logs an error message at `ERROR` level and **returns** `None`.  
4. Outside the function, calls `call_api()` with the following arguments:
   - `"https://httpbin.org"` as the base URL  
   - the path parts `"get"` and `"anything"` (so the full path becomes `/get/anything`)  
   - `show_env="1"` as a keyword argument (this becomes a query parameter)  
5. Prints the returned JSON (which should be a dictionary) so that it appears nicely formatted at the command line when you run the script.

Use only techniques taught so far in this course. Do not use advanced structures like list comprehensions, lambdas, or classes.

When your script works correctly, you should see output similar to the following (timestamps will differ, and the JSON structure may vary slightly depending on httpbin’s response):

```
INFO:root:Requesting: https://httpbin.org/get/anything?show_env=1
INFO:root:Status code: 200
{'args': {'show_env': '1'}, 'headers': {...}, 'origin': '...', 'url': 'https://httpbin.org/get/anything?show_env=1'}
```

> [!warning]  
> If your script does not use `*args` or `**kwargs` correctly this exercise is not complete.  
> The function definition **must** collect extra positional arguments into `*path_parts` and extra keyword arguments into `**params`.