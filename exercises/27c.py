from pathlib import Path
import re

working_dir = Path("lesson_27/docs")
md_files = working_dir.rglob("*.md")
metadata = []
metadata_pattern = re.compile(r"\A---\s*?\ntitle:\s+(.*?)\s*\nsidebar_position:\s+(.*?)\s*\ntags:\s+(.*?)\s*\n---")

for file in md_files:
    content = file.read_text(encoding='utf-8')
    m = metadata_pattern.search(content)
    metadata.append((m.group(1), m.group(2), m.group(3), file.name))
    metadata = sorted(list(metadata), key=lambda p: p[1])

print("Documentation sidebar order:")
for item in metadata:
    print(f"{item[1]}. {item[0]} ({item[3]})")