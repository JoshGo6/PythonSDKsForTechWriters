'''
repo = {
    "name": "api-reference",
    "full_name": "acme-corp/api-reference",
    "private": False,
    "description": "Public API reference documentation",
    "open_issues_count": 7,
    "default_branch": "main"
}

print(f"Repository: {repo.get('full_name')}")
print(f"Description: {repo['description']}")
print(f"Default branch: {repo['default_branch']}")
print(f"Open issues: {repo['open_issues_count']}")
'''

issue_1 = {"number" : 3, "title": "Update OAth docs", "open_issues_count": 11,}
issue_2 = {"number" : 17, "title": "Fix broken links", "open_issues_count": 7,}
issue_3 = {"number" : 3}

issue_3["title"] = "Typo in README"
issues = [issue_1, issue_2, issue_3]
for issue in issues:
    count = issue.get("open_issues_count", 0)
    if count > 10:
        priority = "High"
    elif count > 4:
        priority = "Medium"
    else:
        priority = "Low"
    print(f"Issue #{issue["number"]:<2d} - {issue["title"]:<18s} [Priority: {priority}] ")

