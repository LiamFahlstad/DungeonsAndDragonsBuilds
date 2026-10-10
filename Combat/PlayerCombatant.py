"""A player character as the combat UI holds it.

The combat UI keeps every combatant - monster or player - as a dict of what it
shows and what changes during a fight (HP, conditions, ...).
combatant_from_character() builds a player's from their Character. The
Character itself rides along under "_stat_block", so anything the dict doesn't
hold is asked of it. Nothing here imports Qt, so it can be tested and
snapshotted (tests/test_combatant_snapshots.py).

Combat state (current HP, conditions, spent slots) lives in the dict, never
on the Character, which doesn't change. Replacing the dicts with a
combat-side object that holds a Character is a follow-up
(Notes/engine-simplification-plan.md, section 7).
"""

import Core.Definitions as Definitions
from CharacterContent.Spells.SpellFactory import SpellFactory
from Model.Character import Character
from Model.Content.Weapon import AbstractWeapon


def combatant_from_character(character: Character) -> dict:
    """The combat UI's dict for a player character. The battle statistics
    ("stats") are the UI's own and aren't included."""
    character = character.validate()
    hp = character.calculate_hit_points()

    # Pre-compute spell levels (display_name, level, Ability enum)
    spells_with_level = []
    spell_objects: dict[str, object] = {}
    for spell in character.spells:
        spell_name, ability, ruling = spell.name, spell.ability, spell.ruling
        display_name = getattr(spell_name, "value", str(spell_name))
        try:
            spell_obj = SpellFactory.create(spell_name, ability, ruling)
            spells_with_level.append((display_name, spell_obj.level, ability))
            spell_objects[display_name] = spell_obj
        except Exception:
            spells_with_level.append((display_name, 0, ability))

    return {
        "name": character.character_name,
        "create_name": character.character_name,
        "hp": hp,
        "max_hp": hp,
        "ac": _armor_class_text(character),
        "temp_hp": 0,
        "conditions": [],
        "visibility_states": [],
        "death_saves_fail": 0,
        "death_saves_success": 0,
        "spell_slots": character.spell_slots,
        "Ability Scores": {
            ability.short_name: character.get_ability_score(ability)
            for ability in Definitions.Ability
        },
        "Saving Throws": {
            ability.short_name: character.get_saving_throw_modifier(ability)
            for ability in Definitions.Ability
        },
        "_is_player": True,
        "_stat_block": character,
        "_weapons_objects": list(character.weapons),
        "_weapon_masteries": list(character.weapon_masteries),
        "class_levels": {
            cls.value: lvl for cls, lvl in character.level_per_class.items()
        },
        "subclass": character.character_subclass or "",
        "proficiency_bonus": character.get_proficiency_bonus(),
        "speed": character.calculate_speed(),
        "size": character.size.value,
        "spells_with_level": spells_with_level,
        "_spell_objects": spell_objects,
        "features": [feature.name for feature in character.features],
        "_feature_objects": list(character.features),
        "invocations": list(character.invocations),
    }


def _armor_class_text(character: Character) -> str:
    """The AC, and while wielding a Shield also the AC without it (worked
    out by the rules, not as "minus 2": a +1 Shield, or Unarmored Defense
    that the Shield turns off, change it by more)."""
    ac = character.calculate_armor_class()
    if any(armor.is_shield and armor.is_wearing for armor in character.armors):
        without = character.calculate_armor_class(ignore_shield=True)
        return f"{ac} (with Shield) and {without} (without Shield)"
    return f"{ac} (no Shield)"


def weapon_summary(weapon: AbstractWeapon, character: Character) -> str:
    """One line for the weapon list: name, attack roll and damage, with
    every bonus the sheet's weapon card counts (Dueling, a +1 weapon, ...)."""
    to_hit = weapon.calculate_total_attack_roll_bonus_int(character)
    damage = weapon.calculate_damage_bonus_int(character)
    return f"{weapon.name}  1d20{to_hit:+}  dmg {weapon.damage_roll.value} {damage:+}"
