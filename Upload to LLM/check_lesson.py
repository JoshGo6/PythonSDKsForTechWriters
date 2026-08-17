#!/usr/bin/env python3
"""Check a generated lesson against the lesson contract and the house style.

Catches the mechanical failures that are otherwise caught by reading:
malformed callouts, a missing or ragged lookup table, unbackticked exception
names, code in an unlabeled fence, relic sections, and time estimates.

It cannot check whether a heading carries a claim, whether an example can
fail, or whether the exercise has a forward dependency. Those stay human.

Usage:  python3 check_lesson.py <lesson.md> [more.md ...]
        python3 check_lesson.py <folder>
"""
import re
import sys
from collections import Counter
from pathlib import Path

NOT_AN_EXCEPTION = {
    "an", "a", "the", "rather", "on", "when", "instead", "it", "in", "does",
    "so", "and", "with", "no", "for", "nothing", "this", "that", "them",
    "here", "only", "if", "is", "are", "one", "two", "both", "either",
}

CODEY = re.compile(
    r"^\s*(import |from \w+ import |def |class |for \w+ in |if .*:$|with .+ as |"
    r"print\(|return\b|\w+ = |\w+\.\w+\()", re.M)

TIME_ESTIMATE = re.compile(
    r"\b(should take|takes about|roughly \d+ ?(min|hour)|\d+[-–]\d+ ?minutes|"
    r"\d+ ?minutes\b|quick exercise|shouldn't take long)", re.I)


def check(path):
    t = path.read_text(encoding="utf-8")
    lines = t.splitlines()
    heads = [l.lstrip("#").strip() for l in lines if re.match(r"^#{1,4} ", l)]
    joined = " ".join(heads).lower()
    p = []

    # required parts, matched loosely because heading wording varies
    if not re.search(r"terminolog|theory|concept", joined):
        p.append("no Terminology/Theory section found in the headings")
    if not re.search(r"syntax", joined):
        p.append("no Syntax section found in the headings")
    if not re.search(r"example", joined):
        p.append("no Worked Examples section found in the headings")
    if not re.search(r"lookup", joined):
        p.append("no Lookup Table section found in the headings")
    if not re.search(r"exercise", joined):
        p.append("no Exercise section found in the headings")

    # relic sections from the pre-2026 contract
    for relic, why in (
        ("quick reference", "replaced by the Lookup Table"),
        ("audit", "replaced by silent verification"),
        ("snippet reference", "removed by settled policy"),
        ("reference delta", "no longer emitted; hand over the lesson instead"),
        ("verification report", "verification is silent; do not print it"),
    ):
        if relic in joined:
            p.append(f"relic section {relic!r} -- {why}")

    # a lookup table must actually exist and be square
    rows = [l for l in lines if l.startswith("|") and "---" not in l]
    if not rows:
        p.append("no Markdown table in the file; the Lookup Table is required")
    else:
        ncols = [len(r.strip().strip("|").split("|")) for r in rows]
        if len(set(ncols)) > 1 and min(Counter(ncols).values()) == 1:
            p.append(f"ragged table row widths {sorted(set(ncols))}")
        if ncols[0] not in (2, 3, 4):
            p.append(f"first table has {ncols[0]} columns (expect 2, 3, or 4)")
        if any("…and it" in r or "\u2026 and" in r for r in rows):
            p.append("ellipsis continuation row in table -- name every operation")

    # exception naming
    for m in re.finditer(r"raises (?!`)(\w+)", t):
        if m.group(1) not in NOT_AN_EXCEPTION:
            n = t[:m.start()].count("\n") + 1
            p.append(
                f"line {n}: backtick the exception name "
                f"({m.group(1)}): {lines[n - 1].strip()[:70]!r}"
            )
    if re.search(r"raises an error\b", t, re.I):
        p.append("'raises an error' -- name the exception instead")
    if re.search(r"\braises\b[^.\n]{0,20}\bmeans\b", t, re.I):
        p.append("defines 'raises' -- assumed vocabulary, delete the sentence")

    # callout format
    for i, l in enumerate(lines):
        m = re.match(r"^> \[!(\w+)\]\s*(.*)$", l)
        if m:
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if not nxt.startswith(">"):
                p.append(
                    f"callout [!{m.group(1)}] line {i + 2} does not start with '> ': "
                    f"{nxt.strip()[:40]!r}"
                )

    # unlabeled fences hold output only
    for m in re.finditer(r"^```(\w*)\n(.*?)^```", t, re.M | re.S):
        if m.group(1) == "" and CODEY.search(m.group(2)):
            first = next(l for l in m.group(2).splitlines() if CODEY.match(l))
            p.append(f"code in an unlabeled fence -- label it or fix: {first.strip()!r}")

    # no time estimates
    m = TIME_ESTIMATE.search(t)
    if m:
        n = t[:m.start()].count("\n") + 1
        p.append(f"line {n}: time estimate -- remove it: {lines[n - 1].strip()[:70]!r}")

    return p


def main():
    args = sys.argv[1:]
    if not args:
        print("usage: python3 check_lesson.py <lesson.md> [more.md ...] | <folder>")
        return 2

    files = []
    for a in args:
        path = Path(a)
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
        elif path.exists():
            files.append(path)
        else:
            print(f"not found: {a}")
            return 2

    fails = 0
    for f in files:
        probs = check(f)
        if probs:
            fails += 1
            print(f"FAIL {f.name}")
            for x in probs:
                print(f"      - {x}")
        else:
            print(f"ok   {f.name}")

    print(f"\n{len(files)} lessons checked; {fails} with contract violations")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
