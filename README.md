# Python SDK Learning Path for Tech. Writers

This repo contains a tech. writer-oriented Python course that I've developed over the course of many hours (and continue to periodically refine)—first with GPT, and then with Claude. There are many Python courses available, but their scopes vary widely. Some courses are small, and some are geared to making the student a full-blown Python developer. I wanted a course specific to the needs of a senior tech. writer.

## Scope of the Course

After finishing the course, the student should be able to do the following with Python:

- Process text files—in particular, Markdown, YAML, JSON, and CSV files—to include extracting text; changing text; reading and writing files; and deleting, moving, and renaming files.
- Place raw API calls and extract and transform the JSON objects they return.
- Use Python SDKs skillfully to the point that they can document them for others.

> [!note]
> This course is **not** designed to make the student into a full-blown Python developer. After finishing the course, the student will be able to skillfully work with objects, but not to author classes.

A typical use case addressed by this course is a situation where a Markdown document contains headings with sequential digits (for instance, "Lesson 1," "Lesson 2,", "Lesson 3," and so forth). When you insert a new heading in the middle of the document, the subsequent heading numbers are all off by one. Using the tools taught in this course, you can author a Python script to fix this numbering. I had this problem, and using the skills in this course, I authored a Python script to fix the problem.

## Instructions for use

This course ships as a pair of [Claude Code](https://claude.com/claude-code) skills under [`.claude/skills`](./.claude/skills/), rather than as files you upload by hand.

> [!note]
> **Prerequisite:** you need [Claude Code](https://claude.com/claude-code) installed and set up.

**Installing the skills**

This bundle installs two skills:

- `python-sdk-lesson` — the curriculum contract: the 63-lesson roadmap, the required structure for each lesson, and the verification rules specific to a lesson.
- `doc-house-style` — the shared writing contract (`references/house-style.md`) and the lesson validator (`scripts/check_lesson.py`) that `python-sdk-lesson` depends on. Both skills must be installed together.

To use them with this repo, clone it, then do one of the following:

- Run Claude Code from the repo root. It picks up `.claude/skills` automatically as project-scoped skills, or
- Copy both folders under `.claude/skills` into `~/.claude/skills` to make them available in any project.

**Generating a lesson**

Once the skills are installed, open Claude Code and give it a prompt such as this one:

```text
Generate lesson 12
```

Claude Code reads the roadmap stub for that lesson number, writes it to house style, and verifies it before showing it to you — no other files need to be attached.

> [!caution]
> LLMs, like humans, are fallible. It's quite common to find errors in LLM output, and errors have shown up in generated lessons, including in the exercises. If you clone this repo, it is on you to verify that the material produced is accurate.

## Personal progress

As of September 7, 2026, I am up to lesson 39, [Handling and Debugging API Responses](./39th%20Lesson%20—%20Handling%20and%20Debugging%20API%20Responses.md).

