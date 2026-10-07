from typing import Type

from CharacterContent.Features.SubClassFeatures.Druid.DruidMoonFeatures import (
    CircleForms,
)
from Model.Creatures.Combatants import ExtendedCombatantData
from Presentation.CreatureStatBlocks import format_creature_stat_block
from Model.View import CharacterView


def wild_shape_temp_hp_formula(character: CharacterView) -> str:
    """Temporary Hit Points gained on assuming a form (Circle of the Moon triples it)."""
    if character.has_feature(CircleForms):
        return "+ 3 × Druid level (Circle Forms)"
    return "+ Druid level"


def format_wild_shape_form(
    monster_cls: Type[ExtendedCombatantData],
    character: CharacterView,
) -> str:
    return format_creature_stat_block(
        monster_cls(),
        retain_mental_abilities=True,
        temp_hp_text=wild_shape_temp_hp_formula(character),
    )
