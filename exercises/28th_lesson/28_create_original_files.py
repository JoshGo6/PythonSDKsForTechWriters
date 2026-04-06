from pathlib import Path


def json_filename(raw_filename):
    return raw_filename.replace("_content", "").replace("_", "-") + ".json"

before = set(vars())

quickstart_content = '''\
{
    "title": "Quickstart Guide",
    "status": "published",
    "tags": ["getting-started", "tutorial"],
    "word_count": 1250
}
'''

api_reference_content = '''\
{
    "title": "API Reference",
    "status": "draft",
    "tags": ["api", "reference"],
    "word_count": 3400
}
'''

missing_key_content = '''\
{
    "title": "Advanced Procedures",
    "status": "draft",
    "tags": ["api", "tutorial"]
}
'''

changelog_content = '''\
{
    "title": "Changelog",
    "status": "published",
    "tags": ["changelog"],
    "word_count": 870
}
'''

broken_content = '''\
{"title": "Bad Entry", "status": "published", "tags": ["oops"]
'''

auth_guide_content = '''\
{
    "title": "Authentication Guide",
    "status": "review",
    "tags": ["auth", "security", "getting-started"],
    "word_count": 2100
}
'''

after = set(vars())
files_with_suffix = list(after - before - {"before"})

working_dir = Path("pages")
for raw_filename in files_with_suffix:
    json_file = json_filename(raw_filename)
    Path(working_dir / json_file).write_text(globals()[raw_filename], encoding="utf-8")