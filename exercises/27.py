import re
import mistune
from pathlib import Path

usage_content = '''\
---
title: Usage
sidebar_position: 2
tags: api, examples
---

## title: Usage Overview 

# Usage Overview

Import the SDK and initialize a client:

```python
# Create a client instance
from example_sdk import Client
client = Client(token="your-token")
```

## Fetching Data

Use the [fetch method](https://docs.example.com/fetch) to retrieve records:

```python
# Fetch all records
records = client.fetch_all()
```

## Error Handling

## Wrap calls in a try/except block. See the [error reference](https://claude.ai/chat/errors.md) for details.'''


config_content = '''\
---
title: Configuration Reference
sidebar_position: 5
tags: config, settings, advanced
---

## title: Configuration Reference sidebar_position: 5 tags: config, settings, advanced

# Configuration Reference

## Environment Variables

Set `EXAMPLE_TOKEN` before running. See [token setup](https://docs.example.com/auth) for details.

### Required Variables

The following are required:

- `EXAMPLE_TOKEN` — your API token
- `EXAMPLE_ENV` — set to `production` or `staging`

To set an environment variable, use the following code:

```bash
# This is a comment. It is not a heading, and it shouldn't be promoted.
export var="VAR_VALUE"
```

### Optional Variables

These are optional:

- `EXAMPLE_TIMEOUT` — request timeout in seconds
- `EXAMPLE_LOG_LEVEL` — one of `debug`, `info`, `warn`

```bash
# You can change the value of a variable.
export var="DIFFERENT_VALUE"
```

## Config File

## You can also use a [YAML config file](https://docs.example.com/config-file) instead of environment variables. See the [advanced setup guide](https://claude.ai/chat/advanced.md).'''

install_content = '''\
---
title: Installation Guide
sidebar_position: 1
tags: setup, quickstart
---

## title: Installation Guide

# Installation Guide

Download the package from [the releases page](https://github.com/example/releases).

## Prerequisites

You need [Python 3.10+](https://python.org/) installed.

## Steps

Run the following command:

```bash
# Install the package globally
pip install example-sdk
```

Then verify:

```bash
# Check the version
example-sdk --version
```

## See the [usage guide](https://claude.ai/chat/usage.md) for next steps.'''

working_dir = Path("lesson_27/docs")
working_dir.mkdir(parents=True, exist_ok=True)
Path(working_dir / "install.md").write_text(install_content, encoding='utf-8')
Path(working_dir / "config.md").write_text(config_content, encoding='utf-8')
Path(working_dir / "usage.md").write_text(usage_content, encoding = 'utf-8')

md = mistune.create_markdown(renderer=None)
found = False

for file in sorted(working_dir.rglob("*.md")):
    if found:
        print()
        found = False
    print(file.name)
    content = file.read_text(encoding='utf-8')
    tokens = md(content)
    for token in tokens:
        if "children" in token:
            for child in token["children"]:
                if child["type"] == "link":
                    found = True
                    url = child["attrs"]["url"]
                    link_text_parts = [c["raw"] for c in child["children"] if c["type"] == "text"]
                    link_text = "".join(link_text_parts)
                    print(f"  [{link_text}]({url})")
                    found = True
