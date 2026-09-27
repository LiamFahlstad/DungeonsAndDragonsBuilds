"""Feature application must not depend on the order features/armor/items apply.

A bonus "equal to your <ability> modifier" used to be computed inside apply()
and stored as a constant, freezing it at whatever the score was when that
feature happened to run. Primal Order (added at Druid level 1) therefore
missed every later Ability Score Improvement, and LAST-phase features still
missed ability-raising magic items (items apply after every feature). Such
bonuses are now formulas evaluated at read time - these tests pin that down.
"""

import ast
import pathlib

import pytest

from CharacterContent.Features.ClassFeatures.Bard import BardFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Features.ClassFeatures.Druid import DruidFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Features.SubClassFeatures.Ranger import (
    RangerGloomStalkerFeatures,
    RangerHollowWardenFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Rogue import (
    RogueSwashbucklerFeatures,
)
from Core.Definitions import Ability, CharacterClass, Skill
from RunCharacterCreator import BuildSelector, ExampleSelector


def _source_bonus(character, skill, source):
    return [
        value
        for value, name in character.get_skill_bonus_sources(skill)
        if name == source
    ]


class TestModifierBonusesTrackLaterScoreIncreases:
    """Apply the feature first, raise the score afterwards (as a later ASI or a
    magic item would), and expect the bonus to reflect the final score."""

    def test_primal_order_magician(self, make_character):
        character = make_character(wisdom=16)  # +3
        DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.MAGICIAN).apply(
            character
        )
        character.abilities.add_bonus(Ability.WISDOM, 4)  # 20 -> +5
        for skill in (Skill.ARCANA, Skill.NATURE):
            assert _source_bonus(character, skill, "Primal Order") == [5]
            # INT 10 (+0), not proficient: the bonus is the whole modifier.
            assert character.get_skill_modifier(skill) == 5

    def test_primal_order_warden_grants_no_skill_bonus(self, make_character):
        character = make_character(wisdom=16)
        DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.WARDEN).apply(character)
        assert character.get_skill_bonus(Skill.ARCANA) == 0

    def test_thaumaturge(self, make_character):
        character = make_character(wisdom=14)  # +2
        feature = ClericFeatures.DivineOrderThaumaturge(extra_cantrip="Guidance")
        feature.apply(character)
        character.abilities.add_bonus(Ability.WISDOM, 4)  # 18 -> +4
        for skill in (Skill.ARCANA, Skill.RELIGION):
            assert _source_bonus(character, skill, feature.name) == [4]

    def test_modifier_bonus_keeps_minimum_of_one(self, make_character):
        character = make_character(wisdom=8)  # -1
        feature = ClericFeatures.DivineOrderThaumaturge(extra_cantrip="Guidance")
        feature.apply(character)
        assert character.get_skill_bonus(Skill.RELIGION) == 1

    def test_aura_of_protection(self, make_character):
        character = make_character(charisma=14)  # +2
        PaladinFeatures.AuraOfProtection().apply(character)
        character.abilities.add_bonus(Ability.CHARISMA, 4)  # 18 -> +4
        for ability in Ability:
            expected = character.get_ability_modifier(ability) + 4
            assert character.get_saving_throw_modifier(ability) == expected

    def test_hungering_might(self, make_character):
        character = make_character(wisdom=12)  # +1
        RangerHollowWardenFeatures.HungeringMightBonus().apply(character)
        character.abilities.add_bonus(Ability.WISDOM, 6)  # 18 -> +4
        assert character.get_saving_throw_modifier(Ability.CONSTITUTION) == 4
        assert character.get_saving_throw_modifier(Ability.STRENGTH) == 0

    def test_dread_ambusher(self, make_character):
        character = make_character(wisdom=16)  # +3
        RangerGloomStalkerFeatures.DreadAmbusher().apply(character)
        character.abilities.add_bonus(Ability.WISDOM, 2)  # 18 -> +4
        assert character.initiative == 4

    def test_rakish_audacity(self, make_character):
        character = make_character(charisma=16)  # +3
        RogueSwashbucklerFeatures.RakishAudacityBonus().apply(character)
        character.abilities.add_bonus(Ability.CHARISMA, 4)  # 20 -> +5
        assert character.initiative == 5


class TestJackOfAllTrades:
    def test_proficiency_granted_later_switches_bonus_off(self, make_character):
        # Bard 5: proficiency bonus +3, Jack of All Trades adds 3 // 2 = 1.
        character = make_character(levels={CharacterClass.BARD: 5})
        BardFeatures.JackOfAllTrades().apply(character)
        assert character.get_skill_modifier(Skill.STEALTH) == 1

        # A proficiency from anything that applies afterwards (species,
        # another builder, an item) must replace the half bonus, not stack.
        character.skills.add_skill_proficiency(Skill.STEALTH)
        assert character.get_skill_modifier(Skill.STEALTH) == 3
        assert _source_bonus(character, Skill.STEALTH, "Jack of All Trades") == []

    def test_unproficient_skills_list_the_source(self, make_character):
        character = make_character(levels={CharacterClass.BARD: 5})
        BardFeatures.JackOfAllTrades().apply(character)
        assert _source_bonus(character, Skill.ARCANA, "Jack of All Trades") == [1]


ALL_BUILDS = {**BuildSelector.builds(), **ExampleSelector.builds()}
_WISDOM_SKILL_BONUS_FEATURES = {
    "Primal Order": Skill.ARCANA,
    "Divine Order: Thaumaturge": Skill.ARCANA,
}


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_wisdom_skill_bonuses_use_final_wisdom(name):
    # Regression: four example Druids printed Primal Order's Arcana bonus
    # from their level-1 Wisdom (+3) instead of their final Wisdom (+5).
    data = type(ALL_BUILDS[name])().build()
    character = data.setup_character_stat_block()
    expected = max(1, character.get_ability_modifier(Ability.WISDOM))
    for feature in data.features:
        skill = _WISDOM_SKILL_BONUS_FEATURES.get(feature.name)
        if skill is None:
            continue
        for value in _source_bonus(character, skill, feature.name):
            assert value == expected, feature.name


# ── Guard: apply() must not snapshot derived stats ────────────────────────────

_DERIVED_READERS = {
    "get_ability_modifier",
    "get_ability_score",
    "get_proficiency_bonus",
    "get_strength_modifier",
    "get_dexterity_modifier",
    "get_constitution_modifier",
    "get_intelligence_modifier",
    "get_wisdom_modifier",
    "get_charisma_modifier",
    "get_modifier",
    "get_score",
    "is_proficient",
    "has_expertise",
    "is_proficient_in_skill",
    "is_proficient_in_saving_throw",
    "calculate_armor_class",
}

# apply() methods that read state on purpose. Anything else that needs a
# stat-dependent value must pass a formula (see Improvements.Value).
_ALLOWED_EAGER_READERS = {
    # Validator: raises when the requirement isn't met.
    "StrengthRequirement.apply",
    # "To a maximum of 20": the cap is judged against the score so far.
    "AbilityScoreBonus.apply",
    # Choices resolved against what the character already has.
    "SkillExpert.apply",
    "UnfetteredMind.apply",
    "IronMind.apply",
}


def _apply_methods_reading_derived_stats():
    root = pathlib.Path(__file__).resolve().parent.parent / "CharacterContent"
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            for method in cls.body:
                if not isinstance(method, ast.FunctionDef):
                    continue
                if method.name not in ("apply", "apply_after_armor"):
                    continue
                # Calls inside a nested def/lambda are formulas evaluated at
                # read time, not snapshots - skip those subtrees.
                nested = {
                    id(node)
                    for inner in ast.walk(method)
                    if inner is not method
                    and isinstance(inner, (ast.FunctionDef, ast.Lambda))
                    for node in ast.walk(inner)
                }
                reads = sorted(
                    {
                        node.func.attr
                        for node in ast.walk(method)
                        if id(node) not in nested
                        and isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr in _DERIVED_READERS
                    }
                )
                if reads:
                    yield f"{cls.name}.{method.name}", path, method.lineno, reads


def test_apply_methods_do_not_snapshot_derived_stats():
    offenders = [
        f"{path.name}:{line} {qualname} reads {', '.join(reads)}"
        for qualname, path, line, reads in _apply_methods_reading_derived_stats()
        if qualname not in _ALLOWED_EAGER_READERS
    ]
    assert not offenders, (
        "apply() computes a stat-dependent value up front, freezing it before "
        "later features/items apply - pass a formula instead "
        "(e.g. SkillBonus(skill, lambda cs: cs.get_wisdom_modifier())):\n"
        + "\n".join(offenders)
    )
