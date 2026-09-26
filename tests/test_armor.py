"""
Armor stats and AC calculation (CharacterContent/Items/Armor).

The armor table is transcribed from the PHB, not read back from the code.
"""

import pytest

from CharacterContent.Items import Armor
from Core.Definitions import ArmorType, DiceRollCondition, Skill

L, M, H = ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.HEAVY

# class, type, base AC, Str requirement, stealth disadvantage, weight lb, cost GP
PHB_ARMOR = [
    (Armor.PaddedArmor, L, 11, None, True, 8, 5),
    (Armor.LeatherArmor, L, 11, None, False, 10, 10),
    (Armor.StuddedLeatherArmor, L, 12, None, False, 13, 45),
    (Armor.HideArmor, M, 12, None, False, 12, 10),
    (Armor.ChainShirtArmor, M, 13, None, False, 20, 50),
    (Armor.ScaleMailArmor, M, 14, None, True, 45, 50),
    (Armor.BreastplateArmor, M, 14, None, False, 20, 400),
    (Armor.HalfPlateArmor, M, 15, None, True, 40, 750),
    (Armor.RingMailArmor, H, 14, None, True, 40, 30),
    (Armor.ChainMailArmor, H, 16, 13, True, 55, 75),
    (Armor.SplintArmor, H, 17, 15, True, 60, 200),
    (Armor.PlateArmor, H, 18, 15, True, 65, 1500),
]


@pytest.mark.parametrize(
    "armor_class,armor_type,base_ac,strength,stealth,weight,cost",
    PHB_ARMOR,
    ids=[row[0].__name__ for row in PHB_ARMOR],
)
def test_armor_matches_phb(
    armor_class, armor_type, base_ac, strength, stealth, weight, cost
):
    armor = armor_class()
    assert armor.armor_type == armor_type
    assert armor.base_ac == base_ac
    assert armor.strength_requirement == strength
    assert armor.stealth_disadvantage == stealth
    assert armor.weight == weight
    assert armor.value == cost
    assert not armor.is_shield


def test_shield_matches_phb():
    shield = Armor.ShieldArmor()
    assert shield.is_shield
    assert shield.ac_bonus == 2
    assert shield.weight == 6
    assert shield.value == 10


class TestArmorClass:
    def test_unarmored_is_10_plus_dex(self, make_character):
        character = make_character(dexterity=16)
        assert character.calculate_armor_class() == 13

    def test_light_armor_adds_full_dex(self, make_character):
        character = make_character(dexterity=20)
        Armor.StuddedLeatherArmor().apply(character)
        assert character.calculate_armor_class() == 12 + 5

    def test_medium_armor_caps_dex_at_2(self, make_character):
        character = make_character(dexterity=20)
        Armor.BreastplateArmor().apply(character)
        assert character.calculate_armor_class() == 14 + 2

    def test_medium_armor_below_cap(self, make_character):
        character = make_character(dexterity=12)
        Armor.HalfPlateArmor().apply(character)
        assert character.calculate_armor_class() == 15 + 1

    def test_medium_armor_negative_dex_applies(self, make_character):
        character = make_character(dexterity=8, strength=15)
        Armor.HideArmor().apply(character)
        assert character.calculate_armor_class() == 12 - 1

    def test_heavy_armor_ignores_dex(self, make_character):
        character = make_character(dexterity=20, strength=15)
        Armor.PlateArmor().apply(character)
        assert character.calculate_armor_class() == 18

    def test_heavy_armor_ignores_negative_dex(self, make_character):
        character = make_character(dexterity=6, strength=15)
        Armor.PlateArmor().apply(character)
        assert character.calculate_armor_class() == 18

    def test_shield_stacks_with_armor(self, make_character):
        character = make_character(dexterity=14, strength=13)
        Armor.ChainMailArmor().apply(character)
        Armor.ShieldArmor().apply(character)
        assert character.calculate_armor_class() == 16 + 2

    def test_shield_alone_adds_to_unarmored(self, make_character):
        character = make_character(dexterity=14)
        Armor.ShieldArmor().apply(character)
        assert character.calculate_armor_class() == 10 + 2 + 2

    def test_unworn_armor_has_no_effect(self, make_character):
        character = make_character(dexterity=14)
        Armor.PlateArmor(is_wearing=False).apply(character)
        assert character.calculate_armor_class() == 12

    def test_stealth_disadvantage_applied(self, make_character):
        character = make_character(strength=15)
        Armor.PlateArmor().apply(character)
        assert (
            character.get_skill_roll_condition(Skill.STEALTH)
            == DiceRollCondition.DISADVANTAGE
        )

    def test_no_stealth_disadvantage_for_leather(self, make_character):
        character = make_character()
        Armor.LeatherArmor().apply(character)
        assert (
            character.get_skill_roll_condition(Skill.STEALTH)
            == DiceRollCondition.NEUTRAL
        )


class TestStrengthRequirement:
    # House rule, documented in Improvements.StrengthRequirement: the engine
    # rejects the build outright. (PHB: speed -10 ft instead.)
    def test_below_requirement_rejected(self, make_character):
        character = make_character(strength=14)
        with pytest.raises(ValueError, match="Strength"):
            Armor.PlateArmor().apply(character)

    def test_exactly_meets_requirement(self, make_character):
        character = make_character(strength=15)
        Armor.PlateArmor().apply(character)
        assert character.calculate_armor_class() == 18
