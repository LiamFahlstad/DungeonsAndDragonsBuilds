"""
Rules that setup_character_stat_block() enforces on the whole sheet:
- at most one worn body armor (a shield on top is fine);
- at most three attuned magic items (DMG: "no more than three").
"""

import pytest

from Builds.Tests.SpellSlotTestWizard5 import SpellSlotTestWizard5CharacterBuilder
from CharacterContent.Items import Armor, Items


@pytest.fixture
def wizard():
    return SpellSlotTestWizard5CharacterBuilder().build()


def attunement_items(n, is_wearing=True):
    classes = [
        Items.RingOfIntellect,
        Items.CloakOfProtection,
        Items.BracersOfArchery,
        Items.GauntletsOfStrength,
    ]
    return [cls(is_wearing=is_wearing) for cls in classes[:n]]


class TestArmorRule:
    def test_two_body_armors_rejected(self, wizard):
        wizard.add_armor(Armor.LeatherArmor())
        wizard.add_armor(Armor.PaddedArmor())
        with pytest.raises(ValueError, match="multiple armors"):
            wizard.setup_character_stat_block()

    def test_armor_plus_shield_allowed(self, wizard):
        wizard.add_armor(Armor.LeatherArmor())
        wizard.add_armor(Armor.ShieldArmor())
        wizard.setup_character_stat_block()

    def test_unworn_second_armor_allowed(self, wizard):
        wizard.add_armor(Armor.LeatherArmor())
        wizard.add_armor(Armor.PaddedArmor(is_wearing=False))
        wizard.setup_character_stat_block()


class TestAttunementLimit:
    def test_three_allowed(self, wizard):
        for item in attunement_items(3):
            wizard.add_item(item)
        wizard.setup_character_stat_block()

    def test_four_rejected(self, wizard):
        for item in attunement_items(4):
            wizard.add_item(item)
        with pytest.raises(ValueError, match="attune"):
            wizard.setup_character_stat_block()

    def test_unworn_items_not_attuned(self, wizard):
        for item in attunement_items(3):
            wizard.add_item(item)
        wizard.add_item(Items.GauntletsOfStrength(is_wearing=False))
        wizard.setup_character_stat_block()
