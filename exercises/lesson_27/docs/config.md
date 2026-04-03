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

## You can also use a [YAML config file](https://docs.example.com/config-file) instead of environment variables. See the [advanced setup guide](https://claude.ai/chat/advanced.md).