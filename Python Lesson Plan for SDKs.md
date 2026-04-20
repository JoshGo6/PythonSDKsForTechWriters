---
name: python-sdk-lesson
description: Generate a Python lesson for tech. writers where the learning goal is processing text files, making API calls, and working with Python SDKs.
---

# Python Lesson Plan for GitHub SDK Project

## Purpose of This Artifact

This document is a reusable curriculum contract between the learner (Josh) and an LLM.

Its purpose is to:

- Provide a structured, fast‑track learning path for Python.
- Focus primarily on the Python needed to effectively use and document the GitHub Python SDK (PyGithub).
- Secondarily, provide instruction on reading from, writing to, and manipulating text documents (the stuff you actually want to automate).
- Serve as a stable input artifact that can be uploaded into a future conversation so the LLM can generate individual lessons on demand.

This artifact defines the lesson roadmap and the rules for generating individual lessons.

## Instructions for the LLM When Generating a Lesson

When the user says:

> "Generate Lesson X"

You must:

1. Follow the scope defined in this artifact.
2. Assume prior lessons have already been completed.
3. Reinforce earlier material where appropriate.
4. Keep the exercises in the lessons completable within 30 minutes (excluding reading time).
5. Use the required lesson structure.
6. Perform an audit on your lesson before presenting your final output to the reader.
7. Follow the constraints given in this document.

## Required Lesson Structure

Each generated lesson must contain the following elements, in the order they're presented here:

1. **Terminology and Theory**
    - Define new vocabulary clearly.
    - Keep explanations practical, not academic.
2. **Syntax Section**
    - Show the relevant syntax patterns.
    - Explain what each component does.
3. **Worked Examples (2-3)**
    - Fully runnable examples.
    - Clearly explain what is happening.
    - Use realistic patterns aligned with SDK usage and text-processing scripts.
4. **Quick Reference**
    - A single code block of Python code, complete with a `python` code slug that contains doublets.
    - A "doublet" is a comment line followed by one or more lines of Python code in the script, followed by a blank line.
    - Each doublet illustrates Python syntax covered in the lesson.
    - All new Python syntax introduced MUST be covered in the quick reference.
5. **Exercises (1)**
    - Require use of _new_ material from the current lesson.
    - Should take no more than 30 minutes to complete, excluding the time to read the lesson and exercise instructions.
    - Should not contain hints as to how to complete the exercises.
    - **Hard rule**: Should reinforce previous lessons by requiring knowledge of them.
    - Should reinforce a diverse set of skills from previous lessons, instead of just skills from one previous lesson. Additionally, should require skills from the previous three lessons, if doing so would not make the exercise be awkward.
    - **Hard rule:** An exercise **MUST NOT** require _any_ Python operation, syntax, library, or tool that has not been taught in the current lesson or in earlier lessons. If a helpful technique exists but is "coming later," the exercise must not depend on it. In other words, exercises require the use of the current lesson and previous lessons, not future lessons.
    - **Hard rule:** Every exercise must require the learner to write and run code that produces output testable at the command line. An exercise that involves only passive reading or providing a written answer is not sufficient.
    - Should not hint to the user how to perform the exercise.
    - Should present the desired output so the user can verify that he got the correct answer.

## Audit

After drafting the exercises but before presenting them, you must perform an explicit audit of the entire lesson, including the exercises. For each exercise, identify every Python operation, syntax pattern, library, and built-in function it requires. Then verify that each one was introduced in the current lesson or in a prior lesson's roadmap entry. If any exercise depends on something from a future lesson — even something minor like a loop, a conditional, or an import — revise the exercise to eliminate the dependency before presenting the lesson. If a revision needs to take place, use your judgement as to whether its appropriate to revise the lesson so that it covers the dependency, or to revise the exercise as to eliminate the dependency. Use the overall lesson roadmap to decide which is the most appropriate action. Do not present the lesson until every exercise passes this check. Before presenting the lesson, output a short audit table or list showing each exercise, the operations it requires, and which lesson introduced each one. Then present the lesson.

## Constraints

- Avoid unnecessary depth intended for full software engineering roles.
- Ensure lessons are practical, incremental, and aligned with SDK usage.
- The goal is fluency for SDK work _and_ text manipulation a technical writer can use for scripting operations.
- The goal is **NOT** mastery of Python as a language. Do not include unnecessary digressions (advanced OOP theory, decorators beyond `@property` recognition, metaclasses, etc.).
- When choosing examples, prioritize:
    - Working with strings, lists, dicts, and JSON-like objects.
    - Reading/writing files safely (encoding, newlines, paths).
    - "Glue code" patterns: loops, conditionals, functions, exceptions, logging, CLI args.
    - Consuming SDK objects and translating SDK behavior into docs-friendly explanations.
    - **Hard rule:** An exercise **MUST NOT** require _any_ Python operation, syntax, library, or tool that has not been taught in the current lesson or in earlier lessons. If a helpful technique exists but is "coming later," the exercise must not depend on it but instead must give details on its use sufficient to understand the material in the lesson and to perform the coding exercise at the end.
- **Hard rule:** Callout slugs (`> [!note]`, `> [!tip]`, etc.) must appear on their own line. The content must begin on the following line. Never place body text on the same line as the slug.
    
    ## Output Format
    
    The output you, the LLM, create must be in a single Markdown file for use in Obsidian. If you have parenthetical notes, important information, tips, or warnings, you can use these formats, where you MUST put the note-type slug (for example `> [!tip]`) on the first line, by itself, rather than run it into the text. The following examples show incorrect patterns and correct patterns for callouts. Do not use the incorrect patterns. **HARD RULE:**: You **MUST** use the correct patterns. 
    
**Incorrect pattern for a note:**

> [!note] Closing the file terminates the process.

**Correct pattern for a note:**

> [!note] 
> Closing the file terminates the process.

**Incorrect pattern for a tip:**

> [!tip] Closing the file terminates the process.

**Correct pattern for a tip:**

> [!tip] 
> Closing the file terminates the process.

**Incorrect pattern for info:**

> [!info] Closing the file terminates the process.

**Correct pattern for info:**

> [!info] 
> Closing the file terminates the process.

**Incorrect pattern for a warning:**

> [!warning] Closing the file terminates the process.

**Correct pattern for a warning:**

> [!warning] 
> Closing the file terminates the process.

## Final Objective

By completing these lessons, the learner will:

- Be fluent enough in Python to read and write scripts using PyGithub and work with mastery in most Python-centric SDKs.
- Be able to work with REST APIs directly using the `requests` library, including authenticated requests, error handling, and response parsing — essential for API documentation work where SDKs may not exist or where understanding the raw API behavior is required.
- Understand how SDK abstractions map to REST APIs.
- Be capable of producing meaningful, employer‑ready SDK documentation for any Python-centric SDK, not just PyGithub.
- Be able to understand and document Python that developers write, including common patterns like list comprehensions, type hints, `*args`/`**kwargs`, `@property`, lambda expressions, and `async/await`.
- Know what to look up when encountering unfamiliar Python patterns.
- Be able to write Python scripts to process text documents to extract text, modify text, and reorganize text for his technical writing job. This includes editing documents in place, as well as creating new documents from existing documents.

This curriculum intentionally avoids advanced software engineering depth. It prioritizes clarity, speed, practical SDK literacy, and the ability to use Python for technical writing.

---

#### Lesson Roadmap

### Phase 1 — Core Python, built for scripts

#### Lesson 1: Running Python Using the REPL and Scripts

Learn how to run Python in a terminal, in a file, and in an interactive session. Introduce indentation as "syntax," and establish the mental model of "top to bottom execution." Exercises only use `print()`, variables, and running code.

#### Lesson 2: Variables, names, and basic types

Cover assignment, naming rules, and the idea that variables point at values. Introduce `str`, `int`, `float`, and `bool` just enough to recognize them in code. Exercises focus on creating values, printing them, and verifying types with `type()`.

#### Lesson 3: Printing and simple debugging habits

Show `print()` patterns for inspecting values (labels, multiple values, and separators). Introduce the idea of "inspect → change → rerun" as your default debugging loop. Exercises are small "observe what Python did" tasks—no new syntax beyond printing and variables.

#### Lesson 4: Strings I — quotes, escaping, and indexing

Introduce strings as sequences of characters, basic indexing, and escaping quotes. Cover triple-quoted strings for multi-line text (especially useful for docs). Exercises only use indexing, printing, and simple concatenation.

#### Lesson 5: Strings II — common methods you'll use constantly

Cover `.lower()`, `.upper()`, `.strip()`, `.replace()`, `.split()`, `.startswith()`, `.endswith()`, and a few more high-value methods like `.join()` and `.find()`. Emphasize immutability: methods return new strings. Exercises are "transform this line of text" problems using only the taught methods.

#### Lesson 6: String formatting I — f-strings for readable output

Introduce f-strings for building readable messages and logs. Cover basic formatting and embedding expressions you already know (variables and simple indexing). Exercises generate clear, human-readable output you'd put in a script or doc.

#### Lesson 7: Lists I — creation, indexing, slicing

Introduce list literals, indexing, slicing, and basic list methods (`append`, `extend`). Emphasize "a list is a container of values," which will mirror paginated lists and SDK results. This lesson covers flat lists only; nested lists are covered next. Exercises stay strictly within list creation and element access.

#### Lesson 8: Lists II — nested lists

Teach lists that contain other lists and how to access elements using chained indexing (e.g., `matrix[0][1]`). Show how nested lists represent tabular data and grouped records. Exercises create, read from, and modify nested list structures using only list operations and printing.

#### Lesson 9: Loops I — `for` loops over lists and strings

Teach `for item in iterable` with strings and lists, plus `range()` for simple counts. Introduce the habit of printing inside a loop to verify behavior. Exercises iterate and summarize values without using any advanced helpers.

#### Lesson 10: Conditionals I — `if`, `elif`, `else` and comparisons

Introduce boolean expressions, comparison operators, and basic `if/elif/else`. Show how conditionals combine with loops for filtering. Exercises are "filter these items" tasks that only use loops, comparisons, and printing.

#### Lesson 11: Dictionaries I — keys, values, and lookups

Teach dictionary literals, key access, adding keys, and `.get()` for safer lookups. Connect this directly to "JSON-like objects" returned by APIs and SDKs. Exercises manipulate small nested dicts without introducing JSON parsing yet.

#### Lesson 12: Dictionaries II — iterating, `.items()`, and nested structures

Teach iterating through dicts (`for k, v in d.items()`), and reading nested dict/list combos. Show how to guard against missing keys using `.get()` and conditionals. Exercises walk nested data carefully using only the patterns introduced here.

#### Lesson 13: Tuples and Unpacking (Python Idioms You Must Recognize)

Teach what a tuple is, how tuple literals look (including the "comma makes a tuple" pattern), and how tuple unpacking works. Cover unpacking in loops (`for k, v in d.items()`) and why you'll see this constantly when reading SDK examples and SDK documentation. Keep it recognition-oriented: you should be able to look at tuple/unpacking code and understand what values are being assigned to which names.

#### Lesson 14: Truthiness and defensive checks

Explain how empty strings/lists/dicts behave in conditions, and when to compare explicitly vs rely on truthiness. Teach simple "guard clause" patterns to keep scripts readable. Exercises rewrite small snippets to avoid KeyError/IndexError using only prior concepts.

#### Lesson 15: Functions I — defining and calling functions

Introduce `def`, parameters, return values, and why functions matter for scripts. Keep it practical: "name a chunk of logic so you can reuse it." Exercises create 1–2 small helper functions that process strings/lists.

#### Lesson 16: Functions II — default parameters and `None`

Cover default values, optional parameters, and using `None` as "no value provided." Show how to write a function that can be called in multiple scenarios without copy/paste. Exercises modify a function to support optional behavior using only defaults and conditionals.

#### Lesson 17: Modules and imports (standard library first)

Teach `import` and `from x import y`, and how to read module docs at a basic level. Introduce a few standard library modules you'll need later (`pathlib`, `json`, `re`) without using them deeply yet. Exercises import and call a couple of standard functions, staying within what you've already learned.

#### Lesson 18: Exceptions I — what errors mean and how to read them

Teach the anatomy of a traceback and how to identify the failing line. Introduce a small set of common exceptions you'll actually see (TypeError, KeyError, IndexError, ValueError). Exercises are "cause an error on purpose, then fix it" using only prior syntax.

#### Lesson 19: Exceptions II — `try/except` for script resilience

Teach `try/except`, catching specific exceptions, and when not to catch. Show practical patterns: parsing user input, missing keys, and file-not-found. Exercises add safe handling to small scripts without introducing new libraries.

#### Lesson 20: Iterators — understanding lazy sequences

Teach what an iterator is and how it differs from a list. Cover the core concept: iterators produce values on demand and can only be traversed once. Show common iterators you'll encounter: file handles from `open()`, `re.finditer()` results, and later, paginated API results. Explain why looping twice over the same iterator yields nothing the second time, and how to convert an iterator to a list when you need multiple passes or random access (`list(iterator)`). Teach how to recognize when you're working with an iterator vs. a list using `type()`. Exercises loop over file handles and `finditer()` results, demonstrate the "exhausted iterator" behavior, and convert iterators to lists to enable re-iteration.

#### Lesson 21: The `logging` module — replacing `print()` for real scripts

Introduce the `logging` module as the production replacement for `print()`-based debugging. Teach `logging.basicConfig()`, the core log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`), and how to set the threshold so debug messages appear during development but not in production. Exercises convert a small `print()`-based script into one that uses `logging` calls at appropriate levels.

#### Lesson 22: Working with files I — open/read/write (text)

Teach `open()` with context managers (`with`), reading full files vs line-by-line, and writing output. Cover encoding (`utf-8`) and newline basics enough to prevent "why is this file weird" pain. Exercises read a small text file and produce a transformed output file using only strings, loops, and functions you already know.

#### Lesson 23: Working with files II — paths with `pathlib`

Teach `Path`, joining paths, checking existence, and iterating directories. Keep it practical for a docs repo: "find all files matching X and process them." Exercises build a tiny "scan a folder" script using only `pathlib`, loops, and string methods.

#### Lesson 24: Text processing I — regex fundamentals for writers

Introduce regular expressions as a practical search tool, not theory. Teach `re.search`, `re.findall`, and `re.sub` with a small, curated pattern set (anchors, character classes, groups). Exercises perform safe substitutions and extractions on strings you provide—no advanced regex features.

#### Lesson 25: Text processing II — structured transforms at scale

Combine `pathlib` + regex + file IO to do multi-file transformations. Teach "dry run" output (print what would change) before writing changes, and how to avoid accidental mass edits. Exercises implement a two-pass script: preview changes, then write changes.

#### Lesson 26: File management — finding, moving, renaming, and deleting with `pathlib`, `re`, and `shutil`

Teach how to use Python to perform filesystem management tasks that the learner currently does in Bash. Combine `pathlib` directory traversal (Lesson 23) with `re` pattern matching (Lesson 24) to locate files and directories whose names match a regex pattern, including recursive searches with `Path.rglob()`. Introduce `shutil.move()` for moving files and directories, `Path.rename()` for renaming, `Path.unlink()` for deleting files, and `shutil.rmtree()` for deleting directories. Emphasize the same "dry run before writing" discipline taught in Lesson 25 — print what would be affected before executing destructive operations, because deletions and moves are not reversible from a script. Exercises build a script that scans a directory tree for files matching a regex pattern, previews the planned operations, and then executes moves, renames, or deletions only when a confirmation flag is provided.

#### Lesson 27: Text processing III — parsing and editing Markdown structurally

Teach how to treat Markdown as a structured format rather than raw text. Cover reliable patterns for identifying headings, links, code fences, and front matter using the regex and string tools already learned, and show where regex breaks down. Introduce a lightweight parsing library (`mistune` or `python-markdown`) for cases that need structural awareness. Exercises extract all links from a Markdown file, rewrite heading levels, and pull front matter fields from a set of docs.

#### Lesson 28: Data formats — JSON read/write and pretty printing

Teach `json.loads`, `json.dumps`, `json.load`, and `json.dump`, focusing on readability and inspection. Connect JSON objects to dict/list structures you already understand. Exercises load JSON, extract a couple of fields, and write a summarized JSON output.

#### Lesson 29: Command-line interfaces I — `sys.argv` and basic arguments

Teach what `sys.argv` is and how scripts receive inputs from the shell. Cover basic argument presence checks and simple usage messages. Exercises modify a script to accept an input file path and an output file path.

#### Lesson 30: Command-line interfaces II — `argparse` for real scripts

Introduce `argparse` with a small, repeatable template (positional args, optional flags). Emphasize discoverability: `--help` should explain your tool. Exercises convert a `sys.argv` script into an `argparse` version with one optional flag.

#### Lesson 31: Environment variables and secrets (token-safe habits)

Teach reading environment variables with `os.environ` / `os.getenv`, and why secrets should not live in code. Show practical patterns for GitHub tokens and "fail fast with a helpful message." Exercises implement token loading and validation without calling external APIs yet.

---

### Phase 2 — Python package workflow (what SDK users actually do)

#### Lesson 32: pip, packages, and reading signatures

Teach installing packages with `pip`, pinning versions, and reading the basics of a function signature. Cover the difference between a module, a package, and an installed distribution. Exercises install a small library, import it, and call a documented function using only prior Python.

#### Lesson 32a: Markdown formatting with `mdformat`

Teach `mdformat` as a command-line tool and Python library for enforcing consistent style across Markdown files. Cover installation via `pip`, the CLI (`mdformat file.md`, `--check` for dry runs), and the Python API (`mdformat.file()` and `mdformat.text()`). Teach the options dict for controlling list numbering and line wrap behavior. Introduce the plugin model: explain why `mdformat` mangles non-standard syntax without the correct plugin, and show how to find and install the right plugin for a given Markdown flavor. Emphasize the operational discipline of always testing against a copy of a file before running against a directory. Exercises apply `mdformat` via the Python API to a set of Markdown files, verify the output matches expected style, and demonstrate the consequence of running without the correct plugin on a file containing non-standard syntax.
#### Lesson 33: Virtual environments with `venv` (repeatable setups)

Teach creating/activating a venv, installing into it, and freezing dependencies. Emphasize reproducibility: "same environment = same behavior." Exercises create a venv and run a script that imports an installed library.

---

### Phase 3 — HTTP and API mental models (SDK user edition)

#### Lesson 34: HTTP essentials for SDK users

Teach request/response, endpoints, methods, status codes, headers, and JSON bodies at a practical level. Show how this maps onto "SDK method calls that perform requests under the hood." Exercises write small Python scripts that parse sample HTTP response data (provided as strings or dicts) and print what a script should do next based on the status code and body.

#### Lesson 35: curl vs SDK calls — reading raw API behavior

Teach `curl` patterns for GET requests, auth headers, and basic pagination hints. Compare a raw REST call to the SDK abstraction and show what information is preserved vs hidden. Exercises write Python scripts that parse provided curl JSON output (as strings) and print doc-style explanations of the API behavior.

#### Lesson 36: Making HTTP requests with `requests` — GET and response basics

Teach installing and using the `requests` library for GET requests. Cover `requests.get()`, the `Response` object (`.status_code`, `.text`, `.json()`, `.headers`), and query parameters via `params=`. Connect this to the curl patterns from Lesson 35 — "here's what curl was doing under the hood." Exercises make real GET requests to a public API (like httpbin.org or a public GitHub endpoint), inspect the response, and extract fields using JSON/dict skills already learned.

#### Lesson 37: Making HTTP requests with `requests` — POST, headers, and authentication

Teach `requests.post()`, `requests.put()`, and `requests.delete()`. Cover sending JSON bodies (`json=`), custom headers (`headers=`), and authentication patterns: API keys in headers, Bearer tokens, and basic auth. Emphasize loading tokens from environment variables (Lesson 31). Exercises send authenticated requests to a test API, handle the responses, and print doc-friendly summaries of what the API returned.

#### Lesson 38: API response handling and debugging

Teach systematic response handling: checking status codes before parsing, raising exceptions on failures (`response.raise_for_status()`), logging request/response details for debugging, and handling common HTTP errors (400, 401, 403, 404, 500). Show how to build a reusable "make a request and handle errors" function. Exercises implement a robust API-calling script that logs its behavior and handles errors gracefully.

---

### Phase 3.5 — Intermediate Python patterns for SDK readiness

#### Lesson 39: `*args` and `**kwargs` — reading flexible signatures

Teach `*args` and `**kwargs` as a reading-comprehension skill. Explain what `*args` collects (positional arguments into a tuple) and what `**kwargs` collects (keyword arguments into a dict). Show examples from SDK-style code: `def create_issue(self, *args, **kwargs)` and calls like `repo.get_issues(**filters)`. Exercises call functions that accept `*args` and `**kwargs` and print the received values to confirm understanding.

#### Lesson 40: List comprehensions — reading compact Python

Teach list comprehensions (`[expression for item in iterable]` and `[expression for item in iterable if condition]`) as a recognition-oriented skill. Show how a comprehension maps to an equivalent `for` loop with `append`, so the learner can mentally "unpack" any comprehension they encounter. Exercises use list comprehensions to process lists and produce formatted output, and rewrite a given `for` loop as a comprehension.

#### Lesson 41: Lambda expressions and `sorted()` with `key=`

Teach lambda expressions (`lambda x: x.field`) as small anonymous functions used primarily as arguments to `sorted()`, `min()`, and `max()`. Focus on the `key=` parameter pattern: `sorted(items, key=lambda x: x.created_at)`. Exercises sort lists of dictionaries and simple objects by various fields and print the results.

---

### Phase 4 — PyGithub: using it, then documenting it

#### Lesson 42: Classes and Instances — Reading `__init__` and `self`

Teach what a class is and what an instance is. Explain `__init__` as the constructor that runs when an object is created, and `self` as the instance referring to itself — framed entirely as reading comprehension, not writing. Show how you recognize object creation in SDK code (`g = Github(token)`). The lesson provides a small pre-written mock module. Exercises require the learner to write short scripts that instantiate the provided objects and produce formatted output from their attributes.

#### Lesson 43: Methods, Attributes, and Object Chaining

Distinguish attributes (state you read) from methods (actions you call). Teach object chaining (`client.get_repo(...).get_issues(...)`) and how to read SDK object hierarchies in documentation. The lesson provides a pre-written mock module with chained objects. Exercises require the learner to navigate the chain and produce a formatted report to stdout.

#### Lesson 44: The `@property` decorator — why attribute access can be a method

Teach the `@property` decorator purely as a reading-comprehension skill. Explain that `repo.full_name` or `issue.user` in PyGithub may invoke a method defined with `@property`, not read a stored value. Show what this looks like in source code so the learner can recognize it. The lesson does not require writing properties, only recognizing them. Exercises provide small mock classes with `@property` methods and require the learner to access these properties and print the results.

#### Lesson 45: Inheritance Recognition and `isinstance()`

Teach inheritance purely as a reading skill: when you see `class Foo(Bar)`, Foo inherits Bar's methods, which is why you can call methods not directly defined on the class you are looking at. Introduce `isinstance()` as a tool for checking what type of object you are working with, which appears frequently in SDK source and error-handling patterns. The lesson provides a pre-written mock module demonstrating both concepts. Exercises require the learner to write scripts that use `isinstance()` to filter or branch on object types and produce specific output.

#### Lesson 46: Installing PyGithub and authenticating safely

Teach installing PyGithub inside a venv and authenticating using an environment variable token. Show a minimal "connect and fetch my user login" script, with clear error handling. Exercises extend the script to print a few user attributes and handle missing token errors.

#### Lesson 47: The PyGithub object model (what objects represent)

Teach the mental model: `Github()` → user/org → repo → issue/PR/etc. Focus on how to discover methods and attributes and how to read them in docs. Exercises navigate from an authenticated client to a repo object and print basic metadata.

#### Lesson 48: Repositories I — listing and selecting repositories

Teach listing repos for a user/org and selecting a specific repo by name. Introduce the idea of returned "paginated lists" at a gentle, observable level. Exercises output a clean, formatted list of repo names and URLs.

#### Lesson 49: Repositories II — reading contents and files

Teach how to fetch repository contents and read file metadata via PyGithub. Connect this directly to doc workflows: "find all Markdown files" / "inspect README changes." Exercises fetch a file, print its path/sha/size, and safely handle "file not found."

#### Lesson 50: The `csv` module — writing structured report output

Teach `csv.writer` and `csv.DictWriter` for producing well-formed CSV files. Show why raw string concatenation breaks when fields contain commas or quotes, and how the `csv` module handles escaping automatically. Cover `csv.reader` and `csv.DictReader` briefly for reading CSV back in. Exercises write a list of dictionaries to a CSV file, then read it back and print the contents.

#### Lesson 51: Issues I — listing, filtering, and summarizing

Teach listing issues, filtering by state, and extracting high-value fields for a report. Emphasize careful iteration and readable output. Exercises generate a short report (stdout or CSV) using only patterns already taught.

#### Lesson 52: Datetime for SDK Reports

Teach basic use of `datetime` for reports built from SDK data: reading timestamps returned by APIs, comparing and sorting timestamps, and printing readable time values. Include minimal timezone awareness so you don't accidentally write misleading documentation (for example, clearly labeling whether a timestamp is UTC or local time when you format it). Avoid advanced timezone libraries and avoid calendar arithmetic beyond basic comparisons.

#### Lesson 53: Issues II — creating and updating issues safely

Teach creating an issue, adding a comment, and updating title/body with careful safeguards. Emphasize "avoid accidental writes": dry run and explicit confirmation flags (handled via CLI args you already learned). Exercises create a "preview mode" script that only writes when a flag is provided.

#### Lesson 54: Pull requests — reading PR metadata and review state

Teach retrieving PRs, reading status fields you'd document, and relating PRs to issues when applicable. Focus on interpreting object properties and mapping them into a docs-friendly explanation. Exercises produce a PR summary report for a repository.

#### Lesson 55: Pagination in PyGithub — iteration behavior and performance

Teach how PyGithub paginates, what happens when you iterate, and why "just loop everything" can be slow. Show practical strategies: limit results, break early, and fetch only what you need. Exercises compare a "full scan" vs "first N items" approach without introducing new libraries.

#### Lesson 56: Rate limiting — detecting, documenting, and behaving well

Teach what GitHub rate limits are, how to inspect them via PyGithub, and how to write scripts that fail gracefully. Emphasize how to document rate-limit behavior and recommended user actions. Exercises add a pre-flight rate-limit check to an existing script.

#### Lesson 57: Error behavior — mapping HTTP failures to Python exceptions

Teach common failure scenarios (401/403/404/422) and how they surface in PyGithub exceptions. Show a repeatable pattern for catching, logging, and presenting helpful messages to the user. Exercises implement targeted exception handling and verify behavior using controlled "bad inputs."

#### Lesson 58: Reading type hints in SDK signatures

Teach how to read Python type hints in function and method signatures. Cover `parameter: Type`, the `-> ReturnType` return annotation, and common vocabulary: `Optional[str]`, `List[...]`, `Dict[..., ...]`, `Union[..., ...]`. This is reading-comprehension only — the learner must be able to look at an annotated signature and explain what it accepts and returns. Exercises provide annotated function stubs and require the learner to call them with correct argument types and print the results.

#### Lesson 59: `async/await` recognition — reading modern SDK patterns

Teach `async def`, `await`, and `asyncio.run()` purely as a reading-comprehension skill. Explain what problem async code solves and why modern SDKs for cloud services and AI APIs use it. Show what async function definitions and `await` calls look like so the learner can follow async SDK examples. Exercises provide small async scripts to run, observe, and modify slightly to confirm understanding.

---

### Phase 5 — Producing employer-ready documentation

#### Lesson 60: Reading SDK source and docs like a writer

Teach how to find the "real behavior" by reading docstrings, type hints, and method implementations at a surface level. Show how to extract: inputs, outputs, side effects, errors, and rate-limit considerations. Exercises create a structured notes template from 2–3 PyGithub methods.

#### Lesson 61: Documenting workflows, not just methods

Teach how to document end-to-end tasks (auth → pick repo → list issues → export report). Emphasize mental models, realistic examples, and troubleshooting sections. Exercises produce a short "task guide" draft using outputs from scripts you already built.

#### Lesson 62: Documentation capstone — a PyGithub feature page

Pick one PyGithub feature area (issues, contents, PRs, or rate limits) and create a full doc page outline. Include: overview, prerequisites, examples, error handling, pagination notes, and "how this maps to REST" notes. Exercises require writing a script that generates the doc page skeleton (with live SDK data filling in examples and outputs) and writes it to a file.