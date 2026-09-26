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
        Items.BracersOfArchery().apply_to_weapons([longbow, shortbow])
        for bow in (longbow, shortbow):
            assert bow.player_is_proficient
            assert bow.calculate_damage_bonus_int(character) == 3 + 2

    def test_other_weapons_unaffected(self, make_character):
        character = make_character(dexterity=16, strength=16)
        crossbow, sword = Weapons.LightCrossbow(), Weapons.Longsword()
        Items.BracersOfArchery().apply_to_weapons([crossbow, sword])
        assert crossbow.calculate_damage_bonus_int(character) == 3
        assert sword.calculate_damage_bonus_int(character) == 3
        assert not crossbow.player_is_proficient

    def test_does_not_change_dexterity(self, make_character):
        character = make_character(dexterity=16)
        Items.BracersOfArchery().apply(character)
        assert character.get_ability_score(Ability.DEXTERITY) == 16

    def test_idempotent(self):
        bow = Weapons.Longbow()
        bracers = Items.BracersOfArchery()
        bracers.apply_to_weapons([bow])
        bracers.apply_to_weapons([bow])
        assert sum(b for b, _ in bow.damage_roll_bonuses) == 2

    def test_through_sheet_only_when_worn(self):
        from Builds.Tests.SpellSlotTestWizard5 import (
            SpellSlotTestWizard5CharacterBuilder,
        )

        for worn, expected in ((True, 2), (False, 0)):
            data = SpellSlotTestWizard5CharacterBuilder().build()
            bow = Weapons.Longbow()
            data.add_weapon(bow)
            data.add_item(Items.BracersOfArchery(is_wearing=worn))
            data.setup_character_stat_block()
            assert sum(b for b, _ in bow.damage_roll_bonuses) == expected
