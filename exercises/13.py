repos = [
    {"name": "auth-service", "owner": "acme-corp", "stars": 230, "status": "active"},
    {"name": "legacy-api", "owner": "acme-corp", "stars": 14, "status": "archived"},
    {"name": "docs-site", "owner": "acme-corp", "stars": 87, "status": "active"},
    {"name": "test-harness", "owner": "acme-corp", "stars": 5, "status": "archived"},
    {"name": "sdk-python", "owner": "acme-corp", "stars": 412, "status": "active"},
    {"name": "old-dashboard", "owner": "acme-corp", "stars": 31, "status": "archived"},
]

active_repos = []
archived_repos = []

for repo in repos:
    name = repo["name"]
    owner = repo["owner"]
    stars = repo["stars"]
    if repo["status"] == "active":
        active_repos.append((name, owner, stars,))
    else:
        archived_repos.append((name, owner, stars,))

print("=== Active Repos ===")
for repo in active_repos:
    print(f"{repo[0]:<15} {(repo[1] + ':'):<12} {repo[2]}")
print(f"Total active = {len(active_repos)}")
print("")
print("=== Archived Repos ===")
for repo in archived_repos:
    print(repo)
print(f"Total archived = {len(archived_repos)}")
for repo in active_repos:
    print(repo)