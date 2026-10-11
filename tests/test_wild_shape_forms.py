"""Every example druid's Wild Shape known forms obey the 2024 limits
(SourceTexts/SubclassTexts2024/wild_shape_rules.txt) at the build's final
Druid level:

    Druid level   Known forms   Max CR   Fly speed
    2             4             1/4      No
    4             6             1/2      No
    8             8             1        Yes

Circle of the Moon raises the max CR to Druid level // 3 (Circle Forms).
"""

from fractions import Fraction

from CharacterContent.Features.ClassFeatures.Druid.DruidFeatures import WildShape
from CharacterContent.Features.SubClassFeatures.Druid.DruidMoonFeatures import (
    CircleForms,
)
from Core.Definitions import CharacterClass
from tests._snapshot_helpers import BUILD_PARAMS, build


def _limits(druid_level: int, circle_forms: bool) -> tuple[int, Fraction, bool]:
    if druid_level >= 8:
        count, max_cr, fly = 8, Fraction(1), True
    elif druid_level >= 4:
        count, max_cr, fly = 6, Fraction(1, 2), False
    else:
        count, max_cr, fly = 4, Fraction(1, 4), False
    if circle_forms:
        max_cr = Fraction(druid_level // 3)
    return count, max_cr, fly


def _problems(character) -> list[str]:
    wild_shapes = character.get_features_by_type(WildShape)
    druid_level = character.get_class_level(CharacterClass.DRUID)
    count, max_cr, fly = _limits(druid_level, character.has_feature(CircleForms))

    forms = [form_cls() for ws in wild_shapes for form_cls in ws.known_forms]
    problems = []
    if len(forms) > count:
        problems.append(f"{len(forms)} known forms, limit {count}")
    for form in forms:
        if Fraction(form.cr) > max_cr:
            problems.append(f"{form.combatant_type} is CR {form.cr}, max {max_cr}")
        if form.speed_fly_ft and not fly:
            problems.append(f"{form.combatant_type} has a Fly Speed before level 8")
    return problems


def test_known_forms_within_limits():
    checked = 0
    failures = []
    for name in BUILD_PARAMS:
        character = build(name)
        if not character.has_feature(WildShape):
            continue
        checked += 1
        problems = _problems(character)
        if problems:
            level = character.get_class_level(CharacterClass.DRUID)
            failures.append(f"{name} (Druid {level}): " + "; ".join(problems))
    assert checked, "no example build has Wild Shape"
    assert not failures, "\n".join(failures)
