""""
## Exercise 2: Build a label list incrementally

Create a Python script called `label_builder.py`.

Start with this list already defined:

    labels = ["bug", "documentation"]

Then, in order:

1. Use `append()` to add the string "  enhancement  " (extra spaces — intentional).
2. Before printing anything, clean up that last item: retrieve it by index,
   call `.strip()` on it, and reassign it back to the same position
   using `labels[-1] = ...`
3. Use `extend()` to add these three labels at once:
   "help wanted", "good first issue", "wontfix"
4. Print the final list.
5. Print the total number of labels:   f"Total labels: {len(labels)}"
6. Print the second-to-last label:     f"Second to last: {labels[-2]}"

The goal of step 2 is to practice combining index access with a string method —
a pattern you will use often when cleaning up SDK-returned data.
"""
labels = ["bug", "documentation"]
print(labels)
labels.append("  enhancement  ")
cleaned_up = labels[-1].strip()
print(cleaned_up)
labels[-1] = cleaned_up
print(labels)
labels.extend(["help wanted", "good first issue", "wontfix"])
print(labels)
print(f"The total number of labels is {len(labels)}")
print(f"Second to last label: {labels[-2]}.")
