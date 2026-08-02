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

WEAPON_CARD_CSS = """/* ── Weapon cards ─────────────────────────────────────────────── */
        .weapons {
            max-width: 100%;
        }

        /* Gap between consecutive weapon cards */
        .weapon-gap {
            display: none;
        }

        /* Each weapon is its own bordered card table */
        table.weapon-card {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            border: 2px solid #d4a0a0;
            border-radius: 4px;
            margin: 0 0 8px 0;
            table-layout: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }

        table.weapon-card td,
        table.weapon-card th {
            border: 1px solid var(--border-color);
            padding: 3px 7px;
            vertical-align: top;
        }

        /* Weapon name — full-width header row */
        .weapon-name {
            color: #8a4a4a;
            font-size: 1rem;
            font-weight: 700;
            text-align: left;
            letter-spacing: 0.02em;
            padding: 4px 7px;
            border-bottom: 2px solid #a06060;
        }

        /* Quick-stats row — two cells side by side */
        tr.weapon-quickstats td {
            font-size: 0.82rem;
            white-space: normal;
            padding: 3px 7px;
        }

        .wqs-left {
            width: 40%;
        }

        .wqs-right {
            width: 60%;
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

        /* Properties tag row */
        tr.weapon-tags-row td {
            padding: 3px 7px;
            font-size: 0.82rem;
        }

        .wlabel-col {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .wtags-cell {
            padding: 3px 7px;
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

        /* Per-property description rows */
        tr.weapon-prop-row td {
            font-size: 0.8rem;
            padding: 2px 7px;
        }

        .wprop-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: var(--muted-color);
        }

        .wprop-desc {
            color: #444;
        }

        /* Mastery description row */
        tr.weapon-mastery-row td {
            font-size: 0.8rem;
            padding: 2px 7px;
        }

        .wmastery-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: #3a6e3a;
        }

        .wmastery-desc {
            color: #3a3a3a;
        }

        /* Additional description row */
        tr.weapon-addl-row td {
            font-size: 0.82rem;
            padding: 3px 7px;
            font-style: italic;
        }

        .waddl-desc {
            color: #333;
        }

        
/* ── Weapon hit-probability row ──────────────────────────────────── */
        tr.weapon-hit-row td {
            padding: 3px 7px;
            vertical-align: middle;
        }

        """


def _write_single_weapon(
    weapon: AbstractWeapon,
    character_stat_block: CharacterStatBlock,
    file: TextIO,
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

    file.write("<table class='weapon-card'>\n")

    # ── Weapon name header ──────────────────────────────────────────────────
    wielded_tag = ""
    if not isinstance(weapon, UnarmedStrike):
        if weapon.is_wearing:
            wielded_tag = " <span class='wtag wtag-worn'>Wielded</span>"
        else:
            wielded_tag = " <span class='wtag wtag-not-worn'>Not wielded</span>"
    file.write(
        f"<tr><th class='weapon-name' colspan='2'>{weapon.name}{wielded_tag}</th></tr>\n"
    )

    # ── Quick-stats row ─────────────────────────────────────────────────────
    # Two cells: left = type/category info, right = roll info
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
        f"<tr class='weapon-quickstats'>"
        f"<td class='wqs-left'>{type_cell}</td>"
        f"<td class='wqs-right'>{roll_cell}</td>"
        f"</tr>\n"
    )

    # ── Hit probability row ─────────────────────────────────────────────────
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
        f"<tr class='weapon-hit-row'>"
        f"<td class='wlabel-col'>Hit % by AC</td>"
        f"<td class='whit-cell'>{inner_table}</td>"
        f"</tr>\n"
    )

    # ── Properties row ──────────────────────────────────────────────────────
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
            f"<tr class='weapon-tags-row'>"
            f"<td class='wlabel-col'>Properties</td>"
            f"<td class='wtags-cell'>{tags_html.strip()}</td>"
            f"</tr>\n"
        )

    # ── Per-property descriptions ────────────────────────────────────────────
    for prop in weapon.properties:
        prop_desc_processed = Html.boxes_to_html(prop.description)
        prop_desc_html = prop_desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-prop-row'>"
            f"<td class='wprop-label'>{prop.value}</td>"
            f"<td class='wprop-desc'>{prop_desc_html}</td>"
            f"</tr>\n"
        )

    # ── Mastery description (only if the player has mastery) ────────────────
    if weapon.mastery and weapon.player_has_mastery:
        mastery_desc_processed = Html.boxes_to_html(weapon.mastery.description)
        mastery_desc_html = mastery_desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-mastery-row'>"
            f"<td class='wmastery-label'>Mastery — {weapon.mastery.value}</td>"
            f"<td class='wmastery-desc'>{mastery_desc_html}</td>"
            f"</tr>\n"
        )

    # ── Additional description ───────────────────────────────────────────────
    if weapon.description_text:
        # Replace newlines with <br> for HTML display
        desc_processed = Html.boxes_to_html(weapon.description_text)
        desc_html = desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-addl-row'>"
            f"<td class='wlabel-col'>Notes</td>"
            f"<td class='waddl-desc'>{desc_html}</td>"
            f"</tr>\n"
        )

    file.write("</table>\n")


def write_weapons_to_file(
    weapons: list[AbstractWeapon],
    character_stat_block: CharacterStatBlock,
    file: TextIO,
):
    if not weapons:
        return

    file.write("<div class='weapons'>\n")
    file.write("<h2>Weapons</h2>\n")

    for i, weapon in enumerate(weapons):
        if i > 0:
            file.write("<div class='weapon-gap'></div>\n")
        _write_single_weapon(weapon, character_stat_block, file)

    file.write("</div>\n")
