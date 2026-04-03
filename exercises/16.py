repos = [
    {"name": "sdk-python",    "language": "Python",     "archived": False},
    {"name": "docs-site",     "language": "JavaScript", "archived": False},
    {"name": "old-cli",       "language": "Python",     "archived": True},
    {"name": "api-reference", "language": "Markdown",   "archived": False},
    {"name": "legacy-tools",  "language": "Python",     "archived": True},
]

def build_inventory(repos, language_filter=None, include_archive=True, bullet="-"):
    output_list=[]
    for repo in repos:
        if language_filter and repo.get("language") != language_filter:
            continue
        if include_archive == False and repo.get("archived") == True:
            continue
        output_list.append(f"{bullet} {repo.get("name")} ({repo.get("language")})")
    return output_list

print("All repos")
print("="*len("All repos"))
all_repos = build_inventory(repos)
for repo in all_repos:
    print(repo)
print()

print("Python repos")
print("="*len("Python repos"))
python_repos = build_inventory(repos, language_filter="Python")
for repo in python_repos:
    print(repo)
print()

print("Active repos")
print("="*len("Active repos"))
active_repos = build_inventory(repos, include_archive=False)
for repo in active_repos:
    print(repo)
print()

complex_call = "Python, no archived, * bullet"
print(complex_call)
print("="*len(complex_call))
complex_repos = build_inventory(repos, language_filter="Python", include_archive=False, bullet="*")
for repo in complex_repos:
    print(repo)

