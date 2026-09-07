#!/usr/bin/env python3
"""House-style rules both checkers enforce, stated once.

check_pages.py and check_lesson.py check different artifacts against the same
writing contract, so the rules that belong to the contract rather than to the
artifact live here. A rule stated in two scripts is the same defect as a rule
stated in two skills: one copy goes stale and nothing reports it.

Nothing here knows about pages or lessons. Each function takes the lines and
returns a list of findings, and the caller decides which ones apply.
"""
import re

from mdparts import fence_line_set, fences

# Words that can legitimately follow "raises" without being an exception name.
NOT_AN_EXCEPTION = {
    "an", "a", "the", "rather", "on", "when", "instead", "it", "in", "does",
    "so", "and", "with", "no", "for", "nothing", "this", "that", "them",
    "here", "only", "if", "is", "are", "one", "two", "both", "either",
}

# Statement keywords at the START of a line, used to catch code that has been
# put in a `text` fence. Real output legitimately contains "for", "with", and
# "n = 42" ("invalid literal for int() with base 10"), so the test is anchored.
PY_CODEY = re.compile(
    r"^\s*(import |from \w+ import |def |class |for \w+ in |if .*:$|with .+ as |"
    r"print\(|return\b)", re.M)

SH_CODEY = re.compile(
    r"^\s*(#!/|\$ |if \[|for \w+ in |while |case \w+ in|function \w+|"
    r"\w+\(\) *\{|declare |local |export |echo |printf |read -|set -[eux])", re.M)

# Info strings that name a thing the house style does not have. `text` covers
# output, tracebacks and file contents; a transcript is `shellsession`.
BAD_INFO = {
    "output": "there is no `output` label -- use `text`",
    "console": "use `shellsession` for a transcript, `text` for output",
    "terminal": "use `shellsession` for a transcript, `text` for output",
    "shell": "use `bash` for a script, `shellsession` for a transcript",
    "sh": "the course authors Bash -- use `bash`",
    "zsh": "the course authors Bash -- use `bash`",
    "bash-session": "use `shellsession`",
    "commandline": "use `shellsession`",
}

# A command that deletes, overwrites in place, or moves something away. The
# house style requires these to run inside a sandbox, because a page teaching
# them is the page a reader copies from fastest.
DESTRUCTIVE = re.compile(
    r"(?:^|[\s;&|(])(?:rm\s+-|rm\s+\S|shred\s|truncate\s+-|"
    r"find\b[^\n]*\s-delete\b|sed\s+(?:-\w*\s+)*-i\b|"
    r"shutil\.rmtree|os\.remove|os\.unlink|(?:Path\([^)]*\)|\w+)\.unlink\()")

# Any of these anywhere in the file is taken as the sandbox. The test is
# per-file rather than per-block because the fixture is declared once, near the
# top, and the destructive example that runs against it is further down.
SANDBOX = re.compile(r"mktemp|tempfile|TemporaryDirectory|\$TMPDIR|/tmp/")

# Deleting a rebuildable artifact is not the failure the rule names: the page
# that teaches `venv` has to show how to throw one away. A virtual environment
# counts as rebuildable when the same page creates it, which is why the names
# are read off the page rather than guessed at.
VENV_MADE = re.compile(r"(?:-m\s+venv|virtualenv)\s+([\w./-]+)")
REBUILDABLE = {"__pycache__", "node_modules", ".tox", ".mypy_cache",
               ".pytest_cache", "dist", "build"}

BASH4 = [
    (re.compile(r"declare +-A\b"), "declare -A (associative arrays)"),
    (re.compile(r"\bmapfile\b"), "mapfile"),
    (re.compile(r"\breadarray\b"), "readarray"),
    (re.compile(r"\$\{\w+,,"), "${var,,}"),
    (re.compile(r"\$\{\w+\^\^"), "${var^^}"),
    (re.compile(r"\bglobstar\b"), "globstar"),
    (re.compile(r"\bcoproc\b"), "coproc"),
    (re.compile(r"declare +-n\b"), "declare -n (namerefs)"),
]


def _codey_hit(body, codey):
    """First body line the codey heuristic flags, skipping a traceback echo.

    A traceback frame ('File "...", line N, in <module>') is followed by the
    offending source line copied verbatim -- 'import x' or 'print(...)' right
    after that frame line is real traceback content, not a code block mislabeled
    as `text`.
    """
    for i, l in enumerate(body):
        if codey.match(l):
            prev = body[i - 1] if i > 0 else ""
            if re.match(r'^\s*File "', prev):
                continue
            return l
    return None


def check_fences(lines, codey=None, bad_info=True):
    """Every fence carries a usable info string and has a lead-in above it.

    The lead-in is the nearest non-blank line above the opener, outside any
    fence. Inside a callout the search skips past the callout's own lines: its
    header is a label, and the prose that orients the reader sits above it.
    """
    p = []
    blocks = fences(lines)
    closers = {f.close_line for f in blocks if f.close_line is not None}

    for f in blocks:
        n = f.open_line + 1                        # 1-based, for the reader
        if f.close_line is None:
            p.append(f"line {n}: fence is never closed")
        if f.info == "":
            first = next((b for b in f.body if b.strip()), "")
            p.append(
                f"line {n}: bare fence -- label it (`text` for output): {first[:50]!r}"
            )
        elif bad_info and f.info.lower() in BAD_INFO:
            p.append(f"line {n}: fence labeled `{f.info}` -- {BAD_INFO[f.info.lower()]}")
        elif f.info == "text" and codey is not None:
            hit = _codey_hit(f.body, codey)
            if hit is not None:
                p.append(f"line {n}: code inside a `text` fence: {hit.strip()[:50]!r}")

        j = f.open_line - 1
        if ">" in f.prefix:
            while j >= 0 and (lines[j].lstrip().startswith(">") or not lines[j].strip()):
                j -= 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        if j < 0:
            p.append(f"line {n}: fence with nothing above it")
            continue
        above = lines[j].strip()
        if j in closers:
            p.append(f"line {n}: two fenced blocks with no text between them")
        elif above.startswith("#"):
            p.append(f"line {n}: fence under a heading, no lead-in: {above[:50]!r}")
        elif above.startswith("|"):
            p.append(f"line {n}: fence under a table row, no lead-in")
        elif not above.endswith((".", ":", "?")):
            p.append(f"line {n}: lead-in does not end in '.' or ':': {above[-60:]!r}")
    return p


def check_triplets(lines):
    """Every `shellsession` triplet surfaces something the reader can verify.

    A comment and a command with nothing under them prove nothing ran. Where a
    command is silent by design, the contract says to append an inspection
    command rather than to write 'no output' and move on.
    """
    p = []
    for f in fences(lines):
        if f.info != "shellsession":
            continue
        chunk, start = [], f.open_line + 1
        chunks = []
        for i, l in enumerate(f.body):
            if l.strip():
                if not chunk:
                    start = f.open_line + 2 + i
                chunk.append(l)
            elif chunk:
                chunks.append((start, chunk))
                chunk = []
        if chunk:
            chunks.append((start, chunk))

        for line_no, body in chunks:
            cmds = [i for i, l in enumerate(body) if l.lstrip().startswith("$")]
            if not cmds:
                continue
            # Everything after the last command line is that command's output.
            # A '#' there is a line of output, not a comment, which is why the
            # test is position and not prefix: `cat` on a script prints one.
            if any(l.strip() for l in body[cmds[-1] + 1:]):
                continue
            p.append(
                f"line {line_no + cmds[-1]}: triplet shows no output -- add an "
                f"inspection command: {body[cmds[-1]].strip()[:50]!r}"
            )
    return p


def check_bash4(t):
    """Bash 4+ features need a portability note; macOS ships Bash 3.2."""
    if re.search(r"\b3\.2\b|\bbash 4\b|\bbash 5\b", t, re.I):
        return []                          # the text already raises portability
    p = []
    for rx, name in BASH4:
        m = rx.search(t)
        if m:
            n = t[:m.start()].count("\n") + 1
            p.append(
                f"line {n}: {name} needs Bash 4+ -- add a callout, macOS ships 3.2"
            )
    return p


def check_sandbox(lines):
    """A destructive example runs against the fixture, not against real files.

    The command itself is never the problem and the contract says to show it.
    What this reports is a page that pastes one with no sandbox anywhere in it,
    so copying the example costs the reader something.

    Reported per file rather than per line: the finding is that the page never
    establishes a sandbox at all, and the repair is one fixture change, not one
    change per call. The lines are listed so the finding can be judged.

    Deleting something the page itself built and can rebuild is exempt, so the
    `venv` page can show how to throw an environment away without tripping this.
    """
    text = "\n".join(lines)
    if SANDBOX.search(text):
        return []
    rebuildable = REBUILDABLE | {m.group(1).strip("/") for m in VENV_MADE.finditer(text)}

    hits = []
    for f in fences(lines):
        for i, l in enumerate(f.body):
            if not DESTRUCTIVE.search(l):
                continue
            if any(re.search(rf"(?:^|[\s/'\"]){re.escape(name)}/?(?:$|[\s'\"])", l)
                   for name in rebuildable):
                continue
            hits.append((f.open_line + 2 + i, l.strip()))
    if not hits:
        return []
    first = ", ".join(f"line {n}" for n, _ in hits[:3])
    return [
        f"{len(hits)} destructive command(s) with no sandbox on the page "
        f"({first}): {hits[0][1][:50]!r} -- keep the command, build the "
        f"fixture under `mktemp -d` so it runs there"
    ]


def check_heading_stack(lines):
    """A heading is followed by text, never straight by another heading.

    Two stacked headings hand the reader a label under a label. Whatever the
    lower one is about, the upper one has promised it and said nothing, so the
    reader arrives at the subheading with no idea what the section covers or
    how its parts divide up.

    The fix is always the same: one or two sentences under the upper heading
    saying what the section does and how it is split. It is never to delete
    the upper heading.

    The file's own level-1 title is exempt, because the section heading under
    it is the first line on the page that can carry text.

    A fenced block counts as content here, so a section opening with a code
    block is not reported twice: check_fences already fails a fence with no
    lead-in above it, and that finding names the actual repair.
    """
    p = []
    inside = fence_line_set(lines)
    prev, body_since, count = None, True, 0
    for i, l in enumerate(lines):
        if i in inside:
            body_since = True
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", l)
        if m:
            count += 1
            if prev and not body_since and not (prev[1] == 1 and count == 2):
                p.append(
                    f"line {i + 1}: heading directly under a heading -- add a "
                    f"lead-in under {prev[2][:40]!r} before {m.group(2)[:40]!r}"
                )
            prev, body_since = (i, len(m.group(1)), m.group(2)), False
        elif l.strip():
            body_since = True
    return p


def check_callouts(lines):
    """'> [!type] Title' on the header line, every body line prefixed '> '."""
    p = []
    for i, l in enumerate(lines):
        m = re.match(r"^> \[!(\w+)\]\s*(.*)$", l)
        if m:
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if not nxt.startswith(">"):
                p.append(
                    f"callout [!{m.group(1)}] line {i + 2} does not start with '> ': "
                    f"{nxt.strip()[:40]!r}"
                )
    return p


def check_exceptions(t, lines):
    """A raising call names its exception, backticked. Python profiles only."""
    p = []
    for m in re.finditer(r"raises (?!`)(\w+)", t):
        if m.group(1) not in NOT_AN_EXCEPTION:
            n = t[:m.start()].count("\n") + 1
            p.append(
                f"line {n}: backtick the exception name "
                f"({m.group(1)}): {lines[n - 1].strip()[:70]!r}"
            )
    if re.search(r"raises an error\b", t, re.I):
        p.append("'raises an error' -- name the exception instead")
    if re.search(r"\braises\b[^.\n]{0,20}\bmeans\b", t, re.I) or re.search(
        r"\*+raises\*+\s+(is|means)", t, re.I
    ):
        p.append("defines 'raises' -- assumed vocabulary, delete the sentence")
    return p


# Ten and up are digits. Below ten stays a word, so those are not listed.
# "hundred" and "thousand" are left out on purpose: "a hundred times" is
# idiomatic prose rather than a count, and flagging it would be noise.
SPELLED_TENS = (
    "ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen"
    "|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
)
SPELLED_RE = re.compile(rf"\b({SPELLED_TENS})\b", re.I)

# A spelled number hyphenated onto a magnitude -- "ten-thousands". Not a count,
# so the digits rule does not apply, and not English either: the idiom is "tens
# of thousands". Reported separately so the finding names the actual fix.
HYPHEN_MAGNITUDE = re.compile(r"^-(hundred|thousand|million|billion)s?\b", re.I)


def check_numbers(lines):
    """Numbers ten and up are digits. Prose only, and only whole words.

    Ordinals are already safe: 'tenth' and 'twentieth' do not match on a word
    boundary, and neither does 'tens of thousands'. Fenced blocks are skipped,
    because a spelled number inside sample output or code is that block's
    business rather than the prose's.
    """
    p = []
    inside = fence_line_set(lines)
    for i, line in enumerate(lines):
        if i in inside:
            continue
        # Inline code and wiki links are not prose either.
        prose = re.sub(r"`[^`]*`", "", re.sub(r"\[\[[^\]]*\]\]", "", line))
        seen = set()
        for m in SPELLED_RE.finditer(prose):
            word = m.group(1).lower()
            if word in seen:
                continue
            seen.add(word)
            tail = HYPHEN_MAGNITUDE.match(prose[m.end():])
            if tail:
                p.append(
                    f"line {i + 1}: {word + tail.group(0)!r} is not English -- "
                    f"write 'tens of {tail.group(1)}s', or just '{tail.group(1)}s'"
                )
                continue
            # Quote around the match, not the start of the line: a finding is
            # fixed by searching the page for the quoted text.
            lo = max(0, m.start() - 30)
            quote = prose[lo:m.end() + 30].strip()
            p.append(
                f"line {i + 1}: spell out one through nine only -- write "
                f"{word!r} as digits: {quote!r}"
            )
    return p
