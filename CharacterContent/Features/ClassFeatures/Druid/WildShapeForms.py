from CharacterContent.Features.SubClassFeatures.Druid.DruidMoonFeatures import (
    CircleForms,
)
from Model.Creatures.Combatants import CreatureForm
from Presentation.CreatureStatBlocks import format_creature_stat_block
from Model.View import CharacterView


def wild_shape_temp_hp_formula(character: CharacterView) -> str:
    """Temporary Hit Points gained on assuming a form (Circle of the Moon triples it)."""
    if character.has_feature(CircleForms):
        return "+ 3 × Druid level (Circle Forms)"
    return "+ Druid level"


def wild_shape_ac_override(character: CharacterView) -> int | None:
    """Circle Forms AC (13 + WIS mod), used when higher than the Beast's AC."""
    if not character.has_feature(CircleForms):
        return None
    wisdom_modifier = character.get_wisdom_modifier()
    return 13 + wisdom_modifier


def format_wild_shape_form(
    monster_cls: CreatureForm,
    character: CharacterView,
) -> str:
    monster = monster_cls()
    ac_override = wild_shape_ac_override(character)
    if ac_override is not None and ac_override > monster.ac:
        monster.ac = ac_override
        monster.ac_note = "13 + Wisdom modifier, Circle Forms"
    return format_creature_stat_block(
        monster,
        retain_mental_abilities=True,
        temp_hp_text=wild_shape_temp_hp_formula(character),
    )
