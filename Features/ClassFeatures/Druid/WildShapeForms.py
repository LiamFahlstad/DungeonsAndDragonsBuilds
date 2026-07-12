from typing import Type

from Combat.Definitions import ExtendedCombatantData
from Features.ClassFeatures.CreatureStatBlocks import format_creature_stat_block
from StatBlocks.CharacterStatBlock import CharacterStatBlock


def format_wild_shape_form(
    monster_cls: Type[ExtendedCombatantData],
    character_stat_block: CharacterStatBlock,
) -> str:
    return format_creature_stat_block(
        monster_cls(), character_stat_block, retain_mental_abilities=True
    )
