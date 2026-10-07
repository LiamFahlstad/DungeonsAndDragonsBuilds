"""
The Character model (Model/Character.py): one object holding the sources
and answering every query, with evaluation cached under a version key.
"""

import subprocess
import sys

import pytest

from Model.Character import Character
from Builds.Tests.SpellSlotTestPaladin5 import SpellSlotTestPaladin5CharacterBuilder
from Model.Content.Feature import Feature
from Model.Content.Improvements import AbilityScoreBonus, SkillBonus, SkillProficiency
from CharacterContent.Items import Items
from Core.Definitions import Ability, CharacterClass, Skill
from Model.Effects import Ledger
from Model.Recorder import SealedError
from tests._fake_view import FakeView
from tests._grants import grant
from Model.FeatureGrants import IfParentMissing
from Presentation.FeatureCards import feature_label
from Presentation.FeatureOrder import feature_sort_key
from Model.Records.GrantStamp import GrantKind


def test_a_build_is_one_character():
    data = SpellSlotTestPaladin5CharacterBuilder().build()
    assert type(data) is Character
    assert data.validate() is data


class TestReEvaluatesAfterEveryKindOfChange:
    def test_assigning_a_field(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        before = data.calculate_speed()
        data.base_speed = data.base_speed + 10
        assert data.calculate_speed() == before + 10

    def test_changing_the_inventory_directly(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        before = data.calculate_armor_class()
        data.inventory.add_adventuring_gear(
            "Loot", items=[(Items.CloakOfProtection(), 1)]
        )
        assert data.calculate_armor_class() == before + 1

    def test_extending_a_feature_after_a_query(self):
        from CharacterContent.Features.SubClassFeatures2014.Cleric import (
            ClericForgeFeatures,
        )
        from Core.Definitions import DamageType
        from tests.test_all_builds import ALL_BUILDS

        data = type(ALL_BUILDS["Y2014DruidDreamsSomnaDriftwillowCharacterBuilder"])()
        data = data.build()
        assert not data.is_immune_to_damage(DamageType.FIRE)
        grant(data).add_feature(
            ClericForgeFeatures.SaintOfForgeAndFire(), extends=data.features[0]
        )
        assert data.is_immune_to_damage(DamageType.FIRE)

    def test_evaluation_never_changes_the_base_scores(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        base = [data.base_abilities.get_score(a) for a in Ability]
        final = [data.get_ability_score(a) for a in Ability]
        data._changed()
        assert [data.get_ability_score(a) for a in Ability] == final
        assert [data.base_abilities.get_score(a) for a in Ability] == base


def test_requirements_are_checked_by_validate_not_by_queries(make_character):
    # STR/DEX 10: a Fighter/Wizard misses Fighter's multiclass prerequisite.
    character = make_character(
        levels={CharacterClass.FIGHTER: 1, CharacterClass.WIZARD: 1},
        intelligence=13,
    )
    assert character.calculate_hit_points() > 0
    with pytest.raises(ValueError, match="Multiclassing"):
        character.validate()


def test_model_package_imports_nothing_from_character_content():
    # CharacterContent imports the model (for Character and Effects), so the
    # model importing CharacterContent at load time would be an import cycle.
    code = (
        "import sys, pathlib, importlib; "
        "[importlib.import_module('Model.' + p.stem) "
        "for p in pathlib.Path('Model').glob('*.py') if p.stem != '__init__']; "
        "loaded = [m for m in sys.modules if m.startswith('CharacterContent')]; "
        "assert not loaded, loaded"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


class TestTheEvaluatedLedgerIsSealed:
    """Everything the Character answers comes from a Ledger it rebuilds from
    its sources, so a write into an evaluated part would be lost at the next
    rebuild. It raises instead."""

    def test_a_part_rejects_writes_after_evaluation(self, make_character):
        character = make_character()
        character.validate()
        with pytest.raises(SealedError):
            character.ledger.skills.add_skill_proficiency(Skill.STEALTH)
        with pytest.raises(SealedError):
            character.ledger.ability_increases.add(Ability.WISDOM, 2)

    def test_a_part_inside_a_part_is_sealed_too(self, make_character):
        character = make_character()
        character.add_effect(SkillBonus(Skill.ARCANA, 1, source="Test"))
        bonuses = character.ledger.skills._bonuses[Skill.ARCANA]
        with pytest.raises(SealedError):
            bonuses.add(1, "Test")


class TestBaseAbilitiesAreASource:
    """The base scores are immutable: changing one in place used to leave the
    cached evaluation stale, because nothing told the Character."""

    def test_a_base_score_cannot_be_changed_in_place(self, make_character):
        character = make_character(strength=10)
        with pytest.raises(AttributeError):
            character.base_abilities.strength = 18

    def test_assigning_new_base_scores_re_evaluates(self, make_character):
        character = make_character(strength=10)
        assert character.get_ability_score(Ability.STRENGTH) == 10
        character.base_abilities = character.base_abilities.with_scores(strength=18)
        assert character.get_ability_score(Ability.STRENGTH) == 18

    def test_evaluating_never_changes_the_base_scores(self, make_character):
        character = make_character(strength=10)
        character.add_effect(
            AbilityScoreBonus([(Ability.STRENGTH, 2)], total=2, max_score=20)
        )
        for _ in range(2):
            character.base_speed = character.base_speed + 5  # re-evaluate
            assert character.get_ability_score(Ability.STRENGTH) == 12
        assert character.base_abilities.strength == 10

    def test_a_fresh_ledger_is_empty(self):
        ledger = Ledger()
        view = FakeView()
        assert ledger.ability_increases.score(Ability.STRENGTH, view) == 10
        assert ledger.speed.total(view) == 30
        assert ledger.spellcasting.spell_slots(view) == {}


class TestAddEffect:
    def test_survives_re_evaluation(self, make_character):
        character = make_character()
        character.add_effect(SkillProficiency([Skill.STEALTH]))
        assert character.is_proficient_in_skill(Skill.STEALTH)
        # Any change to the sources rebuilds the Ledger; the effect is a
        # source, so it's recorded again.
        character.base_speed = 35
        assert character.calculate_speed() == 35
        assert character.is_proficient_in_skill(Skill.STEALTH)

    def test_is_a_change_to_the_sources(self, make_character):
        character = make_character(wisdom=10)
        assert character.get_ability_score(Ability.WISDOM) == 10
        character.add_effect(AbilityScoreBonus([(Ability.WISDOM, 2)], total=2))
        assert character.get_ability_score(Ability.WISDOM) == 12


def test_apply_order_change_re_evaluates(make_character):
    applied = []

    class _Recording:
        def __init__(self, label):
            self.label = label

        def apply(self, effects):
            applied.append(self.label)

    character = make_character()
    character.add_effect(_Recording("a"))
    character.add_effect(_Recording("b"))
    character.validate()
    assert applied == ["a", "b"]
    applied.clear()
    character._apply_order = lambda effects: effects[::-1]
    character.validate()
    assert applied == ["b", "a"]


class _Parent(Feature):
    pass


class _Child(Feature):
    pass


class TestDeclaredExtensions:
    """Extensions are declared grants (add_feature(child, extends=...)),
    resolved when the character is read - so parent and child may be granted
    in either order, and nothing is changed on a feature after granting."""

    def test_child_granted_before_its_parent(self, make_character):
        character = make_character()
        child = _Child(name="Child")
        grant(character).add_feature(child, extends=_Parent)
        parent = _Parent(name="Parent")
        grant(character).add_feature(parent)
        assert character.extensions_of(parent) == [child]
        assert list(character.iter_features_with_extensions()) == [parent, child]

    def test_extends_a_specific_instance(self, make_character):
        character = make_character()
        first, second = _Parent(name="First"), _Parent(name="Second")
        child = _Child(name="Child")
        grant(character).add_feature(first)
        grant(character).add_feature(second)
        grant(character).add_feature(child, extends=second)
        assert character.extensions_of(first) == []
        assert character.extensions_of(second) == [child]

    def test_missing_parent_raises(self, make_character):
        character = make_character()
        grant(character).add_feature(_Child(name="Child"), extends=_Parent)
        with pytest.raises(ValueError, match="extends _Parent, which isn't granted"):
            character.validate()

    def test_ambiguous_parent_type_raises(self, make_character):
        character = make_character()
        grant(character).add_feature(_Parent(name="First"))
        grant(character).add_feature(_Parent(name="Second"))
        grant(character).add_feature(_Child(name="Child"), extends=_Parent)
        with pytest.raises(ValueError, match="2 granted features match it"):
            character.validate()

    def test_if_missing_drop(self, make_character):
        character = make_character()
        grant(character).add_feature(
            _Child(name="Child"), extends=_Parent, if_missing=IfParentMissing.DROP
        )
        character.validate()
        assert list(character.iter_features_with_extensions()) == []

    def test_if_missing_standalone(self, make_character):
        character = make_character()
        child = _Child(name="Child")
        grant(character).add_feature(
            child, extends=_Parent, if_missing=IfParentMissing.STANDALONE
        )
        assert character.top_level_features() == [child]
        parent = _Parent(name="Parent")
        grant(character).add_feature(parent)
        assert character.top_level_features() == [parent]
        assert character.extensions_of(parent) == [child]

    def test_if_missing_needs_extends(self, make_character):
        with pytest.raises(ValueError, match="only applies with extends"):
            grant(make_character()).add_feature(
                _Child(), if_missing=IfParentMissing.DROP
            )

    def test_a_shared_feature_instance_keeps_extensions_per_character(
        self, make_character
    ):
        shared = _Parent(name="Shared")
        first, second = make_character(), make_character()
        grant(first).add_feature(shared)
        grant(second).add_feature(shared)
        child = _Child(name="Child")
        grant(first).add_feature(child, extends=shared)
        assert first.extensions_of(shared) == [child]
        assert second.extensions_of(shared) == []


class TestAbjureFoes:
    """2024 PHB: a Paladin gains Abjure Foes as a Channel Divinity option at
    level 9. Worked out from the Paladin level, not added to the feature
    after it was granted."""

    def _descriptions(self, make_character, paladin_level):
        """(Channel Divinity's description, Abjure Foes' own text)."""
        from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures

        character = make_character(levels={CharacterClass.PALADIN: paladin_level})
        channel_divinity = PaladinFeatures.ChannelDivinity()
        channel_divinity.add_spell("Divine Sense")
        grant(character).add_feature(channel_divinity)
        abjure_foes = PaladinFeatures.AbjureFoes().get_description(character)
        return channel_divinity.get_description(character), abjure_foes

    def test_not_before_level_9(self, make_character):
        description, abjure_foes = self._descriptions(make_character, 8)
        assert abjure_foes not in description

    def test_from_level_9(self, make_character):
        description, abjure_foes = self._descriptions(make_character, 9)
        assert abjure_foes in description


class TestGrantStamps:
    """Every feature is stamped with where it was granted (Model/Grants.py),
    and the sheet orders features by the stamp - never by grant order."""

    def test_grants_scope_stamps_level_kind_and_source(self, make_character):
        from Model.Grants import Grants

        character = make_character()
        feature = _Parent(name="Rage")
        Grants(character, 3, "Barbarian", GrantKind.CLASS).add_feature(feature)
        stamp = character.stamp_of(feature)
        assert (stamp.level, stamp.kind, stamp.granted_by) == (
            3,
            GrantKind.CLASS,
            "Barbarian",
        )

    def test_same_name_features_order_by_who_granted_them(self, make_character):
        from Model.Grants import Grants

        character = make_character()
        from_class = _Parent(name="Expertise")
        from_species = _Parent(name="Expertise")
        Grants(character, 1, "Rogue", GrantKind.CLASS).add_feature(from_class)
        Grants(character, 1, "Elf", GrantKind.SPECIES).add_feature(from_species)
        ordered = sorted(
            character.features,
            key=lambda feature: feature_sort_key(character, feature),
        )
        assert ordered == [from_species, from_class]

    def test_extensions_order_by_grant_level_then_name(self, make_character):
        from Model.Grants import Grants

        character = make_character()
        parent = _Parent(name="Rage")
        late = _Child(name="Instinctive Pounce")
        early = _Child(name="Relentless Rage")
        Grants(character, 7, "Barbarian", GrantKind.CLASS).add_feature(
            late, extends=parent
        )
        Grants(character, 1, "Barbarian", GrantKind.CLASS).add_feature(parent)
        Grants(character, 5, "Barbarian", GrantKind.CLASS).add_feature(
            early, extends=parent
        )
        assert character.extensions_of(parent) == [early, late]


class TestFeatureLabels:
    """A card's origin label agrees with where the feature was granted."""

    def _granted(
        self, make_character, feature, level, kind=GrantKind.CLASS, source="Bard"
    ):
        from Model.Grants import Grants

        character = make_character()
        Grants(character, level, source, kind).add_feature(feature)
        return character

    def test_a_level_label_takes_the_stamped_level(self, make_character):
        # The second Expertise is granted at level 9, but its origin says 1.
        expertise = _Parent(name="Expertise", origin="Bard Level 1")
        character = self._granted(make_character, expertise, 9)
        assert feature_label(expertise, character) == "Bard Level 9"

    def test_a_subclass_prefix_is_kept(self, make_character):
        feature = _Parent(name="Bladesong", origin="Bladesinger Wizard Level 3")
        character = self._granted(
            make_character, feature, 3, GrantKind.SUBCLASS, "Wizard"
        )
        assert feature_label(feature, character) == "Bladesinger Wizard Level 3"

    def test_free_text_is_kept(self, make_character):
        feature = _Parent(name="Resourceful", origin="Human Trait")
        character = self._granted(
            make_character, feature, 1, GrantKind.SPECIES, "Human"
        )
        assert feature_label(feature, character) == "Human Trait"

    def test_an_empty_class_label_names_the_class_level(self, make_character):
        feature = _Parent(name="Class Skill Proficiencies")
        character = self._granted(
            make_character, feature, 1, GrantKind.CLASS, "Paladin"
        )
        assert feature_label(feature, character) == "Paladin Level 1"

    def test_a_feature_not_granted_keeps_its_origin(self, make_character):
        feature = _Parent(name="Expertise", origin="Bard Level 1")
        assert feature_label(feature, make_character()) == "Bard Level 1"

    def test_a_general_feat_is_labeled_with_the_level_it_was_taken(
        self, make_character
    ):
        from CharacterContent.Features.CharacterFeats import GeneralFeats

        feat = GeneralFeats.AbilityScoreImprovement(
            [(Ability.STRENGTH, 1), (Ability.CONSTITUTION, 1)]
        )
        character = self._granted(make_character, feat, 8, GrantKind.CLASS, "Fighter")
        assert feature_label(feat, character) == "Fighter Level 8"


class TestFeatsTakenOnce:
    """2024 PHB: a feat can be taken only once unless it's Repeatable."""

    def test_a_feat_granted_twice_fails(self, make_character):
        from CharacterContent.Features.CharacterFeats import OriginFeats

        character = make_character()
        grant(character).add_feature(OriginFeats.Tough(), kind=GrantKind.BACKGROUND)
        grant(character).add_feature(OriginFeats.Tough(), kind=GrantKind.SPECIES)
        with pytest.raises(ValueError, match="Tough is granted 2 times"):
            character.validate()

    def test_a_repeatable_feat_may_be_taken_again(self, make_character):
        from CharacterContent.Features.CharacterFeats import GeneralFeats

        character = make_character(strength=12, constitution=12)
        for ability in (Ability.STRENGTH, Ability.CONSTITUTION):
            grant(character).add_feature(
                GeneralFeats.AbilityScoreImprovement([(ability, 2)])
            )
        character.validate()

    def test_class_features_repeat_freely(self, make_character):
        character = make_character()
        grant(character).add_feature(_Parent(name="Expertise"))
        grant(character).add_feature(_Parent(name="Expertise"))
        character.validate()
