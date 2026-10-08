# Working in this repo

This repo holds the lesson files for Josh's Python curriculum, and it publishes a copy of
the two skills that generate them so that people who clone it can generate their own.

## Never read the contract in `skills/`

**`skills/python-sdk-lesson` and `skills/doc-house-style` are a frozen published snapshot,
not the contract in force.** They were packaged in September 2026 and are deliberately not
updated. The live contract is the installed skill:

```text
~/.claude/skills/python-sdk-lesson/
~/.claude/skills/doc-house-style/
```

Read those, and nothing under `skills/` here, whenever you generate or regenerate a lesson,
check one against the rules, or answer a question about how lessons are written. The two
differ substantially: the published copy predates the rule IDs, the GitHub API rules, the
worked-example size limit, and the current lead-in and heading rules.

Invoking the skill by name is safe — the installed copy takes precedence, confirmed on
2026-10-07 — so the risk is reading a file here directly. A search of this directory will
turn up `skills/doc-house-style/references/house-style.md`, and that file is the wrong
authority. This happened once already, on 2026-10-07, when the published copy was found by
a grep of the project and briefly taken for the real contract.

## Changing the published copy

Josh publishes lessons here, not contract updates, so leave `skills/` alone unless he asks
for it specifically. If he does ask, the change is a repackaging job: the live skill now
reads files that aren't in the bundle, hardcodes `/home/josh` paths in several places, and
names a private repository in its examples, so none of it can simply be copied across.
