"""Combatants as the combat UI holds them.

The combat UI keeps every combatant - monster or player - as a dict of what it
shows and what changes during a fight (HP, conditions, ...).
combatant_from_stat_block() builds a monster's from its stat block, which is
also how a prepared encounter log stores its starting combatants
(Combat/EncounterLogs.py). combatant_from_character() builds a player's from
their Character. The
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
from Model.Creatures.Combatants import BasicCombatantData, ExtendedCombatantData


def combatant_from_stat_block(combatant: BasicCombatantData) -> dict:
    """The combat UI's dict for a monster, NPC or other stat-block combatant,
    named "<name> (<type>)" when it has a name of its own. The battle
    statistics ("stats") are the UI's own and aren't included."""
    if combatant.name and combatant.name != combatant.combatant_type:
        display_name = f"{combatant.name} ({combatant.combatant_type})"
    else:
        display_name = combatant.combatant_type

    char = {
        "name": display_name,
        "create_name": (
            combatant.create_name
            if combatant.create_name is not None
            else combatant.combatant_type
        ),
        "combatant_type": combatant.combatant_type,
        "hp": combatant.hp,
        "max_hp": combatant.max_hp,
        "ac": combatant.ac,
        "temp_hp": combatant.temp_hp,
        "conditions": [cond.value for cond in combatant.conditions],
        "visibility_states": [vis.value for vis in (combatant.visibility_states or [])],
        "death_saves_fail": 0,
        "death_saves_success": 0,
        "spell_slots": combatant.spell_slots,
        "Ability Scores": combatant.ability_scores,
        "Saving Throws": combatant.saving_throws,
    }
    if combatant.initiative_group:
        # Shares one initiative roll and one turn with the rest of its group.
        char["initiative_group"] = combatant.initiative_group
    if isinstance(combatant, ExtendedCombatantData):
        char.update(
            {
                "cr": combatant.cr,
                "monster_type": combatant.monster_type,
                "monster_type_note": combatant.monster_type_note,
                "alignment": combatant.alignment,
                "size": combatant.size,
                "ac_note": combatant.ac_note,
                "hp_formula": combatant.hp_formula,
                "speed_ground_ft": combatant.speed_ground_ft,
                "speed_fly_ft": combatant.speed_fly_ft,
                "speed_climb_ft": combatant.speed_climb_ft,
                "speed_special_rules": combatant.speed_special_rules,
                "skills": combatant.skills,
                "damage_vulnerabilities": combatant.damage_vulnerabilities,
                "damage_resistances": combatant.damage_resistances,
                "damage_immunities": combatant.damage_immunities,
                "condition_immunities": combatant.condition_immunities,
                "senses": combatant.senses,
                "languages": combatant.languages,
                "description": combatant.description,
                "traits": combatant.traits,
                "actions": combatant.actions,
                "bonus_actions": combatant.bonus_actions,
                "reactions": combatant.reactions,
                "legendary_actions": combatant.legendary_actions,
                "legendary_resistances": combatant.legendary_resistances,
                "lair_actions": combatant.lair_actions,
                "mythic_actions": combatant.mythic_actions,
                "death_saves": combatant.death_saves,
            }
        )
    return char


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
        "damage_resistances": _damage_entries(character.damage_resistances()),
        "damage_immunities": _damage_entries(character.damage_immunities()),
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


def _damage_entries(damage_types) -> list[dict]:
    """A character's resistances or immunities the way a monster's look once
    reloaded from a saved fight, so the combat UI treats them alike."""
    return [{"damage_types": [damage_type.value]} for damage_type in damage_types]


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
    return f"{weapon.name}  1d20{to_hit:+}  dmg {weapon.get_damage_roll(character).value} {damage:+}"
