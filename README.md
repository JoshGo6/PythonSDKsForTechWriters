# Python SDK Learning Path for Technical Writers

This repo contains a technical writer-oriented Python course that I've developed over the course of many hours (and continue to periodically refine)—first with GPT, and then with Claude. There are many Python courses available, but their scopes vary widely. Some courses are small, and some are geared to making the student a full-blown Python developer. I wanted a course specific to the needs of a senior tech. writer.

## Scope of the Course

After finishing the course, the student should be able to do the following with Python:

- Process text files—in particular, Markdown, YAML, JSON, and CSV files—to include extracting text; changing text; reading and writing files; and deleting, moving, and renaming files.
- Place raw API calls and extract and transform the JSON objects they return.
- Use Python SDKs skillfully to the point that they can document them for others.

> [!note]
> This course is **not** designed to make the student into a full-blown Python developer. After finishing the course, the student will be able to skillfully work with objects, but not to author classes.

A typical use case addressed by this course is a situation where a Markdown document contains headings with sequential digits (for instance, "Lesson 1," "Lesson 2,", "Lesson 3," and so forth). When you insert a new heading in the middle of the document, the subsequent heading numbers are all off by one. Using the tools taught in this course, you can author a Python script to fix this numbering. I had this problem, and using the skills in this course, I authored a Python script to fix the problem.

## Instructions for use

This course ships as a pair of [Claude Code](https://claude.com/claude-code) skills under [`skills/`](./skills/), rather than as files you upload by hand.

### Prerequisite

- [Claude Code](https://claude.com/claude-code) installed and set up.

### Installing the skills

This bundle installs two skills:

- `python-sdk-lesson` — the curriculum contract, including the description of each lesson's content, the required structure for each lesson, and the verification rules specific to a lesson.
- `doc-house-style` — the shared writing contract (`references/house-style.md`) and the lesson validator (`scripts/check_lesson.py`) that `python-sdk-lesson` depends on. Both skills must be installed together.

The bundle here is a frozen snapshot, and I don't update it. My own copies of these skills have moved on, but they now read files outside the two skill folders and hardcoded paths on my own machine, so they can't be published as they stand. The snapshot generates complete, verified lessons on its own, so the lessons you generate will differ in small ways from the sample, which my newer copies wrote.

To install the skills, clone this repo and copy both folders into your own skills directory:

```bash
cp -r skills/python-sdk-lesson skills/doc-house-style ~/.claude/skills/
```

That makes them available in every project rather than only in this one. Claude Code reads `~/.claude/skills` on startup, so restart it afterward.

> [!note]
> The folders deliberately sit under `skills/` rather than `.claude/skills/`, so that cloning this repo never silently overrides a newer copy of these skills you may already have installed.

### Generating a lesson

Once the skills are installed, open Claude Code and give it a prompt such as this one:

```text
Generate lesson 12
```

> [!important]
> The skills write each lesson in Obsidian-flavored Markdown, for reading in [Obsidian](https://obsidian.md). A lesson uses callouts with titles, collapsible callouts, and links in Obsidian's `[[#Heading]]` form, and GitHub shows the markup of each of those as literal text, so open your lessons in Obsidian or modify the skills to generate the lessons in another flavor of Markdown, such as GitHub Flavored Markdown (GFM).

## The sample lesson

[`sample/`](./sample/) holds the latest lesson I've finished working through. I copy it there by hand and convert it to GitHub-flavored Markdown so it displays correctly here: the collapsible callouts become HTML `<details>` blocks, and I remove the references to other lessons so the lesson reads on its own. When I finish a newer lesson, it replaces the one in `sample/`.

## Personal progress

As of October 22, 2026, I'm up to Lesson 41, [List Comprehensions](./sample/41st%20Lesson%20%E2%80%94%20List%20Comprehensions.md).

## Changelog

- **October 22, 2026:** I removed the lesson files and the `update_callouts.py` script from the top of the repo, and added the single sample lesson in `sample/`. The removed lessons are still in the Git history, and you can browse them as they last stood at commit [`273c081`](https://github.com/JoshGo6/PythonSDKsForTechWriters/tree/273c081).
