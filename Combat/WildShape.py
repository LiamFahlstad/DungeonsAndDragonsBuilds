"""Wild Shape in the combat simulator: a Druid's combatant dict wearing a
Beast form's stat block, and taking it off again.

A shape-shifted Druid stays one combatant, with the same name, card, Hit
Points, conditions and log history. assume_form() puts the form's game
statistics into the Druid's dict (Combat/PlayerCombatant.py) as the 2024
rules give them: its AC, size, speeds, senses and defenses, its traits and
actions, its Strength, Dexterity and Constitution, and saves and skills that
keep the Druid's proficiencies. What it replaced is kept under "wild_shape",
and leave_form() puts that back. The combat UI reads everything from the dict,
so with no other code knowing about Wild Shape the form's attacks show up as
buttons on the Druid's turn, attacks against them use its AC and saves its
modifiers. "wild_shape" is a public key, so undo takes a transformation back
like any other change. Nothing here imports Qt.
"""

import re

from CharacterContent.Features.ClassFeatures.Druid.DruidFeatures import (
    AdditionalWildShapeForms,
    BeastSpells,
    WildShape,
)
from CharacterContent.Features.ClassFeatures.Druid.WildShapeForms import (
    wild_shape_form,
)
from CharacterContent.Features.SubClassFeatures.Druid.DruidMoonFeatures import (
    MOON_SPELLS_SOURCE,
    CircleOfTheMoonSpells,
    ImprovedCircleForms,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Core.Definitions import Ability, Skill
from Core.Rules import ability_modifier
from Model.Character import Character
from Model.Creatures.Combatants import CreatureForm, ExtendedCombatantData
from Model.Ledger.Skills import DEFAULT_SKILL_ABILITIES

WILD_SHAPE_KEY = "wild_shape"

_PASSIVE_PERCEPTION = re.compile(r"Passive Perception \d+")
_MATERIAL_COST = re.compile(r"\d[\d,]*\+?\s*GP", re.IGNORECASE)

# The scores a form replaces; the Druid keeps their Intelligence, Wisdom and
# Charisma.
FORM_ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY, Ability.CONSTITUTION)

# The parts of a form's stat block a combatant's dict shows, read by the info
# dialog and the turn column like a monster's.
_STAT_BLOCK_KEYS = (
    "ac_note",
    "speed_ground_ft",
    "speed_fly_ft",
    "speed_climb_ft",
    "speed_special_rules",
    "senses",
    "damage_vulnerabilities",
    "condition_immunities",
    "traits",
    "actions",
    "bonus_actions",
    "reactions",
    "cr",
)


def known_forms(character: Character) -> dict[str, CreatureForm]:
    """The Beast forms character can Wild Shape into, by name, in the order
    their features list them."""
    forms: dict[str, CreatureForm] = {}
    for feature in character.iter_features_with_extensions():
        if isinstance(feature, (WildShape, AdditionalWildShapeForms)):
            for form in feature.known_forms:
                forms[form().combatant_type] = form
    return forms


def wild_shape_feature(char: dict) -> WildShape | None:
    """char's Wild Shape feature, if it has one."""
    return next(
        (f for f in char.get("_feature_objects", []) if isinstance(f, WildShape)),
        None,
    )


def current_form(char: dict) -> str | None:
    """The name of the form char is in, or None if it isn't shape-shifted."""
    state = char.get(WILD_SHAPE_KEY)
    return state["form"] if state else None


def form_badge(form: str) -> str:
    """The condition badge a combatant in `form` wears on its card."""
    return f"Wild Shape ({form})"


def assume_form(char: dict, form: str) -> None:
    """Put the Beast form called `form` on char, a player's combatant dict,
    leaving any form it's already in first (using Wild Shape again ends it).
    Hit Points and temporary Hit Points are the caller's. Raises KeyError if
    char's Character doesn't know the form."""
    character: Character = char["_stat_block"]
    stat_block = wild_shape_form(known_forms(character)[form], character)
    leave_form(char)
    statistics = _form_statistics(char, character, stat_block)
    char[WILD_SHAPE_KEY] = {
        "form": form,
        "kept": {key: char[key] for key in statistics if key in char},
        "added": [key for key in statistics if key not in char],
    }
    char.update(statistics)


def leave_form(char: dict) -> str | None:
    """Take char's form off, putting back what it replaced. Returns the form's
    name, or None if it wasn't in one."""
    state = char.pop(WILD_SHAPE_KEY, None)
    if state is None:
        return None
    for key in state["added"]:
        char.pop(key, None)
    char.update(state["kept"])
    return state["form"]


def can_cast_in_form(char: dict, spell_name: str) -> bool:
    """Whether char can cast `spell_name` as it is: anything when not
    shape-shifted; in a form, only with Beast Spells (but not a spell whose
    Material component has a cost or is consumed), or a spell Circle of the
    Moon Spells grants."""
    if current_form(char) is None:
        return True
    character = char.get("_stat_block")
    if not isinstance(character, Character):
        return True
    if character.has_feature(BeastSpells):
        return not _has_costly_material(spell_name)
    if not character.has_feature(CircleOfTheMoonSpells):
        return False
    return any(
        getattr(grant.name, "value", str(grant.name)) == spell_name
        for grant in character.spell_grants
        if grant.source == MOON_SPELLS_SOURCE
    )


def _has_costly_material(spell_name: str) -> bool:
    """Whether the spell's Material component has a cost ("worth 300+ GP")
    or is consumed, which Beast Spells excludes."""
    try:
        material = SpellFactory.create(spell_name).material_description or ""
    except Exception:
        return False  # a spell the factory doesn't know: the GM's call
    return bool(_MATERIAL_COST.search(material)) or "consume" in material.lower()


def _form_statistics(
    char: dict, character: Character, form: ExtendedCombatantData
) -> dict:
    """The dict entries `form` gives char ("Game Statistics" in Wild Shape's
    rules). Damage resistances and immunities are the Druid's and the form's
    together: the dict can't tell the ones a class feature or feat gives,
    which the Druid keeps, from a species trait's."""
    scores = {
        ability.short_name: (
            (form.ability_scores or {}).get(ability.short_name, 10)
            if ability in FORM_ABILITIES
            else character.get_ability_score(ability)
        )
        for ability in Ability
    }
    statistics = {key: getattr(form, key) for key in _STAT_BLOCK_KEYS}
    skills = _skills(character, form, scores)
    statistics.update(
        {
            "ac": form.ac,
            "speed": form.speed_ground_ft or 0,
            "size": form.size.value if form.size else char.get("size"),
            "Ability Scores": scores,
            "Saving Throws": _saving_throws(character, form, scores),
            "skills": skills,
            "senses": _PASSIVE_PERCEPTION.sub(
                f"Passive Perception {10 + skills[Skill.PERCEPTION]}", form.senses
            ),
            "damage_resistances": [
                *char.get("damage_resistances", []),
                *(form.damage_resistances or []),
            ],
            "damage_immunities": [
                *char.get("damage_immunities", []),
                *(form.damage_immunities or []),
            ],
        }
    )
    return statistics


def _in_form(
    character: Character, ability: Ability, own: int, scores: dict[str, int]
) -> int:
    """A modifier of character's that adds `ability`'s modifier, with the
    form's score in place of the Druid's: what they add besides the score
    (their Proficiency Bonus, ...) stays."""
    if ability not in FORM_ABILITIES:
        return own
    form_modifier = ability_modifier(scores[ability.short_name])
    return own - character.get_ability_modifier(ability) + form_modifier


def _beast_is_proficient(
    form: ExtendedCombatantData, ability: Ability, listed: int | None
) -> bool:
    """Whether the form's stat block lists a modifier (`listed`) for a save
    or skill of `ability` that adds more than its ability modifier: a
    proficiency, which a Druid in the form gains."""
    score = (form.ability_scores or {}).get(ability.short_name, 10)
    return listed is not None and listed > ability_modifier(score)


def _saving_throws(
    character: Character, form: ExtendedCombatantData, scores: dict[str, int]
) -> dict[str, int]:
    """The Druid's saves with the form's scores and proficient in the form's
    too, or the form's own where it lists a higher one; Improved Circle
    Forms adds Wisdom to Constitution."""
    saves = {}
    for ability in Ability:
        own = character.get_saving_throw_modifier(ability)
        listed = (form.saving_throws or {}).get(ability.short_name)
        if not character.is_proficient_in_saving_throw(
            ability
        ) and _beast_is_proficient(form, ability, listed):
            own += character.get_proficiency_bonus()
        save = _in_form(character, ability, own, scores)
        if listed is not None:
            save = max(save, listed)
        if ability is Ability.CONSTITUTION and character.has_feature(
            ImprovedCircleForms
        ):
            save += character.get_wisdom_modifier()
        saves[ability.short_name] = save
    return saves


def _skills(
    character: Character, form: ExtendedCombatantData, scores: dict[str, int]
) -> dict[Skill, int]:
    """Every skill's modifier in the form: the higher of the Druid's (using
    the form's scores, and proficient in the form's skills too) and the one
    the form lists. All of them, as the character sheet's own skill table no
    longer holds."""
    skills = {}
    for skill in Skill:
        listed = (form.skills or {}).get(skill)
        ability = character.get_skill_ability(skill)
        own = character.get_skill_modifier(skill)
        if not character.is_proficient_in_skill(skill) and _beast_is_proficient(
            form, DEFAULT_SKILL_ABILITIES[skill], listed
        ):
            own += character.get_proficiency_bonus()
        modifier = _in_form(character, ability, own, scores)
        skills[skill] = modifier if listed is None else max(modifier, listed)
    return skills
