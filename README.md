# md-toc

Generate or update a table of contents in a Markdown file — zero-dependency Python CLI.

It scans `#` … `######` headings (skipping fenced code blocks), builds a nested
bullet list with GitHub-style anchor links, and inserts it between
`<!-- TOC -->` and `<!-- /TOC -->` markers (or right after the first heading
if no markers exist). Running it again updates the existing TOC in place.

## Install

No dependencies — just Python 3.8+.

```sh
git clone https://github.com/heyzcx/md-toc.git
cd md-toc
```

## Usage

Print the file with a TOC to stdout:

```sh
python3 md_toc.py example.md
```

Update the file in place:

```sh
python3 md_toc.py example.md --in-place
```

Only include headings of a certain depth:

```sh
python3 md_toc.py example.md --min-depth 2 --max-depth 3
```

## Example

Input:

```markdown
# My Project

## Installation

### From source

## Usage
```

Output (with `--in-place`):

```markdown
# My Project

<!-- TOC -->
- [My Project](#my-project)
  - [Installation](#installation)
    - [From source](#from-source)
  - [Usage](#usage)
<!-- /TOC -->

## Installation
...
```

Duplicate headings get GitHub-style `-1`, `-2` suffixes, matching how GitHub
renders anchors.

## License

MIT.
