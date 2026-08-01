from typing import TextIO
from Utils import DamageCalculator, StringUtils
from Core.Definitions import DiceRollCondition
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from .base import AbstractWeapon, UnarmedStrike
from .enums import WeaponsDamageTypes


_DAMAGE_TYPE_CSS_CLASS = {
    WeaponsDamageTypes.SLASHING: "wtag-dmg-slashing",
    WeaponsDamageTypes.PIERCING: "wtag-dmg-piercing",
    WeaponsDamageTypes.BLUDGEONING: "wtag-dmg-bludgeoning",
    WeaponsDamageTypes.ACID: "wtag-dmg-acid",
    WeaponsDamageTypes.COLD: "wtag-dmg-cold",
    WeaponsDamageTypes.FIRE: "wtag-dmg-fire",
    WeaponsDamageTypes.LIGHTNING: "wtag-dmg-lightning",
    WeaponsDamageTypes.THUNDER: "wtag-dmg-thunder",
    WeaponsDamageTypes.NECROTIC: "wtag-dmg-necrotic",
    WeaponsDamageTypes.RADIANT: "wtag-dmg-radiant",
    WeaponsDamageTypes.POISON: "wtag-dmg-poison",
    WeaponsDamageTypes.PSYCHIC: "wtag-dmg-psychic",
    WeaponsDamageTypes.FORCE: "wtag-dmg-force",
}


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
        _, damage_bonus_label = weapon._calculate_ability_modifier_bonus(character_stat_block)
    damage_roll_str = f"{weapon.damage_roll.value} {damage_bonus_int:+} ({damage_bonus_label})"

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
    file.write(f"<tr><th class='weapon-name' colspan='2'>{weapon.name}{wielded_tag}</th></tr>\n")

    # ── Quick-stats row ─────────────────────────────────────────────────────
    # Two cells: left = type/category info, right = roll info
    type_cell = (
        f"{weapon.weapon_type.value}"
        f"<span class='wsep'>·</span>"
        f"{proficient_label}"
    )
    damage_type_class = _DAMAGE_TYPE_CSS_CLASS.get(weapon.damage_type, "")
    damage_type_tag = f" <span class='wtag {damage_type_class}'>{weapon.damage_type.value}</span>"
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
        hit_probs = weapon.calculate_hit_probabilities(character_stat_block, condition=cond)
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
        prop_desc_processed = StringUtils.boxes_to_html(prop.description)
        prop_desc_html = prop_desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-prop-row'>"
            f"<td class='wprop-label'>{prop.value}</td>"
            f"<td class='wprop-desc'>{prop_desc_html}</td>"
            f"</tr>\n"
        )

    # ── Mastery description (only if the player has mastery) ────────────────
    if weapon.mastery and weapon.player_has_mastery:
        mastery_desc_processed = StringUtils.boxes_to_html(weapon.mastery.description)
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
        desc_processed = StringUtils.boxes_to_html(weapon.description_text)
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
