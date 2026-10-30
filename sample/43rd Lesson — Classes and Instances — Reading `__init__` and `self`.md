# Lesson 43: Read a class, its `__init__`, and `self`

A class is the definition that objects of one kind are built from, and an instance is one object built from it. This lesson teaches you to read a class the way you'll meet one in SDK source: what `__init__` does with the arguments you pass, what `self` refers to, and how to spot the line in SDK code that creates an object. It covers reading classes, not designing them, so it leaves out writing methods in depth, chaining one object to the next, `@property`, and inheritance.

If you've used an object from the outside, by reading its attributes and calling its methods, this lesson opens one up. You may already have created instances without the word: `Path("docs/api/auth.md")` calls the `Path` class and hands back an instance of it, and `argparse.ArgumentParser(...)` does the same. Nothing in this lesson calls GitHub, because the objects come from a small module you save beside your scripts.

## Code blocks the examples use

Every example imports from `mockhub.py`, a module of about 40 lines that stands in for four PyGithub classes: `Token`, which holds a token; `Github`, which is the client; `Repository`; and `Issue`. Their names and several of their attribute names match PyGithub's, so what you read here carries over to PyGithub itself. Save the module as `mockhub.py` in the folder you run your scripts from. Python looks for an imported module in the running script's own folder first, so `from mockhub import Issue` finds it the same way `import math` finds a module that ships with Python. Expand the collapsible below and copy its code into `mockhub.py`. The Terminology and Theory section reads the module line by line, and each example repeats the classes it uses in a collapsible of its own.

<details>
<summary>The whole of <code>mockhub.py</code></summary>

```python
"""Stand-ins for four PyGithub classes, for practice reading class code."""

API_URL = "https://api.github.com"


class Token:
    def __init__(self, token):
        self.token = token


class Github:
    def __init__(self, auth=None, base_url=API_URL, timeout=15):
        self.auth = auth
        self.base_url = base_url
        self.timeout = timeout


class Repository:
    def __init__(self, owner, name, stars=0, description=None):
        self.owner = owner
        self.name = name
        self.full_name = f"{owner}/{name}"
        self.stargazers_count = stars
        self.description = description


class Issue:
    def __init__(self, number, title, user=None, labels=None):
        if labels is None:
            labels = []
        self.number = number
        self.title = title
        self.user = user
        self.labels = labels
        self.state = "open"

    def describe(self):
        return f"#{self.number} {self.title} [{', '.join(self.labels)}]"
```

</details>

Each example is a script that starts with an import from `mockhub`, and its sample data is written into the block, so it runs on its own as long as `mockhub.py` sits beside it. The issues are numbered 41, 42, and 43, and issue 42 has no user and no labels, so you can see what the constructor does when you leave arguments out.

## Terminology and Theory

A **class** is a definition that describes the data and the functions every object of one kind carries. `class Repository:` starts one, and the indented block under it holds the functions that belong to it, the same way the indented block under a `def` holds a function's body. Defining a class creates no objects. Python stores the definition under the class's name and builds nothing until you call it.

The following lines name the parts of a class definition in the order they're written:

```python
class ClassName:
    def __init__(self, parameter):
        self.attribute = parameter
```

An **instance** is one object built from a class. You create one by calling the class like a function, with parentheses and arguments, so `Repository("psf", "requests")` builds a new `Repository` instance and hands it back. Every instance of a class has the same attribute names, but each holds its own values, which is why two `Repository` instances can have different `full_name` values. *Object* and *instance* name the same thing from two angles: every instance is an object, and *an instance of `Repository`* also says which class built it. `type(x).__name__` names that class.

The **constructor** is the method Python runs automatically each time you create an instance, and in a Python class it's always named `__init__`. By the time `__init__` runs, Python has already made a new, empty instance, so the job of `__init__` is to give that instance its starting attributes. The arguments in your call go to the parameters of `__init__`: `Repository("psf", "requests")` runs it with `owner` set to `"psf"` and `name` set to `"requests"`. You never call `__init__` by name, because calling the class does it for you. The two underscores on each side mark a name Python itself looks for, like `__name__` and `__doc__`.

**`self`** is the first parameter of every method in a class, and it holds the instance the method is working on. Inside `__init__`, `self` is the new instance, so `self.name = name` reads as "store the argument `name` on this instance, as an attribute called `name`." You never pass `self` yourself. Python fills it in, which is why `Repository("psf", "requests")` passes two arguments to an `__init__` whose parameter list starts with three names. `self` is a naming convention rather than a keyword, so Python would accept another name in its place, but SDK source and the Python documentation use `self` everywhere.

Reading the four `__init__` methods in `mockhub.py` with that rule tells you which attributes each instance has. `Token` and `Github` store each of their parameters under the parameter's own name. `Repository` stores `owner`, `name`, and `description` under their own names, builds `full_name` out of two of them, and stores `stars` under a different name, `stargazers_count`, which is the name PyGithub and the GitHub API use. `Issue` gives `labels` a new empty list when you don't pass one, by giving the parameter a default of `None` and creating the list inside `__init__`, so no two issues share a list. It also sets `state` to `"open"` without any parameter at all.

So a class's parameter list and its attribute list aren't the same list. The parameters say what you pass in, and the `self.` lines say what you can read back out. When you document a class, the difference is the one a reader trips on: someone who passes `stars=` and then reads `repo.stars` gets an `AttributeError`, because the instance has no attribute by that name.

`Issue` also defines `describe()`, which is a method, a function defined inside the class. You call a method through an object with parentheses, and `self` is how the method knows which object that was. When you call `first.describe()`, Python passes `first` as `self`, so the call means the same as `Issue.describe(first)`. Inside `describe()`, `self.number` holds the value you'd read from outside as `first.number`.

In SDK code, a call whose name starts with a capital letter usually creates an instance, because PEP 8, Python's style guide, names classes in CapWords, with a capital letter at the start of each word. `g = Github(auth=Token(token))` creates two instances, a `Token` and then a `Github`, and names the `Github` instance `g`, and `Path("docs")` creates a `Path`. A lowercase name after a dot, such as `g.get_repo("PyGithub/PyGithub")`, is a method call: it may hand back an instance, but the SDK built that instance, not your line. The convention has exceptions in Python's built-in classes, since `str`, `list`, and `dict` are classes with lowercase names, so `str(4300)` creates a string instance. When the name alone doesn't settle it, print the name without calling it: a class prints as `<class '…'>`.

## Syntax and Examples

The five examples below create an instance, follow the arguments of that call into `__init__`, show what `self` is, recognize the line that creates an SDK client, and finally create instances from a list of API-shaped dicts. Every example except the fourth catches its failing calls with `try` and `except`, so one run shows the working form and the failure together.

### Example 1: Create an instance by calling the class

This example creates one instance and sets it beside the class it came from, so you can tell the two apart on sight.

<details>
<summary>The <code>Repository</code> class from <code>mockhub.py</code></summary>

```python
class Repository:
    def __init__(self, owner, name, stars=0, description=None):
        self.owner = owner
        self.name = name
        self.full_name = f"{owner}/{name}"
        self.stargazers_count = stars
        self.description = description
```

</details>

The following script creates a `Repository`, reads two of its attributes, prints it, and then makes the mistake of leaving the parentheses off the class:

```python
from mockhub import Repository

repo = Repository("PyGithub", "PyGithub", stars=7400)
print(repo.full_name, repo.stargazers_count)
print(type(repo).__name__)
print(repo)

not_called = Repository
print(not_called)
print(type(not_called).__name__)
try:
    print(not_called.full_name)
except AttributeError as exc:
    print("AttributeError:", exc)
```

The following output shows the instance's attributes and class, how an instance prints, and how the class prints:

```output
PyGithub/PyGithub 7400
Repository
<mockhub.Repository object at 0x77d034194d70>
<class 'mockhub.Repository'>
type
AttributeError: type object 'Repository' has no attribute 'full_name'
```

`repo` is an instance, so its attributes hold the values `__init__` stored: `full_name` was built from the two strings, and `stargazers_count` holds the `stars` argument. `type(repo).__name__` names the class that built it. Printing the instance shows `<mockhub.Repository object at 0x…>`, which says only which module and class it came from, followed by its memory address. The address changes every run, so yours will differ. An instance whose class doesn't define how to display itself always prints this way, which is why you print its attributes when you want to see what's in it.

`not_called = Repository` has no parentheses, so nothing was called and no instance exists: `not_called` is just a second name for the class. It prints as `<class '…'>`, and its type is `type`, which is the type of a class. The class has no `full_name`, because `full_name` is set on each instance by `__init__`, and `__init__` never ran. So the read raised `AttributeError`, and the message calls the class a `type object`. Assigning a class to a name raises nothing, so leaving off the parentheses goes unnoticed until a later line reads an attribute, as this one does.

### Example 2: Follow the arguments into `__init__`

This example adds the constructor's side of the call: which argument lands in which parameter, which attributes the `self.` lines create, and what the error messages say when the call and the parameters don't match.

<details>
<summary>The <code>Repository</code> class from <code>mockhub.py</code></summary>

```python
class Repository:
    def __init__(self, owner, name, stars=0, description=None):
        self.owner = owner
        self.name = name
        self.full_name = f"{owner}/{name}"
        self.stargazers_count = stars
        self.description = description
```

</details>

The following script creates a `Repository` with one default left in place, lists its attributes with `vars()`, and then makes three mistakes:

```python
from mockhub import Repository

repo = Repository("psf", "requests", description="HTTP for Humans")
print(vars(repo))

try:
    Repository("psf")
except TypeError as exc:
    print("TypeError:", exc)
try:
    Repository("psf", "requests", 53000, "HTTP for Humans", "python")
except TypeError as exc:
    print("TypeError:", exc)
try:
    print(repo.stars)
except AttributeError as exc:
    print("AttributeError:", exc)
```

The following output shows every attribute the instance holds, then three failures:

```output
{'owner': 'psf', 'name': 'requests', 'full_name': 'psf/requests', 'stargazers_count': 0, 'description': 'HTTP for Humans'}
TypeError: Repository.__init__() missing 1 required positional argument: 'name'
TypeError: Repository.__init__() takes from 3 to 5 positional arguments but 6 were given
AttributeError: 'Repository' object has no attribute 'stars'
```

`vars()` returns a dict of the attributes an instance holds, which here are the ones `__init__` stored. The five keys match the five `self.` lines in `Repository`, in the order they ran, so `vars()` is the quickest way to check what a class's constructor actually set. The call passed `"psf"` and `"requests"` by position, so they landed in `owner` and `name`, and it passed `description` by keyword. `stars` wasn't passed, so its default of `0` ended up in `stargazers_count`.

The two `TypeError` messages name `Repository.__init__()` even though neither line mentions `__init__`, because calling the class is what runs it. The first call left out `name`, which has no default. The second message is the one to read carefully: the call passed five arguments, and the message says six were given, because Python counts the `self` it filled in. `__init__` takes three to five positional arguments for the same reason, `self` plus two required plus two optional. When a constructor error's count is one higher than you expect, `self` is the extra one.

The last failure is the parameter-and-attribute difference from the Terminology and Theory section. `stars` is the name of a parameter, but `__init__` stored its value as `stargazers_count`, so the instance has no `stars` attribute. The `self.` lines are the only place the attribute names are written, which is why the source or a `vars()` call settles the question faster than guessing from the parameter list.

### Example 3: Read `self` as the instance before the dot

This example adds a second and third instance of one class, to show that `self` holds a different object in each call, and calls the class's one method two ways.

<details>
<summary>The <code>Issue</code> class from <code>mockhub.py</code></summary>

```python
class Issue:
    def __init__(self, number, title, user=None, labels=None):
        if labels is None:
            labels = []
        self.number = number
        self.title = title
        self.user = user
        self.labels = labels
        self.state = "open"

    def describe(self):
        return f"#{self.number} {self.title} [{', '.join(self.labels)}]"
```

</details>

The following script creates three issues, changes two attributes on the second one only, and then calls `describe()` through an instance, through the class, and through the class with no instance:

```python
from mockhub import Issue

first = Issue(41, "Broken link in install.md", user="kmp", labels=["docs", "bug"])
second = Issue(42, "Clarify rate-limit.md")
third = Issue(43, "Add auth.md example", user="rivera")

second.labels.append("triage")
second.state = "closed"
print(first.labels, second.labels, third.labels)
print(first.user, second.user, third.user)
print(first.state, second.state, third.state)

print(first.describe())
print(second.describe())
print(Issue.describe(first))
try:
    Issue.describe()
except TypeError as exc:
    print("TypeError:", exc)
```

The following output shows each issue's own attributes, then three calls to `describe()` that succeed and one that fails:

```output
['docs', 'bug'] ['triage'] []
kmp None rivera
open closed open
#41 Broken link in install.md [docs, bug]
#42 Clarify rate-limit.md [triage]
#41 Broken link in install.md [docs, bug]
TypeError: Issue.describe() missing 1 required positional argument: 'self'
```

Each call to `Issue` ran `__init__` with a different new instance as `self`, so each `self.labels = labels` line stored a list on a different object. `second` and `third` both left `labels` out, and `__init__` gave each one a new empty list, so appending `"triage"` to `second.labels` left `third.labels` empty. `second.state = "closed"` is the same kind of line as `self.state = "open"` inside `__init__`, written from outside, and it changed only the instance before the dot. Every issue started with `state` set to `"open"` even though no call passed a state, because `__init__` sets it unconditionally.

`first.describe()` and `Issue.describe(first)` printed the same line, because they're the same call: Python takes the instance before the dot and passes it as `self`. Inside `describe()`, `self.number` and `self.title` are therefore `first.number` and `first.title`, and when `second` is before the dot, they're the second issue's. Calling `Issue.describe()` with no instance fails, and the message names the parameter it couldn't fill: `'self'`. That message tells you a method was called on a class instead of on an instance, and the fix is to create an instance first.

### Example 4: Recognize the lines that create an SDK client

This example adds the line every SDK script opens with, the one that creates the client, using the mock's `Github` and `Token` classes, which take the same `auth`, `base_url`, and `timeout` arguments as PyGithub's.

<details>
<summary><code>API_URL</code>, <code>Token</code>, and <code>Github</code> from <code>mockhub.py</code></summary>

```python
API_URL = "https://api.github.com"


class Token:
    def __init__(self, token):
        self.token = token


class Github:
    def __init__(self, auth=None, base_url=API_URL, timeout=15):
        self.auth = auth
        self.base_url = base_url
        self.timeout = timeout
```

</details>

The following script, saved as `client.py`, creates three clients, two of them authenticated with a `Token` built from one environment variable, and then prints three classes and a function by name:

```python
import os
from pathlib import Path
from mockhub import Github, Token

token = os.getenv("GITHUB_TOKEN")
g = Github(auth=Token(token))
enterprise = Github(auth=Token(token), base_url="https://ghe.example.com/api/v3", timeout=30)
anonymous = Github()

for client in [g, enterprise, anonymous]:
    has_auth = client.auth is not None
    print(f"{client.base_url:<32} timeout={client.timeout:<3} auth: {has_auth}")

print(type(g.auth).__name__, g.auth.token[:4])
print(Github, Token, Path, len)
```

The following command runs it with a made-up token set for this one run, so the output doesn't depend on any token you've exported:

```shellsession
$ GITHUB_TOKEN=ghp_example1234abcd python3 client.py
https://api.github.com           timeout=15  auth: True
https://ghe.example.com/api/v3   timeout=30  auth: True
https://api.github.com           timeout=15  auth: False
Token ghp_
<class 'mockhub.Github'> <class 'mockhub.Token'> <class 'pathlib.Path'> <built-in function len>
```

`g = Github(auth=Token(token))` is the line to recognize, and it creates two instances. Python runs the inner call first: `Token(token)` creates a `Token` instance that holds the token string, and that instance becomes the `auth` argument of `Github(...)`, which creates the client. The client is assigned to a short name, `g`, that the rest of the script uses, and its `base_url` and `timeout` came from the defaults in `__init__`. `enterprise` overrode both defaults by keyword, which is how you'd point a client at a company's own GitHub server. `anonymous` passed nothing, so its `auth` kept the default of `None`, which is how a client reads public data without a token. Each client is its own instance, so changing one's settings never changes another's.

The fourth line of output shows where the token ended up. `g.auth` is the `Token` instance, so `type(g.auth).__name__` is `Token`, and `g.auth.token` is the string that instance stored, sliced to its first four characters so the token never prints whole. The last line printed `Github`, `Token`, and `Path` as classes and `len` as a function, which is the check to use when a name's capital letter, or lack of one, leaves you unsure.

Real PyGithub code differs from the mock only in where `Token` lives. PyGithub keeps it in a module called `Auth`, so you import `Auth` and write `Auth.Token(token)`, reaching into the module for the class the same way `argparse.ArgumentParser(...)` reached into `argparse`. Running it needs PyGithub installed, so here you only read it.

The following lines create a client the way PyGithub 2.10.0 documents it:

```python
import os
from github import Auth, Github

token = os.getenv("GITHUB_TOKEN")
g = Github(auth=Auth.Token(token))
```

The real `Github.__init__` takes 16 parameters after `self`, every one with a default, and `base_url` defaults to `"https://api.github.com"` and `timeout` to `15`, which are the defaults the mock copies. Older scripts and tutorials pass the token straight to the client as `Github(token)`, which puts it in the first parameter, `login_or_token`. PyGithub 2.10.0 still accepts that form, but it prints a `DeprecationWarning` whose message reads `Argument login_or_token is deprecated, please use auth=github.Auth.Token(...) instead`. When you meet `Github(token)` in someone else's code, read it as the same client creation, and write the `auth=` form in your own.

### Example 5: Create instances from API-shaped dicts

This example adds many instances at once, built from dicts like the ones an API returns, with `**` and a list comprehension, and sorts them by an attribute with the `key=` argument of `sorted()`.

<details>
<summary>The <code>Repository</code> class from <code>mockhub.py</code></summary>

```python
class Repository:
    def __init__(self, owner, name, stars=0, description=None):
        self.owner = owner
        self.name = name
        self.full_name = f"{owner}/{name}"
        self.stargazers_count = stars
        self.description = description
```

</details>

The following script creates three `Repository` instances from made-up records, ranks them by star count, and then passes a dict whose key is an attribute name instead of a parameter name:

```python
from mockhub import Repository

records = [
    {"owner": "psf", "name": "requests", "stars": 410},
    {"owner": "pallets", "name": "flask", "stars": 950, "description": "Microframework"},
    {"owner": "PyGithub", "name": "PyGithub", "stars": 410},
]
repos = [Repository(**record) for record in records]
for repo in sorted(repos, key=lambda r: r.stargazers_count, reverse=True):
    print(f"{repo.full_name:<18} {repo.stargazers_count:>4} {repo.description or '-'}")

try:
    Repository(**{"owner": "psf", "name": "requests", "stargazers_count": 410})
except TypeError as exc:
    print("TypeError:", exc)
```

The following output shows the three instances ranked, and the dict the constructor refused:

```output
pallets/flask       950 Microframework
psf/requests        410 -
PyGithub/PyGithub   410 -
TypeError: Repository.__init__() got an unexpected keyword argument 'stargazers_count'
```

`Repository(**record)` spreads each dict into keyword arguments, so the first record becomes `Repository(owner="psf", name="requests", stars=410)`, and the comprehension does that once per record. The two records without a `description` got the default `None`, and `repo.description or '-'` printed `-` in its place, because `or` returns its right side when its left side is false, and `None` counts as false. `requests` and `PyGithub` tie at 410, so they stayed in the order they had in `records`, because `sorted()` keeps tied items in their original order. The lambda reads `r.stargazers_count`, the attribute name, because by the time `sorted()` runs, each item is an instance, not a dict.

The refused dict used `stargazers_count`, which is the attribute's name, and the constructor accepts only its own parameter names, so it raised `TypeError` naming the unexpected keyword. A real API response is full of keys that a constructor may not accept, so check the dict's keys against the parameter list of `__init__`, not against the attribute names you've read off an instance.

### Patterns worth knowing by heart

The following patterns are the ones worth memorizing, and everything else in this lesson is for looking up:

- `name = ClassName(arguments)` creates an instance, and `name.attribute` reads what `__init__` stored on it.
- The `self.` lines in `__init__` are the list of attribute names, and the parameter list is the list of what you pass in.
- `vars(instance)` shows every attribute an instance holds, with its value.
- `[ClassName(**record) for record in records]` creates one instance per dict, as long as the dicts' keys are the parameter names.

## Lookup Table

The following table covers everything this lesson introduces, with every result taken from a real run:

| Task | Call | Result |
| --- | --- | --- |
| Define a class | `class Issue:` with a `def __init__(self, ...):` block | the definition is stored under the name `Issue`, and no instance exists yet |
| Store an argument on the new instance | `self.title = title` inside `__init__` | every instance has a `title` attribute holding its own argument |
| Create an instance | `repo = Repository("PyGithub", "PyGithub", stars=7400)` | a `Repository` instance whose `full_name` is `'PyGithub/PyGithub'` and `stargazers_count` is `7400` |
| Name the class an instance came from | `type(repo).__name__` | `'Repository'` |
| Print an instance whose class has no display of its own | `print(repo)` | `<mockhub.Repository object at 0x77d034194d70>`, with an address that changes every run |
| Accidentally leave the parentheses off the class | `not_called = Repository` | `not_called` prints as `<class 'mockhub.Repository'>`, and its type is `type` |
| Accidentally read an attribute from the class | `Repository.full_name` | raises `AttributeError: type object 'Repository' has no attribute 'full_name'` |
| List every attribute an instance holds | `vars(repo)` | `{'owner': 'psf', 'name': 'requests', 'full_name': 'psf/requests', 'stargazers_count': 0, 'description': 'HTTP for Humans'}` |
| Accidentally leave out a required argument | `Repository("psf")` | raises `TypeError: Repository.__init__() missing 1 required positional argument: 'name'` |
| Accidentally pass too many arguments | `Repository("psf", "requests", 53000, "HTTP for Humans", "python")` | raises `TypeError: Repository.__init__() takes from 3 to 5 positional arguments but 6 were given`, with `self` in both counts |
| Accidentally read a parameter name as an attribute | `repo.stars` | raises `AttributeError: 'Repository' object has no attribute 'stars'` |
| Give each instance its own default list | `Issue(42, "Clarify rate-limit.md")` and `Issue(43, "Add auth.md example")` | appending to the first one's `labels` leaves the second one's `[]` |
| Read an attribute no parameter sets | `second.state` | `'open'` on every new `Issue` |
| Change an attribute on one instance | `second.state = "closed"` | `second.state` is `'closed'`, and the other issues' `state` stays `'open'` |
| Call a method through an instance | `first.describe()` | `'#41 Broken link in install.md [docs, bug]'` |
| Pass the instance as `self` explicitly | `Issue.describe(first)` | the same string as `first.describe()` |
| Accidentally call a method on the class alone | `Issue.describe()` | raises `TypeError: Issue.describe() missing 1 required positional argument: 'self'` |
| Create an SDK client with a token | `g = Github(auth=Token(token))` | `Token(token)` runs first, and its instance becomes `g.auth`; `g.base_url` is `'https://api.github.com'` and `g.timeout` is `15`, both from the defaults |
| Read an instance stored on another instance | `type(g.auth).__name__, g.auth.token[:4]` | `('Token', 'ghp_')` |
| Override a constructor's defaults | `Github(auth=Token(token), base_url="https://ghe.example.com/api/v3", timeout=30)` | `base_url` and `timeout` hold the values passed |
| Create an instance with every default | `Github()` | `auth` is `None`, a client with no token |
| Check whether a name is a class | `print(Github, Token, Path, len)` | `<class 'mockhub.Github'> <class 'mockhub.Token'> <class 'pathlib.Path'> <built-in function len>` |
| Create a real PyGithub client | `Github(auth=Auth.Token(token))` | `Auth.Token(token)` creates a `Token` instance from PyGithub's `Auth` module, and it becomes the `auth` argument |
| Recognize the deprecated client form | `Github(token)` in PyGithub 2.10.0 | creates the client, and prints `DeprecationWarning: Argument login_or_token is deprecated, please use auth=github.Auth.Token(...) instead` |
| Create one instance per dict | `[Repository(**record) for record in records]` | three `Repository` instances, with `description` set to `None` where a record lacks it |
| Accidentally pass an attribute name as a keyword | `Repository(**{"owner": "psf", "name": "requests", "stargazers_count": 410})` | raises `TypeError: Repository.__init__() got an unexpected keyword argument 'stargazers_count'` |
| Sort instances by an attribute | `sorted(repos, key=lambda r: r.stargazers_count, reverse=True)` | `pallets/flask`, then `psf/requests` and `PyGithub/PyGithub`, tied at 410, in their original order |

## Exercise: Report on a tracker file's issues

Write `issue_report.py`, which reads a tracker file, turns its records into instances of the `mockhub` classes, and prints a report built from those instances' attributes.

The following is `tracker.json`, the input file to create beside your script, and its fourth record carries a key that `Issue` doesn't accept:

```json
{
  "repository": {"owner": "JoshGo6", "name": "ThrowAway", "description": "Practice repository for API writes"},
  "issues": [
    {"number": 41, "title": "Broken link in install.md", "user": "kmp", "labels": ["docs", "bug"]},
    {"number": 42, "title": "Clarify rate-limit.md"},
    {"number": 43, "title": "Add auth.md example", "user": "rivera", "labels": ["docs"]},
    {"number": 44, "title": "Rename api.md", "user": "kmp", "labels": ["docs"], "state": "closed"},
    {"number": 45, "title": "Document the version header", "user": "rivera", "labels": ["api", "docs", "triage"]}
  ]
}
```

Your script must do all of the following:

1. Import `Token`, `Github`, `Repository`, and `Issue` from `mockhub.py`, and change nothing in that module.
2. Take the tracker file's path as a required positional argument, and accept an optional `--base-url` flag, both explained under `--help`.
3. Create one `Github` instance. When the `GITHUB_TOKEN` environment variable is set, the client's `auth` is a `Token` instance holding the variable's value, and when it isn't, the client has no `auth`. When `--base-url` is given, the client's `base_url` is that value. When it isn't, the client's `base_url` comes from the class's own default, and the URL `https://api.github.com` appears nowhere in your script. Print the client's base URL, its timeout, and the class name of its `auth` instance, or `none` when it has no `auth`.
4. Create one `Repository` instance from the file's `repository` object, and print the instance's full name and description.
5. Create one `Issue` instance from each record in `issues`, passing the record's keys and values to the constructor as keyword arguments. When the constructor rejects a record, log a warning that names the issue number and the exception's message, and go on to the next record.
6. Print one line per `Issue` instance, ordered by how many labels it has, most first, with ties kept in file order. Each line shows what the instance's `describe()` method returns, then the instance's user, or `nobody` when it has none, and then the instance's state.
7. Finish with a line saying how many records became `Issue` instances, out of how many records the file holds.

### Expected output

The wording and spacing of your output may differ, but the base URL, timeout, `auth` class name, repository name, description, issue numbers, titles, labels, users, states, and counts must match, in the same order.

The following is what my own solution printed, with the warning line coming from `logging` on standard error:

```output
client: https://api.github.com (timeout 15, auth Token)
JoshGo6/ThrowAway: Practice repository for API writes
WARNING:root:skipped issue 44: Issue.__init__() got an unexpected keyword argument 'state'
  #45 Document the version header [api, docs, triage] by rivera, open
  #41 Broken link in install.md [docs, bug] by kmp, open
  #43 Add auth.md example [docs] by rivera, open
  #42 Clarify rate-limit.md [] by nobody, open
4 of 5 records became Issue instances
```

The following command is the one that produced it, with a made-up token set for this one run so the output doesn't depend on any token you've exported:

```bash
GITHUB_TOKEN=ghp_example1234abcd python3 issue_report.py tracker.json
```

Run it a second time with `--base-url https://ghe.example.com/api/v3` added, and the first line changes to `client: https://ghe.example.com/api/v3 (timeout 15, auth Token)` while the rest stays the same.

## Review

These three drills practice Python syntax outside this lesson's topic, and nothing else in this lesson depends on them. Write each one from memory, run it, and compare your output with the expected output before you open the answer.

### Drill 1: Pretty-print a record as JSON

Turn the dict `{"number": 41, "labels": ["docs", "bug"]}` into a JSON string indented by two spaces, using the `json` module, and print it.

The following is the output to expect:

```output
{
  "number": 41,
  "labels": [
    "docs",
    "bug"
  ]
}
```

<details>
<summary>Answer</summary>

```python
import json

print(json.dumps({"number": 41, "labels": ["docs", "bug"]}, indent=2))
```

</details>

### Drill 2: Take a path apart

Create a `Path` for `docs/api/auth.md` with `pathlib`, and print its stem, its suffix, and its parent on one line.

The following is the output to expect:

```output
auth .md docs/api
```

<details>
<summary>Answer</summary>

```python
from pathlib import Path

p = Path("docs/api/auth.md")
print(p.stem, p.suffix, p.parent)
```

</details>

### Drill 3: Pull issue numbers out of a line

Use `re.findall()` with a group to pull every issue number out of the string `"Fixes #41 and #42, see #7"`, without the `#`, and print the list.

The following is the output to expect:

```output
['41', '42', '7']
```

<details>
<summary>Answer</summary>

```python
import re

print(re.findall(r"#(\d+)", "Fixes #41 and #42, see #7"))
```

</details>
