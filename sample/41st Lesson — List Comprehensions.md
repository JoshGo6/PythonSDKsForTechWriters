# Lesson 41: Read and write list comprehensions

A list comprehension builds a new list from an existing one in a single line, which is the job a `for` loop does when all its body does is call `.append()`. This lesson teaches you to read a comprehension by unpacking it into that loop, to write the two forms you'll meet most often, one that changes every item and one that also drops some, and to tell when a loop should stay a loop. It leaves out the comprehensions that build a dict, a set, or a generator, comprehensions with two `for` clauses, and comprehensions that choose between two values with `if` and `else`.

Every example that calls GitHub sends an unauthenticated `GET` to `https://api.github.com`, so nothing is created or changed, and each one uses one of the 60 requests an hour that GitHub allows a client that doesn't sign in.

## Set up the examples

Every code block in this lesson runs on its own, so you never scroll back to find something an earlier block defined. When a block needs one of the samples below, a sample of three lines or fewer is written into the block itself. A longer one sits in a collapsed copy directly above the block: click its title to expand it, and paste its code in front of the block's code before you run it. Run everything in a virtual environment that has the `requests` library installed, which `pip install requests` does from inside the environment.

`issues` is a list of three issue dicts, so a comprehension that drops one issue still returns more than one. The second issue is missing `user` and `labels` on purpose, so a comprehension that reads `user` has to cope with a key that isn't there.

The following list holds three issues, and the second has no `user` or `labels`:

```python
issues = [
    {"number": 41, "title": "Broken link in install.md", "user": {"login": "kmp"},
     "labels": ["docs", "bug"]},
    {"number": 42, "title": "Clarify rate-limit.md"},
    {"number": 43, "title": "Add auth.md example", "user": {"login": "rivera"},
     "labels": ["docs"]},
]
```

`files` holds six file names, and one of them isn't a Markdown file, so a comprehension that keeps only Markdown files has something to drop.

The following list is one line long, so every block that uses it repeats it:

```python
files = ["install.md", "api.md", "auth.md", "rate-limit.md", "index.md", "notes.txt"]
```

`results` is a real response from GitHub's issues endpoint for the `psf/requests` repository. Asking for closed entries, oldest first, returns entries from 2011 that no longer change, so the output in this lesson matches what you'll see.

The following script fetches the repository's eight oldest closed entries:

```python
import requests

url = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "direction": "asc", "per_page": 8}
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
response = requests.get(url, params=params, headers=headers, timeout=10)
response.raise_for_status()
results = response.json()
```

## Terminology and Theory

A **list comprehension** is an expression that builds a new list by running a short loop inside square brackets. An **expression** is any piece of code that Python evaluates to one value, such as `issue["title"]`, `len(files)`, or `name.upper()`. A comprehension is an expression itself, so you can assign its list to a name, print it, or pass it to a function, like any other value.

An **iterable** is anything a `for` loop can walk through, such as a list, a string, or a file handle. A comprehension walks through an iterable too, and it has up to three parts.

The following line names the three parts in the order they're written:

```text
[expression for item in iterable if condition]
```

The **`for` clause** is `for item in iterable`, and it works the way the first line of a `for` loop does: it takes each item of the iterable in turn and assigns it to the loop variable, which is `item` here. The **`if` clause** is `if condition`, and it's optional. It decides whether the current item is kept. The expression at the front says what each kept item becomes in the new list.

Every comprehension unpacks into a loop with the same parts, and reading a comprehension means mapping each part onto that loop. The loop starts with an empty list. The `for` clause becomes the loop's first line, the `if` clause becomes an `if` inside the loop, and inside that `if`, the loop appends the expression's value to the list. The Syntax section shows each comprehension beside the loop it unpacks into.

Python runs the parts in the loop's order, not in the order they're written: the `for` clause first, then the `if` clause, and the expression last, only for the items that passed. So read a comprehension starting at `for`, then read the `if`, and come back to the expression at the front last. The empty list and the `.append()` don't appear in a comprehension, because the square brackets stand for both.

A comprehension builds a new list and leaves the iterable as it was. Some calls build a new value and leave the original alone, such as `name.replace(".md", ".html")`, and others change the object in place, such as `pages.append(name)`. A comprehension works like the first kind, so a comprehension on a line with no `=` builds a list and then throws it away.

Not every loop can become a comprehension. You can rewrite a loop as one only when its body does nothing but append one value per item, either always or under a single `if`. A loop that prints, logs, appends to two lists, or has an `else` branch stays a loop, because a comprehension has nowhere to put the extra work. When you aren't sure, keep the loop: it builds the same list, and the comprehension only saves lines.

## Syntax

The first three sections below build lists: one from every item, one from the items that pass a test, and one that does both at once. The next two cover the mistakes a comprehension's expression and its `if` clause invite. The last two show where a comprehension's loop variable lives, and why `print()` doesn't belong inside one.

### Build a list from every item

A comprehension with no `if` clause turns every item of the iterable into one item of the new list. The block below builds a list of titles from the `issues` sample twice, once with a loop and once with a comprehension, and then compares the two lists with `==`.

<details>
<summary>The <code>issues</code> sample</summary>

```python
issues = [
    {"number": 41, "title": "Broken link in install.md", "user": {"login": "kmp"},
     "labels": ["docs", "bug"]},
    {"number": 42, "title": "Clarify rate-limit.md"},
    {"number": 43, "title": "Add auth.md example", "user": {"login": "rivera"},
     "labels": ["docs"]},
]
```

</details>

The following block builds the same list with a loop and with a comprehension:

```python
titles = []
for issue in issues:
    titles.append(issue["title"])

titles_comp = [issue["title"] for issue in issues]

print(titles)
print(titles_comp)
print(titles == titles_comp)
```

The following output shows two identical lists:

```output
['Broken link in install.md', 'Clarify rate-limit.md', 'Add auth.md example']
['Broken link in install.md', 'Clarify rate-limit.md', 'Add auth.md example']
True
```

In the comprehension, the expression is `issue["title"]` and the `for` clause is `for issue in issues`. Map them onto the loop: `for issue in issues` is the loop's first line, and `issue["title"]` is what the loop appends. There's no `if` clause, so every issue contributes one title, and the new list has three items, the same number as `issues`.

### Keep only the items that pass a test

An `if` clause after the `for` clause drops every item whose condition is false. When the expression is the loop variable on its own, as `name` is here, the items that pass go into the new list unchanged.

The following block keeps the Markdown files, once with a loop and once with a comprehension:

```python
files = ["install.md", "api.md", "auth.md", "rate-limit.md", "index.md", "notes.txt"]

pages = []
for name in files:
    if name.endswith(".md"):
        pages.append(name)

pages_comp = [name for name in files if name.endswith(".md")]

print(pages_comp)
print(pages == pages_comp)
print(len(files), "names in,", len(pages_comp), "kept")
```

The following output shows that `notes.txt` was dropped:

```output
['install.md', 'api.md', 'auth.md', 'rate-limit.md', 'index.md']
True
6 names in, 5 kept
```

The `if` clause ran once per name, and `notes.txt` failed it, so it never reached the expression. Six names went in and five came out, and that difference is how you spot an `if` clause at work: a comprehension without one always returns a list as long as its iterable.

### Change and filter items in one comprehension

A comprehension can change each item and drop some items at once, by putting a call in the expression and a test in the `if` clause. The order Python runs the parts in decides what the test sees.

The following block renames the Markdown files to `.html`, and then repeats the comprehension with the wrong test:

```python
files = ["install.md", "api.md", "auth.md", "rate-limit.md", "index.md", "notes.txt"]

html = [name.replace(".md", ".html") for name in files if name.endswith(".md")]
print(html)

html_wrong = [name.replace(".md", ".html") for name in files if name.endswith(".html")]
print(html_wrong)
```

The following output shows five renamed files, then an empty list:

```output
['install.html', 'api.html', 'auth.html', 'rate-limit.html', 'index.html']
[]
```

The `if` clause runs before the expression, so it tests the original name, not the renamed one. In the second comprehension, no original name ends in `.html`, so every item failed the test and the list came back empty. An empty list is a valid result, so a test written against the changed value doesn't raise anything, and the only sign of the mistake is the missing output. Write the `if` clause to test the item before the expression changes it.

### Handle a key that some records lack

When the expression reads a key that one record doesn't have, the whole comprehension raises `KeyError`. Issue 42 in the `issues` sample has no `user` key, so a comprehension that reads every issue's login fails on it.

<details>
<summary>The <code>issues</code> sample</summary>

```python
issues = [
    {"number": 41, "title": "Broken link in install.md", "user": {"login": "kmp"},
     "labels": ["docs", "bug"]},
    {"number": 42, "title": "Clarify rate-limit.md"},
    {"number": 43, "title": "Add auth.md example", "user": {"login": "rivera"},
     "labels": ["docs"]},
]
```

</details>

The following block reads every login, and then tries two ways around the missing key:

```python
try:
    logins = [issue["user"]["login"] for issue in issues]
except KeyError as exc:
    print("KeyError:", exc)

with_fallback = [issue.get("user", {}).get("login", "unknown") for issue in issues]
only_present = [issue["user"]["login"] for issue in issues if "user" in issue]
print(with_fallback)
print(only_present)
```

The following output shows the failure, then two lists of different lengths:

```output
KeyError: 'user'
['kmp', 'unknown', 'rivera']
['kmp', 'rivera']
```

The first comprehension raised on issue 42, and `logins` was never assigned. A comprehension is one expression, so it either builds the whole list or raises, and nothing keeps the login it had already read from issue 41. The two fixes give different answers. `with_fallback` uses `.get()` with a default, which returns the default instead of raising `KeyError` when the key is missing, so it keeps one entry per issue and puts `'unknown'` where the login is missing. `only_present` adds an `if` clause that skips any issue without a `user` key, so it's shorter than `issues`. When each item of the list has to line up with a record, such as one report line per issue, use `.get()`, and when the missing records shouldn't appear at all, use the `if` clause.

### Leave `else` out of the `if` clause

The `if` clause only decides whether an item is kept, so it takes no `else`. Adding one is a syntax error, which Python reports before it runs any of the script.

The following command adds an `else` to the `if` clause:

```shellsession
$ python3 -c 'files = ["api.md", "notes.txt"]; print([name for name in files if name.endswith(".md") else "skip"])'
  File "<string>", line 1
    files = ["api.md", "notes.txt"]; print([name for name in files if name.endswith(".md") else "skip"])
                                                                                           ^^^^
SyntaxError: invalid syntax
```

The caret points at the `else`, and nothing printed, not even the first statement, because Python checks the syntax of the whole script before it runs any line of it. A comprehension that keeps every item and swaps some of them for another value puts its `if` and `else` before the `for`.

### Use the loop variable only inside the brackets

A comprehension's loop variable exists only inside its square brackets, but a `for` loop's variable stays defined after the loop ends. The difference matters when you rewrite a loop as a comprehension and a line after the loop still reads the loop variable.

The following block reads `page` after a comprehension, and then after a loop:

```python
files = ["install.md", "api.md", "auth.md", "rate-limit.md", "index.md", "notes.txt"]

pages = [page for page in files if page.endswith(".md")]
try:
    print(page)
except NameError as exc:
    print("NameError:", exc)

loop_pages = []
for page in files:
    if page.endswith(".md"):
        loop_pages.append(page)
print(page)
```

The following output shows the comprehension's `page` gone and the loop's `page` still set:

```output
NameError: name 'page' is not defined
notes.txt
```

After the comprehension, no variable named `page` exists, so reading it raised `NameError`. After the loop, `page` holds the last item the loop looped over, which is `notes.txt`, even though the `if` rejected it. So before you replace a loop with a comprehension, check the lines after the loop for its variable, because after the rewrite each of those lines raises `NameError`.

### Keep `print()` out of a comprehension

A comprehension whose expression is a `print()` call prints every item, but it also builds a list nobody uses, and the list holds what `print()` returns.

The following block prints two names from inside a comprehension, and then prints the list the comprehension built:

```python
files = ["install.md", "api.md", "auth.md", "rate-limit.md", "index.md", "notes.txt"]

shown = [print(name) for name in files[:2]]
print(shown)
```

The following output shows the two names, then a list of two `None` values:

```output
install.md
api.md
[None, None]
```

`print()` returns `None`, as any function with no `return` statement does, so the comprehension built `[None, None]`. The printing happened as a side effect of building that list. In a script, write a loop when the point is to print, and keep comprehensions for building lists you're going to use.

## Worked Examples

Each example adds one thing to the one before it, starting with one comprehension over a real response and ending with a loop that shouldn't be rewritten. Every example starts from `results`, the response the setup section fetched, and every output block is from a real run against `api.github.com`.

### Example 1: Turn an API response into report lines

This example adds real data: a comprehension over `results` that builds one formatted line per entry.

<details>
<summary>The <code>results</code> sample</summary>

```python
import requests

url = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "direction": "asc", "per_page": 8}
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
response = requests.get(url, params=params, headers=headers, timeout=10)
response.raise_for_status()
results = response.json()
```

</details>

The following script builds the lines and prints them:

```python
lines = [f"#{issue['number']} {issue['title']}" for issue in results]
print(len(lines), "lines")
for line in lines:
    print(line)
```

The following output shows one line per entry:

```output
8 lines
#1 Cookie support?
#2 a "40x" error my have content
#3 Eventlet Support
#4 Updates and Cleanup
#5 Case-Insensitive MultiDict for Headers
#6 parse url parameter and set params
#7 POST + file + auth
#8 Small workaround for issue #7
```

The expression is an f-string, so each entry becomes a string built from two of its fields. The keys inside the f-string use single quotes because the f-string itself is in double quotes. The printing happens in a separate loop, because printing is the extra work a comprehension shouldn't do. Two of these eight entries, 4 and 8, aren't issues at all: GitHub treats every pull request as an issue too, so its issues endpoint returns both.

### Example 2: Drop the pull requests that GitHub returns as issues

This example adds an `if` clause that tests whether each entry has a key.

<details>
<summary>The <code>results</code> sample</summary>

```python
import requests

url = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "direction": "asc", "per_page": 8}
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
response = requests.get(url, params=params, headers=headers, timeout=10)
response.raise_for_status()
results = response.json()
```

</details>

The following script keeps only the entries that have no `pull_request` key:

```python
real_issues = [issue for issue in results if "pull_request" not in issue]
print(len(results), "entries,", len(real_issues), "issues")
for issue in real_issues:
    print(f"#{issue['number']} {issue['title']}")
```

The following output shows six issues left out of eight entries:

```output
8 entries, 6 issues
#1 Cookie support?
#2 a "40x" error my have content
#3 Eventlet Support
#5 Case-Insensitive MultiDict for Headers
#6 parse url parameter and set params
#7 POST + file + auth
```

GitHub adds a `pull_request` key only to the entries that are pull requests, so `"pull_request" not in issue` is true for the real issues, because `in` tests a dict's keys, not its values. The expression is the loop variable on its own, so `real_issues` holds the whole dict for each issue, and the loop below it can still read any field. Entries 4 and 8 are gone.

### Example 3: Join a comprehension's numbers into one line

This example adds a comprehension whose list goes straight into another call, `", ".join()`, and the conversion that call needs.

<details>
<summary>The <code>results</code> sample</summary>

```python
import requests

url = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "direction": "asc", "per_page": 8}
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
response = requests.get(url, params=params, headers=headers, timeout=10)
response.raise_for_status()
results = response.json()
```

</details>

The following script collects the pull requests' numbers, and then joins them with and without converting them first:

```python
pr_numbers = [issue["number"] for issue in results if "pull_request" in issue]
print(pr_numbers)
try:
    print(", ".join(pr_numbers))
except TypeError as exc:
    print("TypeError:", exc)
print(", ".join([str(number) for number in pr_numbers]))
```

The following output shows the list, the failed join, and the working one:

```output
[4, 8]
TypeError: sequence item 0: expected str instance, int found
4, 8
```

GitHub sends issue numbers as JSON numbers, so `pr_numbers` holds the integers `4` and `8`. `", ".join()` combines a list's items into one string with `, ` between them. It accepts only strings, and the `TypeError` says which item it stopped on: item 0, the `4`. The last line passes `.join()` a second comprehension whose expression is `str(number)`, which converts each number to a string before the join sees it.

### Example 4: Call a function that holds its own comprehension

This example adds a comprehension inside a function, and calls that function from another comprehension's expression.

<details>
<summary>The <code>results</code> sample</summary>

```python
import requests

url = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "direction": "asc", "per_page": 8}
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
response = requests.get(url, params=params, headers=headers, timeout=10)
response.raise_for_status()
results = response.json()
```

</details>

The following script prints each entry's label names:

```python
def label_names(issue):
    names = [label["name"] for label in issue["labels"]]
    return ", ".join(names) or "no labels"

lines = [f"#{issue['number']} [{label_names(issue)}]" for issue in results]
for line in lines:
    print(line)
```

The following output shows one labeled entry among eight:

```output
#1 [no labels]
#2 [no labels]
#3 [no labels]
#4 [no labels]
#5 [no labels]
#6 [Feature Request]
#7 [no labels]
#8 [no labels]
```

GitHub sends each label as a dict with a `name` key, so `label_names` uses a comprehension to pull out the names, and the outer comprehension calls `label_names` once per entry. Seven entries have an empty `labels` list. A comprehension over an empty list returns an empty list without raising, `.join()` turns that into an empty string, and an empty string is falsy, meaning Python treats it as false in a test. `or` returns the value on its right when the value on its left is falsy, so it returns `"no labels"` in place of the empty string.

### Example 5: Keep the loop when it logs what it skips

This example adds a loop that can't become a comprehension, because its body logs a message as well as appending.

<details>
<summary>The <code>results</code> sample</summary>

```python
import requests

url = "https://api.github.com/repos/psf/requests/issues"
params = {"state": "closed", "direction": "asc", "per_page": 8}
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
response = requests.get(url, params=params, headers=headers, timeout=10)
response.raise_for_status()
results = response.json()
```

</details>

The following script keeps the issues and logs each pull request it skips:

```python
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
real_issues = []
for issue in results:
    if "pull_request" in issue:
        logging.info("skipped pull request #%s", issue["number"])
    else:
        real_issues.append(issue)
print(len(real_issues), "issues kept")
```

The following output shows a log line for each pull request, then the count:

```output
INFO skipped pull request #4
INFO skipped pull request #8
6 issues kept
```

`real_issues` holds the same six issues as in Example 2, but the loop also records what it dropped, and a comprehension can only produce the list's items. Rewriting this loop as the comprehension from Example 2 would build the same list and lose both `INFO` lines. A loop whose body has an `else` branch, or does anything besides append, stays a loop.

## Lookup Table

The following table covers everything this lesson introduces, with every result taken from a real run:

| Task | Call | Result |
| --- | --- | --- |
| Build a list from every item | `[issue["title"] for issue in issues]` | `['Broken link in install.md', 'Clarify rate-limit.md', 'Add auth.md example']` |
| Keep only the items that pass a test | `[name for name in files if name.endswith(".md")]` | `['install.md', 'api.md', 'auth.md', 'rate-limit.md', 'index.md']`, with `notes.txt` dropped |
| Change and filter items in one comprehension | `[name.replace(".md", ".html") for name in files if name.endswith(".md")]` | `['install.html', 'api.html', 'auth.html', 'rate-limit.html', 'index.html']` |
| Accidentally test the changed value in the `if` clause | `[name.replace(".md", ".html") for name in files if name.endswith(".html")]` | `[]`, because the `if` clause tests the original name, and nothing raises |
| Drop the records that have a key | `[issue for issue in results if "pull_request" not in issue]` | six of the eight entries, with pull requests 4 and 8 dropped |
| Accidentally read a key that one record lacks | `[issue["user"]["login"] for issue in issues]` | raises `KeyError: 'user'`, and no list is built |
| Supply a fallback for a missing key | `[issue.get("user", {}).get("login", "unknown") for issue in issues]` | `['kmp', 'unknown', 'rivera']` |
| Skip the records that lack a key | `[issue["user"]["login"] for issue in issues if "user" in issue]` | `['kmp', 'rivera']` |
| Accidentally put `else` in the `if` clause | `[name for name in files if name.endswith(".md") else "skip"]` | raises `SyntaxError: invalid syntax` before any line runs |
| Accidentally read the loop variable after a comprehension | `print(page)` after `[page for page in files if page.endswith(".md")]` | raises `NameError: name 'page' is not defined` |
| Read the loop variable after a `for` loop | `print(page)` after `for page in files:` | `notes.txt`, the last item looped over |
| Accidentally print from inside a comprehension | `[print(name) for name in files[:2]]` | prints `install.md` and `api.md`, and builds `[None, None]` |
| Build formatted lines from a response | `[f"#{issue['number']} {issue['title']}" for issue in results]` | eight strings, starting with `'#1 Cookie support?'` |
| Accidentally join a list of numbers | `", ".join([4, 8])` | raises `TypeError: sequence item 0: expected str instance, int found` |
| Convert numbers to strings before joining | `", ".join([str(number) for number in [4, 8]])` | `'4, 8'` |
| Loop over an empty list | `[label["name"] for label in []]` | `[]`, and nothing raises |
| Call a function from the expression | `[f"#{issue['number']} [{label_names(issue)}]" for issue in results]` | `'#6 [Feature Request]'` for the one labeled entry, and `[no labels]` for the other seven |

## Exercise: Print an issue digest for three repositories

Write `issue_digest.py`, which fetches the oldest closed entries from three repositories and prints a short digest of each one.

Your script must do all of the following:

1. Define one function that takes a repository name and any number of query filters given by name. It sends the filters as the query string of that repository's issues endpoint, with the `Accept` and `X-GitHub-Api-Version` headers and a timeout, turns a failing status into an exception, and returns the parsed list.
2. Call the function for `psf/requests`, `PyGithub/PyGithub`, and `psf/no-such-repo-xyz`, in that order, each time asking for closed entries, oldest first, six per page.
3. When a request fails with a bad status, print the repository and the status code the exception carries, then go on to the next repository.
4. For each repository that answers, print its name and the number of entries it returned. Under that, print one line for each entry that isn't a pull request, showing its number, its label names separated by `, ` or `no labels` when it has none, and its title.
5. Print the numbers of the pull requests on one line, separated by `, `, or `none` when there aren't any.
6. The following loop collects the numbers of the entries that have at least one label, and your script rewrites it as a comprehension assigned to the same name, then prints its numbers on one line the way step 5 does:

   ```python
   labeled = []
   for entry in entries:
       if entry["labels"]:
           labeled.append(entry["number"])
   ```

7. Build every list in the script with a comprehension, so that the script never calls `.append()`.

### Expected output

The wording and indentation of your lines may differ, but the issue numbers, the labels, the titles, and the two lists of numbers must match.

The following is what my own solution printed:

```output
psf/requests: 6 entries
  #1 [no labels] Cookie support?
  #2 [no labels] a "40x" error my have content
  #3 [no labels] Eventlet Support
  #5 [no labels] Case-Insensitive MultiDict for Headers
  #6 [Feature Request] parse url parameter and set params
  pull requests: 4
  labeled: 6
PyGithub/PyGithub: 6 entries
  #1 [bug] Gitub -> Github everywhere
  #2 [no labels] Use objects instead of string for shas, ids, etc. arguments
  #3 [no labels] Deduce mandatory parameters
  #4 [no labels] Review public interface homogeneity 
  #5 [no labels] Implement full API
  #6 [no labels] Review exceptions policy when receiving error HTTP status
  pull requests: none
  labeled: 1
psf/no-such-repo-xyz: failed with 404
```

The following command is the one that produced it:

```bash
python3 issue_digest.py
```
