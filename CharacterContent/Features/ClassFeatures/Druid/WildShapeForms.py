from CharacterContent.Features.SubClassFeatures.Druid.DruidMoonFeatures import (
    CircleForms,
)
from Core.Definitions import CharacterClass
from Model.Creatures.Combatants import CreatureForm, ExtendedCombatantData
from Presentation.CreatureStatBlocks import format_creature_stat_block
from Model.View import CharacterView

# Circle Forms: "Temporary Hit Points equal to three times your Druid level".
CIRCLE_FORMS_TEMP_HP_MULTIPLIER = 3


def wild_shape_temp_hp_formula(character: CharacterView) -> str:
    """Temporary Hit Points gained on assuming a form (Circle of the Moon triples it)."""
    if character.has_feature(CircleForms):
        return "+ 3 × Druid level (Circle Forms)"
    return "+ Druid level"


def wild_shape_temp_hp(character: CharacterView) -> int:
    """The Temporary Hit Points wild_shape_temp_hp_formula gives, as a number."""
    druid_level = character.get_class_level(CharacterClass.DRUID)
    if character.has_feature(CircleForms):
        return CIRCLE_FORMS_TEMP_HP_MULTIPLIER * druid_level
    return druid_level


def wild_shape_ac_override(character: CharacterView) -> int | None:
    """Circle Forms AC (13 + WIS mod), used when higher than the Beast's AC."""
    if not character.has_feature(CircleForms):
        return None
    wisdom_modifier = character.get_wisdom_modifier()
    return 13 + wisdom_modifier


def wild_shape_form(
    monster_cls: CreatureForm,
    character: CharacterView,
) -> ExtendedCombatantData:
    """The Beast's stat block as character wears it: with Circle Forms' AC
    when that's higher."""
    monster = monster_cls()
    ac_override = wild_shape_ac_override(character)
    if ac_override is not None and ac_override > monster.ac:
        monster.ac = ac_override
        monster.ac_note = "13 + Wisdom modifier, Circle Forms"
    return monster


def format_wild_shape_form(
    monster_cls: CreatureForm,
    character: CharacterView,
) -> str:
    return format_creature_stat_block(
        wild_shape_form(monster_cls, character),
        retain_mental_abilities=True,
        temp_hp_text=wild_shape_temp_hp_formula(character),
    )
