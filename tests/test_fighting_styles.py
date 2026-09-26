"""
Fighting styles (CharacterContent/Features/CombatFeatures/FightingStyles.py),
checked against the 2024 PHB wording.
"""

import pytest

from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from Core.Definitions import CharacterClass


def bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


class TestArchery:
    def test_plus_two_to_ranged_attack(self, make_character):
        character = make_character(dexterity=16)
        bow = Weapons.Longbow(player_is_proficient=True)
        FightingStyles.Archery().apply([bow])
        assert bow.calculate_total_attack_roll_bonus_int(character) == 3 + 2 + 2

    def test_includes_simple_ranged(self):
        dart = Weapons.Dart()
        FightingStyles.Archery().apply([dart])
        assert sum(b for b, _ in dart.attack_roll_bonuses) == 2

    def test_ignores_melee_and_thrown_melee(self):
        sword, javelin = Weapons.Longsword(), Weapons.Javelin()
        FightingStyles.Archery().apply([sword, javelin])
        assert sword.attack_roll_bonuses == []
        assert javelin.attack_roll_bonuses == []

    def test_does_not_add_damage(self, make_character):
        character = make_character(dexterity=16)
        bow = Weapons.Longbow()
        FightingStyles.Archery().apply([bow])
        assert bow.calculate_damage_bonus_int(character) == 3


class TestDefense:
    def test_plus_one_ac_in_armor(self, make_character):
        character = make_character(dexterity=14)
        Armor.LeatherArmor().apply(character)
        FightingStyles.Defense().apply(character)
        assert character.calculate_armor_class() == 11 + 2 + 1

    def test_shield_alone_is_not_armor(self, make_character):
        character = make_character(dexterity=14)
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
        FightingStyles.Dueling().apply([sword])
        assert sword.calculate_total_attack_roll_bonus_int(character) == 3 + 2
        assert sword.calculate_damage_bonus_int(character) == 3 + 2

    def test_not_applied_to_two_handed(self, make_character):
        greatsword = Weapons.Greatsword()
        FightingStyles.Dueling().apply([greatsword])
        assert greatsword.attack_roll_bonuses == []
        assert greatsword.damage_roll_bonuses == []

    def test_not_applied_to_unarmed_strike(self):
        strike = Weapons.UnarmedStrike(player_is_proficient=True)
        FightingStyles.Dueling().apply([strike])
        assert strike.damage_roll_bonuses == []

    def test_versatile_weapon_qualifies(self):
        # Longsword can be wielded one-handed.
        sword = Weapons.Longsword()
        FightingStyles.Dueling().apply([sword])
        assert sum(b for b, _ in sword.damage_roll_bonuses) == 2

    def test_does_not_stack_when_reapplied(self):
        sword = Weapons.Longsword()
        FightingStyles.Dueling().apply([sword])
        FightingStyles.Dueling().apply([sword])
        assert sum(b for b, _ in sword.damage_roll_bonuses) == 2

    def test_ignores_ranged(self):
        bow = Weapons.Longbow()
        FightingStyles.Dueling().apply([bow])
        assert bow.attack_roll_bonuses == []


class TestThrownWeaponFighting:
    def test_adds_damage_not_attack(self, make_character):
        character = make_character(strength=16)
        javelin = Weapons.Javelin()
        FightingStyles.ThrownWeaponFighting().apply([javelin])
        assert javelin.calculate_total_attack_roll_bonus_int(character) == 3
        assert javelin.calculate_damage_bonus_int(character) == 3 + 2

    def test_only_thrown_weapons(self):
        sword = Weapons.Longsword()
        FightingStyles.ThrownWeaponFighting().apply([sword])
        assert sword.attack_roll_bonuses == []
