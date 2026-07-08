from enum import Enum
from typing import Optional

from Combat.Definitions import ExtendedCombatantData
from Definitions import Ability, CharacterClass, DamageType
from Features.ClassFeatures.CreatureStatBlocks import format_creature_stat_block
from StatBlocks.CharacterStatBlock import CharacterStatBlock

_PRIMAL_BOND_TRAIT = {
    "name": "Primal Bond",
    "description": "Add your Proficiency Bonus to any ability check or saving throw the beast makes.",
}


class CompanionType(str, Enum):
    BEAST_OF_THE_LAND = "Beast of the Land"
    BEAST_OF_THE_SEA = "Beast of the Sea"
    BEAST_OF_THE_SKY = "Beast of the Sky"


# Damage types the player may choose from when summoning each companion stat block.
ALLOWED_STRIKE_DAMAGE_TYPES = {
    CompanionType.BEAST_OF_THE_LAND: (
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
        DamageType.SLASHING,
    ),
    CompanionType.BEAST_OF_THE_SEA: (
        DamageType.BLUDGEONING,
        DamageType.PIERCING,
    ),
    # Beast of the Sky's Strike is fixed to Slashing damage; no choice offered.
    CompanionType.BEAST_OF_THE_SKY: (DamageType.SLASHING,),
}


def _strike_action(
    damage_die: str,
    flat_bonus: int,
    spell_attack_modifier: int,
    damage_type: DamageType,
    extra: str = "",
) -> dict:
    return {
        "name": "Beast's Strike",
        "description": (
            f"Melee Attack Roll: {spell_attack_modifier:+}, reach 5 ft. "
            f"Hit: {damage_die} + {flat_bonus} {damage_type.value} damage{extra}"
        ),
    }


class BeastOfTheLand(ExtendedCombatantData):
    def __init__(
        self,
        ranger_level: int,
        wisdom_modifier: int,
        proficiency_bonus: int,
        spell_attack_modifier: int,
        damage_type: DamageType,
    ):
        super().__init__(
            combatant_type="Beast of the Land",
            hp=5 + (5 * ranger_level),
            ac=13 + wisdom_modifier,
            temp_hp=0,
            conditions=[],
            ability_scores={"Str": 14, "Dex": 14, "Con": 15, "Int": 8, "Wis": 14, "Cha": 11},
            saving_throws={},
            spell_slots={},
            cr="None",
            monster_type="Medium Beast, Neutral",
            ac_note="13 plus your Wisdom modifier",
            hp_formula=f"5 + five times your Ranger level ({ranger_level} d8 Hit Dice)",
            speed="40 ft., Climb 40 ft.,",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 60 ft., Passive Perception 12",
            languages="Understands the languages you know but can't speak",
            traits=[_PRIMAL_BOND_TRAIT],
            actions=[
                _strike_action(
                    "1d8",
                    2 + wisdom_modifier,
                    spell_attack_modifier,
                    damage_type,
                    extra=(
                        " (your choice of Bludgeoning, Piercing, or Slashing when summoned). "
                        "If the beast moved at least 20 feet straight toward the target before "
                        "the hit, the target takes an extra 1d6 damage of the same type, and the "
                        "target has the Prone condition if it is a Large or smaller creature."
                    ),
                )
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class BeastOfTheSea(ExtendedCombatantData):
    def __init__(
        self,
        ranger_level: int,
        wisdom_modifier: int,
        proficiency_bonus: int,
        spell_attack_modifier: int,
        damage_type: DamageType,
        spell_save_dc: int,
    ):
        super().__init__(
            combatant_type="Beast of the Sea",
            hp=5 + (5 * ranger_level),
            ac=13 + wisdom_modifier,
            temp_hp=0,
            conditions=[],
            ability_scores={"Str": 14, "Dex": 14, "Con": 15, "Int": 8, "Wis": 14, "Cha": 11},
            saving_throws={},
            spell_slots={},
            cr="None",
            monster_type="Medium Beast, Neutral",
            ac_note="13 plus your Wisdom modifier",
            hp_formula=f"5 + five times your Ranger level ({ranger_level} d8 Hit Dice)",
            speed="5 ft., Swim 60 ft.,",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 90 ft., Passive Perception 12",
            languages="Understands the languages you know but can't speak",
            traits=[
                {
                    "name": "Amphibious",
                    "description": "The beast can breathe air and water.",
                },
                _PRIMAL_BOND_TRAIT,
            ],
            actions=[
                _strike_action(
                    "1d6",
                    2 + wisdom_modifier,
                    spell_attack_modifier,
                    damage_type,
                    extra=(
                        " (your choice of Bludgeoning or Piercing when summoned), and the target "
                        f"has the Grappled condition (escape DC {spell_save_dc})."
                    ),
                )
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class BeastOfTheSky(ExtendedCombatantData):
    def __init__(
        self,
        ranger_level: int,
        wisdom_modifier: int,
        proficiency_bonus: int,
        spell_attack_modifier: int,
    ):
        super().__init__(
            combatant_type="Beast of the Sky",
            hp=4 + (4 * ranger_level),
            ac=13 + wisdom_modifier,
            temp_hp=0,
            conditions=[],
            ability_scores={"Str": 6, "Dex": 16, "Con": 13, "Int": 8, "Wis": 14, "Cha": 11},
            saving_throws={},
            spell_slots={},
            cr="None",
            monster_type="Small Beast, Neutral",
            ac_note="13 plus your Wisdom modifier",
            hp_formula=f"4 + four times your Ranger level ({ranger_level} d6 Hit Dice)",
            speed="10 ft., Fly 60 ft.,",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 60 ft., Passive Perception 12",
            languages="Understands the languages you know but can't speak",
            traits=[
                {
                    "name": "Flyby",
                    "description": "The beast doesn't provoke Opportunity Attacks when it flies out of an enemy's reach.",
                },
                _PRIMAL_BOND_TRAIT,
            ],
            actions=[
                _strike_action(
                    "1d4",
                    3 + wisdom_modifier,
                    spell_attack_modifier,
                    DamageType.SLASHING,
                )
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


def build_primal_companion(
    companion_type: CompanionType,
    character_stat_block: CharacterStatBlock,
    damage_type: Optional[DamageType] = None,
) -> ExtendedCombatantData:
    ranger_level = character_stat_block.get_class_level(CharacterClass.RANGER)
    wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
    proficiency_bonus = character_stat_block.get_proficiency_bonus()
    spell_attack_modifier = character_stat_block.calculate_attack_bonus_for_ability(Ability.WISDOM)

    allowed_damage_types = ALLOWED_STRIKE_DAMAGE_TYPES[companion_type]
    if damage_type is None:
        damage_type = allowed_damage_types[0]
    elif damage_type not in allowed_damage_types:
        allowed_names = ", ".join(d.value for d in allowed_damage_types)
        raise ValueError(
            f"{companion_type.value}'s Strike damage type must be one of: {allowed_names}."
        )

    if companion_type is CompanionType.BEAST_OF_THE_LAND:
        return BeastOfTheLand(
            ranger_level=ranger_level,
            wisdom_modifier=wisdom_modifier,
            proficiency_bonus=proficiency_bonus,
            spell_attack_modifier=spell_attack_modifier,
            damage_type=damage_type,
        )
    if companion_type is CompanionType.BEAST_OF_THE_SEA:
        return BeastOfTheSea(
            ranger_level=ranger_level,
            wisdom_modifier=wisdom_modifier,
            proficiency_bonus=proficiency_bonus,
            spell_attack_modifier=spell_attack_modifier,
            damage_type=damage_type,
            spell_save_dc=character_stat_block.calculate_difficulty_class_for_ability(Ability.WISDOM),
        )
    return BeastOfTheSky(
        ranger_level=ranger_level,
        wisdom_modifier=wisdom_modifier,
        proficiency_bonus=proficiency_bonus,
        spell_attack_modifier=spell_attack_modifier,
    )


def format_primal_companion(
    companion_type: CompanionType,
    character_stat_block: CharacterStatBlock,
    damage_type: Optional[DamageType] = None,
) -> str:
    companion = build_primal_companion(companion_type, character_stat_block, damage_type)
    return format_creature_stat_block(companion, character_stat_block, retain_mental_abilities=False)


def format_all_primal_companions(
    character_stat_block: CharacterStatBlock,
    selected_type: Optional[CompanionType] = None,
    selected_damage_type: Optional[DamageType] = None,
) -> str:
    """Render all three Beast stat blocks so the player can pick (or switch on a
    Long Rest, per the rules) without needing to regenerate the character sheet."""
    blocks = []
    for companion_type in CompanionType:
        is_selected = companion_type is selected_type
        damage_type = selected_damage_type if is_selected else None
        companion = build_primal_companion(companion_type, character_stat_block, damage_type)
        if is_selected:
            companion.combatant_type += " (Currently Summoned)"
        blocks.append(
            format_creature_stat_block(companion, character_stat_block, retain_mental_abilities=False)
        )
    return "".join(blocks)
