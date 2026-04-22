from pathlib import Path
import re

'''
> [!note]
'''


for md_file in Path('.').glob("*.md"):
    with open(md_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    updated_content = re.sub(r'(> \[!(?:note|tip|important|warning|caution)\] )( )*(?!\n)', r'\1\n> ', original_content, flags=re.MULTILINE)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
