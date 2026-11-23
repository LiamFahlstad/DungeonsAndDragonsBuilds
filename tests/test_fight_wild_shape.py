"""Wild Shape without the combat window (Combat/Fight/wild_shape.py, and
Combat/Fight/conditions.py's Incapacitated, Notes/combat-ui-refactor-plan.md
step 5.3): the uses a Druid has left, the badge a form gives, and which
conditions keep a combatant from taking the Bonus Action it costs."""

from functools import cache

from Combat.Effects.active_effects import effect_for
from Combat.Fight.conditions import incapacitated_by, incapacitates
from Combat.Fight.wild_shape import (
    WILD_SHAPE_COLOR,
    describe_form_badge,
    wild_shape_uses_left,
)
from Combat.PlayerCombatant import combatant_from_character
from Combat.WildShape import form_badge
from tests._snapshot_helpers import build

# Circle of the Moon Druid 3: two uses of Wild Shape (Druid table, level 3),
# forms Brown Bear, Dire Wolf, Giant Spider and Tiger.
MOON = "Y2024DruidMoonBriarWolfshadeCharacterBuilder"


@cache
def _sheet():
    return build(MOON)


def _druid() -> dict:
    return combatant_from_character(_sheet())


def test_a_level_3_druid_has_two_uses_and_never_fewer_than_none():
    druid = _druid()
    assert wild_shape_uses_left(druid) == 2
    druid["feature_uses_used"] = {"Wild Shape": 1}
    assert wild_shape_uses_left(druid) == 1
    druid["feature_uses_used"] = {"Wild Shape": 3}  # used past the last one
    assert wild_shape_uses_left(druid) == 0


def test_no_uses_without_wild_shape():
    assert wild_shape_uses_left({"name": "Goblin", "conditions": []}) == 0


def test_a_forms_badge_shows_its_statistics_in_wild_shape_green():
    druid = _druid()
    badge = describe_form_badge(druid, _sheet(), "Tiger")
    assert badge == form_badge("Tiger")
    effect = effect_for(druid, badge)
    assert effect["color"] == WILD_SHAPE_COLOR
    assert "Tiger" in (effect["tooltip"] or "")


def test_what_keeps_one_from_a_bonus_action():
    # Rules Glossary: Paralyzed, Petrified, Stunned and Unconscious each
    # give Incapacitated; Prone and Frightened don't.
    assert incapacitates("Stunned by Stunning Strike")
    assert not incapacitates("Prone")
    assert incapacitated_by({"conditions": ["Prone", "Frightened"]}) is None
    both = {"conditions": ["Unconscious", "Prone", "Paralyzed"]}
    assert incapacitated_by(both) == "Paralyzed"
