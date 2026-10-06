from typing import Type

from CharacterContent.Features.SubClassFeatures.Druid.DruidMoonFeatures import (
    CircleForms,
)
from Model.Creatures.Combatants import ExtendedCombatantData
from Utils.CreatureStatBlocks import format_creature_stat_block
from Model.Character import Character


def wild_shape_temp_hp_formula(character: Character) -> str:
    """Temporary Hit Points gained on assuming a form (Circle of the Moon triples it)."""
    if character.get_features_by_type(CircleForms):
        return "+ 3 × Druid level (Circle Forms)"
    return "+ Druid level"


def format_wild_shape_form(
    monster_cls: Type[ExtendedCombatantData],
    character: Character,
) -> str:
    return format_creature_stat_block(
        monster_cls(),
        character,
        retain_mental_abilities=True,
        temp_hp_text=wild_shape_temp_hp_formula(character),
    )
