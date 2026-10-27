"""
Tavern Brawler's Enhanced Unarmed Strike (2024 PHB): "When you hit with your
Unarmed Strike and deal damage, you can deal Bludgeoning damage equal to 1d4
plus your Strength modifier instead of the normal damage."

The sheet shows it only where it beats the strike's own die: the default 1
becomes 1d4 + Strength, a Monk's Martial Arts die (d6+, maybe with Dexterity)
is left alone. Neither depends on the order the features apply in.
"""

import itertools

import pytest

from CharacterContent.Features.CharacterFeats.OriginFeats import TavernBrawler
from CharacterContent.Features.ClassFeatures.Monk.MonkFeatures import MartialArts
from CharacterContent.Items import Weapons
from Core.Definitions import Ability, CharacterClass
from Core.Weapons import WeaponDamageRolls
from Model.Character import Character


def _damage(strike, character):
    return (
        strike.get_damage_roll(character),
        strike.calculate_damage_bonus_int(character),
    )


def _character(make_sources, effects, **scores):
    sources = make_sources(**scores)
    for effect in effects:
        sources.add_effect(effect)
    return Character(sources)


class TestEnhancedUnarmedStrike:
    def test_default_strike_becomes_1d4_plus_strength(self, make_sources):
        character = _character(
            make_sources, [TavernBrawler()], strength=16, dexterity=18
        )
        strike = Weapons.UnarmedStrike(player_is_proficient=True)
        assert _damage(strike, character) == (WeaponDamageRolls.D4, 3)

    def test_uses_strength_even_when_the_strike_uses_dexterity(self, make_sources):
        # The feat's damage is always "1d4 plus your Strength modifier".
        character = _character(
            make_sources, [TavernBrawler()], strength=14, dexterity=18
        )
        strike = Weapons.UnarmedStrike(ability=Ability.DEXTERITY)
        assert _damage(strike, character) == (WeaponDamageRolls.D4, 2)

    def test_attack_roll_is_unchanged(self, make_sources):
        without = _character(make_sources, [], strength=16)
        with_feat = _character(make_sources, [TavernBrawler()], strength=16)
        strike = Weapons.UnarmedStrike(player_is_proficient=True)
        assert strike.calculate_total_attack_roll_bonus_int(
            with_feat
        ) == strike.calculate_total_attack_roll_bonus_int(without)

    def test_martial_arts_die_is_left_alone(self, make_sources):
        character = _character(
            make_sources,
            [TavernBrawler(), MartialArts()],
            strength=16,
            dexterity=18,
        )
        strike = Weapons.UnarmedStrike(
            ability=Ability.DEXTERITY, damage_roll=WeaponDamageRolls.D6
        )
        assert _damage(strike, character) == (WeaponDamageRolls.D6, 4)

    def test_other_weapons_are_unaffected(self, make_sources):
        character = _character(make_sources, [TavernBrawler()], strength=16)
        club = Weapons.Club()
        assert _damage(club, character) == (WeaponDamageRolls.D4, 3)
        dart = Weapons.Dart()
        assert dart.get_damage_roll(character) == WeaponDamageRolls.D4

    def test_without_the_feat_the_strike_deals_1(self, make_sources):
        character = _character(make_sources, [], strength=16)
        strike = Weapons.UnarmedStrike(player_is_proficient=True)
        assert _damage(strike, character) == (WeaponDamageRolls.D1, 3)

    def test_the_weapon_is_never_changed(self, make_sources):
        character = _character(make_sources, [TavernBrawler()], strength=16)
        strike = Weapons.UnarmedStrike(player_is_proficient=True)
        strike.get_damage_roll(character)
        assert strike.damage_roll == WeaponDamageRolls.D1


@pytest.mark.parametrize(
    "damage_roll, ability, expected",
    [
        (None, None, (WeaponDamageRolls.D4, 3)),
        (WeaponDamageRolls.D6, Ability.DEXTERITY, (WeaponDamageRolls.D6, 4)),
        (WeaponDamageRolls.D4, Ability.DEXTERITY, (WeaponDamageRolls.D4, 4)),
    ],
)
def test_order_insensitive(make_sources, damage_roll, ability, expected):
    """Tavern Brawler before or after Martial Arts gives the same strike."""
    results = set()
    for order in itertools.permutations([TavernBrawler, MartialArts]):
        character = _character(
            make_sources,
            [feature() for feature in order],
            strength=16,
            dexterity=18,
            levels={CharacterClass.MONK: 5},
        )
        strike = Weapons.UnarmedStrike(ability=ability, damage_roll=damage_roll)
        results.add(_damage(strike, character))
    assert results == {expected}
