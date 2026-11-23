"""Combatant: every key a combatant dict may hold in a fight, with its type
and what it means (Notes/combat-ui-refactor-plan.md, step 2).

The combat UI keeps each combatant (monster, player, summon, ally) as a plain
dict: Combat/PlayerCombatant.py builds it, the fight adds to it, and the
encounter log saves it. One dict holds several shapes at once (a player's has
"_stat_block" and class levels, a monster's its actions and speeds), so most
keys are optional; the required ones are those both builders always set.

How the keys work:

- A key starting with "_" is fixed for the fight (the Character, feature
  objects, ...). Undo doesn't copy it and the encounter log doesn't save it
  (Combat/CombatUIQt/undo.py). Every other key is undone and saved.
- A value that's an enum when built from a stat block is its string once
  reloaded from a log (str enums compare equal to their strings).

This TypedDict is the schema; tests check the code against it
(tests/test_combatant_keys.py): the builders' keys, the keys a fight saves,
and every literal key the combat code reads or writes on a combatant must be
declared here. Signatures still say `dict`: a TypedDict isn't assignable to
or from a plain `dict`, so they switch to Combatant module by module as step
5 moves the fight's code into Combat/Fight/.
"""

from typing import Any, Required, TypedDict

from Core.Definitions import CreatureSize
from Model.Character import Character
from Model.Creatures.Combatants import Alignment, MonsterType

Combatant = TypedDict(
    "Combatant",
    {
        # ---- Set by both builders (Combat/PlayerCombatant.py) ----
        # What the fight calls it: "Goblin 2", "Hanna's Drake Companion".
        "name": Required[str],
        # The name it was made under, before numbering.
        "create_name": Required[str],
        "hp": Required[int],
        # The stored maximum; badges change it (hit_point_maximum).
        "max_hp": Required[int],
        # A monster's number, or a player's text: "15 (no Shield)".
        "ac": Required[int | str | None],
        "temp_hp": Required[int],
        # Rules conditions and statuses, by name.
        "conditions": Required[list[str]],
        "visibility_states": Required[list[str]],
        "death_saves_fail": Required[int],
        "death_saves_success": Required[int],
        # Slots left by level.
        "spell_slots": Required[dict],
        # By ability short name ("STR").
        "Ability Scores": Required[dict],
        "Saving Throws": Required[dict],
        # ---- A monster's stat block (combatant_from_stat_block) ----
        "combatant_type": str,
        "initiative_group": str,
        "hidden_from_players": bool,
        "cr": str,
        "monster_type": MonsterType | str,
        "monster_type_note": str,
        "alignment": Alignment | str,
        "size": CreatureSize | str,
        "ac_note": str,
        "hp_formula": str,
        "speed_ground_ft": int | None,
        "speed_fly_ft": int | None,
        "speed_climb_ft": int | None,
        "speed_swim_ft": int | None,
        "speed_burrow_ft": int | None,
        "speed_special_rules": str,
        "hover": bool,
        "skills": dict,
        "damage_vulnerabilities": list,
        "damage_resistances": list,
        "damage_immunities": list,
        "condition_immunities": list,
        "senses": str,
        "darkvision_ft": int | None,
        "blindsight_ft": int | None,
        "blind_beyond": bool,
        "truesight_ft": int | None,
        "tremorsense_ft": int | None,
        "passive_perception": int,
        "spell_save_dc": int | None,
        "spell_attack_bonus": int | None,
        "languages": str,
        "description": str,
        # Stat-block abilities, as dicts (MonsterAbility.to_dict).
        "traits": list,
        "actions": list,
        "bonus_actions": list,
        "reactions": list,
        "legendary_actions": list,
        "lair_actions": list,
        "mythic_actions": list,
        "legendary_resistances": int,
        # Makes death saving throws like a player (an NPC ally).
        "death_saves": bool,
        # ---- A player (combatant_from_character) ----
        # Their AC without the Shield they wield; None: they wield none.
        "ac_without_shield": int | None,
        "pact_slots": dict,
        "class_levels": dict,
        "subclass": str,
        "proficiency_bonus": int,
        "speed": int,
        # (display name, level, Ability) per spell.
        "spells_with_level": list,
        "features": list[str],
        "invocations": list,
        "_is_player": bool,
        "_stat_block": Character,
        "_weapons_objects": list,
        "_weapon_masteries": list,
        "_spell_objects": dict,
        "_feature_objects": list,
        # ---- What the fight adds ----
        # Battle statistics (Combat/Fight/stats.py).
        "stats": dict,
        # Lasting effects (Combat/Effects/active_effects.py, ActiveEffect).
        "active_effects": list,
        # Spells running from this caster (Combat/Arena/lasting.py).
        "active_spells": list,
        "active_features": list,
        "feature_uses_used": dict,
        # What it spent of its turn, by ActionCost.
        "action_uses": dict,
        "concentration_checks": list,
        # A monster's limited abilities used, and its recharges and repeat
        # saves rolled ahead (turn_panel_mixin, monster_actions).
        "spent_abilities": dict,
        "legendary_actions_left": int,
        "legendary_resistances_left": int,
        "_recharge_rolls": dict,
        "_repeat_rolls": dict,
        # What attack rolls and damage told of it (attack_rolls.py,
        # player_view.py): shown to the players, never more than they learnt.
        "ac_above": int,
        "ac_at_most": int,
        "max_hp_at_least": int,
        "max_hp_at_most": int,
        "known_resistances": list,
        "known_immunities": list,
        # A player who set their Shield down (attack_rolls.SHIELD_OFF).
        "shield_off": bool,
        # The damage type it last dealt, for the Damage field's default.
        "_last_damage_type": str,
        # Its initiative roll (turns_mixin.INITIATIVE_KEY).
        "_initiative": int,
        # ---- The battle map (Combat/Arena/) ----
        "position": list,
        "moved_ft": int,
        "dashes": int,
        # Who has it Grappled, by name.
        "grappled_by": str,
        # The speed it moves by, and how high it flies (speeds.py).
        "moving_by": str,
        "altitude_ft": int,
        # ---- Summons, allies and Wild Shape ----
        # Its owner, by name, and how it was made (Combat/Summons.py).
        "summon_of": str,
        "summon_source": str,
        "summon_spec": str,
        "summon_choice": str,
        "summon_slot": int,
        "summon_lifetime": str,
        "summon_turn": str,
        "summon_on_zero_hp": str,
        # Older logs' names for summon_of and summon_choice (Summons.OLD_KEYS).
        "companion_of": str,
        "companion_choice": str,
        # Allies travelling with the party, or the encounter's own
        # (Combat/PartyAllies.py).
        "party_ally": bool,
        "encounter_ally": bool,
        # The form a Druid has taken and what it replaced (Combat/WildShape.py).
        "wild_shape": dict[str, Any],
    },
    total=False,
)

COMBATANT_KEYS: frozenset[str] = (
    Combatant.__required_keys__ | Combatant.__optional_keys__
)
