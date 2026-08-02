"""Generates a single HTML page listing every spell known to SpellFactory.

Spells are grouped by level (Cantrips first, then Level 1, 2, ...) and sorted
alphabetically within each level. Run directly
(`python Spells/SpellCompendiumGenerator.py`) to regenerate the output file.
"""

import sys
from itertools import groupby
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from CharacterContent.Spells.SpellFactory import SpellFactory
from CharacterContent.Spells.SpellFactory.Writer import SPELL_CARD_CSS
from Utils import Html

OUTPUT_HTML = "CharacterContent/Spells/AllSpells.html"


def _get_css_style() -> str:
    # Page-specific CSS: font imports and layout (rendered before SPELL_CARD_CSS)
    page_css = """@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

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

    /* Two-column layout for spell cards on wide screens */
    .spells {
        max-width: 100%;
        column-count: 2;
        column-gap: 1rem;
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
    }"""

    # Page-specific overrides of SPELL_CARD_CSS rules: rendered *after*
    # SPELL_CARD_CSS so they win the cascade instead of being silently
    # shadowed by the shared card definitions.
    page_overrides_css = """h3.spell-level-header {
        column-span: all;
        margin: 1.2rem 0 0.3rem 0;
    }

    /* Spell cards avoid column breaks */
    table.spell-card {
        break-inside: avoid;
    }"""

    return Html.render_style_block(page_css, SPELL_CARD_CSS, page_overrides_css)


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
