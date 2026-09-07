---
name: doc-house-style
description: The single shared writing contract for your technical documentation — clarity rules, heading rules, placement rules, lookup table rules, fixture conventions, callout format, fence and lead-in rules, the interview principle, the editing standard, and verification rules. Read by every skill that produces documentation or governs how it is written; it is the one place these rules exist. Not invoked on its own. If you want to change how lessons or documentation pages are written — clarity, headings, tables, callouts, fixtures, fences, editing, verification — the edit belongs in this skill's `references/house-style.md`, not in any of the others.
---

# Documentation house style

This skill holds one copy of the writing rules that every documentation artifact obeys — Python and shell, lessons and reference pages alike — so a change to them lands everywhere without being applied seven times.

**The rules live in `references/house-style.md`. Read that file.** Its path on this machine is:

```text
~/.claude/skills/doc-house-style/references/house-style.md
```

If that path does not resolve, find the `doc-house-style` skill wherever skills are installed and read `references/house-style.md` inside it. Do not proceed from recall, and do not assume the file is absent because one path missed.

Every skill that produces documentation points here. Do not restate its contents in any of them. A second copy is a copy that goes stale, and a copy that says *less* than the original is worse than a plain duplicate, because it silently permits what the original forbids.

## What belongs here, and what does not

Here: anything about **how the prose reads** — clarity order, term definitions, heading and page-title style, where material goes on a page, callouts, code fences and their lead-ins, the lookup table's columns and rules, shared fixtures, how much to interview before reshaping a page, how to edit a page that already exists, and the verification standard. These apply identically to a lesson and to a reference page, and to Python and to shell.

Not here: **structure, which differs by artifact.** A Python lesson's required section order lives in `python-sdk-lesson` and a Bash lesson's in a shell-lesson skill, because those two orders are genuinely different. A reference page's section order, hub linking, and `See also` rules belong in a page-spec file covering both sets, because their shape is the same and two copies of it drifting apart is its own kind of defect.

Also not here: rules for a personal or persuasive site, which persuades a browsing reader instead of teaching a working one. Those rules live in a separate site-style skill, which is the only kind of file permitted to override this one, and which names each rule it inverts.

## Scripts

`scripts/` holds the validators referenced by the lesson skills that build on this one. `check_lesson.py` checks a generated lesson under `--profile python|shell`, and `housestyle.py`/`mdparts.py` hold the shared checks it depends on.
