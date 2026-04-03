repos = [
    {"name": "docs-tools", "language": "Python", "open_issues": 4, "archived": False},
    {"name": "old-site", "language": "JavaScript", "open_issues": 0, "archived": True},
    {"name": "sdk-client", "language": "Python", "open_issues": 12, "archived": False},
    {"name": "test-runner", "language": "", "open_issues": 1, "archived": False},
    {"name": "skipped-legacy-api", "language": "Go", "open_issues": 0, "archived": True},
    {"name": "not-skipped-legacy-api", "language": "Go", "open_issues": 0, "archived": False},
    {"name": "doc-linter", "language": "Python", "open_issues": 7, "archived": False},
]

def format_issue_count(num):
    if not num:
        return "no open issues"
    if num == 1:
        return f"{num} open issue"
    elif num > 1:
        return f"{num} open issues"
    else:
        return "data error"

def repo_line(repo_dict):
    language = repo_dict.get("language") if repo_dict.get("language") else "(no language)"
    return f"{repo_dict.get('name')} [{language}] - {format_issue_count(repo_dict.get('open_issues'))}"

for repo in repos:
    if repo.get("archived"):
        continue
    print(repo_line(repo))