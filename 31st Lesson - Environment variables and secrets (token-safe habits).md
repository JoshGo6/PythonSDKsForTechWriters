# Lesson 31: Environment variables and secrets (token-safe habits)

## 1. Terminology and Theory

**Environment variable**: A named string value that lives in the environment of a running process. The shell (Bash, Zsh, etc.) maintains a table of these variables and hands a copy of that table to every program it launches. Your Python script reads from that copy. It cannot change the shell's own table from inside the script — the handoff is one-way.

**Why secrets don't belong in code**: A hardcoded secret like `token = "ghp_abc123..."` is a security hazard. It gets committed to Git, ends up in screenshots and error logs, and sits in the shell history of anyone who ran the script. Storing secrets in environment variables keeps them out of source files, so the same script can be shared, committed, or published without leaking credentials.

**Fail fast**: When a script depends on configuration it cannot produce for itself (a token, a username, an API key), it should check for that configuration immediately — before doing any real work — and exit with a helpful message if anything is missing. The alternative is discovering the missing token after ten minutes of API calls, which wastes time and produces confusing failure traces.

**Environment values are always strings.** If you need a number, convert it explicitly with `int()` or `float()`. Python will not coerce for you, and forgetting this is a classic source of `TypeError` bugs.

> [!note] Every process inherits environment variables from its parent. When you launch `python script.py` from Bash, Python's `os.environ` contains a copy of Bash's exported variables at that moment. Changing `os.environ` inside Python does not change Bash's environment, and it does not persist after the script exits.

---

## 2. Syntax Section

Python reads environment variables through the `os` module. Two interfaces exist, and they behave differently when a variable is missing.

```python
import os

# Strict access: raises KeyError if the variable is unset.
value = os.environ["APP_TOKEN"]

# Safe access via .get(): returns None if unset, or a default if you supply one.
value = os.environ.get("APP_TOKEN")
value = os.environ.get("APP_TOKEN", "fallback")

# Equivalent shortcut. os.getenv() is a thin wrapper around os.environ.get().
value = os.getenv("APP_TOKEN")
value = os.getenv("APP_TOKEN", "fallback")
```

The full mapping is available as `os.environ`, which behaves like a dict (you already know how to iterate these from Lesson 12):

```python
for name, val in os.environ.items():
    print(name, "=", val)
```

For fail-fast exits, use `sys.exit()`. Passing a string prints it to stderr and exits with status 1. Passing an integer exits with that status and no message.

```python
import sys

sys.exit("APP_TOKEN is not set. Export it and try again.")
sys.exit(1)  # non-zero status, no message
```

Setting environment variables happens in the shell, not in Python. Two common patterns:

```bash
# Persistent for the shell session:
export APP_TOKEN=ghp_yourtokenhere
python script.py

# One-shot, scoped to a single command:
APP_TOKEN=ghp_yourtokenhere python script.py
```

The one-shot form is ideal for quick testing because the variable disappears the moment the command finishes — it never touches your shell history as a standalone `export`.

> [!tip] Never paste real secrets into a script file or a committed shell alias. In real workflows you load them from a file with restrictive permissions (for example, `source ~/.secrets/github.env`) or from a password manager. Tools like `direnv` and `python-dotenv` automate this, but they are out of scope for this lesson.

---

## 3. Worked Examples

### Example 1: Reading common environment variables with safe defaults

Almost every Unix shell exports `HOME` and `USER` automatically. This script reads them defensively so it still runs in odd environments (containers, cron jobs, minimal shells) where one might be unset.

```python
# show_env.py
import os

home = os.getenv("HOME", "<unknown>")
user = os.getenv("USER", "<unknown>")

print(f"User:      {user}")
print(f"Home dir:  {home}")
```

Run it normally, then strip both variables for one invocation to see the defaults kick in:

```bash
python show_env.py
# User:      josh
# Home dir:  /home/josh

env -u USER -u HOME python show_env.py
# User:      <unknown>
# Home dir:  <unknown>
```

If you had written `os.environ["USER"]` instead, the second run would crash with `KeyError` and stop the script cold. The `.get()` / `getenv()` form is the right default for anything optional.

### Example 2: Fail-fast token loader

This script loads a GitHub-style token, validates its rough shape, and prints a safe preview — never the whole token.

```python
# check_token.py
import os
import sys

token = os.getenv("GITHUB_TOKEN")

if token is None:
    sys.exit("Error: GITHUB_TOKEN is not set. Export it before running this script.")

if len(token) < 20:
    sys.exit(f"Error: GITHUB_TOKEN is {len(token)} characters; expected at least 20.")

preview = f"{token[:4]}...{token[-4:]}"
print(f"Token loaded ({len(token)} chars): {preview}")
```

Two runs:

```bash
python check_token.py
# Error: GITHUB_TOKEN is not set. Export it before running this script.

GITHUB_TOKEN=ghp_1234567890abcdefghij python check_token.py
# Token loaded (24 chars): ghp_...ghij
```

Three disciplined habits appear in one short script: the token is never hardcoded, the script exits immediately with a clear message when the token is missing, and the printed preview lets a human confirm "this looks like my token" without the full value ever touching the terminal.

### Example 3: Splitting sensitive config from non-sensitive config

Real scripts usually take non-secret options from the command line (paths, modes, flags) and secrets from the environment. This split keeps tokens out of shell history while leaving everyday options easy to type.

```python
# export_config.py
import argparse
import json
import os
import sys

parser = argparse.ArgumentParser(description="Export a config summary to JSON.")
parser.add_argument("--output", required=True, help="Path to the output JSON file.")
args = parser.parse_args()

token = os.getenv("APP_TOKEN")
if not token:
    sys.exit("Error: APP_TOKEN is not set.")

config = {
    "token_length": len(token),
    "token_preview": f"{token[:3]}***{token[-3:]}",
    "output_path": args.output,
}

with open(args.output, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print(f"Wrote config summary to {args.output}")
```

Run it:

```bash
APP_TOKEN=abc123xyz789 python export_config.py --output summary.json
# Wrote config summary to summary.json

cat summary.json
# {
#   "token_length": 12,
#   "token_preview": "abc***789",
#   "output_path": "summary.json"
# }
```

Notice the guard `if not token:` rather than `if token is None:`. Because an empty string is falsy (Lesson 14), `not token` treats both "unset" and "set to empty string" as failures. That's usually what you want for secrets — an empty token is just as useless as a missing one.

---

## 4. Quick Reference

```python
# Import the os module to reach the environment.
import os

# Strict read: raises KeyError if the variable is unset.
token = os.environ["APP_TOKEN"]

# Safe read via .get(): returns None when unset.
token = os.environ.get("APP_TOKEN")

# Safe read with a default.
level = os.environ.get("LOG_LEVEL", "INFO")

# Shortcut. os.getenv() returns None when unset.
token = os.getenv("APP_TOKEN")

# Shortcut with a default.
level = os.getenv("LOG_LEVEL", "INFO")

# Iterate the whole environment as (name, value) pairs.
for name, val in os.environ.items():
    print(name, "=", val)

# Fail fast with a message: prints to stderr, exits with status 1.
import sys
sys.exit("Error: APP_TOKEN is not set.")

# Fail fast with an explicit exit code and no message.
sys.exit(1)

# "Unset or empty" guard using truthiness (Lesson 14).
if not token:
    sys.exit("Error: APP_TOKEN is not set.")

# Safe preview: show only the first few and last few characters.
preview = f"{token[:4]}...{token[-4:]}"

# Environment values are always strings. Convert when needed.
timeout_seconds = int(os.getenv("TIMEOUT", "30"))
```

---

## 5. Exercise

Write a script named `validate_config.py` that loads and validates application configuration from environment variables, then writes a summary to a JSON file whose path is supplied on the command line.

**Requirements**

- The script must accept a required `--output` option specifying the path to the JSON output file.
- The script must read two environment variables: `APP_USER` and `APP_TOKEN`.
- If `APP_USER` is unset or empty, the script must print the exact message `Error: APP_USER is not set.` and exit with a non-zero status.
- If `APP_TOKEN` is unset or empty, the script must print the exact message `Error: APP_TOKEN is not set.` and exit with a non-zero status.
- If `APP_TOKEN` is set but shorter than 10 characters, the script must print the exact message `Error: APP_TOKEN is too short.` and exit with a non-zero status.
- If every check passes, the script must write a JSON file at the `--output` path containing exactly these three keys:
    - `user` — the value of `APP_USER`
    - `token_length` — the number of characters in `APP_TOKEN`
    - `token_preview` — the first three characters of the token, followed by `***`, followed by the last three characters of the token
- The JSON file must be pretty-printed (indented) so it is human-readable.
- On success, the script must print `Wrote config to <path>` to standard output, where `<path>` is the value supplied to `--output`.

**Desired output**

```bash
python validate_config.py --output config.json
# Error: APP_USER is not set.

APP_USER=josh python validate_config.py --output config.json
# Error: APP_TOKEN is not set.

APP_USER=josh APP_TOKEN=short python validate_config.py --output config.json
# Error: APP_TOKEN is too short.

APP_USER=josh APP_TOKEN=ghp_abcdefghij1234567890 python validate_config.py --output config.json
# Wrote config to config.json

cat config.json
# {
#   "user": "josh",
#   "token_length": 23,
#   "token_preview": "ghp***890"
# }
```

> [!tip] After each failing run, check `echo $?` in Bash. A non-zero value confirms your script is signaling failure correctly to the shell — that's what build tools, CI systems, and other scripts rely on.