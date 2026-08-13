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


def boxes_to_html(description: str) -> str:
    def normalize_box_line(line: str) -> str:
        stripped = line.strip()
        if stripped.endswith("<br>"):
            stripped = stripped[:-4].rstrip()
        return stripped

    def box_count(line: str, token: str) -> int:
        parts = line.split()
        if parts and all(part == token for part in parts):
            return len(parts)
        return 0

    def parse_reset_label(line: str) -> str | None:
        """Return the reset label text if *line* is a reset sentinel, else None."""
        normalized = normalize_box_line(line)
        if normalized.startswith(RESET_PREFIX) and normalized.endswith(RESET_SUFFIX):
            return normalized[len(RESET_PREFIX) : -len(RESET_SUFFIX)]
        return None

    lines = description.split("\n")
    new_lines = []
    index = 0

    while index < len(lines):
        top_line = normalize_box_line(lines[index])
        top_count = box_count(top_line, "⬜")

        if top_count:
            boxes_html = '<span class="slot-box"></span>' * top_count

            # Peek at the next line to see if it carries a reset label.
            reset_label = None
            if index + 1 < len(lines):
                reset_label = parse_reset_label(lines[index + 1])

            if reset_label is not None:
                # Capitalize the reset label for proper sentence formatting
                capitalized_label = (
                    reset_label[0].upper() + reset_label[1:] if reset_label else ""
                )
                reset_html = (
                    f'<span class="slot-reset-label">{capitalized_label}.</span>'
                )
                new_lines.append(
                    '<div class="slot-box-group">'
                    + boxes_html
                    + "</div>"
                    + "\n"
                    + reset_html
                )
                index += 2  # consume both the box line and the reset sentinel
            else:
                new_lines.append('<div class="slot-box-group">' + boxes_html + "</div>")
                index += 1
            continue

        # Skip bare reset sentinel lines that appear without a preceding box line
        # (shouldn't normally happen, but guard against it).
        if parse_reset_label(lines[index]) is not None:
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


def write_slot_item_table(file: TextIO, title: str, rows: list[tuple[str, str, int]]):
    """Inventory table with slot cost, carry quantity, and left-behind tracking."""
    import re

    file.write("<table class='item-table'>\n")
    file.write("<tr>\n")
    file.write(f"<th class='item-title'>{title}</th>\n")
    file.write("<th class='item-title item-col-narrow'>Slots</th>\n")
    file.write("<th class='item-title item-col-carry'>Carry</th>\n")
    file.write("<th class='item-title item-col-leftbehind'>Left Behind</th>\n")
    file.write("</tr>\n")

    for label, description, slots in rows:
        plain_label = re.sub(r"<span[^>]*>.*?</span>", "", label)
        plain_label = re.sub(r"<[^>]*>", "", plain_label).strip()
        leftbehind_id = (
            plain_label.replace(" ", "_").replace("(", "").replace(")", "")
            + "_leftbehind"
        )
        file.write("<tr>\n")
        file.write(
            f"<td class='item-entry'><strong>{label}</strong><br/>{description}</td>\n"
        )
        file.write(f"<td style='text-align: center;'>{slots}</td>\n")
        file.write("<td></td>\n")
        file.write(
            f"<td class='item-leftbehind'><input type='checkbox' id='{leftbehind_id}_check' name='{leftbehind_id}_check'/></td>\n"
        )
        file.write("</tr>\n")

    file.write("</table>\n")


def write_slot_table(slots: dict[int, int], file: TextIO, reset_label: str):
    file.write("<table class='stat-table'>\n")
    file.write("<tr>")
    for level in slots:
        file.write(f"<th>Level {level}</th>")
    file.write("</tr>\n<tr>")
    for count in slots.values():
        boxes_html = (
            '<div class="slot-box-group">'
            + '<span class="slot-box"></span>' * count
            + "</div>"
        )
        file.write(f"<td>{boxes_html}</td>")
    file.write("</tr>\n</table>\n")
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

        .section-col table.stat-table {
            width: 100%;
        }

        /* Stat tables: general info, combat, abilities, skills, spell slots */
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

        /* Blank, hand-fillable XP column - widened to leave writing room */
        table.stat-table td.xp-cell {
            min-width: 4rem;
        }

        table.stat-table tr.st-proficient td {
            color: #2e6e3e;
        }

        table.stat-table tr.st-proficient td:first-child {
            font-weight: 700;
        }

        table.stat-table tr.st-expertise td {
            color: #8a6200;
        }

        table.stat-table tr.st-expertise td:first-child {
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
            border-bottom: 2px solid #6a9a7a !important;
        }

        .item-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
        }

        .item-value {
            width: auto;
        }

        /* Carrying capacity: one column of slot checkboxes per source */
        .capacity-table {
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0.25rem 0 0.5rem 0;
        }

        .capacity-table th,
        .capacity-table td {
            border: 1px solid var(--border-color);
            padding: 4px 8px;
            text-align: center;
            vertical-align: middle;
        }

        .capacity-table .slot-box-group {
            flex-wrap: wrap;
            max-width: 12em;
        }

        /* Item inventory rows: name + description, wraps normally */
        .item-entry strong {
            color: #3a6e4a;
        }

        .item-col-narrow {
            width: 3em;
            text-align: center;
        }

        .item-col-carry {
            width: 4.5em;
            text-align: center;
        }

        .item-col-leftbehind {
            width: 9em;
        }

        .item-leftbehind input[type='checkbox'] {
            vertical-align: middle;
        }

        /* Individual item rows separated by a line rather than a full border */
        .item-table tr:not(:first-child) td {
            border: none;
            border-bottom: 1px solid #a4c8b0;
            padding: 5px 7px;
        }

        .item-table tr:last-child td {
            border-bottom: none;
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
        """
