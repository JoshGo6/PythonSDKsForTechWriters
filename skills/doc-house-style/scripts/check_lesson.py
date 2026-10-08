#!/usr/bin/env python3
"""Check a generated lesson against its lesson contract and the house style.

Two curricula share this checker, and they do not have the same lesson shape:

  --profile python   python-sdk-lesson: Terminology, Syntax, Worked Examples,
                     Lookup Table, Exercise. A Quick Reference is a relic here.
  --profile shell    bash-scripting-lesson: Orientation, Terminology, Syntax,
                     Worked Examples, Quick Reference, Exercise. No Lookup
                     Table, transcripts in `shellsession`, and an audit that
                     belongs in a scratch file rather than in the lesson.

Everything else is the house style and runs for both: a lead-in above every
fence, an info string on every fence, callout format, no time estimates.

It cannot check whether a heading carries a claim, whether an example can
fail, or whether the exercise has a forward dependency. Those stay human.

Usage:  python3 check_lesson.py [--profile python|shell] <lesson.md> [more.md ...]
        python3 check_lesson.py [--profile python|shell] <folder>
"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from mdparts import fences, headings
from housestyle import (
    PY_CODEY, SH_CODEY, check_bash4, check_callouts, check_exceptions,
    check_fences, check_heading_stack, check_numbers, check_sandbox,
    check_triplets,
)

TIME_ESTIMATE = re.compile(
    r"\b(should take|takes about|roughly \d+ ?(min|hour)|\d+[-–]\d+ ?minutes|"
    r"\d+ ?minutes\b|quick exercise|shouldn't take long)", re.I)

PROFILES = {
    "python": {
        "required": [
            (r"terminolog|theory|concept", "Terminology/Theory"),
            (r"syntax", "Syntax"),
            (r"example", "Worked Examples"),
            (r"lookup", "Lookup Table"),
            (r"exercise", "Exercise"),
        ],
        "relics": [
            ("quick reference", "replaced by the Lookup Table"),
            ("audit", "replaced by silent verification"),
            ("snippet reference", "removed by settled policy"),
            ("reference delta", "no longer emitted; hand over the lesson instead"),
            ("verification report", "verification is silent; do not print it"),
        ],
        "table_required": True,
        "codey": PY_CODEY,
        "exceptions": True,
        "shell_checks": False,
    },
    "shell": {
        "required": [
            (r"orientation", "Orientation"),
            (r"terminolog|theory|concept", "Terminology and theory"),
            (r"syntax", "Syntax"),
            (r"example", "Worked Examples"),
            (r"quick reference", "Quick Reference"),
            (r"exercise", "Exercise"),
        ],
        "relics": [
            ("audit", "the audit goes to a scratch file, never into the lesson"),
            ("dependency inventory", "the inventory goes to a scratch file"),
            ("verification report", "verification is silent; do not print it"),
            ("snippet reference", "removed by settled policy"),
        ],
        "table_required": False,
        "codey": SH_CODEY,
        "exceptions": False,
        "shell_checks": True,
    },
}


def check(path, prof):
    t = path.read_text(encoding="utf-8")
    lines = t.splitlines()
    heads = [txt for _, txt in headings(lines)]
    joined = " ".join(heads).lower()
    p = []

    # required parts, matched loosely because heading wording varies
    for pattern, label in prof["required"]:
        if not re.search(pattern, joined):
            p.append(f"no {label} section found in the headings")

    for relic, why in prof["relics"]:
        if relic in joined:
            p.append(f"relic section {relic!r} -- {why}")

    # tables: required in one profile, merely checked in the other
    rows = [l for l in lines if l.strip().startswith("|") and "---" not in l]
    if not rows:
        if prof["table_required"]:
            p.append("no Markdown table in the file; the Lookup Table is required")
    else:
        ncols = [len(r.strip().strip("|").split("|")) for r in rows]
        if len(set(ncols)) > 1 and min(Counter(ncols).values()) == 1:
            p.append(f"ragged table row widths {sorted(set(ncols))}")
        if prof["table_required"] and ncols[0] not in (2, 3, 4):
            p.append(f"first table has {ncols[0]} columns (expect 2, 3, or 4)")
        if any("…and it" in r or "… and" in r for r in rows):
            p.append("ellipsis continuation row in table -- name every operation")

    if prof["exceptions"]:
        p += check_exceptions(t, lines)

    p += check_heading_stack(lines)

    p += check_numbers(lines)

    p += check_sandbox(lines)

    p += check_callouts(lines)

    p += check_fences(lines, prof["codey"])

    if prof["shell_checks"]:
        p += check_triplets(lines)
        p += check_bash4(t)
        if not any(f.info == "shellsession" for f in fences(lines)):
            p.append("no `shellsession` block; the Quick Reference is one")

    # no time estimates
    m = TIME_ESTIMATE.search(t)
    if m:
        n = t[:m.start()].count("\n") + 1
        p.append(f"line {n}: time estimate -- remove it: {lines[n - 1].strip()[:70]!r}")

    return p


def main():
    args = sys.argv[1:]
    profile = "python"
    if args and args[0] == "--profile":
        if len(args) < 2 or args[1] not in PROFILES:
            print(f"usage: --profile {'|'.join(PROFILES)}")
            return 2
        profile, args = args[1], args[2:]
    elif args and args[0].startswith("--profile="):
        profile, args = args[0].split("=", 1)[1], args[1:]
        if profile not in PROFILES:
            print(f"usage: --profile {'|'.join(PROFILES)}")
            return 2

    if not args:
        print("usage: python3 check_lesson.py [--profile python|shell] "
              "<lesson.md> [more.md ...] | <folder>")
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

    prof = PROFILES[profile]
    fails = 0
    for f in files:
        probs = check(f, prof)
        if probs:
            fails += 1
            print(f"FAIL {f.name}")
            for x in probs:
                print(f"      - {x}")
        else:
            print(f"ok   {f.name}")

    print(f"\n{len(files)} lessons checked against the {profile} profile; "
          f"{fails} with contract violations")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
