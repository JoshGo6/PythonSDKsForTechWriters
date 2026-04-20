# Lesson 31: Environment Variables and Secrets (Token-Safe Habits)

## Terminology and Theory

**Environment variable** — A named value that lives in your shell session, outside your Python script. Every process you launch inherits a copy of the environment from its parent shell. Environment variables are the standard way to pass configuration — API tokens, file paths, feature flags — into a script without embedding those values in the source code.

**Secret** — Any value that grants access to a protected resource: API tokens, passwords, private keys. Secrets must never appear in source code, version-controlled files, or log output.

**Fail fast** — A design pattern where your script checks for required configuration immediately at startup and exits with a clear error message if anything is missing. This prevents the script from running halfway, doing partial work, and then crashing deep inside a function when the missing value is finally needed.

**`os.environ`** — A dictionary-like object provided by the `os` module that contains all environment variables available to the current process. Accessing a key that does not exist raises a `KeyError`, just like a regular dictionary.

**`os.getenv()`** — A function that looks up an environment variable by name and returns its value, or returns a default (which is `None` if you do not specify one) when the variable is not set. It never raises an exception for a missing key.

> [!note] Environment variables are always strings. If you set `MAX_RETRIES=5` in your shell, Python receives the string `"5"`, not the integer `5`. You must convert explicitly with `int()`, `float()`, or similar functions when you need a non-string type.

### Why This Matters for SDK Work

Every SDK that connects to a remote service requires authentication. The standard professional pattern is:

1. Store the token in an environment variable.
2. Load it at the top of your script.
3. Fail immediately with a helpful message if it is missing.

This keeps secrets out of your code, out of your Git history, and out of your logs.

### Setting Environment Variables in the Shell

Before your Python script can read an environment variable, the variable must exist in the shell session that launches the script. You set one with `export`:

```bash
export GITHUB_TOKEN="ghp_abc123exampletoken"
```

This variable now exists for the current terminal session and any processes launched from it. It disappears when you close the terminal. To make it persist across sessions, add the `export` line to your shell configuration file (such as `~/.bashrc` or `~/.profile`).

You can verify it is set:

```bash
echo $GITHUB_TOKEN
```

You can also set a variable for a single command without `export`:

```bash
GITHUB_TOKEN="ghp_abc123exampletoken" python3 my_script.py
```

This sets `GITHUB_TOKEN` only for that one invocation of `my_script.py`.

> [!warning] Never put real tokens in scripts, notebooks, or documentation examples. Use obviously fake placeholder values like `ghp_EXAMPLE_TOKEN_REPLACE_ME` in any written material.

---

## Syntax Section

### Importing `os`

The `os` module is part of the standard library. No installation is needed.

```python
import os
```

### Reading with `os.environ`

`os.environ` behaves like a dictionary. You access values by key:

```python
token = os.environ["GITHUB_TOKEN"]
```

If `GITHUB_TOKEN` is not set, this raises a `KeyError`. This is sometimes useful — it forces you to handle the missing variable — but it produces an ugly traceback if you do not catch it.

You can also use `.get()` on `os.environ`, which works exactly like `dict.get()`:

```python
token = os.environ.get("GITHUB_TOKEN")
```

This returns `None` if the variable is not set, without raising an exception.

### Reading with `os.getenv()`

`os.getenv()` is a convenience function that does the same thing as `os.environ.get()`:

```python
token = os.getenv("GITHUB_TOKEN")
```

Returns `None` if the variable is not set. You can supply a default as the second argument:

```python
log_level = os.getenv("LOG_LEVEL", "INFO")
```

If `LOG_LEVEL` is not set, `log_level` gets the string `"INFO"`.

> [!tip] Use `os.getenv()` for optional configuration where a sensible default exists. Use `os.environ["KEY"]` (inside a `try/except`) or an explicit check-and-exit for required secrets where there is no safe default.

### Listing All Environment Variables

Because `os.environ` is dict-like, you can iterate over it:

```python
for key, value in os.environ.items():
    print(f"{key}={value}")
```

This prints every environment variable in the current process. You would not normally do this in a production script, but it is useful for debugging.

### Checking Whether a Variable Is Set

You can use the `in` operator, just like with a dictionary:

```python
if "GITHUB_TOKEN" in os.environ:
    print("Token is set.")
else:
    print("Token is NOT set.")
```

---

## Worked Examples

### Example 1: Fail-Fast Token Loader

This script loads a required token at startup and exits immediately with a clear message if it is missing. This is the pattern you will use in every SDK script.

```python
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

token = os.getenv("GITHUB_TOKEN")

if not token:
    logging.error("GITHUB_TOKEN is not set.")
    logging.error("Set it with: export GITHUB_TOKEN='your_token_here'")
    sys.exit(1)

logging.info("Token loaded successfully.")
logging.info(f"Token starts with: {token[:4]}...")
```

Key points:

- `os.getenv("GITHUB_TOKEN")` returns `None` if the variable is not set.
- `if not token` uses truthiness (Lesson 14): both `None` and an empty string `""` are falsy. This catches a variable that is set but accidentally empty.
- `sys.exit(1)` terminates the script with a non-zero exit code, signaling failure to the shell. `sys.exit(0)` or no argument signals success.
- The final `logging.info` line prints only the first four characters of the token. Never print a full secret — even in logs you think are private.

Running without the variable set:

```
ERROR: GITHUB_TOKEN is not set.
ERROR: Set it with: export GITHUB_TOKEN='your_token_here'
```

Running with the variable set:

```bash
export GITHUB_TOKEN="ghp_abc123exampletoken"
python3 token_loader.py
```

```
INFO: Token loaded successfully.
INFO: Token starts with: ghp_...
```

### Example 2: Loading Multiple Configuration Values

Real scripts often need more than one piece of configuration. This example loads a required token and two optional settings, applying defaults for the optional ones.

```python
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def load_config():
    """Load configuration from environment variables.

    Returns a dictionary of configuration values.
    Exits if required variables are missing.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logging.error("Required variable GITHUB_TOKEN is not set.")
        sys.exit(1)

    config = {
        "token": token,
        "org": os.getenv("GITHUB_ORG", "my-default-org"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }
    return config


config = load_config()

logging.info(f"Organization: {config['org']}")
logging.info(f"Log level: {config['log_level']}")
logging.info(f"Token loaded (starts with {config['token'][:4]}...)")
```

Key points:

- Wrapping configuration loading in a function keeps the top of your script clean and makes the config reusable.
- Required values get a check-and-exit. Optional values get a default via the second argument to `os.getenv()`.
- The function returns a dictionary, which the rest of the script uses. This centralizes all environment-variable access in one place.

### Example 3: Validating a Token Format

Sometimes you want to check not just that a variable is set, but that its value looks reasonable before proceeding. This example validates that a GitHub personal access token starts with an expected prefix.

```python
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

VALID_PREFIXES = ("ghp_", "gho_", "ghu_", "ghs_", "ghr_")

token = os.getenv("GITHUB_TOKEN")

if not token:
    logging.error("GITHUB_TOKEN is not set.")
    sys.exit(1)

if not token.startswith(VALID_PREFIXES):
    logging.error(
        f"GITHUB_TOKEN does not start with a recognized prefix: "
        f"{', '.join(VALID_PREFIXES)}"
    )
    logging.error("Check that you copied the full token.")
    sys.exit(1)

logging.info(f"Token validated: starts with {token[:4]}...")
```

Key points:

- `VALID_PREFIXES` is a tuple of strings. `.startswith()` accepts a tuple and returns `True` if the string starts with any of them (Lesson 5).
- This catches common mistakes like pasting a partial token, pasting a URL instead of a token, or accidentally assigning the wrong variable.
- The error message tells the user exactly what went wrong and what to check — this is a hallmark of well-written tooling.

---

## Quick Reference

```python
# Import the os module
import os

# Read a required variable (raises KeyError if missing)
token = os.environ["GITHUB_TOKEN"]

# Read a variable safely (returns None if missing)
token = os.getenv("GITHUB_TOKEN")

# Read a variable with a fallback default
log_level = os.getenv("LOG_LEVEL", "INFO")

# Use .get() on os.environ (same as os.getenv)
org = os.environ.get("GITHUB_ORG", "default-org")

# Check whether a variable exists
if "GITHUB_TOKEN" in os.environ:
    print("Token is available.")

# Fail-fast pattern: check and exit early
token = os.getenv("GITHUB_TOKEN")
if not token:
    print("Error: GITHUB_TOKEN is not set.", file=sys.stderr)
    sys.exit(1)

# Print a partial secret (never print the full value)
print(f"Token starts with: {token[:4]}...")

# Iterate over all environment variables
for key, value in os.environ.items():
    print(f"{key}={value}")

# Validate a token prefix against a tuple of allowed values
VALID_PREFIXES = ("ghp_", "gho_")
if not token.startswith(VALID_PREFIXES):
    sys.exit(1)
```

---

## Audit

The exercise below requires the following operations. Each is verified against the lesson in which it was introduced.

|Operation|Introduced in|
|---|---|
|`import os`|Lesson 17 (modules and imports)|
|`import sys`|Lesson 29 (`sys.argv`)|
|`import logging`|Lesson 21 (`logging` module)|
|`import argparse`|Lesson 30 (`argparse`)|
|`import json`|Lesson 28 (JSON read/write)|
|`os.getenv()`|Lesson 31 (this lesson)|
|`if not variable` (truthiness)|Lesson 14 (truthiness)|
|`sys.exit(1)`|Lesson 31 (this lesson)|
|`logging.basicConfig()`, `logging.info()`, `logging.error()`|Lesson 21|
|`argparse.ArgumentParser`, `add_argument`, `parse_args`|Lesson 30|
|`str.startswith()` with a tuple|Lesson 5 (string methods)|
|String slicing (`token[:4]`)|Lesson 4 (string indexing)|
|`json.dumps()` with `indent`|Lesson 28|
|`open()` with `with` for writing|Lesson 22 (file I/O)|
|f-strings|Lesson 6|
|Functions with `def`, `return`|Lesson 15|
|Dictionaries (creation, key access)|Lesson 11|
|`for` loop over a list|Lesson 9|

All operations are from lesson 31 or earlier. No future-lesson dependencies exist.

---

## Exercise

### Token-Safe Config Loader

Write a script called `config_loader.py` that does the following:

1. Uses `argparse` to accept one optional flag: `--output`, which takes a file path. If `--output` is not provided, the script prints its results to stdout.
    
2. Loads the following three environment variables:
    
    - `APP_TOKEN` — required. The script must exit immediately with a helpful error message (via `logging.error`) if this variable is missing or empty.
    - `APP_ORG` — optional, defaults to `"default-org"`.
    - `APP_LOG_LEVEL` — optional, defaults to `"INFO"`.
3. Validates that `APP_TOKEN` starts with one of these prefixes: `"tok_"`, `"key_"`. If it does not, the script must log an error that lists the valid prefixes and exit.
    
4. Builds a dictionary called `config` with four keys:
    
    - `"token_preview"` — the first four characters of `APP_TOKEN` followed by `"..."` (e.g., `"tok_..."`).
    - `"org"` — the value of `APP_ORG`.
    - `"log_level"` — the value of `APP_LOG_LEVEL`.
    - `"variables_loaded"` — the integer `3`.
5. Converts `config` to a JSON string with an indent of 2 and either:
    
    - Writes it to the file specified by `--output`, then logs an `INFO` message confirming the file was written, or
    - Prints it to stdout if `--output` was not provided.

Put all environment-variable loading and validation logic inside a function called `load_and_validate()`. This function must return the validated `config` dictionary.

### Expected Output

**Test 1 — missing token:**

```bash
python3 config_loader.py
```

```
ERROR: APP_TOKEN is not set. Set it with: export APP_TOKEN='your_token_here'
```

(Script exits with code 1.)

**Test 2 — invalid token prefix:**

```bash
export APP_TOKEN="bad_prefix_abc"
python3 config_loader.py
```

```
ERROR: APP_TOKEN does not start with a recognized prefix: tok_, key_
```

(Script exits with code 1.)

**Test 3 — valid token, no `--output` flag:**

```bash
export APP_TOKEN="tok_abc123secret"
python3 config_loader.py
```

```
{
  "token_preview": "tok_...",
  "org": "default-org",
  "log_level": "INFO",
  "variables_loaded": 3
}
```

**Test 4 — valid token with `--output` flag and custom org:**

```bash
export APP_TOKEN="key_xyz789secret"
export APP_ORG="my-team"
python3 config_loader.py --output config_out.json
```

```
INFO: Configuration written to config_out.json
```

Contents of `config_out.json`:

```json
{
  "token_preview": "key_...",
  "org": "my-team",
  "log_level": "INFO",
  "variables_loaded": 3
}
```