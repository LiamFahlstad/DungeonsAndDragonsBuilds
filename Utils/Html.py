"""Generic HTML generation primitives and character sheet CSS fragments."""

import re
from typing import TextIO

from Core.Definitions import DAMAGE_TYPE_COLORS

_DAMAGE_TYPE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(name) for name in DAMAGE_TYPE_COLORS) + r")\b",
    re.IGNORECASE,
)

# Reset sentinel markers for slot recovery labels
RESET_PREFIX = "[RESET:"
RESET_SUFFIX = "]"

# Box-count sentinel markers - encode both the current and max box counts so
# rendering can defer to render time which one to draw (current on the full
# sheet, max on a level shard page). Format: [BOXES:current:max]
BOXES_PREFIX = "[BOXES:"
BOXES_SUFFIX = "]"

# Current-value-formula sentinel marker - a short plain-English note on how to
# derive the build's real "current" count from the max shown on a level shard
# page (where the boxes render the formula's ceiling, not the current value).
# Only rendered when use_max=True; consumed and discarded otherwise.
CURRENT_PREFIX = "[CURRENT:"
CURRENT_SUFFIX = "]"


def _bold_prefix(line: str, separator: str, max_words: int):
    if separator not in line:
        return None

    first, rest = line.split(separator, 1)
    if len(first.split()) < max_words and rest.strip():
        return f"<strong>{first.strip()}{separator}</strong> {rest.strip()}"

    return None


def _is_reset_sentinel_line(line: str) -> bool:
    """Return True if *line* is (possibly followed by <br>) a reset sentinel."""
    stripped = line.strip()
    if stripped.endswith("<br>"):
        stripped = stripped[:-4].rstrip()
    return stripped.startswith(RESET_PREFIX) and stripped.endswith(RESET_SUFFIX)


def boxes_to_html(description: str, use_max: bool = False) -> str:
    def normalize_box_line(line: str) -> str:
        stripped = line.strip()
        if stripped.endswith("<br>"):
            stripped = stripped[:-4].rstrip()
        return stripped

    def parse_box_counts(line: str) -> tuple[int, int] | None:
        """Return (box_count, max_box_count) if *line* is a box sentinel, else None."""
        normalized = normalize_box_line(line)
        if normalized.startswith(BOXES_PREFIX) and normalized.endswith(BOXES_SUFFIX):
            inner = normalized[len(BOXES_PREFIX) : -len(BOXES_SUFFIX)]
            current_str, max_str = inner.split(":")
            return int(current_str), int(max_str)
        return None

    def parse_reset_label(line: str) -> str | None:
        """Return the reset label text if *line* is a reset sentinel, else None."""
        normalized = normalize_box_line(line)
        if normalized.startswith(RESET_PREFIX) and normalized.endswith(RESET_SUFFIX):
            return normalized[len(RESET_PREFIX) : -len(RESET_SUFFIX)]
        return None

    def parse_current_formula(line: str) -> str | None:
        """Return the current-value-formula text if *line* is a current sentinel, else None."""
        normalized = normalize_box_line(line)
        if normalized.startswith(CURRENT_PREFIX) and normalized.endswith(
            CURRENT_SUFFIX
        ):
            return normalized[len(CURRENT_PREFIX) : -len(CURRENT_SUFFIX)]
        return None

    lines = description.split("\n")
    new_lines = []
    index = 0

    while index < len(lines):
        box_counts = parse_box_counts(lines[index])

        if box_counts is not None:
            box_count, max_box_count = box_counts
            top_count = max_box_count if use_max else box_count
            boxes_html = '<span class="slot-box"></span>' * top_count
            consumed = 1  # the box line itself

            # Peek at the following lines, in order, for an optional reset-label
            # sentinel and then an optional current-value-formula sentinel.
            # Either, both, or neither may be present.
            reset_label = None
            if index + consumed < len(lines):
                reset_label = parse_reset_label(lines[index + consumed])
                if reset_label is not None:
                    consumed += 1

            current_formula = None
            if index + consumed < len(lines):
                current_formula = parse_current_formula(lines[index + consumed])
                if current_formula is not None:
                    consumed += 1

            extra_html_parts = []
            if reset_label is not None:
                # Capitalize the reset label for proper sentence formatting
                capitalized_label = (
                    reset_label[0].upper() + reset_label[1:] if reset_label else ""
                )
                extra_html_parts.append(
                    f'<span class="slot-reset-label">{capitalized_label}.</span>'
                )
            if current_formula is not None and use_max:
                # Only meaningful on level shard pages, where the boxes above
                # show the formula's ceiling rather than the build's current
                # value - not rendered on the full sheet, where the boxes
                # already show the current value directly.
                extra_html_parts.append(
                    f'<span class="slot-reset-label">{current_formula}</span>'
                )

            if extra_html_parts:
                new_lines.append(
                    '<div class="slot-box-group">'
                    + boxes_html
                    + "</div>"
                    + "\n"
                    + "\n".join(extra_html_parts)
                )
            else:
                new_lines.append('<div class="slot-box-group">' + boxes_html + "</div>")
            index += consumed
            continue

        # Skip bare reset/current sentinel lines that appear without a preceding
        # box line (shouldn't normally happen, but guard against it).
        if (
            parse_reset_label(lines[index]) is not None
            or parse_current_formula(lines[index]) is not None
        ):
            index += 1
            continue

        new_lines.append(lines[index])
        index += 1

    return "\n".join(new_lines)


def tables_to_html(description: str) -> str:
    """Convert blocks of consecutive tab-separated lines into HTML tables.

    A block is a run of lines that each contain at least one tab. If every
    row in the block has the same cell count, the first row is rendered as
    a header (<th>); otherwise (ragged column counts, e.g. a printed
    multi-column item list) all rows render as plain <td> rows with no
    header styling.
    """
    lines = description.split("\n")
    new_lines = []
    index = 0

    while index < len(lines):
        if "\t" not in lines[index]:
            new_lines.append(lines[index])
            index += 1
            continue

        block_rows = []
        while index < len(lines) and "\t" in lines[index]:
            cells = [cell.strip() for cell in lines[index].strip().split("\t")]
            block_rows.append(cells)
            index += 1

        cell_counts = {len(row) for row in block_rows}
        has_header = len(cell_counts) == 1 and len(block_rows[0]) > 1

        new_lines.append("<table class='feature-table'>")
        for i, cells in enumerate(block_rows):
            tag = "th" if (has_header and i == 0) else "td"
            cells_html = "".join(f"<{tag}>{cell}</{tag}>" for cell in cells)
            new_lines.append(f"<tr>{cells_html}</tr>")
        new_lines.append("</table>")

    return "\n".join(new_lines)


def key_value_table_to_html(rows: list[tuple[str, str]]) -> str:
    """Render label/value pairs as a two-column feature table, label cells as headers.

    Unlike tables_to_html (which infers header vs. data rows from a tab-separated
    block), every row here is a distinct label/value pair, so the label is always
    a <th> rather than only the first row.
    """
    lines = ["<table class='feature-table'>"]
    for label, value in rows:
        lines.append(f"<tr><th>{label}</th><td>{value}</td></tr>")
    lines.append("</table>")
    return "\n".join(lines)


def bolden_text_html(text: str) -> str:
    new_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            # Preserve empty lines to maintain paragraph breaks
            new_lines.append(line)
            continue

        if stripped == "<br>":
            new_lines.append(line)
            continue

        # Preserve reset sentinel lines so that boxes_to_html can process them.
        if _is_reset_sentinel_line(line):
            new_lines.append(line)
            continue

        bolded_line = _bold_prefix(stripped, ".", 5)
        if bolded_line is not None:
            new_lines.append(bolded_line)
            continue

        bolded_line = _bold_prefix(stripped, ":", 10)
        if bolded_line is not None:
            new_lines.append(bolded_line)
            continue

        new_lines.append(line)

    return "\n".join(new_lines)


def highlight_damage_types(html: str) -> str:
    """Wrap every mention of a damage type word in a color-coded span."""

    def _replace(match: re.Match) -> str:
        word = match.group(0)
        color = DAMAGE_TYPE_COLORS.get(word.capitalize(), "#999999")
        return f"<span style='color: {color}; print-color-adjust: exact;'>{word}</span>"

    return _DAMAGE_TYPE_PATTERN.sub(_replace, html)


def write_table_row(file: TextIO, cells: list, tr_class: str = ""):
    cls = f" class='{tr_class}'" if tr_class else ""
    file.write(f"<tr{cls}>")
    for cell in cells:
        file.write(f"<td>{cell}</td>")
    file.write("</tr>\n")


def write_item_table(file: TextIO, title: str, rows: list[tuple[str, str]]):
    file.write("<table class='item-table'>\n")
    file.write("<tr>\n")
    file.write(f"<th class='item-title' colspan='2'>{title}</th>\n")
    file.write("</tr>\n")

    for label, value in rows:
        file.write("<tr>")
        file.write(f"<td class='item-label'>{label}</td>")
        file.write(f"<td class='item-value'>{value}</td>")
        file.write("</tr>\n")

    file.write("</table>\n")


def write_item_cards(
    file: TextIO, title: str, rows: list[tuple[str, str, int, str, str, str]]
):
    """Inventory items rendered as stacked cards (matching the weapon-entry
    visual language) with type, rarity, buy/sell price, slot cost, and
    carrying tracking. Each row is (label, description, slots, item_type,
    rarity, price_display)."""
    import re

    file.write(f"<h3>{title}</h3>\n")
    file.write("<div class='gear-list'>\n")

    for label, description, slots, item_type, rarity, price in rows:
        plain_label = re.sub(r"<span[^>]*>.*?</span>", "", label)
        plain_label = re.sub(r"<[^>]*>", "", plain_label).strip()
        carrying_id = (
            plain_label.replace(" ", "_").replace("(", "").replace(")", "")
            + "_carrying"
        )

        file.write("<div class='gear-entry'>\n")

        # ── Title row: item name + carrying checkbox always stay
        # together on one line. Quick-stats flow as their own wrapping
        # line below, as a single unit instead of being split apart. ───
        file.write("<div class='gear-header'>\n")
        file.write(f"<span class='gear-name'>{label}</span>\n")
        file.write(
            f"<label class='gear-carrying' for='{carrying_id}_check'>Carrying"
            f"<input type='checkbox' id='{carrying_id}_check' name='{carrying_id}_check'/></label>\n"
        )
        file.write("</div>\n")
        file.write(
            f"<div class='gear-meta'>{item_type}"
            f"<span class='gsep'>·</span>{rarity}"
            f"<span class='gsep'>·</span>"
            f"<span class='glabel'>Buy/Sell</span> {price}"
            f"<span class='gsep'>·</span>"
            f"<span class='glabel'>Slots</span> {slots}</div>\n"
        )

        # ── Description ──────────────────────────────────────────────────
        if description and description != "-":
            file.write(f"<div class='gear-desc'>{description}</div>\n")

        file.write("</div>\n")

    file.write("</div>\n")


def write_slot_table(slots: dict[int, int], file: TextIO, reset_label: str):
    file.write("<div class='slot-grid'>\n")
    for level, count in slots.items():
        file.write(f"  <div class='slot-level'>\n")
        file.write(f"    <div class='slot-level-label'>Level {level}</div>\n")
        boxes_html = (
            '<div class="slot-box-group">'
            + '<span class="slot-box"></span>' * count
            + "</div>"
        )
        file.write(f"    {boxes_html}\n")
        file.write(f"  </div>\n")
    file.write("</div>\n")
    file.write(f"<span class='slot-reset-label'>{reset_label}</span>\n")


def render_style_block(*css_fragments: str) -> str:
    """Compose CSS fragments into a <style> block with proper formatting."""
    # Simply concatenate all fragments - they should already have proper internal formatting
    combined = "".join(css_fragments)
    return "<style>\n" + combined + "</style>"


# ── BASE_CHARACTER_SHEET_CSS ───────────────────────────────────────────────
# Generic HTML structure, typography, print rules, stat tables, item tables,
# capacity tables, and probability-table CSS shared by weapons and spells.

BASE_CHARACTER_SHEET_CSS = """
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

        :root {
            --text-color: #222;
            --muted-color: #555;
            --border-color: #ddd;
        }

        html {
            font-size: 14px;
        }

        body {
            font-family: "EB Garamond", Garamond, "Times New Roman", serif;
            line-height: 1.5;
            color: var(--text-color);
            margin: 0;
            padding: 1.5rem;
        }

        div {
            max-width: 700px;
            margin: 0 auto;
            padding: 0 0.5rem;
        }

        p {
            margin: 0.5em 0;
        }

        h1 {
            color: #3a2c1c;
            border-bottom: 3px solid #9a7040;
            padding-bottom: 0.2em;
            margin: 0 0 1rem 0;
            font-size: 1.6rem;
            letter-spacing: 0.02em;
        }

        h2 {
            color: #3a2c1c;
            border-bottom: 2px solid #9a7040;
            padding-bottom: 0.12em;
            margin: 1.1rem 0 0.4rem 0;
            font-size: 1.2rem;
            letter-spacing: 0.02em;
        }

        ul, ol {
            margin: 0.5em 0 0.5em 1.2em;
        }

        @media print {
            body {
                padding: 0;
                font-size: 10pt;
            }

            div {
                max-width: 100%;
            }

            h1, h2, h3 {
                page-break-after: avoid;
            }

            p, pre, ul, ol {
                page-break-inside: auto;
            }

            .page-break {
                display: none;
            }

            /* Collapse inter-section <br> gaps (but not content line breaks) */
            br.section-gap {
                display: none;
            }

            h1 {
                margin: 0 0 0.3rem 0;
            }

            h2 {
                margin: 0.3em 0 0.1em;
            }

            table.stat-table {
                margin-bottom: 0.4rem;
            }

            table.stat-table th,
            table.stat-table td {
                padding: 3px 6px;
            }
        }

        /* Forces a page break before the element in print/PDF */
        .print-page-break {
            break-before: page;
        }

        /* Cross-links between the per-character-folder pages (character,
           per-level features, weapons, spells, items). Hidden when printing
           since it's pure navigation, not sheet content. */
        .page-nav {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem 0.9rem;
            margin: 0 0 1rem 0;
            padding: 0.4rem 0.6rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            background-color: #fafafa;
            font-size: 0.8rem;
        }

        .page-nav a {
            color: #3a6e4a;
            text-decoration: none;
            font-weight: 600;
        }

        .page-nav a:hover {
            text-decoration: underline;
        }

        .page-nav .page-nav-current {
            color: var(--muted-color);
            font-weight: 600;
        }

        @media print {
            .page-nav {
                display: none;
            }
        }

        /* Side-by-side section layout — overrides the global div rule */
        .section-row {
            display: flex;
            gap: 1.5rem;
            align-items: flex-start;
            max-width: none;
            margin: 0;
            padding: 0;
        }

        .section-col {
            flex: 1;
            min-width: 0;
            max-width: none;
            margin: 0;
            padding: 0;
        }

        /* Abilities tiles are naturally narrower than the two-column skill
           list, which wants the extra room for its longer skill names. */
        .section-col-abilities {
            flex: 0.85;
        }

        .section-col-skills {
            flex: 1.15;
        }

        /* Stat table: spell slots */
        .slot-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem 1.25rem;
            margin: 0 0 0.5rem 0;
        }

        .slot-level {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .slot-level-label {
            color: #3a2c1c;
            font-weight: 700;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.2rem;
        }

        .slot-level .slot-box-group {
            margin: 0;
        }

        table.stat-table {
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0 0 0.75rem 0;
        }

        table.stat-table th,
        table.stat-table td {
            border: 1px solid #c4b49a;
            padding: 5px 10px;
            vertical-align: middle;
            text-align: left;
        }

        table.stat-table th {
            color: #3a2c1c;
            font-weight: 700;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            white-space: nowrap;
            border-bottom: 2px solid #3a2c1c;
        }

        table.stat-table tr.st-proficient td {
            color: #2e6e3e;
        }

        table.stat-table tr.st-proficient td:first-child {
            font-weight: 700;
        }

        /* Expertise badge styling */
        .skill-expertise {
            display: inline-block;
            border: 1px solid #d4a747;
            color: #8a6200;
            padding: 0 5px;
            border-radius: 3px;
            font-weight: 700;
            font-size: 0.85em;
        }

        /* ── Ability tiles ────────────────────────────────────────────────
           The modifier is what gets added to rolls constantly, so it's the
           large number; score/save/DC/ATK are secondary reference info. */
        .ability-tiles {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.4rem;
        }

        .ability-tile {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.05rem;
            padding: 0.3rem 0.4rem;
            border: 1px solid #c4b49a;
            border-radius: 6px;
        }

        .ability-tile.st-proficient {
            border-color: #6a9a7a;
        }

        .ability-tile-name {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #6a5636;
        }

        .ability-tile-mod {
            font-size: 1.4rem;
            font-weight: 700;
            color: #3a2c1c;
            line-height: 1.1;
        }

        .ability-tile.st-proficient .ability-tile-mod {
            color: #2e6e3e;
        }

        .ability-tile-score {
            font-size: 0.68rem;
            color: #7a6a50;
        }

        .ability-tile-extra {
            font-size: 0.62rem;
            color: #7a6a50;
            white-space: nowrap;
            margin-top: 0.15rem;
        }

        /* ── Skill list ───────────────────────────────────────────────────
           Flows into two CSS columns instead of one long table so eighteen
           skills don't dominate the page height. */
        .skills-columns {
            column-count: 2;
            column-gap: 0.9rem;
        }

        .skill-entry {
            break-inside: avoid;
            -webkit-column-break-inside: avoid;
            padding: 0.15rem 0;
            border-bottom: 1px solid #eee;
            font-size: 0.8rem;
        }

        .skill-entry-top {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.4rem;
        }

        .skill-name {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .skill-ability-tag {
            font-size: 0.65rem;
            font-weight: 600;
            color: var(--muted-color);
            margin-left: 0.3rem;
        }

        .skill-mod {
            font-weight: 700;
            flex-shrink: 0;
        }

        .skill-entry.st-proficient .skill-mod,
        .skill-entry.st-proficient .skill-name {
            color: #2e6e3e;
        }

        .skill-entry.st-expertise .skill-mod,
        .skill-entry.st-expertise .skill-name {
            color: #8a6200;
        }

        .skill-entry .skill-expertise {
            margin-left: 0.3rem;
            font-size: 0.6rem;
            padding: 0 3px;
        }

        .skill-breakdown {
            font-size: 0.68rem;
            font-style: italic;
            color: var(--muted-color);
        }

        /* ── Tool proficiencies ──────────────────────────────────────────
           Same flowing card language as .skill-entry, since a tool row is
           the same shape (name + ability tag + modifier + breakdown), plus
           an optional craft line. */
        .tool-list {
            column-count: 2;
            column-gap: 0.9rem;
        }

        .tool-entry {
            break-inside: avoid;
            -webkit-column-break-inside: avoid;
            padding: 0.15rem 0;
            border-bottom: 1px solid #eee;
            font-size: 0.8rem;
        }

        .tool-entry-top {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.4rem;
        }

        .tool-name {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .tool-mod {
            font-weight: 700;
            flex-shrink: 0;
        }

        .tool-entry.st-proficient .tool-mod,
        .tool-entry.st-proficient .tool-name {
            color: #2e6e3e;
        }

        .tool-craft {
            font-size: 0.68rem;
            color: var(--muted-color);
            margin-top: 0.1rem;
        }

        /* Spell slot checkboxes */
        .slot-box {
            display: inline-block;
            width: 1.6em;
            height: 1.6em;
            border: 1px solid currentColor;
            box-sizing: border-box;
            border-radius: 0.2em;
            vertical-align: middle;
        }

        .slot-box-group {
            display: inline-flex;
            gap: 0.5em;
            align-items: center;
            margin: 0.35em 0;
        }

        .slot-reset-label {
            display: block;
            font-size: 0.75em;
            font-style: italic;
            color: #666;
            margin-top: 0.1em;
            margin-bottom: 0.4em;
        }

        /* Item and tool proficiency tables */
        .item-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0.25rem 0;
        }

        .item-table td, .item-table th {
            border: 1px solid var(--border-color);
            padding: 3px 5px;
            vertical-align: top;
        }

        .item-title {
            color: #3a6e4a;
            font-size: 0.78rem;
            font-weight: 700;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            border-bottom: 1px solid #6a9a7a !important;
        }

        .item-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
        }

        .item-value {
            width: auto;
        }

        /* ── Inventory item cards ─────────────────────────────────────── */
        /* Two-column flow so short entries (most armor/weapons/gear) pack
           tightly instead of each spanning the full page width - mirrors
           .skills-columns. */
        .gear-list {
            column-count: 2;
            column-gap: 1.2rem;
        }

        .gear-entry {
            font-size: 0.85rem;
            padding: 0.35rem 0;
            max-width: none;
            break-inside: avoid;
            -webkit-column-break-inside: avoid;
            border-bottom: 1px solid #cde0d2;
        }

        /* Title row: item name and carrying checkbox always stay on
           the same line, pinned to opposite ends. */
        .gear-header {
            display: flex;
            flex-wrap: nowrap;
            justify-content: space-between;
            align-items: baseline;
            gap: 0.5rem;
        }

        .gear-name {
            color: #3a6e4a;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        /* Quick-stats flow as one wrapping unit below the title, instead
           of being split into separate left/right halves. */
        .gear-meta {
            color: var(--muted-color);
            font-size: 0.82rem;
            margin: 0.1rem 0 0 0;
        }

        .gear-carrying {
            font-size: 0.78rem;
            color: var(--muted-color);
            white-space: nowrap;
        }

        .gear-carrying input[type='checkbox'] {
            vertical-align: middle;
            margin-left: 3px;
        }

        /* Inline label within quick-stats */
        .glabel {
            font-weight: 600;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 2px;
        }

        /* Bullet separator between quick-stat items */
        .gsep {
            color: #aaa;
            margin: 0 5px;
        }

        /* Description line */
        .gear-desc {
            font-size: 0.82rem;
            color: #444;
            margin: 0.15rem 0 0 0;
        }


/* Inner table that holds the AC columns */
        table.whit-inner {
            border-collapse: collapse;
            font-size: 0.75rem;
            width: 100%;
        }

        td.whit-cond-label, th.whit-cond-label {
            font-size: 0.7rem;
            font-weight: 600;
            color: #555;
            white-space: nowrap;
            padding: 2px 5px;
            text-align: right;
            border: none;
        }

        th.whit-ac {
            color: #3a2c1c;
            font-weight: 700;
            text-align: center;
            padding: 2px 5px;
            border: 1px solid #5a4030;
            white-space: nowrap;
            min-width: 2.4em;
            font-size: 0.72rem;
            letter-spacing: 0.03em;
        }

        td.whit-pct {
            text-align: center;
            padding: 2px 5px;
            border: 1px solid #ddd;
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
        }

        /* Colour-code the probability cells: green → yellow → red */
        td.whit-pct[data-pct="100"],
        td.whit-pct[data-pct="95"],
        td.whit-pct[data-pct="90"],
        td.whit-pct[data-pct="85"],
        td.whit-pct[data-pct="80"] {
            color: #155724;
            font-weight: 600;
        }

        td.whit-pct[data-pct="75"],
        td.whit-pct[data-pct="70"],
        td.whit-pct[data-pct="65"],
        td.whit-pct[data-pct="60"] {
            color: #856404;
            font-weight: 600;
        }

        td.whit-pct[data-pct="55"],
        td.whit-pct[data-pct="50"],
        td.whit-pct[data-pct="45"],
        td.whit-pct[data-pct="40"] {
            color: #b35900;
            font-weight: 600;
        }

        td.whit-pct[data-pct="35"],
        td.whit-pct[data-pct="30"],
        td.whit-pct[data-pct="25"],
        td.whit-pct[data-pct="20"],
        td.whit-pct[data-pct="15"],
        td.whit-pct[data-pct="10"],
        td.whit-pct[data-pct="5"],
        td.whit-pct[data-pct="0"] {
            color: #b02a37;
            font-weight: 600;
        }

        /* ── Spell save DC fail-probability table ────────────────────────── */
        table.dc-fail-table {
            border-collapse: collapse;
            font-size: 0.75rem;
            margin: 0 0 0.75rem 0;
        }

        table.dc-fail-table th.dc-fail-dc-col {
            color: #3a2c1c;
            font-weight: 700;
            font-size: 0.72rem;
            text-align: left;
            vertical-align: middle;
            padding: 2px 8px;
            border: 1px solid #5a4030;
            white-space: nowrap;
            letter-spacing: 0.03em;
        }

        /* Condition sub-label (Normal/Adv./Disadv.) under a merged bonus cell */
        table.dc-fail-table th.dc-fail-cond-col {
            color: var(--muted-color);
            font-weight: 600;
            font-style: italic;
            font-size: 0.68rem;
            text-align: left;
            padding: 2px 8px;
            border: 1px solid #ddd;
            white-space: nowrap;
        }

        /* Spell school colors — preserved in print */
        span[style*="color:"] {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
        }

        /* Spell preparation checkbox */
        .spell-prep-checkbox {
            display: inline-block;
            width: 1.2em;
            height: 1.2em;
            border: 1.5px solid #3a5a7a;
            box-sizing: border-box;
            border-radius: 2px;
            vertical-align: middle;
            margin-right: 0.3em;
        }

        /* ── Spellcasting headline: Ability / DC / Attack stat tiles ────── */
        .spell-headline {
            max-width: 100%;
            margin: 0.4rem 0 0.9rem 0;
        }

        .spell-headline-group {
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
            max-width: none;
            margin: 0 0 0.5rem 0;
            padding: 0;
        }

        .spell-stat-tile {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.1rem;
            min-width: 5em;
            max-width: none;
            margin: 0;
            padding: 0.25rem 0.6rem;
            border: 1px solid #b89060;
            border-radius: 4px;
        }

        .spell-stat-label {
            font-size: 0.6rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #6a5636;
            white-space: nowrap;
        }

        .spell-stat-value {
            font-size: 1.15rem;
            font-weight: 700;
            color: #3a2c1c;
            line-height: 1.15;
        }

        .spell-stat-value.spell-stat-ability {
            font-size: 1rem;
        }

        /* Probability tables are reference material, not the headline stat */
        .spell-tables-secondary {
            max-width: 100%;
            margin: 0 0 0.75rem 0;
        }

        .spell-tables-secondary .spell-tables-caption {
            max-width: none;
            margin: 0 0 0.25rem 0;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted-color);
        }

        .spell-tables-secondary table.dc-fail-table {
            opacity: 0.85;
        }

        /* ── Overview: HP/AC/Initiative/Speed/Prof. tiles + detail chips ────
           Table-free by design. Stats glanced at constantly in play (HP
           above all) get large tiles; everything else the player already
           knows (class, proficiencies, languages...) is a compact chip. */
        .overview-section {
            margin: 0.5rem 0 0.75rem 0;
        }

        .overview-tiles {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-end;
            gap: 0.6rem;
            margin: 0 0 0.5rem 0;
        }

        .stat-tile {
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.1rem;
            min-width: 4.2em;
            padding: 0.3rem 0.7rem;
            border: 1px solid #b89060;
            border-radius: 6px;
        }

        .stat-tile-label {
            font-size: 0.62rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #6a5636;
            white-space: nowrap;
        }

        .stat-tile-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #3a2c1c;
            line-height: 1.2;
            white-space: nowrap;
        }

        .stat-tile-sub {
            font-size: 0.62rem;
            color: #7a6a50;
            white-space: nowrap;
        }

        /* HP is checked constantly during play — give it outsized emphasis */
        .stat-tile-hero {
            min-width: 5.5em;
            padding: 0.4rem 1rem;
            border-width: 2px;
            border-color: #9a3a3a;
        }

        .stat-tile-hero .stat-tile-value {
            font-size: 2.1rem;
            color: #7a2020;
        }

        /* Class-resource tiles (e.g. Martial Arts die, Focus Points) - a
           class's signature numbers, called out like HP but in their own
           accent color so they don't compete with HP for urgency. Smaller
           than the overview tiles since these sit inside a feature card
           rather than at the top of the sheet. */
        .stat-tile-resource {
            min-width: 3em;
            padding: 0.2rem 0.5rem;
            border-width: 2px;
            border-color: #4a7a4a;
        }

        .stat-tile-resource .stat-tile-label {
            font-size: 0.56rem;
        }

        .stat-tile-resource .stat-tile-value {
            font-size: 1rem;
            color: #2a5a2a;
        }

        .overview-details {
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem 1.2rem;
            font-size: 0.8rem;
            padding: 0.4rem 0.6rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
        }

        .od-label {
            font-weight: 600;
            color: #3a2c1c;
            margin-right: 0.25rem;
        }

        /* Wallet (left) / carrying capacity (right) header row above the
           item cards - a two-sided layout instead of one flat chip list. */
        .wallet-carry-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 0.4rem 1.2rem;
            font-size: 0.88rem;
            margin: 0 0 0.4rem 0;
        }

        /* Starting Gold (computed) above Current Gold (blank line for the
           player to pen in as it changes during play). */
        .wallet-block {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.2rem;
        }

        .carrying-block {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.2rem;
        }

        /* Per-source slot pips - smaller and right-aligned so several
           carrying-capacity sources stack compactly instead of sprawling
           into wide chips. */
        .carrying-source {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.82rem;
            color: var(--muted-color);
        }

        .cs-label {
            white-space: nowrap;
        }

        .carrying-source .slot-box {
            width: 0.85em;
            height: 0.85em;
        }

        .carrying-source .slot-box-group {
            gap: 0.22em;
            flex-wrap: wrap;
            justify-content: flex-end;
            max-width: 10em;
        }

        .xp-blank {
            display: inline-block;
            min-width: 4rem;
            height: 1.2em;
            border-bottom: 1px solid #999;
        }

        /* ── Blank fill-in lines (blank character template) ─────────────────
           Same idea as .xp-blank - an underline instead of a value, for a
           printable sheet meant to be filled out by hand. Sized variants
           for the different field widths a blank template needs. An empty
           element with only a border-bottom has no content to give it
           height, so it collapses to a hairline with nothing to write in -
           an explicit height keeps room above the line. */
        .blank-fill {
            display: inline-block;
            min-width: 4rem;
            height: 1.2em;
            border-bottom: 1px solid #999;
        }

        .blank-fill-sm {
            min-width: 2rem;
        }

        .blank-fill-lg {
            min-width: 8rem;
        }

        .blank-fill-xl {
            min-width: 14rem;
        }

        /* ── Status Section (Inspiration, Death Saves, Conditions) ──────────
           Pen-fillable, not interactive — the sheet is meant to be printed
           and marked by hand, so these reuse the .pen-box square (same idea
           as .slot-box for spell slots) instead of real form controls. Chips
           wrap freely so the row packs to fit whatever width is available. */
        .status-section {
            margin: 0.5rem 0 0.75rem 0;
            padding: 0.5rem 0.6rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
        }

        .status-row {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.4rem 1.5rem;
            padding-bottom: 0.45rem;
            margin-bottom: 0.45rem;
            border-bottom: 1px solid #ddd0b8;
        }

        .conditions-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem 0.9rem;
        }

        .status-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.85rem;
            white-space: nowrap;
        }

        .status-chip-inspiration {
            font-weight: 600;
            color: #3a2c1c;
        }

        .status-chip-label {
            font-weight: 600;
            font-size: 0.8rem;
            color: #3a2c1c;
            margin-right: 0.1rem;
        }

        .pen-box {
            display: inline-block;
            width: 0.85em;
            height: 0.85em;
            border: 1px solid currentColor;
            box-sizing: border-box;
            border-radius: 0.15em;
            vertical-align: middle;
            flex-shrink: 0;
        }

        /* Current-HP blank on the HP tile: an underline (same treatment as
           .blank-fill) rather than a pen-box square, since HP values can
           run to two or three digits. */
        .hp-blank {
            display: inline-block;
            width: 1.4em;
            height: 1.2em;
            border-bottom: 1px solid #999;
        }

        .hp-slash {
            font-weight: 400;
        }

        /* ── Spell Concentration Checkbox ────────────────────────────────── */
        .spell-concentration-checkbox {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            margin-left: 0.4rem;
            vertical-align: middle;
        }

        .spell-concentration-checkbox input[type='checkbox'] {
            width: 1em;
            height: 1em;
            cursor: pointer;
            vertical-align: middle;
        }
        """
