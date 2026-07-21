"""Generates a single HTML page listing every spell known to SpellFactory.

Spells are grouped by level (Cantrips first, then Level 1, 2, ...) and sorted
alphabetically within each level. Run directly
(`python Spells/GenerateSpellCompendium.py`) to regenerate the output file.
"""

import sys
from itertools import groupby
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Spells.SpellFactory import SpellFactory

OUTPUT_HTML = "Spells/AllSpells.html"


def _get_css_style() -> str:
    return """
    <style>
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

    .page {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 0.5rem;
    }

    h1 {
        color: #3a2c1c;
        border-bottom: 3px solid #9a7040;
        padding-bottom: 0.2em;
        margin: 0 0 1rem 0;
        font-size: 1.6rem;
        letter-spacing: 0.02em;
    }

    /* Level section header */
    h3.spell-level-header {
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #4a5568;
        margin: 1.2rem 0 0.3rem 0;
        padding: 0;
        border-bottom: 1px solid #c8ccd8;
    }

    /* Two-column layout for spell cards on wide screens */
    .spells {
        max-width: 100%;
        column-count: 2;
        column-gap: 1rem;
    }

    h3.spell-level-header {
        column-span: all;
    }

    /* Each spell is its own bordered card table */
    table.spell-card {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        border: 2px solid #a8c4d8;
        border-radius: 4px;
        margin: 0 0 8px 0;
        table-layout: auto;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        break-inside: avoid;
    }

    table.spell-card td,
    table.spell-card th {
        border: 1px solid var(--border-color);
        padding: 3px 7px;
        vertical-align: top;
    }

    table.spell-card tr {
        border-bottom: 1px solid #ddd;
    }

    table.spell-card tr:last-child {
        border-bottom: none;
    }

    /* Spell name — full-width header row */
    .spell-name {
        color: #3a5a7a;
        font-size: 1rem;
        font-weight: 700;
        text-align: left;
        letter-spacing: 0.02em;
        padding: 4px 7px;
        border-bottom: 2px solid #6888a8;
    }

    /* Quick-stats row — two cells side by side */
    tr.spell-quickstats td {
        font-size: 0.82rem;
        white-space: normal;
        padding: 3px 7px;
    }

    .sqs-left {
        width: 50%;
    }

    .sqs-right {
        width: 50%;
    }

    /* Inline label within quick-stats */
    .slabel {
        font-weight: 600;
        color: var(--muted-color);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-right: 2px;
    }

    /* Bullet separator between quick-stat items */
    .ssep {
        color: #aaa;
        margin: 0 5px;
    }

    /* Classes row */
    tr.spell-classes-row td {
        font-size: 0.78rem;
        padding: 3px 7px;
    }

    .sclass-chip {
        display: inline-block;
        background: #eef2f7;
        color: #3a5a7a;
        border-radius: 3px;
        padding: 1px 6px;
        margin: 1px 3px 1px 0;
        font-size: 0.78rem;
    }

    /* Description rows */
    tr.spell-desc-row td,
    tr.spell-higher-row td {
        font-size: 0.8rem;
        padding: 3px 7px;
    }

    .sdesc-text {
        color: #333;
    }

    /* Higher-level row gets a subtle accent */
    tr.spell-higher-row td {
        font-style: italic;
        color: #3a5a7a;
    }

    /* Concentration / ritual chips */
    .stag {
        display: inline-block;
        border-radius: 3px;
        padding: 1px 6px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-left: 5px;
        vertical-align: middle;
        white-space: nowrap;
    }

    .stag-concentration {
        border: 1px solid #c8a227;
        color: #7a5c00;
    }

    .stag-ritual {
        border: 1px solid #2a9d8f;
        color: #1a5f58;
    }

    @media print {
        body {
            padding: 0;
            font-size: 10pt;
        }

        .page {
            max-width: 100%;
        }

        .spells {
            column-count: 1;
        }
    }
    </style>
    """


def write_spell_compendium(output_path: str = OUTPUT_HTML):
    all_spells = sorted(SpellFactory.all_spells(), key=lambda s: (s.level, s.name))

    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path_obj, "w", encoding="utf-8") as file:
        file.write("<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
        file.write("<meta charset='utf-8'>\n")
        file.write("<title>Spell Compendium</title>\n")
        file.write(_get_css_style())
        file.write("</head>\n<body>\n<div class='page'>\n")
        file.write(f"<h1>Spell Compendium ({len(all_spells)} spells)</h1>\n")
        file.write("<div class='spells'>\n")

        for level, group in groupby(all_spells, key=lambda s: s.level):
            level_label = "Cantrips" if level == 0 else f"Level {level} Spells"
            file.write(f"<h3 class='spell-level-header'>{level_label}</h3>\n")
            for spell in group:
                spell.write_to_file(file, show_classes=True)

        file.write("</div>\n</div>\n</body>\n</html>\n")

    print(f"Wrote {len(all_spells)} spells to {output_path_obj}")


if __name__ == "__main__":
    write_spell_compendium()
