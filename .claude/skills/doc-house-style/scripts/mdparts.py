#!/usr/bin/env python3
"""Shared Markdown parsing for the reference-set checks.

Both check_pages.py and check_lossless.py need to know where the fenced
blocks are, so the fence walk lives here once. A fence may be indented and
may sit inside a callout ('> ```python'), so the opener and its closer are
matched on the stripped line and on the quote prefix.
"""
import re

FENCE_RE = re.compile(r"^(?P<prefix>\s*(?:>\s?)*)```(?P<info>[^\s`]*)\s*$")


class Fence:
    """One fenced block: where it starts, where it ends, its info string."""

    def __init__(self, open_line, close_line, info, body, prefix):
        self.open_line = open_line      # 0-based index of the ``` opener
        self.close_line = close_line    # 0-based index of the closer, or None
        self.info = info                # '' for a bare fence
        self.body = body                # list of body lines, prefix stripped
        self.prefix = prefix            # quote prefix, e.g. '> ' inside a callout

    @property
    def text(self):
        return "\n".join(self.body)


def fences(lines):
    """Walk the file once and return every fenced block, in order."""
    out, i = [], 0
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        prefix, info, start = m.group("prefix"), m.group("info"), i
        body, i = [], i + 1
        close = None
        while i < len(lines):
            m2 = FENCE_RE.match(lines[i])
            if m2 and m2.group("info") == "":
                close = i
                break
            body.append(re.sub(r"^\s*(?:>\s?)*", "", lines[i]))
            i += 1
        out.append(Fence(start, close, info, body, prefix))
        i = (close + 1) if close is not None else i
    return out


def fence_line_set(lines):
    """Every line index that is part of a fenced block, opener and closer too."""
    inside = set()
    for f in fences(lines):
        end = f.close_line if f.close_line is not None else len(lines) - 1
        inside |= set(range(f.open_line, end + 1))
    return inside


def strip_code(text):
    """Blank out inline code spans and wiki links so prose can be measured.

    'Reading `p.name` from [[Path Objects]]' has three periods that do not end
    a sentence; removing the spans first is what makes sentence counting work.
    """
    text = re.sub(r"`[^`]*`", "CODE", text)
    text = re.sub(r"\[\[[^\]]*\]\]", "LINK", text)
    return text


def sentences(text):
    """Split prose into sentences. Run strip_code() on it first."""
    text = " ".join(text.split())
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(`\"'\u2014])", text)
    return [s for s in (p.strip() for p in parts) if s]


def headings(lines):
    """(level, text) for every ATX heading outside a fence."""
    inside = fence_line_set(lines)
    out = []
    for i, l in enumerate(lines):
        if i in inside:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", l)
        if m:
            out.append((len(m.group(1)), m.group(2)))
    return out


def table_rows(lines):
    """Normalized table rows outside fences; separator rows dropped."""
    inside = fence_line_set(lines)
    out = []
    for i, l in enumerate(lines):
        if i in inside:
            continue
        s = l.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):
            continue                      # the |---|---| separator
        out.append(" | ".join(" ".join(c.split()) for c in cells))
    return out


def wiki_links(lines):
    inside = fence_line_set(lines)
    out = []
    for i, l in enumerate(lines):
        if i not in inside:
            out += re.findall(r"\[\[([^\]|]+)", l)
    return out


def code_spans(lines):
    """Backticked spans in prose -- the call names a page promises to cover."""
    inside = fence_line_set(lines)
    out = []
    for i, l in enumerate(lines):
        if i not in inside:
            out += re.findall(r"`([^`]+)`", l)
    return out
