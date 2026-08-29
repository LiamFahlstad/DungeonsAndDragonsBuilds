from typing import TextIO

from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import DamageCalculator, Html

from .Base import AbstractWeapon, UnarmedStrike
from .Enums import WeaponDamageTypes

_DAMAGE_TYPE_CSS_CLASS = {
    WeaponDamageTypes.SLASHING: "wtag-dmg-slashing",
    WeaponDamageTypes.PIERCING: "wtag-dmg-piercing",
    WeaponDamageTypes.BLUDGEONING: "wtag-dmg-bludgeoning",
    WeaponDamageTypes.ACID: "wtag-dmg-acid",
    WeaponDamageTypes.COLD: "wtag-dmg-cold",
    WeaponDamageTypes.FIRE: "wtag-dmg-fire",
    WeaponDamageTypes.LIGHTNING: "wtag-dmg-lightning",
    WeaponDamageTypes.THUNDER: "wtag-dmg-thunder",
    WeaponDamageTypes.NECROTIC: "wtag-dmg-necrotic",
    WeaponDamageTypes.RADIANT: "wtag-dmg-radiant",
    WeaponDamageTypes.POISON: "wtag-dmg-poison",
    WeaponDamageTypes.PSYCHIC: "wtag-dmg-psychic",
    WeaponDamageTypes.FORCE: "wtag-dmg-force",
}

WEAPON_CARD_CSS = """/* ── Weapon entries ───────────────────────────────────────────── */
        .weapons {
            max-width: 100%;
        }

        /* Each weapon, stacked without an outer box */
        .weapon-entry {
            font-size: 0.85rem;
            padding: 0.4rem 0;
            max-width: none;
            break-inside: avoid;
            -webkit-column-break-inside: avoid;
        }

        /* Separator line between consecutive weapons */
        .weapon-entry + .weapon-entry {
            border-top: 2px solid #a06060;
        }

        /* Weapon name */
        .weapon-name {
            display: block;
            color: #8a4a4a;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin: 0 0 0.2rem 0;
        }

        /* Quick-stats — two flexible columns, wrapping if the page is narrow */
        .weapon-quickstats {
            display: flex;
            flex-wrap: wrap;
            gap: 0.15rem 1.2rem;
            font-size: 0.82rem;
            margin: 0 0 0.2rem 0;
        }

        .wqs-left {
            flex: 1 1 35%;
        }

        .wqs-right {
            flex: 1 1 55%;
        }

        /* Inline label within quick-stats */
        .wlabel {
            font-weight: 600;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 2px;
        }

        /* Bullet separator between quick-stat items */
        .wsep {
            color: #aaa;
            margin: 0 5px;
        }

        /* Properties tag section */
        .weapon-tags {
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            gap: 0.3rem;
            font-size: 0.82rem;
            margin: 0.15rem 0 0 0;
        }

        .wlabel-col {
            font-weight: 600;
            white-space: nowrap;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        /* Individual property/tag chips */
        .wtag {
            display: inline-block;
            border: 1px solid #c8ccd8;
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 0.78rem;
            margin-right: 4px;
            margin-bottom: 2px;
            white-space: nowrap;
        }

        /* Mastery chip — active (player has it) */
        .wtag-mastery {
            border-color: #9abb9a;
            color: #3a6e3a;
            font-weight: 600;
        }

        /* Mastery chip — inactive (weapon has it but player doesn't) */
        .wtag-mastery-inactive {
            border-color: #ccc;
            color: #999;
            font-style: italic;
        }

        /* Wearable item chip — currently worn */
        .wtag-worn {
            border-color: #9abb9a;
            color: #3a6e3a;
            font-weight: 600;
        }

        /* Wearable item chip — carried but not worn */
        .wtag-not-worn {
            border-color: #ccc;
            color: #999;
            font-style: italic;
        }

        /* Damage type chip, next to the Damage roll — one color per type */
        .wtag-dmg-slashing, .wtag-dmg-piercing, .wtag-dmg-bludgeoning {
            border-color: #b0a89a;
            color: #6a5f4e;
            font-weight: 600;
        }

        .wtag-dmg-acid {
            border-color: #9ab04a;
            color: #5c7024;
            font-weight: 600;
        }

        .wtag-dmg-cold {
            border-color: #7ab0d8;
            color: #2a6a9a;
            font-weight: 600;
        }

        .wtag-dmg-fire {
            border-color: #e0955a;
            color: #b0501a;
            font-weight: 600;
        }

        .wtag-dmg-lightning {
            border-color: #c8a828;
            color: #8a6a00;
            font-weight: 600;
        }

        .wtag-dmg-thunder {
            border-color: #8a9ab8;
            color: #445a80;
            font-weight: 600;
        }

        .wtag-dmg-necrotic {
            border-color: #8a5aa0;
            color: #4a2a5a;
            font-weight: 600;
        }

        .wtag-dmg-radiant {
            border-color: #d8b840;
            color: #9a7a00;
            font-weight: 600;
        }

        .wtag-dmg-poison {
            border-color: #5a9a5a;
            color: #2a5a2a;
            font-weight: 600;
        }

        .wtag-dmg-psychic {
            border-color: #d060a8;
            color: #a0206e;
            font-weight: 600;
        }

        .wtag-dmg-force {
            border-color: #8a7ad8;
            color: #5a44b0;
            font-weight: 600;
        }

        /* Per-property description */
        .weapon-prop {
            display: flex;
            gap: 0.5rem;
            font-size: 0.8rem;
            margin: 0.1rem 0 0 0;
        }

        .wprop-label {
            font-weight: 600;
            white-space: nowrap;
            flex-shrink: 0;
            color: var(--muted-color);
        }

        .wprop-desc {
            color: #444;
        }

        /* Mastery description */
        .weapon-mastery {
            display: flex;
            gap: 0.5rem;
            font-size: 0.8rem;
            margin: 0.1rem 0 0 0;
        }

        .wmastery-label {
            font-weight: 600;
            white-space: nowrap;
            flex-shrink: 0;
            color: #3a6e3a;
        }

        .wmastery-desc {
            color: #3a3a3a;
        }

        /* Additional description */
        .weapon-addl {
            display: flex;
            gap: 0.5rem;
            font-size: 0.82rem;
            font-style: italic;
            margin: 0.1rem 0 0 0;
        }

        .waddl-desc {
            color: #333;
        }


/* ── Weapon hit-probability ──────────────────────────────────────── */
        .weapon-hit {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0.2rem 0 0 0;
        }

        """


def _write_single_weapon(
    weapon: AbstractWeapon,
    character_stat_block: CharacterStatBlock,
    file: TextIO,
    include_probability_tables: bool = False,
):
    attack_bonus_int = weapon.calculate_total_attack_roll_bonus_int(
        character_stat_block
    )
    attack_bonus_str = f"{attack_bonus_int:+}"

    damage_bonus_int = weapon.calculate_damage_bonus_int(character_stat_block)
    if weapon._damage_bonus_override is not None:
        damage_bonus_label = "fixed"
    else:
        _, damage_bonus_label = weapon._calculate_ability_modifier_bonus(
            character_stat_block
        )
    damage_roll_str = (
        f"{weapon.damage_roll.value} {damage_bonus_int:+} ({damage_bonus_label})"
    )

    # Add extra damage if present
    if weapon.extra_damage:
        extra_damages = " + ".join(ed.format_damage() for ed in weapon.extra_damage)
        damage_roll_str += f" + {extra_damages}"

    proficient_label = "Proficient" if weapon.player_is_proficient else "Not proficient"

    mastery_label = ""
    if weapon.mastery:
        mastery_label = weapon.mastery.value
        if weapon.player_has_mastery:
            mastery_label += " ✓"

    file.write("<div class='weapon-entry'>\n")

    # ── Weapon name ──────────────────────────────────────────────────────────
    wielded_tag = ""
    if not isinstance(weapon, UnarmedStrike):
        if weapon.is_wearing:
            wielded_tag = " <span class='wtag wtag-worn'>Wielded</span>"
        else:
            wielded_tag = " <span class='wtag wtag-not-worn'>Not wielded</span>"
    file.write(f"<span class='weapon-name'>{weapon.name}{wielded_tag}</span>\n")

    # ── Quick-stats ──────────────────────────────────────────────────────────
    # Left = type/category info, right = roll info
    type_cell = (
        f"{weapon.weapon_type.value}"
        f"<span class='wsep'>·</span>"
        f"{proficient_label}"
    )
    damage_type_class = _DAMAGE_TYPE_CSS_CLASS.get(weapon.damage_type, "")
    damage_type_tag = (
        f" <span class='wtag {damage_type_class}'>{weapon.damage_type.value}</span>"
    )
    roll_cell = (
        f"<span class='wlabel'>Attack</span> 1d20 {attack_bonus_str}"
        f"<span class='wsep'>·</span>"
        f"<span class='wlabel'>Damage</span> {damage_roll_str}{damage_type_tag}"
    )
    file.write(
        f"<div class='weapon-quickstats'>"
        f"<span class='wqs-left'>{type_cell}</span>"
        f"<span class='wqs-right'>{roll_cell}</span>"
        f"</div>\n"
    )

    # ── Hit probability ──────────────────────────────────────────────────────
    if include_probability_tables:
        conditions = [
            ("Normal", DamageCalculator.DiceRollCondition.NEUTRAL),
            ("Adv.", DamageCalculator.DiceRollCondition.ADVANTAGE),
            ("Disadv.", DamageCalculator.DiceRollCondition.DISADVANTAGE),
        ]
        hit_probs_normal = weapon.calculate_hit_probabilities(character_stat_block)
        inner_header = "".join(
            f"<th class='whit-ac'>{ac}</th>" for ac, _ in hit_probs_normal
        )
        inner_rows = ""
        for label, cond in conditions:
            hit_probs = weapon.calculate_hit_probabilities(
                character_stat_block, condition=cond
            )
            cells = "".join(
                f"<td class='whit-pct' data-pct='{round(round(prob * 100) / 5) * 5}'>{prob * 100:.0f}%</td>"
                for _, prob in hit_probs
            )
            inner_rows += f"<tr><td class='whit-cond-label'>{label}</td>{cells}</tr>"
        inner_table = (
            f"<table class='whit-inner'>"
            f"<tr><th class='whit-cond-label'></th>{inner_header}</tr>"
            f"{inner_rows}"
            f"</table>"
        )
        file.write(
            f"<div class='weapon-hit'>"
            f"<span class='wlabel-col'>Hit % by AC</span>"
            f"<span class='whit-cell'>{inner_table}</span>"
            f"</div>\n"
        )

    # ── Properties ───────────────────────────────────────────────────────────
    if weapon.properties or mastery_label:
        tags_html = ""
        for prop in weapon.properties:
            tags_html += f"<span class='wtag'>{prop.value}</span> "
        if mastery_label:
            mastery_cls = (
                "wtag wtag-mastery"
                if weapon.player_has_mastery
                else "wtag wtag-mastery-inactive"
            )
            tags_html += f"<span class='{mastery_cls}'>Mastery: {mastery_label}</span>"
        file.write(
            f"<div class='weapon-tags'>"
            f"<span class='wlabel-col'>Properties</span>"
            f"<span>{tags_html.strip()}</span>"
            f"</div>\n"
        )

    # ── Per-property descriptions ────────────────────────────────────────────
    for prop in weapon.properties:
        prop_desc_processed = Html.boxes_to_html(prop.description)
        prop_desc_html = prop_desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-prop'>"
            f"<span class='wprop-label'>{prop.value}</span>"
            f"<span class='wprop-desc'>{prop_desc_html}</span>"
            f"</div>\n"
        )

    # ── Mastery description (only if the player has mastery) ────────────────
    if weapon.mastery and weapon.player_has_mastery:
        mastery_desc_processed = Html.boxes_to_html(weapon.mastery.description)
        mastery_desc_html = mastery_desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-mastery'>"
            f"<span class='wmastery-label'>Mastery — {weapon.mastery.value}</span>"
            f"<span class='wmastery-desc'>{mastery_desc_html}</span>"
            f"</div>\n"
        )

    # ── Additional description ───────────────────────────────────────────────
    if weapon.description_text:
        # Replace newlines with <br> for HTML display
        desc_processed = Html.boxes_to_html(weapon.description_text)
        desc_html = desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-addl'>"
            f"<span class='wlabel-col'>Notes</span>"
            f"<span class='waddl-desc'>{desc_html}</span>"
            f"</div>\n"
        )

    file.write("</div>\n")


def write_weapons_to_file(
    weapons: list[AbstractWeapon],
    character_stat_block: CharacterStatBlock,
    file: TextIO,
    include_probability_tables: bool = False,
):
    if not weapons:
        return

    file.write("<div class='weapons'>\n")
    file.write("<h3>Weapon Attacks</h3>\n")

    for weapon in weapons:
        _write_single_weapon(
            weapon, character_stat_block, file, include_probability_tables
        )

    file.write("</div>\n")
