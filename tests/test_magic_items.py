"""
Magic items whose effects are computed (DMG text).
"""

from CharacterContent.Items import Items, Weapons
from Core.Definitions import Ability


class TestBracersOfArchery:
    # DMG: proficiency with the Longbow and Shortbow, +2 to damage rolls on
    # ranged attacks with them.
    def test_bows_get_proficiency_and_damage(self, make_character):
        character = make_character(dexterity=16)
        longbow, shortbow = Weapons.Longbow(), Weapons.Shortbow()
        assert not longbow.is_proficient(character)
        # Proficiency and the +2 damage are both recorded on the stat block.
        Items.BracersOfArchery().apply(character)
        for bow in (longbow, shortbow):
            assert bow.is_proficient(character)
            assert bow.calculate_damage_bonus_int(character) == 3 + 2

    def test_other_weapons_unaffected(self, make_character):
        character = make_character(dexterity=16, strength=16)
        crossbow, sword = Weapons.LightCrossbow(), Weapons.Longsword()
        Items.BracersOfArchery().apply(character)
        assert crossbow.calculate_damage_bonus_int(character) == 3
        assert sword.calculate_damage_bonus_int(character) == 3
        assert not crossbow.is_proficient(character)

    def test_does_not_change_dexterity(self, make_character):
        character = make_character(dexterity=16)
        Items.BracersOfArchery().apply(character)
        assert character.get_ability_score(Ability.DEXTERITY) == 16

    def test_does_not_change_the_weapon(self, make_character):
        character = make_character(dexterity=16)
        bow = Weapons.Longbow()
        Items.BracersOfArchery().apply(character)
        assert bow.damage_roll_bonuses == []
        assert bow.calculate_damage_bonus_int(character) == 3 + 2

    def test_through_sheet_only_when_worn(self):
        from Builds.Tests.SpellSlotTestWizard5 import (
            SpellSlotTestWizard5CharacterBuilder,
        )

        for worn, expected in ((True, 2), (False, 0)):
            data = SpellSlotTestWizard5CharacterBuilder().build()
            bow = Weapons.Longbow()
            data.add_weapon(bow)
            data.add_item(Items.BracersOfArchery(is_wearing=worn))
            character = data.setup_character_stat_block()
            bonuses = bow.get_damage_roll_bonuses(character)
            assert sum(b for b, _ in bonuses) == expected
