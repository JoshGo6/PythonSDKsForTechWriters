'''
Exercise 1 — Build and read a contributor table
Create a Python script that builds a nested list. Each inner list should represent one contributor and contain three fields in this order: username (string), number of commits (integer), and primary language (string). Include at least four contributors with realistic-looking data.
Your script must print each contributor as a single formatted line using an f-string, so the output looks like a readable report with labelled fields. Access every value using chained indexing — do not use any other method to pull data out of the list.
Run your script and verify the output at the terminal.
'''
import copy

record_0 = ["josh", 5, "Go"]
record_1 = ["gordon", 10, "Python"]
record_2 = ["bob", 7, "C#"]
record_3 = copy.deepcopy(record_2)

record_3[0] = "alice"
record_3[2] = "Assembly"

records = []
records = [record_0, record_1]
records.extend([record_2, record_3])
print(records)
records.append(["josephine", 8, "Cobol"])
print(records)
for record in records:
    print(record[-1])

