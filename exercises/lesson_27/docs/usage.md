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

## Wrap calls in a try/except block. See the [error reference](https://claude.ai/chat/errors.md) for details.