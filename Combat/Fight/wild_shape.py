"""Wild Shape in a fight, Qt-free (Notes/combat-ui-refactor-plan.md, step
5.3, Wild Shape): the uses a Druid has left and the badge a form gives. The
form itself (its statistics, taking it on and leaving it, what can be cast
in it) is Combat/WildShape.py; the combat window spends the use and the Bonus
Action, logs the change and gives the badge and temporary Hit Points
(WildShapeMixin), because each of those logs too."""

from CharacterContent.Features.ClassFeatures.Druid.WildShapeForms import (
    format_wild_shape_form,
)
from Combat.Effects.active_effects import FEATURE, describe
from Combat.WildShape import form_badge, known_forms, wild_shape_feature
from Model.Character import Character

# A Wild Shape badge's color, apart from other features' blue.
WILD_SHAPE_COLOR = "#4a8a4c"


def wild_shape_uses_left(char: dict) -> int:
    """How many uses of Wild Shape char has left (0 without the feature)."""
    feature = wild_shape_feature(char)
    sheet = char.get("_stat_block")
    if feature is None or not isinstance(sheet, Character):
        return 0
    used = char.get("feature_uses_used", {}).get(feature.name, 0)
    return max(feature.number_of_uses(sheet) - used, 0)


def describe_form_badge(char: dict, sheet: Character, form: str) -> str:
    """Describe the badge char's `form` (one of sheet's forms) gives: its
    statistics, in Wild Shape's color. Returns the badge's name; giving it
    is the caller's."""
    badge = form_badge(form)
    describe(
        char,
        badge,
        format_wild_shape_form(known_forms(sheet)[form], sheet),
        WILD_SHAPE_COLOR,
        FEATURE,
    )
    return badge
