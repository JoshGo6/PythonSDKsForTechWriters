# House Style

The writing contract for every documentation artifact — Python and shell, lessons and reference pages. This is the only copy. Every skill that produces documentation points here, and none of them restates a rule below.

One file is allowed to disagree with this one. A separate site-style file governs your personal site, where the reader is browsing rather than working, and it inverts several rules below. It names every rule it inverts, and it adds nothing that would hold on a documentation page — a rule general enough for both belongs here.

Two goals govern everything: the material must be **easy to find** and **easy to understand** on arrival. Clarity outranks brevity. The fix for a section that feels long is reordering it — answer, then mechanism, then caveat — not cutting it.

Every rule below is pass/fail rather than a preference. A page that breaks one is a page to fix, not a judgment call to weigh against everything else the page does well.

## Clarity

**Answer first, then mechanism, then caveat.** Apply this at every level — the page, the section, the paragraph. State the rule the reader needs to act on before explaining why it holds. A reader who stops after the first sentence should still be correct; a reader who continues should learn why. Never make the reader traverse three paragraphs of background to reach the actionable rule.

One artifact inverts this deliberately. A lesson teaching behavior the learner has repeatedly mispredicted leads with a command and its real output, then gives the rule that explains it, and names the rule last, because an explanation that arrives before the behavior has nothing to attach to. A shell-lesson skill owns that inversion, states the reason, and is the only place it applies.

**Define every term at first use.** If the material uses a word like *iterable*, *idempotent*, *truthy*, or *in place*, define it where it first appears, in one sentence.

Assumed vocabulary, never defined: *raises*, *returns*, *argument*, *string*, *list*, *dict*. What a raising call does need is the **name of the exception**, backticked: ``raises `ValueError` `` is useful, `raises an error` is not. The backticks are required — the validators check for them. Inside a code comment where backticks read badly, drop the word and name the exception alone (`# StopIteration — nothing left`).

**Name the mechanism with its own term.** Where a rule, a form, an option, or an error already has a name, use the name rather than a description of it. `becomes an imperative` beats `becomes a heading that is the claim`: the first names a grammatical form the reader can go and look for, and the second is a formulation they have to decode first. A clever paraphrase reads well the first time and teaches nothing the second.

**An opening is complete sentences.** The first thing on a page says what the page covers and what it excludes, with links to where the excluded material lives. A noun-phrase fragment is not an opening: *Building and taking apart filesystem paths with `pathlib.Path`* is a label, and it leaves the reader to assemble the claim themselves. Say what the thing is or what it does — *A `Path` object is how you build and take apart a filesystem path.* Anything that will not fit gets a section of its own rather than a second paragraph, and that includes a trap governing the whole page, which goes where the reader meets it. How many sentences an opening gets is the artifact's own rule and is in its spec.

**One idea per sentence.** Two short sentences beat one sentence with a subordinate clause. If a sentence carries more than one new term, split it.

**Conjunctions carry the logical relation.** A clause that reverses what the clause before it set up takes *but*, never *and*. "Writing one costs more than doing the work once, and it earns its keep by the third page" throws away the concession the sentence is built on; *but* puts it back. The same goes for *so* where the second clause is a consequence rather than a companion.

**Every sentence carries a subject and a verb.** Short sentences are the goal, but a verbless fragment is not a short sentence — it reads as a tic, and it strands the reader when the missing subject is the thing being described. `Same validator, no findings.` becomes `This time the validator reported no findings.`

**No orphan paragraphs.** A paragraph of roughly 18 words or fewer, sitting between two
full paragraphs, reads as filler. Three ways out, in order: add material that earns the
space, restructure so the text is not needed at all, or fold it into the paragraph above.
Folding lengthens the document, so pay for it by cutting a whole section or merging two,
never by leaving the orphan in place.

A short paragraph that introduces a fenced block or a table is a different object and is
exempt, because the lead-in rule below requires it. A lead-in may be one line or a full
paragraph depending on what the block needs. Only a short paragraph followed by more prose
is an orphan.

**Prefer verbs to nominalizations.** "The shell splits the word into three" reads. "Word splitting occurs during expansion" does not.

**Second person, active voice, present tense.** "You run the script and the shell forks a subshell."

**Contract by default** — `doesn't`, `isn't`, `you're`, `it's`. Spell the pair out only where the negative or the verb carries the stress, because there the expanded form is what puts it there: "passing the first validator is *not* proof."

**Name the referent whenever resolving it costs the reader anything.** Never write "this" or "it" pointing at a whole preceding paragraph. Restate the noun when the referent sits in an earlier sentence, when another noun of the same class could fill the slot, when a bare demonstrative or ordinal carries the subject position, or when a fence, table, or heading intervenes and resets attention. Where the noun was named in the same sentence and nothing competes with it, the short form is better: "saved in three states, with both validators run over all three" does not want *states* a second time.

The competing-noun case is the one most often missed, because the pronoun looks safe until you count the candidates in front of it. In `My skills share a contract, which is one file of writing rules that every page they produce has to satisfy`, *they* has two plural nouns to choose from — the skills and the rules — so the noun comes back: `every page the skills produce`.

Terminology drift is the same defect arriving from the other side. Once a page calls something a *state*, it is never also a *copy* or a *file*, and the reader should never have to work out whether two words name one thing.

**Give the reader a default to copy, not a survey of the options.** The reader wants to use the thing rather than to understand it completely, so a section that ends in a pattern they can paste has done its job and a section that ends in considerations has not. Where behavior varies by environment, version, or locale, name the form that forces the predictable one instead of listing what might happen — passing `encoding="utf-8"` explicitly rather than explaining what the platform default might be. A mechanism explanation that does not change what the reader types is the cheapest thing to add and the least useful.

**Follow every abstract statement with a concrete instance** — real syntax, a real call, or real output. A paragraph of pure abstraction is a defect. A metaphor may open an explanation, but the literal mechanism follows in the same paragraph.

**Name the failure, not the judgment.** An evaluative word asks the reader to take an assessment on faith, where the mechanism behind it is something they can recognize on their own. `a non-standardized editorial process that the agent is likely to do differently each time` beats `a good session with an agent`, and `far cheaper to ask than to guess wrong, requiring lots of tokens for rework` beats stopping at `cheaper`. Where a comparison is carrying the sentence, say what is being compared.

**Headings are short, imperative, and carry a claim.** `Convert values before doing arithmetic` beats `Values are strings — convert before doing arithmetic`, and both beat the bare label `Conversion`. A reader scanning headings should absorb the warnings without reading the body, and should be able to read the heading as an instruction to themselves.

Five rules follow, in order of how hard they are:

- **No dash-separated headings.** An em dash in a heading is the sign of a label with a claim bolted on; make the claim the heading and delete the label. The validator fails these.
- **Imperative unless that is awkward.** Where an imperative genuinely does not fit, a noun or noun phrase is fine — `Patterns`, `Token expiry`. What is never fine is a gerund (`Setting variables`, `Loading a .env file`) or an article or wh-word opener (`The file syntax`, `Where it looks`); those are labels wearing a sentence's clothes, and the validator fails them too.
- **No placeholder headings.** `Overview`, `Putting it together`, `Common Pitfalls`, `Conversion` — these name the slot rather than the content, and a reader scanning them learns nothing. `Common Pitfalls` fails twice over, because failures belong in the sections that teach the calls they apply to rather than in a catch-all at the end.
- **A bare API name is a heading with the claim missing.** `## shutil.move()` is an index entry. So is `## shutil.move() — moves across filesystems`, which just bolts the claim back on with a dash. Write `## Move a file across filesystems with shutil.move()`.
- **Keep it short enough to scan.** If the heading needs a subordinate clause, the section under it probably needs splitting.

**Name a page for the task, not for the command or the call.** A page's title is a heading and the same rules bind it, so name it for the task the reader has, in the words they would search for. `Search file contents by pattern` beats `grep`, because a page named for a command becomes a dump of that command's flags, while a page named for a task can also say where a different command beats it. Where a command genuinely is the task — `rsync`, `jq`, `tar` — naming the page after it is correct.

**Never stack two headings.** A heading is followed by text, never straight by another heading. Put one or two sentences under every heading that has subheadings beneath it, saying what the section covers and how its parts divide up.

A subheading arriving directly under a heading gives the reader a label under a label. The upper heading promised a section and then said nothing, so the reader meets the first subheading without knowing what the whole section is for or what else is in it — and a reader who scrolled to that subheading from elsewhere gets no context at all. The fix is always to write the missing lead-in, never to delete the upper heading. The validators fail a stacked pair.

A section that opens with a fenced block is a different defect with the same repair, and the fence rule below reports it: the block needs a lead-in above it, which is prose, which un-stacks the headings.

The one exception is the file's own `# ` title, because the section heading under it is the first line on the page that can carry text.

**Break a long section with subheadings.** One `## ` running over several screens is hard to read no matter how good the prose is. Add `### ` headings under the same rules.

**Numbers one through nine are words; 10 and up are digits.** `nine skills`, `three states`, `19 findings`. Anything that is an identifier rather than a count keeps its digits at any size: `Python 3`, `HTTP 404`.

A vague magnitude is the one place a spelled number above nine belongs, and it takes the idiom: *tens of thousands*, or just *thousands*. `ten-thousands` is not something anyone says.

**Restrictive clauses take "that."** `a page that doesn't comply`, never `a page which doesn't comply`. A clause you could drop without changing which thing the sentence picks out is non-restrictive, and that one takes a comma and *which*.

**A series takes commas, and semicolons only when an item already carries one.** `headings are imperative, lead-ins sit above every fence, and openings are complete sentences` wants nothing but commas. `headings should be stated in the imperative, without a dash; a lead-in sentence sits above every code block; openings are written in complete sentences` wants semicolons, because the first item has an internal comma and commas alone would read as four items rather than three. Semicolons are a repair for that collision and nothing else — never reach for them to make a list look weightier.

**A fronted clause takes a comma.** "Before it edits anything, it interviews me." The comma is what tells the reader the introductory clause has ended, and without it "anything it" parses as a unit and the reader has to back up.

## Placement

Where a thing goes decides whether the reader finds it. The rules below run from the smallest unit to the largest: which sentence a caveat follows, which section a failure belongs to, what order the sections come in, and what it costs to move any of it later.

**Caveats follow the usage they qualify.** Do not front-load a section with conditions and exceptions before the reader knows what is being qualified.

**Put each failure where the reader meets it.** Name what goes wrong at the point that teaches the call it applies to, usually as a callout. Do not reserve a slot for warnings at the top. Failures belong in their individual sections.

The same holds for anything that behaves differently on another platform or an older version. State the divergence in the section that teaches the call, give the form that works there, and say nothing at all where the material does not diverge. A portability section at the end is the catch-all shape this rule exists to prevent, and a portability note on every page is noise that trains the reader to skip them.

**Order by decision, not by the API's own order.** Lead with the default and the two cases a reader reaches for most, and put the special cases last, labeled as such. A roster that follows the module's order or the man page's is a list nobody reads to the end, and it buries the one call the reader needed behind six they did not. Keep material that shares an import, a module, or a mental model contiguous, and never wedge an unrelated section between two that build on each other.

**Content belongs where the reader already is.** An in-page cross-reference is usually evidence that the material is misfiled: where one section has to send the reader elsewhere on the same page to be understood, the two sections want to be one, and merging beats linking. Where an internal link is genuinely needed, `[[#Heading]]` is the form, and it is fragile — backticks, em dashes, and percent-encoded spaces in a fragment break silently.

**Link only to what exists.** A link to a page nobody has written creates an orphan target rather than an error, so nothing reports it and the reader finds it. Confirm the target resolves before writing the link, and never invent one to round out a `See also`.

**Renaming a heading or a page breaks every link pointing at it, with no error anywhere.** Check what links in before renaming, and say in the report that you checked. This is the one cost that can make leaving a defective heading the right call, and it is a decision to surface rather than to take silently.

## Source formatting

**Never insert a hard line break inside a paragraph. Write one line per paragraph and let
the editor soft-wrap it on screen.** Markdown and HTML both collapse a newline inside a
paragraph into plain whitespace when rendered, so a paragraph broken into short lines and
the same paragraph on one line display identically — hard-wrapping buys nothing on the page
and costs everything at the keyboard. Match an editor that soft-wraps: the file holds one long
logical line per paragraph, and editing anywhere in it changes only that line.
A hard-wrapped paragraph forces every line after an edit to reflow, which turns a one-word
change into a multi-line diff.

**Never reflow a paragraph you did not otherwise change**, in either direction. Joining an
untouched hard-wrapped paragraph into one line is the same defect as breaking an untouched
one-line paragraph into several — both rewrite lines nobody asked you to touch.

**This governs prose paragraphs, not code.** A code block keeps whatever line length the
language and the example demand. A table row, a list item, and a heading are each already
one line by construction and this rule adds nothing to them.

**Never break a URL or a single attribute value to make a line fit.** A long `href` or
`content` attribute stays on its line regardless.

## Examples and fixtures

**Examples must be able to fail.** An example whose output would look the same if the feature did not exist teaches nothing. Sample data must be rich enough that the behavior is self-evident: a search example needs more than one match, a defensive-access example needs a record with the field missing, a renumbering example needs more than one item.

Two shapes follow from that, and which one applies depends on what the example teaches:

- **Plurality, where the lesson is shape.** If the point is "one tuple per match" or "one row per record," the sample must produce at least two. A single-element result cannot distinguish a list from a scalar.
- **Contrast, where the lesson is a distinction.** Put the succeeding call beside the failing one — anchored beside unanchored, `PUT` beside `PATCH` — adjacent, against the same fixture, with real output for both. A behavior stated in a comment and never run is an assertion, not a demonstration.

**Every section that teaches something shows it running.** A claim with no example is a claim the reader has to go verify somewhere else, and a section that cannot be demonstrated usually does not belong on the page at all. A flag is held to this as strictly as a call is: a flag documented without a contrasting run is a flag nobody can check.

**Choose sample data to serve the demonstration, not to keep the page tidy.** Two named samples doing different jobs beat one reused sample that does both badly. `Reading and Writing Files` needs three files precisely because one file cannot show line-by-line shape, newline translation, and an encoding failure at once.

**Fixtures must contain the awkward case** — a hyphenated filename, a record with a missing field, a file that should not change. A fixture where everything works cannot distinguish a correct page from a wrong one.

**Use one shared fixture per artifact where possible.** Declare the sample data once, explain why each part of it is there, and have the examples operate on it. Changing fixtures between examples forces the reader to re-orient at every step.

**Make the fixture reachable without scrolling.** One declaration point does not help a reader who arrives in the middle of the page from the lookup table or a link, and who then cannot read the example in front of them. There are exactly three permitted forms, and the choice between them is decided by how much of the fixture the example actually touches:

- **Declare it once, unfolded, in `The samples`.** This is the canonical copy and the only unfolded full copy on the page.
- **Excerpt inline** where the example depends on part of the fixture — the two `.env` lines the example reads, the one record with the missing field. Put the excerpt immediately above the example. Prefer this: it is the cheapest for the reader and the most common case.
- **Recap in a folded callout** where the section genuinely needs the whole fixture. `> [!note]- The sample .env, again` collapses by default and expands in place, so it costs a skipping reader nothing and a returning reader one click.

Never paste the whole fixture unfolded a second time. Repetition at that scale is what makes a page painful to re-read, and the validator fails a fenced block repeated verbatim outside a callout. An excerpt must be copied verbatim from the canonical declaration; a fixture that drifts between its copies is worse than one the reader has to scroll to.

**A destructive example runs against the fixture, not against the reader's own files.** A page teaching `rm`, `mv`, `find -delete`, `sed -i` or `shutil.rmtree` is exactly the page a reader copies from fastest, so the fixture is built inside a sandbox — `mktemp -d`, or a temporary directory — and the examples run there.

**Show the destructive command itself.** Withholding it, or paraphrasing it into a description, leaves the reader to reconstruct the thing they came to the page for, and they will reconstruct it worse. `rm -rf "$dir"` is the answer, so write it. A callout is owed only where the damage is not evident from the command — `sed -i` rewriting the file rather than printing, `mv` over an existing name, a glob that matches more than the reader expects. Where it is evident, name the consequence in the sentence and move on: heavier framing than that trains the reader to skip every callout on the page.

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
- Cells hold data or runnable code. Never a pointer to elsewhere in the artifact, never a clause of commentary — that text belongs in prose.

**The table is an index; the prose is the authority.** They serve different readers, and the overlap between them is intended rather than redundant: the table is the entry point for someone who already understands the material and needs to pick, and the body is where someone meeting it first actually learns it. Three consequences:

- **Never write "as shown in the table above" in place of an explanation.** The moment the prose defers to the table, the artifact has no explanation in it.
- **Never thin the table because the prose now covers the same ground.** That is the overlap working as intended.
- **Every item named in the table gets prose in the body.** That is a checkable promise, so check it before delivering — a table row with no section is the most common way an artifact silently under-delivers.

## Code blocks and callouts

**There is no limit on code blocks.** Demonstration code in the body is necessary, and it is especially necessary for showing how sibling functions differ. Put two related calls side by side in one block with the difference commented rather than describing it in prose.

**Every fenced block gets a lead-in sentence.** The sentence sits immediately above the fence, says what the block does or what to notice in it, and ends in a period, a colon, or a question mark. This applies to output blocks and tracebacks exactly as it applies to code: the reader should never have to work out for themselves what they are looking at. Two things follow from it. Two fences cannot sit in sequence with nothing between them — code and its output are two blocks and need two lead-ins. And a fence cannot sit directly under a heading, because a heading labels and cannot orient. A contentless lead-in does not satisfy the rule either; "For example:" and "Run this:" spend a line and tell the reader nothing they did not already have from the heading.

**A colon-ending lead-in is still a complete sentence.** The colon introduces the block; it does not let the clause before it stay unfinished. `The two skills are:` and `clone it and either:` are fragments that lean on the block to finish the grammar — write `This bundle installs two skills:` or `clone it, then do one of the following:` instead, where the sentence stands on its own and the colon simply points at what comes next.

**Fence labels.** Every fence carries an info string; a bare fence is a failure. Code takes its language: `python`, `bash`, plus `toml`, `yaml`, `json`, `markdown` where they apply. Everything that is not code takes `text` — program output, tracebacks, and the contents of a file. There is no `output` label; `text` covers all three, and it is what the pages already use for tracebacks.

**Shell material has one more form.** A terminal transcript — comment, command, and the output it produced, together in one block — takes `shellsession`, and inside it the comment line starts with `#`, each command line starts with `$`, and output lines carry no prefix, with a blank line between triplets. Use `bash` for a script file or a snippet that produces no output, and `text` for output shown on its own. Choose by what the block *is*: a transcript is `shellsession` even when it holds a single command, and a script is `bash` even when the page discusses what it prints.

The lead-in rule governs `shellsession` exactly as it governs everything else, and this is where it is most often missed. **The `#` comment inside the block does not satisfy it**, because the lead-in sits above the fence and that comment is inside it. One sentence above the whole block is enough, however many triplets the block holds — a 10-triplet quick-reference block needs one lead-in, not 10.

**Callouts are for genuine danger, or for material that would break the flow of the surrounding text.** The vast majority of explanation belongs integrated into the body. There is no fixed limit on how many an artifact may have, and no per-page budget: there is a standard each one must meet, and counting them is not the test.

The failure the standard exists to stop is **callout as storage** — normal behavior, recommended practice, and definitions parked in `> [!warning]` blocks because they felt important. If it is how the thing works, it is not a warning, and a page that files its explanations into callouts is harder to read rather than better organized. A callout that restates the paragraph above it is that paragraph's content, not a callout.

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

**A title is a real title** — a short noun phrase that names the point, the way a heading does. The opening words of the body sentence pushed up onto the header line are not a title, and they leave the body starting mid-thought.

Three mechanics are easy to get wrong. There is no space after the `!`: `> [! warning]` does not render in Obsidian at all. A bare `>` on its own line is what separates two paragraphs inside a callout — a blank unprefixed line ends the callout instead. And a fenced block inside a callout carries the prefix on every one of its lines, the fence delimiters included.

## Interviewing before you reshape

**Ask in proportion to the cost of rework.** A question costs you one tap; a wrong guess costs a full round on a page you then have to re-read. That ratio, not a fixed question count, decides how much to ask.

- **Reshaping a page or a set: interview, and prefer more questions to fewer.** Three or four per round is normal, and later rounds may ask follow-ups that branch on earlier answers. Fewer is right when the page is small; more is right when it is not. Ask every question whose two answers produce different pages: the fixture's shape and how many samples it needs, the table's columns, section order, how far to trim a weak section, whether a marginal example survives, and any rename that could break inbound links.
- **Adding to a page: do not interview.** A new section is cheap to redo, and the value of that work is a fast turnaround. Ask one question only when the brief has two plausible readings that produce different pages.
- **Never ask before you have read the material.** A question about breadth or structure asked before either party has seen what is there forces an answer given blind. Inventory first, then ask.
- **Do not ask what the material already answers**, do not ask permission for the obvious, and do not ask about anything the house style or the page spec already settles.

## Editing what already exists

A page that exists is edited, never regenerated. Rewriting from scratch reconstructs the page from a reading of it, and reconstruction drops things — a table row, the backticks around a call name, the sentence that named an exception — while silently normalizing punctuation, whitespace, and comment alignment. Every repair worth making is local: insert the lead-in, replace the one paragraph, relabel the fence.

**Edit region by region, and never retype the page.** Use `Edit` on one region at a time rather than rewriting the file with `Write`. Every line you wrote and the assistant did not deliberately change survives byte-for-byte, your table padding and your em dashes included. Prefer changing the words that are wrong to replacing the paragraph that contains them: you review diffs, and a rewritten block costs you the time to re-read a paragraph you had already approved.

**Keep a pristine original.** You are editing in place, so snapshot the file before you touch it — copy it to the scratch directory, or recover it with `git show HEAD:<path>` when it is committed and clean. Letting the only copy of the original be the file you are editing makes every later comparison run against itself and pass for the wrong reason.

**Diff before delivering.** Read the diff and confirm that every `-` line is one you decided on. A `-` line you did not intend is drift: restore the original wording and diff again. The step is not optional, because it is the only thing that catches drift you did not know you had introduced.

For a page in your vault, that is one command:

```bash
git -C /path/to/your/vault diff -- "<path to the page>"
```

**How much may change is the job's decision and not this file's.** Adding to a page keeps that page's existing register even where it conflicts with the rules above, and says so in the report. Reshaping a page applies the current rules to everything it passes over, including text it is only crossing, since material carried forward from an older draft is exactly what survives a revamp unexamined. Which job you are on decides this; what does not vary between them is the mechanics above.

**Leave the work uncommitted** unless you ask otherwise. You review with `git diff` and commit yourself. When you do ask for a commit, the message takes a summary line and then the findings grouped under short headings — `Wording`, `Punctuation and sentences`.

## Verification

Nothing ships unverified. Do all of this **before** presenting any part of the artifact.

**Execute every example.** Run each syntax block, worked example, and table row, and paste the real output. Never write an output you have not seen. Two parts of this are routinely skipped: the table's **Result** column is output and gets run like any other, and when you are revising an artifact, the examples you are **keeping unchanged** get run too. Restructuring changes sample data more often than expected, and a stale offset in a comment is indistinguishable from a lie.

**Do the work you are asking the reader to do.** Where an artifact asks the reader to produce something — an exercise, a script, a pattern to adapt — write a complete working solution and run it before shipping the ask. That is what proves the task is possible with only the material the reader has by then, and it is the only honest source for the output you show them. The solution itself does not ship.

**Isolate each behavior.** Settings applied earlier in a script silently change later results — testing pipe-subshell behavior after enabling `shopt -s lastpipe` in the same script produces the opposite of the correct answer. When in doubt, one behavior per script.

**Say what could not be run; never invent what it would have printed.** Some examples legitimately cannot execute here: remote hosts, hardware, network calls, destructive operations, commands needing privileges. Mark those as illustrative and say so plainly at delivery. Plausible-looking output is fabricated output, and presenting it as real is the one failure that costs the reader their trust in everything else on the page. Where the output is what carries the lesson, get it another way rather than dropping the example: run the command against a local stand-in, or quote output you supplied from your own machine and say that is where it came from.

**Trigger the failures too.** Exception names and messages are copied from real tracebacks, not recalled.

**Read the source before saying what a thing does.** A signature, an exception type, a default, and a pagination behavior are all looked up in the project's own code or documentation, never paraphrased from memory. An illustrative example is legitimate as long as what it illustrates is really true, but anything presented as the output of a run has to be the output of a run.

**When the source and the run disagree, show the failing form.** Correcting a note, a page, or an earlier draft in silence leaves the reader wondering whether they misremembered. Put the corrected version in the body, keep the source's version beside it as the trap it is, and paste the real output of both. A bare correction teaches nothing; the failing form and what it actually prints is what stops the reader repeating it.

**Source every polarity claim.** A polarity claim is any statement about what a default is, or about whether omitting something enables or disables it: "the default is X," "omitting this implies Y," "passing this limits the set." These are the errors that read fluently and are exactly backwards, and inference from how an API *seems* like it should behave is how they happen. Confirm each one by running it or by reading the project's own documentation — never from recall. Where confusion is likely, state the claim against its inverse ("this is not a filter, it is the switch"), which forces the commitment into the open where a reader can catch it.

**A set's `repr` order is not stable between runs.** Never paste a set literal as fixed output; wrap it in `sorted()`.

**Verify silently.** Do not print a verification report — you will not read it, and the work is the point, not the account of it. The one thing that does get said out loud is a genuine gap: if something could not be run at all, say so plainly at delivery and name which claims are therefore unverified. Do not present unverified output as though it were tested, and do not hedge material you did verify.

Silent does not mean unwritten. Where the check is a list — a dependency audit, an inventory, a walk of every rule against every section — write it out in full to a scratch file, because writing it is what makes you actually perform it. Put it in the session scratchpad directory when your environment names one and in `/tmp` otherwise, never in the vault and never in the artifact.
