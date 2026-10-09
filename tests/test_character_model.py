"""
The Character model (Model/Character.py): an immutable character built from
its CharacterSources, answering every query from one evaluation.
"""

import subprocess
import sys

import pytest

from Model.Character import Character
from Model.CharacterSources import CharacterSources
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


class TestACharacterIsBuiltFromItsSources:
    """A Character never changes: a different character is a new Character
    built from changed sources."""

    def test_it_has_no_mutators(self):
        mutators = [
            name
            for name in dir(Character)
            if name.startswith(("add_", "set_", "replace_", "record_"))
        ]
        assert not mutators
        # Nor a way to reach one: the inventory is read through properties.
        assert not hasattr(Character, "inventory")

    def test_a_required_source_left_unset_raises_on_read(self):
        character = Character(CharacterSources())
        with pytest.raises(ValueError, match="speed must be set"):
            character.base_speed

    def test_its_fields_are_read_only(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        with pytest.raises(AttributeError):
            # The assignment the type checker rejects is the point of the test.
            data.base_speed = 40  # pyright: ignore[reportAttributeAccessIssue]

    def test_changing_its_sources_afterwards_does_not_change_it(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        before = data.calculate_speed()
        sources = data.sources
        sources.base_speed = sources.base_speed + 10
        assert data.calculate_speed() == before
        assert Character(sources).calculate_speed() == before + 10

    def test_the_sources_it_was_built_from_are_copied(self, make_sources):
        sources = make_sources()
        character = Character(sources)
        sources.add_effect(SkillProficiency([Skill.STEALTH]))
        assert not character.is_proficient_in_skill(Skill.STEALTH)
        assert Character(sources).is_proficient_in_skill(Skill.STEALTH)

    def test_its_inventory_is_a_copy(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        before = data.calculate_armor_class()
        sources = data.sources
        sources.inventory.add_adventuring_gear(
            "Loot", items=[(Items.CloakOfProtection(), 1)]
        )
        assert data.calculate_armor_class() == before
        assert Character(sources).calculate_armor_class() == before + 1

    def test_evaluation_never_changes_the_base_scores(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        base = [data.base_abilities.get_score(a) for a in Ability]
        final = [data.get_ability_score(a) for a in Ability]
        again = Character(data.sources)
        assert [again.get_ability_score(a) for a in Ability] == final
        assert [again.base_abilities.get_score(a) for a in Ability] == base


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

    def test_a_part_inside_a_part_is_sealed_too(self, make_sources):
        sources = make_sources()
        sources.add_effect(SkillBonus(Skill.ARCANA, 1, source="Test"))
        character = Character(sources)
        bonuses = character.ledger.skills._bonuses[Skill.ARCANA]
        with pytest.raises(SealedError):
            bonuses.add(1, "Test")


class TestBaseAbilitiesAreASource:
    """The base scores are immutable: different scores are new sources, and
    a new Character built from them."""

    def test_a_base_score_cannot_be_changed_in_place(self, make_sources):
        sources = make_sources(strength=10)
        with pytest.raises(AttributeError):
            sources.base_abilities.strength = 18

    def test_new_base_scores_make_a_new_character(self, make_sources):
        sources = make_sources(strength=10)
        character = Character(sources)
        assert character.get_ability_score(Ability.STRENGTH) == 10
        sources.base_abilities = sources.base_abilities.with_scores(strength=18)
        character = Character(sources)
        assert character.get_ability_score(Ability.STRENGTH) == 18

    def test_evaluating_never_changes_the_base_scores(self, make_sources):
        sources = make_sources(strength=10)
        sources.add_effect(
            AbilityScoreBonus([(Ability.STRENGTH, 2)], total=2, max_score=20)
        )
        for _ in range(2):
            character = Character(sources)
            assert character.get_ability_score(Ability.STRENGTH) == 12
        assert sources.base_abilities.strength == 10

    def test_a_fresh_ledger_is_empty(self):
        ledger = Ledger()
        view = FakeView()
        assert ledger.ability_increases.score(Ability.STRENGTH, view) == 10
        assert ledger.speed.total(view) == 30
        assert ledger.spellcasting.spell_slots(view) == {}


class TestAddEffect:
    def test_every_character_built_from_the_sources_records_it(self, make_sources):
        sources = make_sources()
        sources.add_effect(SkillProficiency([Skill.STEALTH]))
        character = Character(sources)
        assert character.is_proficient_in_skill(Skill.STEALTH)
        # The effect is a source, so it's recorded again for the next one.
        sources.base_speed = 35
        character = Character(sources)
        assert character.calculate_speed() == 35
        assert character.is_proficient_in_skill(Skill.STEALTH)

    def test_is_a_change_to_the_sources(self, make_sources):
        sources = make_sources(wisdom=10)
        character = Character(sources)
        assert character.get_ability_score(Ability.WISDOM) == 10
        sources.add_effect(AbilityScoreBonus([(Ability.WISDOM, 2)], total=2))
        character = Character(sources)
        assert character.get_ability_score(Ability.WISDOM) == 12


def test_apply_order_sets_the_order_effects_apply_in(make_sources):
    applied = []

    class _Recording:
        def __init__(self, label):
            self.label = label

        def apply(self, effects):
            applied.append(self.label)

    sources = make_sources()
    sources.add_effect(_Recording("a"))
    sources.add_effect(_Recording("b"))
    Character(sources).validate()
    assert applied == ["a", "b"]
    applied.clear()
    Character(sources, apply_order=lambda effects: effects[::-1]).validate()
    assert applied == ["b", "a"]


class _Parent(Feature):
    pass


class _Child(Feature):
    pass


class TestDeclaredExtensions:
    """Extensions are declared grants (add_feature(child, extends=...)),
    resolved when the character is read - so parent and child may be granted
    in either order, and nothing is changed on a feature after granting."""

    def test_child_granted_before_its_parent(self, make_sources):
        sources = make_sources()
        child = _Child(name="Child")
        grant(sources).add_feature(child, extends=_Parent)
        parent = _Parent(name="Parent")
        grant(sources).add_feature(parent)
        character = Character(sources)
        assert character.extensions_of(parent) == [child]
        assert list(character.iter_features_with_extensions()) == [parent, child]

    def test_extends_a_specific_instance(self, make_sources):
        sources = make_sources()
        first, second = _Parent(name="First"), _Parent(name="Second")
        child = _Child(name="Child")
        grant(sources).add_feature(first)
        grant(sources).add_feature(second)
        grant(sources).add_feature(child, extends=second)
        character = Character(sources)
        assert character.extensions_of(first) == []
        assert character.extensions_of(second) == [child]

    def test_missing_parent_raises(self, make_sources):
        sources = make_sources()
        grant(sources).add_feature(_Child(name="Child"), extends=_Parent)
        character = Character(sources)
        with pytest.raises(ValueError, match="extends _Parent, which isn't granted"):
            character.validate()

    def test_ambiguous_parent_type_raises(self, make_sources):
        sources = make_sources()
        grant(sources).add_feature(_Parent(name="First"))
        grant(sources).add_feature(_Parent(name="Second"))
        grant(sources).add_feature(_Child(name="Child"), extends=_Parent)
        character = Character(sources)
        with pytest.raises(ValueError, match="2 granted features match it"):
            character.validate()

    def test_if_missing_drop(self, make_sources):
        sources = make_sources()
        grant(sources).add_feature(
            _Child(name="Child"), extends=_Parent, if_missing=IfParentMissing.DROP
        )
        character = Character(sources)
        character.validate()
        assert list(character.iter_features_with_extensions()) == []

    def test_if_missing_standalone(self, make_sources):
        sources = make_sources()
        child = _Child(name="Child")
        grant(sources).add_feature(
            child, extends=_Parent, if_missing=IfParentMissing.STANDALONE
        )
        character = Character(sources)
        assert character.top_level_features() == [child]
        parent = _Parent(name="Parent")
        grant(sources).add_feature(parent)
        character = Character(sources)
        assert character.top_level_features() == [parent]
        assert character.extensions_of(parent) == [child]

    def test_if_missing_needs_extends(self, make_sources):
        with pytest.raises(ValueError, match="only applies with extends"):
            grant(make_sources()).add_feature(_Child(), if_missing=IfParentMissing.DROP)

    def test_a_shared_feature_instance_keeps_extensions_per_character(
        self, make_sources
    ):
        shared = _Parent(name="Shared")
        first, second = make_sources(), make_sources()
        grant(first).add_feature(shared)
        grant(second).add_feature(shared)
        child = _Child(name="Child")
        grant(first).add_feature(child, extends=shared)
        assert Character(first).extensions_of(shared) == [child]
        assert Character(second).extensions_of(shared) == []


class TestAbjureFoes:
    """2024 PHB: a Paladin gains Abjure Foes as a Channel Divinity option at
    level 9. Worked out from the Paladin level, not added to the feature
    after it was granted."""

    def _descriptions(self, make_sources, paladin_level):
        """(Channel Divinity's description, Abjure Foes' own text)."""
        from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures

        sources = make_sources(levels={CharacterClass.PALADIN: paladin_level})
        channel_divinity = PaladinFeatures.ChannelDivinity()
        channel_divinity.add_spell("Divine Sense")
        grant(sources).add_feature(channel_divinity)
        character = Character(sources)
        abjure_foes = PaladinFeatures.AbjureFoes().get_description(character)
        return channel_divinity.get_description(character), abjure_foes

    def test_not_before_level_9(self, make_sources):
        description, abjure_foes = self._descriptions(make_sources, 8)
        assert abjure_foes not in description

    def test_from_level_9(self, make_sources):
        description, abjure_foes = self._descriptions(make_sources, 9)
        assert abjure_foes in description


class TestGrantStamps:
    """Every feature is stamped with where it was granted (Model/Grants.py),
    and the sheet orders features by the stamp - never by grant order."""

    def test_grants_scope_stamps_level_kind_and_source(self, make_sources):
        from Model.Grants import Grants

        sources = make_sources()
        feature = _Parent(name="Rage")
        Grants(sources, 3, "Barbarian", GrantKind.CLASS).add_feature(feature)
        character = Character(sources)
        stamp = character.stamp_of(feature)
        assert (stamp.level, stamp.kind, stamp.granted_by) == (
            3,
            GrantKind.CLASS,
            "Barbarian",
        )

    def test_same_name_features_order_by_who_granted_them(self, make_sources):
        from Model.Grants import Grants

        sources = make_sources()
        from_class = _Parent(name="Expertise")
        from_species = _Parent(name="Expertise")
        Grants(sources, 1, "Rogue", GrantKind.CLASS).add_feature(from_class)
        Grants(sources, 1, "Elf", GrantKind.SPECIES).add_feature(from_species)
        character = Character(sources)
        ordered = sorted(
            character.features,
            key=lambda feature: feature_sort_key(character, feature),
        )
        assert ordered == [from_species, from_class]

    def test_extensions_order_by_grant_level_then_name(self, make_sources):
        from Model.Grants import Grants

        sources = make_sources()
        parent = _Parent(name="Rage")
        late = _Child(name="Instinctive Pounce")
        early = _Child(name="Relentless Rage")
        Grants(sources, 7, "Barbarian", GrantKind.CLASS).add_feature(
            late, extends=parent
        )
        Grants(sources, 1, "Barbarian", GrantKind.CLASS).add_feature(parent)
        Grants(sources, 5, "Barbarian", GrantKind.CLASS).add_feature(
            early, extends=parent
        )
        character = Character(sources)
        assert character.extensions_of(parent) == [early, late]


class TestFeatureLabels:
    """A card's origin label agrees with where the feature was granted."""

    def _granted(
        self, make_sources, feature, level, kind=GrantKind.CLASS, source="Bard"
    ):
        from Model.Grants import Grants

        sources = make_sources()
        Grants(sources, level, source, kind).add_feature(feature)
        return Character(sources)

    def test_a_level_label_takes_the_stamped_level(self, make_sources):
        # The second Expertise is granted at level 9, but its origin says 1.
        expertise = _Parent(name="Expertise", origin="Bard Level 1")
        character = self._granted(make_sources, expertise, 9)
        assert feature_label(expertise, character) == "Bard Level 9"

    def test_a_subclass_prefix_is_kept(self, make_sources):
        feature = _Parent(name="Bladesong", origin="Bladesinger Wizard Level 3")
        character = self._granted(
            make_sources, feature, 3, GrantKind.SUBCLASS, "Wizard"
        )
        assert feature_label(feature, character) == "Bladesinger Wizard Level 3"

    def test_free_text_is_kept(self, make_sources):
        feature = _Parent(name="Resourceful", origin="Human Trait")
        character = self._granted(make_sources, feature, 1, GrantKind.SPECIES, "Human")
        assert feature_label(feature, character) == "Human Trait"

    def test_an_empty_class_label_names_the_class_level(self, make_sources):
        feature = _Parent(name="Class Skill Proficiencies")
        character = self._granted(make_sources, feature, 1, GrantKind.CLASS, "Paladin")
        assert feature_label(feature, character) == "Paladin Level 1"

    def test_a_feature_not_granted_keeps_its_origin(self, make_character):
        feature = _Parent(name="Expertise", origin="Bard Level 1")
        assert feature_label(feature, make_character()) == "Bard Level 1"

    def test_a_general_feat_is_labeled_with_the_level_it_was_taken(self, make_sources):
        from CharacterContent.Features.CharacterFeats import GeneralFeats

        feat = GeneralFeats.AbilityScoreImprovement(
            [(Ability.STRENGTH, 1), (Ability.CONSTITUTION, 1)]
        )
        character = self._granted(make_sources, feat, 8, GrantKind.CLASS, "Fighter")
        assert feature_label(feat, character) == "Fighter Level 8"


class TestFeatsTakenOnce:
    """2024 PHB: a feat can be taken only once unless it's Repeatable."""

    def test_a_feat_granted_twice_fails(self, make_sources):
        from CharacterContent.Features.CharacterFeats import OriginFeats

        sources = make_sources()
        grant(sources, kind=GrantKind.BACKGROUND).add_feature(OriginFeats.Tough())
        grant(sources, kind=GrantKind.SPECIES).add_feature(OriginFeats.Tough())
        character = Character(sources)
        with pytest.raises(ValueError, match="Tough is granted 2 times"):
            character.validate()

    def test_a_repeatable_feat_may_be_taken_again(self, make_sources):
        from CharacterContent.Features.CharacterFeats import GeneralFeats

        sources = make_sources(strength=12, constitution=12)
        for ability in (Ability.STRENGTH, Ability.CONSTITUTION):
            grant(sources).add_feature(
                GeneralFeats.AbilityScoreImprovement([(ability, 2)])
            )
        character = Character(sources)
        character.validate()

    def test_class_features_repeat_freely(self, make_sources):
        sources = make_sources()
        grant(sources).add_feature(_Parent(name="Expertise"))
        grant(sources).add_feature(_Parent(name="Expertise"))
        character = Character(sources)
        character.validate()
