'''
Write a script called `dep_report.py` that reads a JSON file containing a list of software dependencies and prints a formatted table to the terminal. Make sure your virtual environment is active and `tabulate` is installed before running the script.

**Input file (`deps.json`):**

Create this file in your working directory:

```json
[
    {"name": "PyGithub", "version": "1.59.1", "category": "sdk"},
    {"name": "requests", "version": "2.31.0", "category": "http"},
    {"name": "tabulate", "version": "0.9.0", "category": "formatting"},
    {"name": "Flask", "version": "3.0.0", "category": "http"},
    {"name": "mistune", "version": "3.0.2", "category": "parsing"},
    {"name": "PyYAML", "version": "6.0.1", "category": "parsing"},
    {"name": "black", "version": "24.3.0", "category": "formatting"}
]
```

**Requirements:**

1. The script must accept two command-line arguments using `argparse`:
    - A required positional argument: the path to the JSON file.
    - An optional flag `--category` that filters the output to only show dependencies in that category. If omitted, show all dependencies.
2. Load the JSON file. If the file does not exist, catch the `FileNotFoundError`, log an error message, and exit.
3. If `--category` is provided, filter the list to only include entries where the `"category"` value matches the flag's value. If no entries match, log a warning and exit.
4. Sort the filtered list alphabetically by `"name"` using `sorted()` with a `key=` argument. The key should be a small function you define that returns the lowercase name of a dependency dict. (Do not use `lambda` — it has not been taught yet.)
5. Format the sorted list as a table using `tabulate` with `headers="keys"` and `tablefmt="grid"`.
6. Print the table.
7. Use `logging` at the `INFO` level to report how many dependencies were loaded and how many are being displayed.
'''