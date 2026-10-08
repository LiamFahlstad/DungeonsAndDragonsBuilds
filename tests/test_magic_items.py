"""
Magic items whose effects are computed (DMG text).
"""

from CharacterContent.Items import Items, Weapons
from Core.Definitions import Ability
from Model.Character import Character


class TestBracersOfArchery:
    # DMG: proficiency with the Longbow and Shortbow, +2 to damage rolls on
    # ranged attacks with them.
    def test_bows_get_proficiency_and_damage(self, make_sources):
        sources = make_sources(dexterity=16)
        longbow, shortbow = Weapons.Longbow(), Weapons.Shortbow()
        character = Character(sources)
        assert not longbow.is_proficient(character)
        # Proficiency and the +2 damage are both recorded on the stat block.
        sources.add_effect(Items.BracersOfArchery())
        character = Character(sources)
        for bow in (longbow, shortbow):
            assert bow.is_proficient(character)
            assert bow.calculate_damage_bonus_int(character) == 3 + 2

    def test_other_weapons_unaffected(self, make_sources):
        sources = make_sources(dexterity=16, strength=16)
        crossbow, sword = Weapons.LightCrossbow(), Weapons.Longsword()
        sources.add_effect(Items.BracersOfArchery())
        character = Character(sources)
        assert crossbow.calculate_damage_bonus_int(character) == 3
        assert sword.calculate_damage_bonus_int(character) == 3
        assert not crossbow.is_proficient(character)

    def test_does_not_change_dexterity(self, make_sources):
        sources = make_sources(dexterity=16)
        sources.add_effect(Items.BracersOfArchery())
        character = Character(sources)
        assert character.get_ability_score(Ability.DEXTERITY) == 16

    def test_does_not_change_the_weapon(self, make_sources):
        sources = make_sources(dexterity=16)
        bow = Weapons.Longbow()
        sources.add_effect(Items.BracersOfArchery())
        assert bow.damage_roll_bonuses == []
        character = Character(sources)
        assert bow.calculate_damage_bonus_int(character) == 3 + 2

    def test_through_sheet_only_when_worn(self):
        from Builds.Tests.SpellSlotTestWizard5 import (
            SpellSlotTestWizard5CharacterBuilder,
        )

        for worn, expected in ((True, 2), (False, 0)):
            sources = SpellSlotTestWizard5CharacterBuilder().build().sources
            bow = Weapons.Longbow()
            sources.add_weapon(bow)
            sources.add_item(Items.BracersOfArchery(is_wearing=worn))
            character = Character(sources).validate()
            bonuses = bow.get_damage_roll_bonuses(character)
            assert sum(b for b, _ in bonuses) == expected
