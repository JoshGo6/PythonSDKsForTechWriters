# House Style — Python curriculum

The writing contract for both lessons and reference pages. This is the only copy. `python-sdk-lesson` and `python-reference-set` both point here; neither restates any rule below.

Two goals govern everything: the material must be **easy to find** and **easy to understand** on arrival. Clarity outranks brevity. The fix for a section that feels long is reordering it — answer, then mechanism, then caveat — not cutting it.

## Clarity

**Answer first, then mechanism, then caveat.** Apply this at every level — the page, the section, the paragraph. State the rule the reader needs to act on before explaining why it holds. A reader who stops after the first sentence should still be correct; a reader who continues should learn why. Never make the reader traverse three paragraphs of background to reach the actionable rule.

**Define every term at first use.** If the material uses a word like *iterable*, *idempotent*, *truthy*, or *in place*, define it where it first appears, in one sentence.

Assumed vocabulary, never defined: *raises*, *returns*, *argument*, *string*, *list*, *dict*. What a raising call does need is the **name of the exception**, backticked: ``raises `ValueError` `` is useful, `raises an error` is not. The backticks are required — the validators check for them. Inside a code comment where backticks read badly, drop the word and name the exception alone (`# StopIteration — nothing left`).

**Headings carry claims, not labels.** `Renaming — rename() overwrites without asking` beats `Renaming`. A reader scanning headings should absorb the warnings without reading the body.

**Caveats follow the usage they qualify.** Do not front-load a section with conditions and exceptions before the reader knows what is being qualified.

**Put each failure where the reader meets it.** Name what goes wrong at the point that teaches the call it applies to, usually as a callout. Do not reserve a slot for warnings at the top. Failures belong in their individual sections.

## Examples and fixtures

**Examples must be able to fail.** An example whose output would look the same if the feature did not exist teaches nothing. Sample data must be rich enough that the behavior is self-evident: a search example needs more than one match, a defensive-access example needs a record with the field missing, a renumbering example needs more than one item.

**Fixtures must contain the awkward case** — a hyphenated filename, a record with a missing field, a file that should not change. A fixture where everything works cannot distinguish a correct page from a wrong one.

**Use one shared fixture per artifact where possible.** Declare the sample data once, explain why each part of it is there, and have the examples operate on it. Changing fixtures between examples forces the reader to re-orient at every step.

**Reused fixture conventions**, so examples stay recognizable across the whole curriculum:

- Docs filenames: `install.md`, `api.md`, `auth.md`, `rate-limit.md`, `index.md`, `notes.txt`
- Tree: `docs/` with a nested `docs/api/`, plus `archive/` or `.backup/` as a destination
- Records: a `repo` dict, and an `issues` list where the second issue is missing `user` and `labels`
- Log lines: `2026-08-14 WARN  docs/api/auth.md missing front matter`

The hyphen in `rate-limit.md` and the incomplete second issue are load-bearing. They are what make `\w` and `.get()` examples demonstrate rather than assert.

## The lookup table

Default columns: **Use when** | **Call** | **Result**.

- *Use when* is the reader's goal in their words, not the function's name.
- *Call* is the syntax, copyable.
- *Result* is what actually comes back, taken from a real run.

Add a fourth **On disk** column only when *most* rows change filesystem state — moving, renaming, deleting, writing in place. When only one or two rows change state, report it inside the Result cell instead. Never include the column when nothing changes state, and never omit disk effects when they exist: a returned `Path` does not reveal whether anything happened.

For before/after behavior — what a tool does to input — use a two-column **Input | Output** table instead. Both kinds may appear in one artifact.

Rules:

- Name every operation explicitly in the left column. No ellipsis continuation rows ("…and it fails when").
- Include the failure rows, not just the success rows: what raises, what returns `-1`, what silently does nothing. Name the exception, backticked.
- Everything new the artifact introduces appears in the table.
- Do not emit a separate code block that restates the table. Multi-line code that will not fit in a cell belongs in the body where it is taught, or — if it composes material from several sections and belongs to none of them — in a short **Patterns** section after the table. Most artifacts will not need one, and a Patterns section is never a snippet reference.

## Code blocks and callouts

**There is no limit on code blocks.** Demonstration code in the body is necessary, and it is especially necessary for showing how sibling functions differ. Put two related calls side by side in one block with the difference commented rather than describing it in prose.

**Two code blocks cannot be put directly in sequence.** Putting code blocks one directly after another one, with no intervening text, reduces clarity. The user doesn't understand why there are multiple code blocks, instead of just one, larger one. A code block always requires introductory text explaining what its purpose is. Instead of putting multiple code blocks directly in sequence, put text in between them introducing each code block (including output code blocks), in turn. 

**Fence labels.** Code fences carry a language, except in output blocks. Labels in use: `output`, `python`, `bash`, `text` (tracebacks and config files whose contents would otherwise read as code), plus `toml`, `yaml`, `json`, `markdown` where they apply.

**Callouts are for genuine danger, or for material that would break the flow of the surrounding text.** The vast majority of explanation belongs integrated into the body. There is no fixed limit on how many an artifact may have; there is a standard each one must meet.

**Callout format.** The type and title go together on the header line. Every body line goes on its own line, prefixed with `> `. Never run the body text onto the header line, and never leave a body line unprefixed.

Incorrect — body run onto the header line:

```markdown
> [!warning] Closing the file terminates the process and any buffered writes are lost.
```

Incorrect — body not prefixed:

```markdown
> [!warning] Buffered writes are lost
Closing the file terminates the process.
```

Correct:

```markdown
> [!warning] Buffered writes are lost
> Closing the file terminates the process.
> Anything still in the buffer is discarded.
```

A callout with no title is also correct where no title is needed:

```markdown
> [!note]
> Closing the file terminates the process.
```

## Verification

Nothing ships unverified. Do all of this **before** presenting any part of the artifact.

**Execute every example.** Run each syntax block, worked example, and table row, and paste the real output. Never write an output you have not seen.

**Trigger the failures too.** Exception names and messages are copied from real tracebacks, not recalled.

**Source every polarity claim.** A polarity claim is any statement about what a default is, or about whether omitting something enables or disables it: "the default is X," "omitting this implies Y," "passing this limits the set." These are the errors that read fluently and are exactly backwards, and inference from how an API *seems* like it should behave is how they happen. Confirm each one by running it or by reading the project's own documentation — never from recall. Where confusion is likely, state the claim against its inverse ("this is not a filter, it is the switch"), which forces the commitment into the open where a reader can catch it.

**When the system cannot be reached, the standard does not relax — the source changes.** Some material targets a live API this container cannot reach. Nothing there is written from recall either. Split the claim in two before deciding how to verify it:

- **Python behavior is always executable.** What `requests` does with a response, what `.json()` returns on an empty body, what a header lookup raises when the header is absent, what a cached value does once it goes stale — these are claims about Python, and they run locally against a fixture. Run them.
- **Remote behavior is sourced, never inferred.** Which fields a response carries, which status codes an endpoint returns, what a parameter is named, what an enum admits, which headers come back — take these from the API's own OpenAPI description, or from a real response body the user has pasted with its secrets removed. Both are documents you read, which is the authority the polarity rule already accepts.

Then build the fixture from what you sourced, so the local server returns the documented shape. That is what makes a page both unexecutable against the real API and fully verified: every Python claim on it has been run, and every remote claim traces to the spec.

**Never present as executed:** a response body you assembled yourself, a status code the spec does not document, a field name appearing in neither the spec nor a pasted response, a header the spec does not document, or error text from the remote service. Where a page needs one of these and no source exists, leave it out and say so at delivery.

**A set's `repr` order is not stable between runs.** Never paste a set literal as fixed output; wrap it in `sorted()`.

**Verify silently.** Do not print a verification report — Josh does not read it, and the work is the point, not the account of it. The one thing that does get said out loud is a genuine gap: if something could not be run at all, say so plainly at delivery and name which claims are therefore unverified. Do not present unverified output as though it were tested, and do not hedge material you did verify.

