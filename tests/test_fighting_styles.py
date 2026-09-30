"""
Fighting styles (CharacterContent/Features/CombatFeatures/FightingStyles.py),
checked against the 2024 PHB wording.
"""

import pytest

from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from Core.Definitions import ArmorType, CharacterClass


def bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


class TestArchery:
    def test_plus_two_to_ranged_attack(self, make_character):
        character = make_character(dexterity=16)
        bow = Weapons.Longbow(player_is_proficient=True)
        FightingStyles.Archery().apply(character)
        assert bow.calculate_total_attack_roll_bonus_int(character) == 3 + 2 + 2

    def test_includes_simple_ranged(self, make_character):
        character = make_character()
        dart = Weapons.Dart()
        FightingStyles.Archery().apply(character)
        assert sum(b for b, _ in dart.get_attack_roll_bonuses(character)) == 2

    def test_ignores_melee_and_thrown_melee(self, make_character):
        character = make_character()
        sword, javelin = Weapons.Longsword(), Weapons.Javelin()
        FightingStyles.Archery().apply(character)
        assert sword.get_attack_roll_bonuses(character) == []
        assert javelin.get_attack_roll_bonuses(character) == []

    def test_does_not_add_damage(self, make_character):
        character = make_character(dexterity=16)
        bow = Weapons.Longbow()
        FightingStyles.Archery().apply(character)
        assert bow.calculate_damage_bonus_int(character) == 3

    def test_does_not_change_the_weapon(self, make_character):
        # The bonus is recorded on the stat block, so a weapon shared between
        # builds (or characters) never carries it.
        character = make_character()
        bow = Weapons.Longbow()
        FightingStyles.Archery().apply(character)
        assert bow.attack_roll_bonuses == []


class TestDefense:
    def test_plus_one_ac_in_armor(self, make_character):
        character = make_character(dexterity=14)
        Armor.LeatherArmor().apply(character)
        FightingStyles.Defense().apply(character)
        assert character.calculate_armor_class() == 11 + 2 + 1

    def test_shield_alone_is_not_armor(self, make_character):
        character = make_character(dexterity=14, armor_training=[ArmorType.SHIELD])
        Armor.ShieldArmor().apply(character)
        FightingStyles.Defense().apply(character)
        assert character.calculate_armor_class() == 10 + 2 + 2

    def test_no_bonus_unarmored(self, make_character):
        character = make_character(dexterity=14)
        FightingStyles.Defense().apply(character)
        assert character.calculate_armor_class() == 10 + 2


class TestDueling:
    def test_adds_damage_not_attack(self, make_character):
        character = make_character(strength=16, levels={CharacterClass.FIGHTER: 1})
        sword = Weapons.Longsword(player_is_proficient=True)
        FightingStyles.Dueling().apply(character)
        assert sword.calculate_total_attack_roll_bonus_int(character) == 3 + 2
        assert sword.calculate_damage_bonus_int(character) == 3 + 2

    def test_not_applied_to_two_handed(self, make_character):
        character = make_character()
        greatsword = Weapons.Greatsword()
        FightingStyles.Dueling().apply(character)
        assert greatsword.get_attack_roll_bonuses(character) == []
        assert greatsword.get_damage_roll_bonuses(character) == []

    def test_not_applied_to_unarmed_strike(self, make_character):
        character = make_character()
        strike = Weapons.UnarmedStrike(player_is_proficient=True)
        FightingStyles.Dueling().apply(character)
        assert strike.get_damage_roll_bonuses(character) == []

    def test_versatile_weapon_qualifies(self, make_character):
        # Longsword can be wielded one-handed.
        character = make_character()
        sword = Weapons.Longsword()
        FightingStyles.Dueling().apply(character)
        assert sum(b for b, _ in sword.get_damage_roll_bonuses(character)) == 2

    def test_ignores_ranged(self, make_character):
        character = make_character()
        bow = Weapons.Longbow()
        FightingStyles.Dueling().apply(character)
        assert bow.get_attack_roll_bonuses(character) == []
        assert bow.get_damage_roll_bonuses(character) == []


class TestThrownWeaponFighting:
    def test_adds_damage_not_attack(self, make_character):
        character = make_character(strength=16)
        javelin = Weapons.Javelin()
        FightingStyles.ThrownWeaponFighting().apply(character)
        assert javelin.calculate_total_attack_roll_bonus_int(character) == 3
        assert javelin.calculate_damage_bonus_int(character) == 3 + 2

    def test_only_thrown_weapons(self, make_character):
        character = make_character()
        sword = Weapons.Longsword()
        FightingStyles.ThrownWeaponFighting().apply(character)
        assert sword.get_attack_roll_bonuses(character) == []
        assert sword.get_damage_roll_bonuses(character) == []
