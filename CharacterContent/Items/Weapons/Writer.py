from typing import Optional, TextIO

from Core.Definitions import DiceRollCondition
from Model.Character import Character
from Utils import DamageCalculator, Html, ItemSheetSettings

from .Base import AbstractWeapon, BonusPart, UnarmedStrike
from Core.Weapons import WeaponDamageTypes, WeaponProperty

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
            border-top: 1px solid #e0c8c8;
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

        /* Attack / Damage - one labelled line each, under the meta line */
        .weapon-roll-line {
            display: flex;
            align-items: baseline;
            flex-wrap: wrap;
            gap: 0.4rem;
            font-size: 0.82rem;
            margin: 0.15rem 0 0 0;
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

        /* Attunement chip - shown next to the name on any item category
           (weapon, armor, wondrous, ...) that requires attunement, since
           the 3-item attunement limit matters regardless of category. */
        .wtag-attunement {
            border-color: #b89060;
            color: #8a6200;
            font-weight: 600;
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


def _format_bonus_breakdown(parts: list[BonusPart]) -> str:
    """'+ Dex Mod + Proficiency Bonus + 2 (Archery Fighting Style)': parts
    from the wielder's stats by name, flat bonuses as value and source."""
    terms = []
    for part in parts:
        if part.from_stats:
            terms.append(f"+ {part.label}")
        else:
            sign = "-" if part.value < 0 else "+"
            terms.append(f"{sign} {abs(part.value)} ({part.label})")
    return " ".join(terms)


def _write_single_weapon(
    weapon: AbstractWeapon,
    character: Character,
    file: TextIO,
    include_probability_tables: bool = False,
    has_mastery: bool = False,
    name_tags: str = "",
):
    """Render one weapon as a character-resolved attack card. `name_tags`
    is extra chip HTML after the name (where the weapon came from).
    Attack and damage show how the bonus is made up ("1d20 + Dex Mod +
    Proficiency Bonus") rather than the resolved numbers."""
    attack_bonus_str = _format_bonus_breakdown(
        weapon.get_attack_roll_breakdown(character)
    )
    damage_bonus_str = _format_bonus_breakdown(
        weapon.get_damage_roll_breakdown(character)
    )
    damage_roll_str = f"{weapon.damage_roll.value} {damage_bonus_str}"

    if weapon.extra_damage:
        extra_damages = " + ".join(ed.format_damage() for ed in weapon.extra_damage)
        damage_roll_str += f" + {extra_damages}"

    proficient_label = (
        "Proficient" if weapon.is_proficient(character) else "Not proficient"
    )

    mastery_label = ""
    if weapon.mastery:
        mastery_label = weapon.mastery.value
        if has_mastery:
            mastery_label += " ✓"

    file.write("<div class='weapon-entry'>\n")

    # Unarmed Strike isn't an item - nothing to carry, buy or sell - so it
    # gets an "Innate" chip, and no Carrying checkbox, cost or slots.
    is_innate = isinstance(weapon, UnarmedStrike)
    if is_innate:
        file.write(
            f"<div class='gear-header'><span class='weapon-name'>{weapon.name}"
            f" <span class='wtag'>Innate</span></span></div>\n"
        )
    else:
        Html.write_gear_header(
            file,
            f"<span class='weapon-name'>{weapon.name}{Html.attunement_tag(weapon)}"
            f"{name_tags}</span>",
            Html.carrying_checkbox_id(weapon.name),
            weapon.slots,
        )

    # Same layout as every other item card: name, then one meta line, then
    # labelled lines. The meta line leads with the kind of weapon and
    # proficiency in place of a "Weapon" type label the section heading
    # already gives.
    kind = f"{weapon.weapon_type.value}<span class='gsep'>·</span>{proficient_label}"
    if weapon.attack_roll_condition(character) == DiceRollCondition.DISADVANTAGE:
        kind += "<span class='gsep'>·</span>Attacks with Disadvantage (untrained armor)"
    if is_innate:
        file.write(
            f"<div class='gear-meta'><span class='glabel'>Type:</span> {kind}</div>\n"
        )
    else:
        _, rarity, price = Html.item_type_rarity_price(weapon)
        Html.write_gear_meta_line(file, kind, rarity, price)

    damage_type_class = _DAMAGE_TYPE_CSS_CLASS.get(weapon.damage_type, "")
    damage_type_tag = (
        f" <span class='wtag {damage_type_class}'>{weapon.damage_type.value}</span>"
    )
    file.write(
        f"<div class='weapon-roll-line'><span class='wlabel-col'>Attack</span>"
        f"1d20 {attack_bonus_str}</div>\n"
    )
    file.write(
        f"<div class='weapon-roll-line'><span class='wlabel-col'>Damage</span>"
        f"{damage_roll_str}{damage_type_tag}</div>\n"
    )

    if include_probability_tables:
        conditions = [
            ("Normal", DamageCalculator.DiceRollCondition.NEUTRAL),
            ("Adv.", DamageCalculator.DiceRollCondition.ADVANTAGE),
            ("Disadv.", DamageCalculator.DiceRollCondition.DISADVANTAGE),
        ]
        hit_probs_normal = weapon.calculate_hit_probabilities(character)
        inner_header = "".join(
            f"<th class='whit-ac'>{ac}</th>" for ac, _ in hit_probs_normal
        )
        inner_rows = ""
        for label, cond in conditions:
            hit_probs = weapon.calculate_hit_probabilities(character, condition=cond)
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

    if weapon.properties or mastery_label:
        tags_html = ""
        for prop in weapon.properties:
            tags_html += f"<span class='wtag'>{prop.value}</span> "
        if mastery_label:
            mastery_cls = (
                "wtag wtag-mastery" if has_mastery else "wtag wtag-mastery-inactive"
            )
            tags_html += f"<span class='{mastery_cls}'>Mastery: {mastery_label}</span>"
        file.write(
            f"<div class='weapon-tags'>"
            f"<span class='wlabel-col'>Properties</span>"
            f"<span>{tags_html.strip()}</span>"
            f"</div>\n"
        )

    for prop in weapon.properties:
        prop_desc_processed = Html.boxes_to_html(prop.description)
        prop_desc_html = prop_desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-prop'>"
            f"<span class='wprop-label'>{prop.value}</span>"
            f"<span class='wprop-desc'>{prop_desc_html}</span>"
            f"</div>\n"
        )

    if weapon.mastery and has_mastery:
        mastery_desc_processed = Html.boxes_to_html(weapon.mastery.description)
        mastery_desc_html = mastery_desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-mastery'>"
            f"<span class='wmastery-label'>Mastery — {weapon.mastery.value}</span>"
            f"<span class='wmastery-desc'>{mastery_desc_html}</span>"
            f"</div>\n"
        )

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
    character: Character,
    file: TextIO,
    include_probability_tables: bool = False,
    weapon_masteries: "list[AbstractWeapon] | None" = None,
    name_tags: Optional[list[str]] = None,
):
    """Weapons section of character-resolved attack cards. `name_tags`,
    when given, holds each weapon's extra name chips, in the same order as
    `weapons`."""
    if not weapons:
        return

    if name_tags is None:
        name_tags = [""] * len(weapons)

    file.write("<div class='weapons'>\n")
    file.write("<h3>Weapons</h3>\n")

    for weapon, tags in zip(weapons, name_tags):
        _write_single_weapon(
            weapon,
            character,
            file,
            include_probability_tables,
            has_mastery=weapon.has_mastery(weapon_masteries or []),
            name_tags=tags,
        )

    file.write("</div>\n")


def _reference_ability_label(weapon: AbstractWeapon) -> str:
    """Ability a wielder rolls with, without resolving it against any one
    character - the fixed override if set, "Str or Dex" for Finesse
    weapons (the wielder's choice), else the weapon's base ability."""
    if weapon._ability_override is not None:
        return weapon._ability_override.short_name.title()
    if WeaponProperty.FINESSE in weapon.properties:
        return "Str or Dex"
    return weapon.ability.short_name.title()


def _reference_attack_roll_formula(weapon: AbstractWeapon) -> str:
    if weapon._attack_roll_override is not None:
        return f"1d20 {weapon._attack_roll_override:+} (fixed)"
    formula = (
        f"1d20 + {_reference_ability_label(weapon)} Mod"
        f" + Proficiency Bonus (if proficient)"
    )
    for _, label in weapon.attack_roll_bonuses:
        # label is already pre-formatted as "<value> (<reason>)" by
        # AddAttackRollBonus.apply - the raw int isn't reformatted here.
        formula += f" + {label}"
    return formula


def _reference_damage_roll_formula(weapon: AbstractWeapon) -> str:
    if weapon._damage_bonus_override is not None:
        formula = (
            f"{weapon.damage_roll.value} {weapon._damage_bonus_override:+} (fixed)"
        )
    else:
        formula = f"{weapon.damage_roll.value} + {_reference_ability_label(weapon)} Mod"
        for _, label in weapon.damage_roll_bonuses:
            formula += f" + {label}"
    if weapon.extra_damage:
        extra = " + ".join(ed.format_damage() for ed in weapon.extra_damage)
        formula += f" + {extra}"
    return formula


def write_weapon_reference_card(weapon: AbstractWeapon, file: TextIO) -> None:
    """Render a single weapon as a rules-reference card: attack/damage
    roll formulas and properties, with no character-specific bonuses
    resolved - used by standalone item sheets, which have no character to
    compute an attack bonus or a proficiency status against."""
    file.write("<div class='weapon-entry'>\n")

    attunement_tag = Html.attunement_tag(weapon)
    Html.write_gear_header(
        file,
        f"<span class='weapon-name'>{weapon.name}{attunement_tag}</span>",
        Html.carrying_checkbox_id(weapon.name),
        weapon.slots,
    )

    # Same layout as the character-sheet weapon card: one meta line (kind
    # of weapon and the ability it rolls with, then rarity/cost/slots),
    # then one labelled line each for Attack and Damage.
    kind = (
        f"{weapon.weapon_type.value}"
        f"<span class='gsep'>·</span>{_reference_ability_label(weapon)}"
    )
    _, rarity, price = Html.item_type_rarity_price(weapon)
    Html.write_gear_meta_line(file, kind, rarity, price)

    damage_type_class = _DAMAGE_TYPE_CSS_CLASS.get(weapon.damage_type, "")
    damage_type_tag = (
        f" <span class='wtag {damage_type_class}'>{weapon.damage_type.value}</span>"
    )
    file.write(
        f"<div class='weapon-roll-line'><span class='wlabel-col'>Attack</span>"
        f"{_reference_attack_roll_formula(weapon)}</div>\n"
    )
    file.write(
        f"<div class='weapon-roll-line'><span class='wlabel-col'>Damage</span>"
        f"{_reference_damage_roll_formula(weapon)}{damage_type_tag}</div>\n"
    )

    visible_properties = [
        prop
        for prop in weapon.properties
        if prop != WeaponProperty.AMMUNITION or ItemSheetSettings.TRACK_AMMUNITION
    ]

    if visible_properties or weapon.mastery:
        tags_html = ""
        for prop in visible_properties:
            tags_html += f"<span class='wtag'>{prop.value}</span> "
        if weapon.mastery:
            tags_html += f"<span class='wtag wtag-mastery'>Mastery: {weapon.mastery.value}</span>"
        file.write(
            f"<div class='weapon-tags'>"
            f"<span class='wlabel-col'>Properties</span>"
            f"<span>{tags_html.strip()}</span>"
            f"</div>\n"
        )

    for prop in visible_properties:
        prop_desc_processed = Html.boxes_to_html(prop.description)
        prop_desc_html = prop_desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-prop'>"
            f"<span class='wprop-label'>{prop.value}</span>"
            f"<span class='wprop-desc'>{prop_desc_html}</span>"
            f"</div>\n"
        )

    if weapon.mastery:
        mastery_desc_processed = Html.boxes_to_html(weapon.mastery.description)
        mastery_desc_html = mastery_desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-mastery'>"
            f"<span class='wmastery-label'>Mastery — {weapon.mastery.value}</span>"
            f"<span class='wmastery-desc'>{mastery_desc_html}</span>"
            f"</div>\n"
        )

    if weapon.description_text:
        desc_processed = Html.boxes_to_html(weapon.description_text)
        desc_html = desc_processed.replace("\n", "<br>")
        file.write(
            f"<div class='weapon-addl'>"
            f"<span class='wlabel-col'>Notes</span>"
            f"<span class='waddl-desc'>{desc_html}</span>"
            f"</div>\n"
        )

    file.write("</div>\n")


def write_weapons_reference_to_file(
    weapons: list[AbstractWeapon], file: TextIO
) -> None:
    """Character-independent counterpart to write_weapons_to_file, for
    standalone item sheets that have no character to resolve attack/damage
    bonuses against - renders the roll formula (die + modifier + any fixed
    bonuses) in place of a resolved number."""
    if not weapons:
        return

    file.write("<div class='weapons'>\n")
    file.write("<h3>Weapons</h3>\n")

    for weapon in weapons:
        write_weapon_reference_card(weapon, file)

    file.write("</div>\n")
