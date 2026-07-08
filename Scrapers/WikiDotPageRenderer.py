"""Shared plain-text renderer for dnd2024.wikidot.com `#page-content` blocks.

Used by both WikiDotSubclassScraper.py (subclass pages, e.g. paladin:oath-of-the-ancients)
and WikiDotClassScraper.py (main class pages, e.g. paladin:main). Subclass pages happen to
have zero nested wrapper divs, while class pages sometimes wrap a block (typically a table)
in a plain <div>. get_outermost_blocks() handles both cases with one algorithm.
"""

import re

HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
BLOCK_TAGS = ["p", *HEADING_TAGS, "table", "ul"]


def get_outermost_blocks(content, block_tags=BLOCK_TAGS):
    """Find every block-level element under `content`, at any depth, but drop any
    element that is itself nested inside another matching block element (so a table
    wrapped in a plain <div> is still found, while never double-rendering nested
    blocks-within-blocks).
    """
    found = content.find_all(block_tags)

    def is_outermost(el) -> bool:
        for parent in el.parents:
            if parent is content:
                return True
            if parent.name in block_tags:
                return False
        return True

    return [el for el in found if is_outermost(el)]


def render_heading(heading) -> list[str]:
    return [heading.get_text().strip()]


def render_table(table) -> list[str]:
    lines = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        lines.append("\t".join(cell.get_text().strip() for cell in cells))
    return lines


def render_paragraph(p) -> list[str]:
    for br in p.find_all("br"):
        br.replace_with("\n")
    text = p.get_text()
    # The HTML source often has an incidental newline (plus indentation) immediately
    # following a <br> tag, purely from how the page markup is formatted/wrapped. That
    # combines with the "\n" we just inserted for the <br> itself to form "\n\n" (a
    # spurious blank line) unless we collapse it back down to a single explicit line
    # break here.
    text = re.sub(r"[ \t]*\n[ \t\n]*", "\n", text).strip()
    return [text, ""]


def render_list(ul) -> list[str]:
    return [li.get_text().strip() for li in ul.find_all("li", recursive=False)]


def render_content_lines(content, block_tags=BLOCK_TAGS) -> list[str]:
    """Render every outermost block under `content` into the exact plain-text line list,
    with trailing blank line(s) stripped.
    """
    lines: list[str] = []
    for block in get_outermost_blocks(content, block_tags):
        if block.name in HEADING_TAGS:
            lines.extend(render_heading(block))
        elif block.name == "table":
            lines.extend(render_table(block))
        elif block.name == "p":
            lines.extend(render_paragraph(block))
        elif block.name == "ul":
            lines.extend(render_list(block))

    while lines and lines[-1] == "":
        lines.pop()

    return lines
