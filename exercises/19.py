submissions = [
    {"student": "Alice", "score": "92"},
    {"student": "Bob", "score": "not_graded"},
    {"student": "Carol"},
    {"student": "Dan", "score": "78"},
    {"student": "Eve", "score": ""},
    {"student": "Frank", "score": "85"},
    {"student": "Josh", "score": "eighteen"},
]

def process_submission(record):
    name = record["student"]
    try:
        score = int(record["score"])
        error_message = None
    except (KeyError, ValueError) as e:
        score = None
        error_message = str(e)
    return (name, score, error_message)

valid_scores = []
invalid_scores=[]

for submission in submissions:
    flattened_list = process_submission(submission)
    if flattened_list[1] is None:
        invalid_scores.append(flattened_list)
    else:
        valid_scores.append(flattened_list)

print("Valid scores:")
for entry in valid_scores:
    print(f"{entry[0]}: {entry[1]}")
print()
print("Skipped:")
for entry in invalid_scores:
    print(f"{entry[0]}: bad or missing score")
print(f"\nTotal: {len(valid_scores)} valid. Skipped {len(invalid_scores)} invalid entries.")
