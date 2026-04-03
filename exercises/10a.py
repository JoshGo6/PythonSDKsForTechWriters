'''
Write a script that loops over the tickets and prints a formatted line for each one. The line must include:

The ticket ID
The title
A label that says "ACTION REQUIRED" if the ticket is both "open" and "high" priority, "monitor" if it is "open" but not high priority, and "done" if the status is "closed"
'''

tickets = [
    ["T-01", "Login page crash", "high",   "open"],
    ["T-02", "Typo in footer",   "low",    "closed"],
    ["T-03", "API timeout",      "high",   "open"],
    ["T-04", "Dark mode flicker","medium", "open"],
    ["T-05", "Broken image link","low",    "closed"],
    ["T-06", "Token refresh bug","high",   "closed"],
]

print(f"{'Ticket ID':<12s}{'Title':<25s}{'Status':<17s}")
status = "done"
for ticket in tickets:
    if ticket[2] == "high" and ticket[3] == "open":
        status = "ACTION REQUIRED"
    elif ticket[3] == "open":
        status = "monitor"
    else:
        status = "done"
    print(f"{ticket[0]:<12s}{ticket[1]:<25s}{status:<17s}")