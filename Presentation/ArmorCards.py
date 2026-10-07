from typing import Optional, TextIO

import Core.Definitions as Definitions
from Presentation import Html

from CharacterContent.Items.Armor.Base import AbstractArmor

ARMOR_CARD_CSS = """/* ── Armor entries ────────────────────────────────────────────── */
        .armors {
            max-width: 100%;
        }

        /* Each armor, stacked without an outer box */
        .armor-entry {
            font-size: 0.85rem;
            padding: 0.4rem 0;
            max-width: none;
            break-inside: avoid;
            -webkit-column-break-inside: avoid;
        }

        /* Separator line between consecutive armor pieces */
        .armor-entry + .armor-entry {
            border-top: 1px solid #c8d4e0;
        }

        /* Armor name */
        .armor-name {
            display: block;
            color: #3a6a8a;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin: 0 0 0.2rem 0;
        }

        /* AC - one labelled line under the meta line, like a weapon's
           Attack / Damage lines */
        .armor-ac-line {
            display: flex;
            align-items: baseline;
            gap: 0.4rem;
            font-size: 0.82rem;
            margin: 0.15rem 0 0 0;
        }

        /* Restrictions tag section (Strength requirement, Stealth) */
        .armor-tags {
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            gap: 0.3rem;
            font-size: 0.82rem;
            margin: 0.15rem 0 0 0;
        }

        .alabel-col {
            font-weight: 600;
            white-space: nowrap;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        /* Individual restriction chip */
        .atag {
            display: inline-block;
            border: 1px solid #c8ccd8;
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 0.78rem;
            margin-right: 4px;
            margin-bottom: 2px;
            white-space: nowrap;
        }

        .atag-worn {
            border-color: #9abb9a;
            color: #3a6e3a;
            font-weight: 600;
        }

        .atag-not-worn {
            border-color: #ccc;
            color: #999;
            font-style: italic;
        }

        .atag-warn {
            border-color: #d8a840;
            color: #9a6a00;
            font-weight: 600;
        }

        /* Additional description */
        .armor-addl {
            display: flex;
            gap: 0.5rem;
            font-size: 0.82rem;
            font-style: italic;
            margin: 0.1rem 0 0 0;
        }

        .aaddl-desc {
            color: #333;
        }

        """


def _reference_ac_formula(armor: AbstractArmor) -> str:
    if armor.is_shield:
        bonus = f"+{armor.ac_bonus}" if armor.ac_bonus else "+0"
        return f"{bonus} AC (worn with another armor)"
    if armor.ac_ability is None:
        formula = f"{armor.base_ac} AC (fixed)"
    else:
        formula = f"{armor.base_ac} + {armor.ac_ability.short_name.title()} Mod"
        if armor.armor_type == Definitions.ArmorType.MEDIUM:
            formula += " (max +2)"
    if armor.ac_bonus:
        formula += f" {armor.ac_bonus:+}"
    return formula


def write_armor_reference_card(
    armor: AbstractArmor, file: TextIO, name_tags: str = ""
) -> None:
    """Render a single armor/shield as a rules-reference card: its AC
    formula and any wear restrictions, with no character-specific bonuses
    resolved - no character to compute a Dexterity modifier or check a
    Strength score against. `name_tags` is extra chip HTML after the name
    (worn state, where it came from) for the character-sheet equipment
    ledger; standalone item sheets leave it empty."""
    file.write("<div class='armor-entry'>\n")

    attunement_tag = Html.attunement_tag(armor)
    Html.write_gear_header(
        file,
        f"<span class='armor-name'>{armor.name}{attunement_tag}{name_tags}</span>",
        Html.carrying_checkbox_id(armor.name),
        armor.slots,
    )

    # Same layout as every other item card: name, one meta line (leading
    # with the kind of armor in place of an "Armor" type label the section
    # heading already gives), then labelled lines.
    armor_type_label = armor.armor_type.value if armor.armor_type else "-"
    kind = armor_type_label if armor.is_shield else f"{armor_type_label} Armor"
    _, rarity, price = Html.item_type_rarity_price(armor)
    Html.write_gear_meta_line(file, kind, rarity, price)
    file.write(
        f"<div class='armor-ac-line'><span class='alabel-col'>AC</span>"
        f"{_reference_ac_formula(armor)}</div>\n"
    )

    if armor.strength_requirement is not None or armor.stealth_disadvantage:
        tags_html = ""
        if armor.strength_requirement is not None:
            tags_html += (
                f"<span class='atag atag-warn'>Str {armor.strength_requirement}+ "
                f"required (or Speed -10 ft)</span> "
            )
        if armor.stealth_disadvantage:
            tags_html += (
                "<span class='atag atag-warn'>Disadvantage on Stealth checks</span>"
            )
        file.write(
            f"<div class='armor-tags'>"
            f"<span class='alabel-col'>Restrictions</span>"
            f"<span>{tags_html.strip()}</span>"
            f"</div>\n"
        )

    if armor.description_text:
        desc_processed = Html.boxes_to_html(armor.description_text)
        desc_html = desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='armor-addl'>"
            f"<span class='alabel-col'>Notes</span>"
            f"<span class='aaddl-desc'>{desc_html}</span>"
            f"</div>\n"
        )

    file.write("</div>\n")


def write_armors_to_file(
    armors: list[AbstractArmor],
    file: TextIO,
    name_tags: Optional[list[str]] = None,
) -> None:
    """Character-independent armor section: renders each armor's AC
    formula and restrictions in place of a resolved AC number.
    `name_tags`, when given, holds each armor's extra name chips, in the
    same order as `armors`."""
    if not armors:
        return

    if name_tags is None:
        name_tags = [""] * len(armors)

    file.write("<div class='armors'>\n")
    file.write("<h3>Armor</h3>\n")

    for armor, tags in zip(armors, name_tags):
        write_armor_reference_card(armor, file, tags)

    file.write("</div>\n")
