---
name: python-sdk-lesson
description: Generate a Python lesson for tech. writers where the learning goal is processing text files, making API calls, and working with Python SDKs.
---

# Python Lesson Plan for GitHub SDK Project

## Purpose of This Artifact

This document is a reusable curriculum contract between the learner (you) and an LLM.

Its purpose is to:

- Provide a structured, fast-track learning path for Python.
- Focus primarily on the Python needed to effectively use and document the GitHub Python SDK (PyGithub).
- Secondarily, provide instruction on reading from, writing to, and manipulating text documents (the stuff you actually want to automate).
- Serve as a stable contract that any future session can read to generate individual lessons on demand.

This artifact holds the rules for generating individual lessons. The roadmap itself is in `references/roadmap.md`.

## Read these first

Two files, in this order, before drafting any part of a lesson.

| File | What it decides |
| --- | --- |
| `~/.claude/skills/doc-house-style/references/house-style.md` | How every sentence, heading, fence, table and callout is written |
| `references/roadmap.md` | The 63 stubs; the scope of the lesson you are writing and of every lesson before it |

The house style is the only copy of the writing rules, and this skill does not restate them; it adds only what is specific to a Python lesson. If that path does not resolve, find the `doc-house-style` skill wherever skills are installed and read `references/house-style.md` inside it. Only if it is genuinely absent should you say so rather than proceeding from recall — the rules in it are the ones that keep lessons from needing rework.

Two of its rules are the ones this curriculum's output has most often broken, so check them by name before delivering: **every fenced block gets a lead-in sentence above it**, and **headings are imperative and carry no em dash**.

## Instructions for the LLM When Generating a Lesson

These rules apply to every lesson in the roadmap, from Lesson 1 onward. If an earlier lesson was generated under a previous version of this contract, regenerating it under this one is the correct thing to do — the roadmap entry is the specification, not whatever file already exists.

When you say:

> "Generate Lesson X"

The LLM must:

1. Follow the scope the roadmap stub for Lesson X defines.
2. Assume prior lessons have already been completed.
3. Reinforce earlier material where appropriate.
4. Use the required lesson structure below.
5. Write to the house style.
6. Verify the lesson by executing it, before presenting any of it to you. Verify silently.
7. Follow the constraints given in this document.

The exercises are deliberately scaled to real work.

## Required Lesson Structure

Each generated lesson must contain the following elements, in the order they're presented here:

1. **Terminology and Theory**
    - Define new vocabulary clearly.
    - Keep explanations practical, not academic.
2. **Syntax Section**
    - Show the relevant syntax patterns.
    - Explain what each component does.
    - Where two calls are easily confused, show them adjacent in one block with the difference commented.
3. **Worked Examples (2-3)**
    - Fully runnable examples.
    - Clearly explain what is happening.
    - Use realistic patterns aligned with SDK usage and text-processing scripts.
4. **Lookup Table**
    - A Markdown table consolidating every piece of syntax the lesson introduced. Its columns and rules are in the house style.
    - All new syntax introduced in the lesson MUST appear in it.
5. **Exercises (1)**
    - Require use of _new_ material from the current lesson.
    - Should not contain hints as to how to complete the exercise.
    - **Hard rule**: Should reinforce previous lessons by requiring knowledge of them.
    - Should reinforce a diverse set of skills from previous lessons, instead of just skills from one previous lesson. Additionally, should require skills from the previous five lessons, if doing so would not make the exercise be awkward. If this would result in the exercise being awkward, use skills from a subset of the previous five lessons so that the exercise won't be awkward.
    - **Hard rule:** An exercise **MUST NOT** require _any_ Python operation, syntax, library, or tool that has not been taught in the current lesson or in earlier lessons. If a helpful technique exists but is "coming later," the exercise must not depend on it. In other words, exercises require the use of the current lesson and previous lessons, not future lessons.
    - **Hard rule:** Every exercise must require the learner to write and run code that produces output testable at the command line. An exercise that involves only passive reading or providing a written answer is not sufficient.
    - Should present the desired output so you can verify that you got the correct answer. That output must be copied from a real run of your own solution, never composed by hand.

## Verification specific to lessons

The general verification standard is in the house style. Two checks belong only to lessons:

**Solve the exercise yourself.** The house style requires it of any artifact that asks the reader to produce something. Here it carries a second job: a solution that runs using only the material taught so far is the proof that the exercise does not reach forward.

**Check dependencies across the whole lesson.** Create an audit of every Python operation, syntax pattern, library, built-in function, and language construct the lesson uses, and verify each was introduced in the current lesson or a prior roadmap entry. If any depends on a future lesson — even a loop, a conditional, an import, a `class`, or a decorator — decide, using the roadmap, whether to rewrite the code to remove the dependency or to extend the lesson to cover it. Check against your own reference vault's syntax index when one is available, and against `references/roadmap.md` otherwise.

The audit covers every line of Python the lesson contains — the terminology section, the syntax blocks, the worked examples, the setup and fixture code, and the exercise. A worked example or a published fixture that uses syntax the learner has not met is the same defect as an exercise that does, and it is the harder one to notice, because nothing fails when you run it — you simply cannot read what you are running.

**When a forward dependency is genuinely unavoidable, mark it, do not hide it.** Some fixtures cannot be written within the taught set: `http.server` cannot be used without `class`, `self`, and inheritance, and the PyGithub stub server in lessons 47-58 has the same problem. Rewriting is the first choice and marking is the fallback, permitted only for code the learner runs rather than writes. When it applies, all four of these are required:

- A sentence immediately before the code, telling you that you do not need to read it.
- The names of the constructs it uses that you have not met, and the roadmap lessons that cover them.
- The reason it could not be avoided.
- A statement that nothing in the syntax section, the worked examples, or the exercise requires understanding it, having confirmed that this is true.

Comments inside the code carry the same marking where a reader is likely to stop and puzzle at a specific line. The test is whether you can tell, without asking, which parts of the page you are expected to follow and which parts are scaffolding.

Never let an unavoidable dependency reach the exercise. The exercise hard rule above admits no exception: the learner writes that code, so every construct in it must already be taught.

**Write the audit out in full — every construct, every authorization — to a scratch file**, under the house style's rule that a check of this shape is written down rather than printed.

Nothing about the audit is printed with the lesson — but the marking itself is part of the lesson text and always ships.

## Run the PyGithub lessons against a local stub server

Lessons 47-58 use PyGithub, which is not installed by default. Install it yourself into a virtual environment before generating any of them:

```bash
python3 -m venv /tmp/pygithub-venv && /tmp/pygithub-venv/bin/pip install PyGithub
```

Do not generate these lessons with invented output. If the install fails, say which claims cannot be verified before generating, and let you decide.

**The examples still run against a local stub rather than real GitHub.** A lesson that called the live API would depend on your token, on the state of a real repository, and on a rate limit none of the examples control, so its output would not reproduce for you. Build the fixture the same way `HTTP Essentials` already does for `requests`:

1. Serve GitHub-shaped JSON from a local `ThreadingHTTPServer` on `127.0.0.1`. It must be `ThreadingHTTPServer` — a single-threaded `HTTPServer` never accepts the second request and the script hangs with no error.
2. Point the real client at it: `Github(base_url="http://127.0.0.1:PORT")`. PyGithub supports a custom base URL for GitHub Enterprise, so every example runs through genuine PyGithub code.
3. Publish the server in the lesson's setup section, the way the echo server is published, and say plainly that swapping the base URL back hits real GitHub. The server is fixture code written with `class` and `self`, so it carries the marking required under **Check dependencies across the whole lesson** above.

With the package installed you can also read its source directly, which is the authority for signatures, exception types, and pagination behavior. Never source those from the local server's behavior — the server is your fixture, not the SDK.

## Handing off to you

At delivery, in chat prose and not in a file, name the topics the lesson introduced in a few lines, and flag any claim that contradicts something an earlier lesson or an existing reference page states. That is the whole handoff.

## Constraints

- Avoid unnecessary depth intended for full software engineering roles.
- Ensure lessons are practical, incremental, and aligned with SDK usage.
- The goal is fluency for SDK work _and_ text manipulation a technical writer can use for scripting operations.
- The goal is **NOT** mastery of Python as a language. Do not include unnecessary digressions (advanced OOP theory, decorators beyond `@property` recognition, metaclasses, etc.).
- When choosing examples, prioritize:
    - Working with strings, lists, dicts, and JSON-like objects.
    - Reading/writing files safely (encoding, newlines, paths).
    - "Glue code" patterns: loops, conditionals, functions, exceptions, logging, CLI args.
    - Consuming SDK objects and translating SDK behavior into docs-friendly explanations.

## Output Format

The output you, the LLM, create must be a single Markdown file for use in Obsidian. Formatting rules — callouts, fences, tables — are in the house style.

Run the lesson validator before delivering:

```bash
python3 ~/.claude/skills/doc-house-style/scripts/check_lesson.py --profile python <lesson file>
```

Fix everything it reports, then rerun. It catches the mechanical failures that are otherwise caught by reading: a fence with no lead-in above it, malformed callouts, missing or ragged lookup tables, unbackticked exception names, code in an unlabeled or `text` fence, and relic sections. The `--profile` flag selects the lesson shape; `shell` is the Bash curriculum's and expects a different set of sections.

## Final Objective

By completing these lessons, you will:

- Be fluent enough in Python to read and write scripts using PyGithub and work with mastery in most Python-centric SDKs.
- Be able to work with REST APIs directly using the `requests` library, including authenticated requests, error handling, and response parsing — essential for API documentation work where SDKs may not exist or where understanding the raw API behavior is required.
- Understand how SDK abstractions map to REST APIs.
- Be capable of producing meaningful, employer-ready SDK documentation for any Python-centric SDK, not just PyGithub.
- Be able to understand and document Python that developers write, including common patterns like list comprehensions, type hints, `*args`/`**kwargs`, `@property`, lambda expressions, and `async/await`.
- Know what to look up when encountering unfamiliar Python patterns.
- Be able to write Python scripts to process text documents to extract text, modify text, and reorganize text for your technical writing job. This includes editing documents in place, as well as creating new documents from existing documents.

This curriculum intentionally avoids advanced software engineering depth. It prioritizes clarity, speed, practical SDK literacy, and the ability to use Python for technical writing.
