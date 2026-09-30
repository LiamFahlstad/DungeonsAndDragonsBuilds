from typing import Type

from Combat.Definitions import ExtendedCombatantData
from Utils.CreatureStatBlocks import format_creature_stat_block
from Model.Character import Character


def format_wild_shape_form(
    monster_cls: Type[ExtendedCombatantData],
    character: Character,
) -> str:
    return format_creature_stat_block(
        monster_cls(), character, retain_mental_abilities=True
    )
