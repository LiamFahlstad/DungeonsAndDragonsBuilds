"""Spells are order-free grants (Notes/model-refactor-plan.md, Step 9).

Every spell is a SpellGrant stamped by the builder's Grants scope with its
grant level and who grants it; replacements are declared and resolved when
the spells are read. Nothing depends on the order of the calls.
"""

import itertools

import pytest

from CharacterContent.Features.CharacterFeats import EpicBoon, OriginFeats
from CharacterContent.Spells.SpellFactory.Enums import School
from CharacterContent.Spells.SpellLists import ClericLevel0Spells, ClericLevel1Spells
from Core.Definitions import Ability
from Model.Character import Character
from Model.Grants import Grants
from Model.CharacterSources import CharacterSources, SpellSource
from Model.Content.Feature import Feature
from Model.FeatureGrants import IfParentMissing
from Model.Records.GrantStamp import GrantKind, GrantStamp
from Model.Spells import FeatureSpell

INT = Ability.INTELLIGENCE
WIS = Ability.WISDOM
CHA = Ability.CHARISMA


def _names(character: Character) -> list[str]:
    return [spell.name for spell in character.spells]


class TestGrantsScope:
    def test_stamps_level_and_grant(self):
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 5, "Wizard").add_spell("Fireball")
        character = Character(sources)
        (spell,) = character.spells
        assert (spell.grant_level, spell.granted_by) == (5, "Wizard")

    def test_an_origin_feat_lists_its_grants_under_the_feat(self):
        # An origin feat granted through a species (a Human's Versatile) is
        # still an origin feat, and its spells are listed under it.
        sources = CharacterSources(spell_casting_ability=INT)
        feat = OriginFeats.MagicInitiateCleric(
            ClericLevel0Spells.GUIDANCE,
            ClericLevel0Spells.LIGHT,
            ClericLevel1Spells.BLESS,
            WIS,
        )
        feat.grant_to(Grants(sources, 1, "Human", GrantKind.SPECIES))
        character = Character(sources)
        assert character.stamp_of(feat) == GrantStamp(
            1, GrantKind.ORIGIN_FEAT, feat.name
        )
        assert {spell.granted_by for spell in character.spells} == {feat.name}

    def test_keeps_the_free_text_source_label(self):
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 1, "Wizard").add_spell("Shield", source="Chosen spell")
        character = Character(sources)
        assert character.spells[0].source == "Chosen spell"


class TestDuplicates:
    def test_the_same_spell_from_two_grants_is_listed_for_each(self):
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 1, "Wizard").add_cantrip("Prestidigitation")
        Grants(sources, 1, "Rock Gnome").add_cantrip("Prestidigitation")
        character = Character(sources)
        assert sorted(s.granted_by for s in character.spells) == [
            "Rock Gnome",
            "Wizard",
        ]

    def test_the_same_spell_twice_from_one_grant_fails(self):
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 1, "Wizard").add_spell("Shield")
        Grants(sources, 3, "Wizard").add_spell("Shield")
        character = Character(sources)
        with pytest.raises(ValueError, match="already added"):
            character.spells


class TestReplacements:
    def test_a_replacement_keeps_level_grant_and_label(self):
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 1, "Wizard").add_spell("Sleep", source="Chosen spell")
        sources.replace_spell("Sleep", "Shield")
        character = Character(sources)
        (spell,) = character.spells
        assert (spell.name, spell.grant_level, spell.granted_by, spell.source) == (
            "Shield",
            1,
            "Wizard",
            "Chosen spell",
        )

    def test_a_replacement_may_be_declared_before_its_target(self):
        sources = CharacterSources(spell_casting_ability=INT)
        sources.replace_spell("Sleep", "Shield")
        Grants(sources, 1, "Wizard").add_spell("Sleep")
        character = Character(sources)
        assert _names(character) == ["Shield"]

    def test_replacing_a_spell_nobody_grants_fails(self):
        sources = CharacterSources(spell_casting_ability=INT)
        sources.replace_spell("Sleep", "Shield")
        character = Character(sources)
        with pytest.raises(ValueError, match="not found to replace"):
            character.spells

    def test_a_chain_fails(self):
        # Sleep -> Shield -> Mage Armor would depend on which resolves first.
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 1, "Wizard").add_spell("Sleep")
        sources.replace_spell("Sleep", "Shield")
        sources.replace_spell("Shield", "Mage Armor")
        character = Character(sources)
        with pytest.raises(ValueError, match="chain"):
            character.spells

    def test_replacing_into_a_spell_already_known_fails(self):
        # The six builds this step fixed: swapping Sleep for a spell learned
        # at a later level listed that spell twice.
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 1, "Bard").add_spell("Sleep")
        Grants(sources, 4, "Bard").add_spell("Enhance Ability")
        sources.replace_spell("Sleep", "Enhance Ability")
        character = Character(sources)
        with pytest.raises(ValueError, match="already added"):
            character.spells


def test_grant_order_never_changes_the_spells():
    calls = [
        lambda c: Grants(c, 1, "Wizard").add_spell("Sleep", source="Chosen spell"),
        lambda c: Grants(c, 3, "Wizard").add_spell("Misty Step"),
        lambda c: Grants(c, 1, "Rock Gnome").add_cantrip("Mending"),
        lambda c: c.replace_spell("Sleep", "Shield"),
    ]
    results = set()
    for ordered in itertools.permutations(calls):
        sources = CharacterSources(spell_casting_ability=INT)
        for call in ordered:
            call(sources)
        results.add(tuple(Character(sources).spells))
    assert len(results) == 1


class _Ritualist(Feature):
    """A feature that grants its own spells (Feature.granted_spells())."""

    def __init__(self, ability=None):
        super().__init__(name="Ritualist")
        self.ability = ability

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell("Detect Magic", self.ability, "Ritual only"),
            FeatureSpell("Light", source=SpellSource.CHOSEN),
        ]


class _Parent(Feature):
    def __init__(self):
        super().__init__(name="Parent")


class TestFeatureSpells:
    def test_granted_with_the_feature_and_stamped_like_it(self):
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 3, "Fighter", GrantKind.SUBCLASS).add_feature(_Ritualist(WIS))
        detect, light = Character(sources).spells
        assert (detect.name, detect.ability, detect.ruling) == (
            "Detect Magic",
            WIS,
            "Ritual only",
        )
        assert (light.name, light.source) == ("Light", SpellSource.CHOSEN)
        for spell in (detect, light):
            assert (spell.grant_level, spell.kind, spell.granted_by) == (
                3,
                GrantKind.SUBCLASS,
                "Fighter",
            )

    def test_no_ability_uses_the_one_the_character_had_when_granted(self):
        # A Paladin's Divine Smite stays Charisma after levels in Wizard
        # change the character's spellcasting ability.
        sources = CharacterSources(spell_casting_ability=CHA)
        Grants(sources, 2, "Paladin").add_feature(_Ritualist())
        sources.spell_casting_ability = INT
        assert {s.ability for s in Character(sources).spells} == {CHA}

    def test_no_ability_at_grant_falls_back_to_the_final_one(self):
        # A non-caster's ability is only set once the build is finished.
        sources = CharacterSources()
        Grants(sources, 19, "Fighter").add_feature(_Ritualist())
        sources.spell_casting_ability = WIS
        assert {s.ability for s in Character(sources).spells} == {WIS}

    def test_a_dropped_extension_grants_no_spells(self):
        sources = CharacterSources(spell_casting_ability=INT)
        Grants(sources, 3, "Wizard").add_feature(
            _Ritualist(), extends=_Parent, if_missing=IfParentMissing.DROP
        )
        assert Character(sources).spells == []

    def test_an_extension_grants_its_spells(self):
        sources = CharacterSources(spell_casting_ability=INT)
        data = Grants(sources, 3, "Wizard")
        data.add_feature(_Parent())
        data.add_feature(_Ritualist(), extends=_Parent)
        assert _names(Character(sources)) == ["Detect Magic", "Light"]

    def test_granting_a_feature_spell_again_by_hand_fails(self):
        sources = CharacterSources(spell_casting_ability=INT)
        data = Grants(sources, 3, "Wizard")
        data.add_feature(_Ritualist())
        data.add_spell("Light")
        with pytest.raises(ValueError, match="already added"):
            Character(sources).spells


class TestEpicBoonSpells:
    """DI-012: a boon taken at a class level grants its spells, listed
    under the boon's name."""

    def _spells(self, boon):
        sources = CharacterSources(spell_casting_ability=CHA)
        Grants(sources, 19, "Bard").add_feature(boon)
        return {s.name: s for s in Character(sources).spells}

    def test_revelry_grants_ottos_irresistible_dance(self):
        spells = self._spells(EpicBoon.BoonOfRevelry(CHA))
        spell = spells["Otto's Irresistible Dance"]
        assert (spell.ability, spell.source, spell.grant_level) == (
            CHA,
            "Boon of Revelry",
            19,
        )

    def test_siberys_grants_the_chosen_spell_with_its_ability(self):
        boon = EpicBoon.BoonOfSiberys(
            CHA, EpicBoon.SiberysDragonmarkSpell.TELEPORT, INT
        )
        spell = self._spells(boon)["Teleport"]
        assert (spell.ability, spell.source) == (INT, "Boon of Siberys")

    def test_magic_school_mastery_grants_both_spells(self):
        boon = EpicBoon.BoonOfMagicSchoolMastery(
            CHA, School.EVOCATION, "Magic Missile", "Fireball"
        )
        assert set(self._spells(boon)) == {"Magic Missile", "Fireball"}
