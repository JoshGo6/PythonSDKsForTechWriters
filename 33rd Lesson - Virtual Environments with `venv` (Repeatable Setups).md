# Lesson 33: Virtual Environments with `venv` (Repeatable Setups)

## Terminology and Theory

In Lesson 32, you created a virtual environment as a practical prerequisite for `pip install`. You ran `python3 -m venv`, activated it, and installed a package — but the focus was on `pip` and package signatures, not on the environment itself. This lesson is the full treatment. It covers what a virtual environment actually is, why it exists, how to share one reliably, and how to detect one from within a script.

**Virtual environment (venv)** A self-contained directory tree that holds its own Python interpreter and its own `site-packages` folder. When you activate a venv, `pip install` puts packages into that directory instead of into your system Python. This means you can have one project using `requests==2.31.0` and another using `requests==2.32.3` without conflict.

**System Python** The Python interpreter installed at the operating-system level (for example, `/usr/bin/python3` on Ubuntu). Installing packages into system Python affects every script on the machine, which is why Ubuntu requires the `--break-system-packages` flag when you `pip install` outside a venv. A venv eliminates this problem entirely.

**Activation** A shell command that modifies your current terminal session so that `python` and `pip` point to the venv's copies instead of the system copies. Activation is per-terminal — opening a new terminal starts unactivated. You already did this in Lesson 32 with `source <venv>/bin/activate`. This lesson explains what that command actually changes and what happens when you deactivate.

**`requirements.txt`** A plain-text file listing every package (and optionally its exact version) that a project depends on. You generate it with `pip freeze` and consume it with `pip install -r`. This is the mechanism that makes setups repeatable: hand someone the file, they recreate the exact same environment.

**Freezing** Running `pip freeze` to capture the current state of installed packages as a list of `package==version` lines. The word "freeze" means "snapshot the current state" — it does not prevent future installs.

**Reproducibility** The core motivation for venvs: given the same `requirements.txt` and the same Python version, two different machines should behave identically. This matters for documentation work because your scripts need to produce the same output on your machine, a colleague's machine, and CI.

> [!note] 
> A venv does not install a separate copy of Python from the internet. It creates a lightweight wrapper that links back to the system Python version you used to create it. The isolation applies to packages, not to Python itself.

---

## Syntax Section

### Creating a virtual environment

```bash
# Run this in your terminal, not inside Python
python3 -m venv myenv
```

`python3 -m venv` tells Python to run the `venv` module as a script. `myenv` is the directory name — you can call it anything, but `venv`, `.venv`, and `env` are common conventions.

### Activating the virtual environment

```bash
# On Linux / macOS (Bash or Zsh)
source myenv/bin/activate
```

After activation, your shell prompt changes to show the venv name in parentheses, such as `(myenv)`. This visual cue tells you that `python` and `pip` now point to the venv.

### Verifying activation

```bash
which python
# Should print something like: /home/josh/project/myenv/bin/python

which pip
# Should print something like: /home/josh/project/myenv/bin/pip
```

### Installing packages inside the venv

```bash
pip install requests
```

No `--break-system-packages` flag needed. The package goes into `myenv/lib/python3.x/site-packages/`.

### Freezing installed packages

```bash
pip freeze > requirements.txt
```

This writes every installed package and its version to `requirements.txt`. The `>` operator is shell redirection — it writes the output of `pip freeze` to the file, replacing any existing content.

### Reproducing an environment from a requirements file

```bash
pip install -r requirements.txt
```

The `-r` flag tells `pip` to read package specifications from the file. Each line is treated as a separate `pip install` argument.

### Deactivating the virtual environment

```bash
deactivate
```

This restores your shell to the system Python. The venv directory still exists — you can reactivate it later with `source myenv/bin/activate`.

### Deleting a virtual environment

There is no special command. A venv is just a directory:

```bash
rm -rf myenv
```

### Detecting a venv from within Python

```python
import sys

in_venv = sys.prefix != sys.base_prefix
```

`sys.prefix` returns the path to the active Python environment. `sys.base_prefix` returns the path to the base Python installation. When they differ, a venv is active.

> [!tip] 
> Add your venv directory name to `.gitignore` if you are using Git. You never commit the venv itself — you commit `requirements.txt` and let others recreate the venv on their own machine.

---

## Worked Examples

### Example 1: Creating a venv, installing a package, and verifying isolation

This example walks through the full lifecycle: create, activate, install, verify, deactivate, verify again.

```bash
# Step 1: Create a venv called "demo_env"
python3 -m venv demo_env

# Step 2: Activate it
source demo_env/bin/activate

# Step 3: Confirm pip points to the venv
which pip
# Output: /home/josh/project/demo_env/bin/pip

# Step 4: Install a package
pip install humanize

# Step 5: Confirm the package is available
python3 -c "import humanize; print(humanize.naturalsize(1048576))"
# Output: 1.0 MB

# Step 6: Deactivate
deactivate

# Step 7: Try the same import with system Python
python3 -c "import humanize; print(humanize.naturalsize(1048576))"
# Output: ModuleNotFoundError: No module named 'humanize'
```

The `ModuleNotFoundError` at step 7 confirms that `humanize` was installed only inside the venv. System Python has no knowledge of it. This is the isolation that venvs provide.

### Example 2: Freezing and reproducing an environment

This example shows the workflow for handing a project to someone else (or to your future self on a different machine).

```bash
# Inside an activated venv where you've already installed packages:
pip freeze
# Output (example):
# certifi==2024.2.2
# charset-normalizer==3.3.2
# humanize==4.9.0
# idna==3.6
# requests==2.31.0
# urllib3==2.2.1

# Write that list to a file
pip freeze > requirements.txt

# Later, on a fresh machine or in a new venv:
python3 -m venv fresh_env
source fresh_env/bin/activate
pip install -r requirements.txt

# Verify
python3 -c "import requests; print(requests.__version__)"
# Output: 2.31.0
```

Notice that `pip freeze` lists not only the packages you explicitly installed but also their dependencies. `requests` pulls in `certifi`, `charset-normalizer`, `idna`, and `urllib3`. Freezing captures all of them so the reproduction is exact.

### Example 3: A Python script that checks whether it is running inside a venv

You can detect venv activation from within a Python script using `sys.prefix` and `sys.base_prefix`. When running inside a venv, these two values differ. When running under system Python, they are the same.

```python
import sys

if sys.prefix != sys.base_prefix:
    print(f"Running inside a venv: {sys.prefix}")
else:
    print("Running under system Python — no venv detected.")
    print("Consider activating a venv before running this script.")
    sys.exit(1)
```

Running this inside an activated venv prints:

```
Running inside a venv: /home/josh/project/demo_env
```

Running it outside a venv prints:

```
Running under system Python — no venv detected.
Consider activating a venv before running this script.
```

This pattern is useful when you write a script that depends on packages installed in a venv and you want to give the user a clear error message instead of a confusing `ModuleNotFoundError`.

---

## Quick Reference

```python
# Create a virtual environment named "myenv"
# (run in terminal, not inside Python)
python3 -m venv myenv

# Activate the virtual environment (Linux/macOS)
source myenv/bin/activate

# Verify which python and pip are active
which python
which pip

# Install a package into the active venv
pip install requests

# Install a specific version of a package
pip install requests==2.31.0

# Freeze current packages to a requirements file
pip freeze > requirements.txt

# Install all packages from a requirements file
pip install -r requirements.txt

# Check whether a venv is active from Python
import sys
in_venv = sys.prefix != sys.base_prefix

# Deactivate the virtual environment
deactivate

# Delete a virtual environment (it is just a directory)
rm -rf myenv
```

---

## Audit

The exercise below requires the following operations. Each one is verified against the lesson where it was introduced.

|Operation|Introduced in|
|---|---|
|`python3 -m venv`, `source .../bin/activate`, `deactivate`|Lesson 33 (current)|
|`pip freeze > requirements.txt`|Lesson 33 (current)|
|`pip install -r requirements.txt`|Lesson 33 (current)|
|`sys.prefix` vs `sys.base_prefix`|Lesson 33 (current)|
|`json.load()`, `json.dumps()`|Lesson 28|
|`sys.argv` (conceptual foundation)|Lesson 29|
|`argparse` with positional arg and optional flags|Lesson 30|
|`os.getenv()`, environment variable loading|Lesson 31|
|`pip install` (into a venv)|Lesson 32|
|`import sys`, `sys.exit()`|Lesson 17 (imports), Lesson 29 (`sys` module)|
|`import pathlib`, `Path`, `.exists()`, `.read_text()`|Lesson 23|
|`logging.basicConfig()`, `logging.info()`, `logging.error()`|Lesson 21|
|`try/except` for specific exceptions|Lesson 19|
|`if/elif/else`|Lesson 10|
|`for` loop, `.split()`, `.strip()`|Lessons 9, 5|
|f-strings|Lesson 6|
|Functions with default parameters|Lessons 15–16|

All five previous lessons (28–32) are represented. No forward dependencies exist.

---

## Exercise

### Venv Dependency Reporter

Write a script called `venv_report.py` that inspects a virtual environment's installed packages and produces a summary report. The script must be run from inside an activated venv.

The script must do the following:

1. Accept two arguments via `argparse`: a positional argument for the path to a `requirements.txt` file, and an optional flag `--output` that takes a file path. When `--output` is provided, the report is written as JSON to that file. When `--output` is omitted, the report is printed to stdout as plain text.
    
2. Read an environment variable called `REPORT_LABEL` using `os.getenv()`. This value is used as a label in the report output. If the variable is not set, default to the string `"unlabeled"`.
    
3. Check whether the script is running inside a virtual environment by comparing `sys.prefix` to `sys.base_prefix`. If no venv is active, log an error message and exit with code `1`.
    
4. Read the `requirements.txt` file at the given path. Parse each non-empty, non-comment line to extract the package name (the part before `==`). Collect these names into a list.
    
5. For each package name, attempt to import it using a `try/except` block. Build two lists: one for packages that imported successfully, and one for packages that raised `ModuleNotFoundError`.
    
6. Build a report dictionary with three keys: `"label"` (the value from step 2), `"available"` (the list from step 5), and `"missing"` (the list from step 5).
    
7. If `--output` was provided, write the report dictionary to the specified path as a JSON file using `json.dump()` with `indent=2`, and log an `INFO`-level message confirming the write. If `--output` was omitted, print the report as formatted plain text to stdout.
    

> [!tip] 
> Some packages use hyphens in their PyPI name (e.g., `charset-normalizer`) but underscores in their import name (`charset_normalizer`). When you extract the package name from a `requirements.txt` line, replace any hyphens with underscores before attempting the import.

> [!note] 
> Lines in `requirements.txt` that begin with `#` are comments. Your parser should skip them, along with blank lines.

#### Setup

Before running the script, create a test environment:

```bash
python3 -m venv test_env
source test_env/bin/activate
pip install requests
pip freeze > test_requirements.txt
export REPORT_LABEL="test-run-01"
```

#### Expected output (plain-text mode)

```
$ python3 venv_report.py test_requirements.txt
Report: test-run-01

Available packages:
  - certifi
  - charset_normalizer
  - idna
  - requests
  - urllib3

Missing packages:
  (none)
```

#### Expected output (JSON mode)

```
$ python3 venv_report.py test_requirements.txt --output report.json
INFO:root:Report written to report.json
```

Contents of `report.json`:

```json
{
  "label": "test-run-01",
  "available": [
    "certifi",
    "charset_normalizer",
    "idna",
    "requests",
    "urllib3"
  ],
  "missing": []
}
```

#### Expected output (no venv active)

```
$ deactivate
$ python3 venv_report.py test_requirements.txt
ERROR:root:No virtual environment detected. Activate a venv before running this script.
```

#### Expected output (REPORT_LABEL not set)

```
$ unset REPORT_LABEL
$ python3 venv_report.py test_requirements.txt
Report: unlabeled

Available packages:
  - certifi
  - charset_normalizer
  - idna
  - requests
  - urllib3

Missing packages:
  (none)
```