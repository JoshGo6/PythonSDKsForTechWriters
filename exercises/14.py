repos = [
    {
        "name": "webhook-service",
        "description": "Handles incoming GitHub webhooks",
        "language": "C++",
        "stars": 42,
        "topics": ["webhooks", "github", "automation"],
    },
    {
        "name": "old-experiment",
        "description": "",
        "language": None,
        "stars": 0,
        "topics": [],
    },
    {
        "name": "data-pipeline",
        "description": None,
        "language": "Python",
        "stars": 7,
        "topics": ["etl"],
    },
    {
        "name": "",
        "description": "A mystery repo with no name",
        "language": "Go",
        "stars": 3,
        "topics": ["experimental"],
    },
        {
        "name": "old-experiment",
        "description": "",
        "language": "",
        "topics": [],
    },
]

for repo in repos:
    if not repo.get("name"):
        print("Skipping unnamed repo.")
        print()
        continue
    description = repo.get("description")
    language = repo.get("language")
    stars = repo.get("stars")
    topics = repo.get("topics")
    print(f"Repository: {repo["name"]}")
    print("    " + (f"{description}" if description else "(no description)"))
    print("    " + ("Language unknown" if language is None else f"Language is \"{language}\""))
    print("    " + ("Unknown star number" if stars is None else f"{stars} stars"))
    if topics == []:
        print("    (no topics)")
        print("")
        continue
    print("    " + f"The topics are {", ".join(topics)}.")
    print()

