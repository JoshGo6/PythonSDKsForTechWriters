"""
Exercise 1 — Values and Types with f-strings

Create three variables: one string (repo_name), one integer (issue_count), and one boolean (has_wiki).
Using a single f-string per line, print each variable in a way that shows both the value and the result of calling type() on it.
Each printed line should clearly show the variable name, its value, and its type.

Exercise 2 — Inspect → Change → Rerun (with visible spaces)

Create a string variable containing leading and trailing spaces.
Use an f-string to print the variable inside visible quotes so you can see the whitespace.
Run the script and observe the output.
Then remove the spaces from the string’s value, rerun the script, and compare the two outputs.
"""

repo_name = "Josh's great repo"
issue_count = 8
has_wiki = False

print(f"\"{repo_name}\" has an issue count of {issue_count}, is {has_wiki} and is of type {type(repo_name)}")