"""
# Lesson 7 Exercises — Lists I: Creation, Indexing, Slicing

---

## Exercise 1: Slice and report a file list

Create a Python script called `file_report.py`.

Inside it, define a list called `doc_files` containing these seven strings, in this order:

    "intro.md"
    "quickstart.md"
    "authentication.md"
    "endpoints.md"
    "pagination.md"
    "errors.md"
    "changelog.md"

Using only indexing, slicing, `len()`, and f-strings, your script must print
the following — with actual values filled in, not hardcoded strings:

1. The first file in the list.
2. The last file in the list.
3. The total number of files.
4. A slice containing only the middle three files (indices 2, 3, and 4),
   printed as a list.
5. A slice containing everything except the first and last files.

Run the script and verify the output matches what you expect before moving on.

"""
doc_files = [ "intro.md", "quickstart.md", "authentication.md", "endpoints.md", "pagination.md", "errors.md" "changelog.md" ]
print(doc_files)
print(f"The first item is {doc_files[0]}.")
print(f"The last item is {doc_files[-1]}.")
print(f"The total numer of files is {len(doc_files)}.")
print(f"Items at indices 2, 3, and 4: {doc_files[2:5]}.")
print(f"Everything but the first and last: {doc_files[1:-1]}.")

"""
