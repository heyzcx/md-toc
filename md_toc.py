#!/usr/bin/env python3
"""md-toc: generate or update a table of contents in a Markdown file.

Scans headings (# ... ######), builds a nested bullet list with GitHub-style
anchor links, and inserts it between <!-- TOC --> and <!-- /TOC --> markers
(or after the first heading if no markers exist).

Usage:
    python3 md_toc.py FILE.md [--in-place] [--max-depth N] [--min-depth N]

With --in-place the file is updated; otherwise the TOC is printed to stdout.
"""
import argparse
import re
import sys
import unicodedata

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
TOC_START = "<!-- TOC -->"
TOC_END = "<!-- /TOC -->"


def slugify(text: str) -> str:
    """GitHub-style anchor slug for a heading."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"`[^`]*`", lambda m: m.group(0).strip("`"), text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_~`]", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def extract_headings(lines, min_depth=1, max_depth=6):
    headings = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line.rstrip("\n"))
        if m:
            depth = len(m.group(1))
            if min_depth <= depth <= max_depth:
                headings.append((depth, m.group(2).strip()))
    return headings


def build_toc(headings):
    if not headings:
        return ""
    base = min(d for d, _ in headings)
    out = []
    seen = {}
    for depth, title in headings:
        slug = slugify(title)
        seen[slug] = seen.get(slug, 0) + 1
        if seen[slug] > 1:
            slug = f"{slug}-{seen[slug] - 1}"
        indent = "  " * (depth - base)
        out.append(f"{indent}- [{title}](#{slug})")
    return "\n".join(out)


def insert_toc(text, toc, min_depth=1, max_depth=6):
    lines = text.splitlines()
    headings = extract_headings(lines, min_depth, max_depth)
    toc = build_toc(headings)
    block = f"{TOC_START}\n{toc}\n{TOC_END}"
    try:
        start = next(i for i, l in enumerate(lines) if TOC_START in l)
        end = next(i for i, l in enumerate(lines) if TOC_END in l)
        if end < start:
            raise ValueError("TOC end marker before start marker")
        new_lines = lines[:start] + [block] + lines[end + 1:]
        return "\n".join(new_lines) + "\n", len(headings)
    except StopIteration:
        pass
    # No markers: insert after the first heading.
    for i, line in enumerate(lines):
        if HEADING_RE.match(line):
            new_lines = lines[: i + 1] + ["", block, ""] + lines[i + 1:]
            return "\n".join(new_lines) + "\n", len(headings)
    return block + "\n\n" + text, len(headings)


def main(argv=None):
    p = argparse.ArgumentParser(description="Generate a TOC for a Markdown file.")
    p.add_argument("file", help="Markdown file to process")
    p.add_argument("--in-place", action="store_true", help="Update the file in place")
    p.add_argument("--min-depth", type=int, default=1)
    p.add_argument("--max-depth", type=int, default=6)
    args = p.parse_args(argv)

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"error: cannot read {args.file}: {e}", file=sys.stderr)
        return 1

    new_text, count = insert_toc(text, "", args.min_depth, args.max_depth)
    if count == 0:
        print("no headings found; nothing to do", file=sys.stderr)
        return 1

    if args.in_place:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"updated {args.file}: {count} headings in TOC")
    else:
        print(new_text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
