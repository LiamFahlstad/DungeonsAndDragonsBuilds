"""
Weapon stats and attack/damage math (CharacterContent/Items/Weapons).

The weapon table is transcribed from the 2024 PHB, not read back from the
code. A row that disagrees with the PHB is a bug: mark it with
marks=bug("...") (a strict xfail) until the data is fixed.
"""

import pytest

from CharacterContent.Items import Weapons
from CharacterContent.Items.Weapons.Base import is_proficient_with
from CharacterContent.Items.Weapons.Enums import (
    WeaponDamageRolls as R,
    WeaponDamageTypes as T,
    WeaponMastery as Ma,
    WeaponProficiency,
    WeaponProperty as P,
    WeaponType as W,
)
from Core.Definitions import Ability, CharacterClass

SM, MM, SR, MR = W.SIMPLE_MELEE, W.MARTIAL_MELEE, W.SIMPLE_RANGED, W.MARTIAL_RANGED
B, Pi, S = T.BLUDGEONING, T.PIERCING, T.SLASHING
AMMO, FIN, HVY, LGT, LOAD, RCH, THR, TWO = (
    P.AMMUNITION,
    P.FINESSE,
    P.HEAVY,
    P.LIGHT,
    P.LOADING,
    P.REACH,
    P.THROWN,
    P.TWO_HANDED,
)
V8, V10 = P.VERSATILE_8, P.VERSATILE_10


def bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


# class, type, damage, damage type, properties, mastery, weight lb, cost GP
PHB_WEAPONS = [
    # Simple melee
    (Weapons.Club, SM, R.D4, B, {LGT}, Ma.SLOW, 2, 0.1),
    (Weapons.Dagger, SM, R.D4, Pi, {FIN, LGT, THR}, Ma.NICK, 1, 2),
    pytest.param(
        Weapons.Greatclub,
        SM,
        R.D8,
        B,
        {TWO},
        Ma.PUSH,
        10,
        0.2,
        id="Greatclub",
    ),
    (Weapons.Handaxe, SM, R.D6, S, {LGT, THR}, Ma.VEX, 2, 5),
    (Weapons.Javelin, SM, R.D6, Pi, {THR}, Ma.SLOW, 2, 0.5),
    (Weapons.LightHammer, SM, R.D4, B, {LGT, THR}, Ma.NICK, 2, 2),
    (Weapons.Mace, SM, R.D6, B, set(), Ma.SAP, 4, 5),
    (Weapons.Quarterstaff, SM, R.D6, B, {V8}, Ma.TOPPLE, 4, 0.2),
    (Weapons.Sickle, SM, R.D4, S, {LGT}, Ma.NICK, 2, 1),
    (Weapons.Spear, SM, R.D6, Pi, {THR, V8}, Ma.SAP, 3, 1),
    # Simple ranged
    (Weapons.Dart, SR, R.D4, Pi, {FIN, THR}, Ma.VEX, 0.25, 0.05),
    (Weapons.LightCrossbow, SR, R.D8, Pi, {AMMO, LOAD, TWO}, Ma.SLOW, 5, 25),
    (Weapons.Shortbow, SR, R.D6, Pi, {AMMO, TWO}, Ma.VEX, 2, 25),
    (Weapons.Sling, SR, R.D4, B, {AMMO}, Ma.SLOW, None, 0.1),
    # Martial melee
    (Weapons.Battleaxe, MM, R.D8, S, {V10}, Ma.TOPPLE, 4, 10),
    (Weapons.Flail, MM, R.D8, B, set(), Ma.SAP, 2, 10),
    (Weapons.Glaive, MM, R.D10, S, {HVY, RCH, TWO}, Ma.GRAZE, 6, 20),
    (Weapons.Greataxe, MM, R.D12, S, {HVY, TWO}, Ma.CLEAVE, 7, 30),
    (Weapons.Greatsword, MM, R.D6x2, S, {HVY, TWO}, Ma.GRAZE, 6, 50),
    (Weapons.Halberd, MM, R.D10, S, {HVY, RCH, TWO}, Ma.CLEAVE, 6, 20),
    (Weapons.Lance, MM, R.D10, Pi, {HVY, RCH, TWO}, Ma.TOPPLE, 6, 10),
    (Weapons.Longsword, MM, R.D8, S, {V10}, Ma.SAP, 3, 15),
    (Weapons.Maul, MM, R.D6x2, B, {HVY, TWO}, Ma.TOPPLE, 10, 10),
    (Weapons.Morningstar, MM, R.D8, Pi, set(), Ma.SAP, 4, 15),
    (Weapons.Pike, MM, R.D10, Pi, {HVY, RCH, TWO}, Ma.PUSH, 18, 5),
    (Weapons.Rapier, MM, R.D8, Pi, {FIN}, Ma.VEX, 2, 25),
    (Weapons.Scimitar, MM, R.D6, S, {FIN, LGT}, Ma.NICK, 3, 25),
    pytest.param(
        Weapons.Shortsword,
        MM,
        R.D6,
        Pi,
        {FIN, LGT},
        Ma.VEX,
        2,
        10,
        id="Shortsword",
    ),
    (Weapons.Trident, MM, R.D8, Pi, {THR, V10}, Ma.TOPPLE, 4, 5),
    pytest.param(
        Weapons.WarPick,
        MM,
        R.D8,
        Pi,
        {V10},
        Ma.SAP,
        5,
        5,
        id="WarPick",
    ),
    pytest.param(
        Weapons.Warhammer,
        MM,
        R.D8,
        B,
        {V10},
        Ma.PUSH,
        5,
        15,
        id="Warhammer",
    ),
    (Weapons.Whip, MM, R.D4, S, {FIN, RCH}, Ma.SLOW, 3, 2),
    # Martial ranged
    (Weapons.Blowgun, MR, R.D1, Pi, {AMMO, LOAD}, Ma.VEX, 1, 10),
    (Weapons.HandCrossbow, MR, R.D6, Pi, {AMMO, LGT, LOAD}, Ma.VEX, 3, 75),
    pytest.param(
        Weapons.HeavyCrossbow,
        MR,
        R.D10,
        Pi,
        {AMMO, HVY, LOAD, TWO},
        Ma.PUSH,
        18,
        50,
        id="HeavyCrossbow",
    ),
    (Weapons.Longbow, MR, R.D8, Pi, {AMMO, HVY, TWO}, Ma.SLOW, 2, 50),
    (Weapons.Musket, MR, R.D12, Pi, {AMMO, LOAD, TWO}, Ma.SLOW, 10, 500),
    (Weapons.Pistol, MR, R.D10, Pi, {AMMO, LOAD}, Ma.VEX, 3, 250),
]


def _row_id(row):
    # pytest.param rows carry their own id.
    return row.id if hasattr(row, "marks") else row[0].__name__


@pytest.mark.parametrize(
    "weapon_class,weapon_type,damage,damage_type,properties,mastery,weight,cost",
    PHB_WEAPONS,
    ids=[_row_id(row) for row in PHB_WEAPONS],
)
def test_weapon_matches_phb(
    weapon_class,
    weapon_type,
    damage,
    damage_type,
    properties,
    mastery,
    weight,
    cost,
):
    weapon = weapon_class()
    assert weapon.weapon_type == weapon_type
    assert weapon.damage_roll == damage
    assert weapon.damage_type == damage_type
    assert set(weapon.properties) == properties
    assert weapon.mastery == mastery
    assert weapon.weight == weight
    assert weapon.value == cost
    assert weapon.is_homebrew is False


def test_war_pick_display_name():
    assert Weapons.WarPick().name == "War Pick"


class TestAbilityUsed:
    def test_melee_uses_strength(self, make_character):
        character = make_character(strength=16, dexterity=18)
        assert Weapons.Longsword().calculate_damage_bonus_int(character) == 3

    def test_ranged_uses_dexterity(self, make_character):
        character = make_character(strength=18, dexterity=14)
        assert Weapons.Longbow().calculate_damage_bonus_int(character) == 2

    def test_thrown_non_finesse_uses_strength(self, make_character):
        character = make_character(strength=14, dexterity=18)
        assert Weapons.Javelin().calculate_damage_bonus_int(character) == 2

    @pytest.mark.parametrize("str_score,dex_score,expected", [(16, 12, 3), (8, 18, 4)])
    def test_finesse_uses_better_of_str_dex(
        self, make_character, str_score, dex_score, expected
    ):
        character = make_character(strength=str_score, dexterity=dex_score)
        assert Weapons.Rapier().calculate_damage_bonus_int(character) == expected

    def test_ability_override(self, make_character):
        character = make_character(strength=10, charisma=18)
        weapon = Weapons.Longsword(ability=Ability.CHARISMA)
        assert weapon.calculate_damage_bonus_int(character) == 4


class TestAttackBonus:
    def test_proficient_adds_proficiency_bonus(self, make_character):
        character = make_character(
            strength=16, levels={CharacterClass.FIGHTER: 5}
        )  # PB 3
        weapon = Weapons.Longsword(player_is_proficient=True)
        assert weapon.calculate_total_attack_roll_bonus_int(character) == 3 + 3

    def test_not_proficient_omits_proficiency_bonus(self, make_character):
        character = make_character(strength=16, levels={CharacterClass.FIGHTER: 5})
        weapon = Weapons.Longsword(player_is_proficient=False)
        assert weapon.calculate_total_attack_roll_bonus_int(character) == 3

    def test_extra_attack_roll_bonuses_add(self, make_character):
        character = make_character(dexterity=16)
        weapon = Weapons.Longbow(
            player_is_proficient=True, attack_roll_bonuses=[(1, "+1 weapon")]
        )
        assert weapon.calculate_total_attack_roll_bonus_int(character) == 3 + 2 + 1

    def test_damage_bonus_excludes_proficiency(self, make_character):
        character = make_character(strength=16, levels={CharacterClass.FIGHTER: 5})
        weapon = Weapons.Longsword(player_is_proficient=True)
        assert weapon.calculate_damage_bonus_int(character) == 3


class TestProficiency:
    def test_simple_proficiency(self):
        assert is_proficient_with(Weapons.Club(), [WeaponProficiency.SIMPLE])
        assert is_proficient_with(Weapons.Shortbow(), [WeaponProficiency.SIMPLE])
        assert not is_proficient_with(Weapons.Longsword(), [WeaponProficiency.SIMPLE])

    def test_martial_proficiency(self):
        assert is_proficient_with(Weapons.Longbow(), [WeaponProficiency.MARTIAL])
        assert not is_proficient_with(Weapons.Dagger(), [WeaponProficiency.MARTIAL])

    def test_martial_light(self):
        profs = [WeaponProficiency.MARTIAL_LIGHT]
        assert is_proficient_with(Weapons.Scimitar(), profs)
        assert not is_proficient_with(Weapons.Rapier(), profs)

    def test_martial_finesse_or_light(self):
        # 2024 Rogue: Martial weapons with the Finesse or Light property.
        profs = [WeaponProficiency.MARTIAL_FINESSE_OR_LIGHT]
        assert is_proficient_with(Weapons.Rapier(), profs)
        assert is_proficient_with(Weapons.HandCrossbow(), profs)
        assert not is_proficient_with(Weapons.Longsword(), profs)


class TestUnarmedStrike:
    def test_damage_is_one_plus_strength(self, make_character):
        character = make_character(strength=16)
        strike = Weapons.UnarmedStrike(player_is_proficient=True)
        assert strike.damage_roll == R.D1
        assert strike.calculate_damage_bonus_int(character) == 3

    def test_rejects_non_str_dex_ability(self):
        with pytest.raises(ValueError):
            Weapons.UnarmedStrike(ability=Ability.WISDOM)

    def test_rejects_mastery(self):
        with pytest.raises(ValueError):
            Weapons.UnarmedStrike(player_has_mastery=True)
