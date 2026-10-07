"""Weapon traits (Core/Weapons.py): wielder bonuses and weapon proficiencies are
checked against a weapon's traits - its type, properties and, for the few
weapons a proficiency names on its own, its kind - never its class name.

Expected values come from the 2024 PHB and DMG: Archery is +2 to attack rolls
with Ranged weapons; Dueling +2 damage with a Melee weapon held in one hand;
Thrown Weapon Fighting +2 damage with a Thrown weapon; Bracers of Archery +2
damage with the Longbow and Shortbow.
"""

import pytest

from CharacterContent.Features.CombatFeatures.FightingStyles import (
    Archery,
    Dueling,
    ThrownWeaponFighting,
)
from CharacterContent.Items import Weapons
from CharacterContent.Items.Items.Wondrous import BracersOfArchery
from CharacterContent.Items.Weapons.Magic import MarksmansLongbow
from CharacterContent.ToolProficiencies.Proficiencies import (
    HerbalismKit,
    ThievesTools,
    tool_item,
)
from Core.Weapons import WeaponProficiency, weapon_matches_proficiency
from Model.EquipmentTraining import EquipmentTraining
from Model.Effects import Effects, Ledger


def _ledger_with(*sources) -> Ledger:
    ledger = Ledger()
    effects = Effects(ledger)
    for source in sources:
        source.apply(effects)
    return ledger


def _attack_bonus(ledger: Ledger, weapon) -> int:
    return sum(
        value for value, _ in ledger.weapon_bonuses.attack_bonuses(weapon.traits)
    )


def _damage_bonus(ledger: Ledger, weapon) -> int:
    return sum(
        value for value, _ in ledger.weapon_bonuses.damage_bonuses(weapon.traits)
    )


@pytest.mark.parametrize(
    "weapon, expected",
    [
        (Weapons.Longbow(), 2),
        (Weapons.LightCrossbow(), 2),
        (Weapons.Longsword(), 0),
        (Weapons.Dagger(), 0),
    ],
)
def test_archery_is_ranged_weapons_only(weapon, expected):
    assert _attack_bonus(_ledger_with(Archery()), weapon) == expected


@pytest.mark.parametrize(
    "weapon, expected",
    [
        (Weapons.Longsword(), 2),
        (Weapons.Scimitar(), 2),
        (Weapons.Greatsword(), 0),  # Two-Handed
        (Weapons.Longbow(), 0),  # Ranged
        (Weapons.UnarmedStrike(), 0),  # not a weapon held in one hand
    ],
)
def test_dueling_is_one_handed_melee_weapons_only(weapon, expected):
    assert _damage_bonus(_ledger_with(Dueling()), weapon) == expected


@pytest.mark.parametrize(
    "weapon, expected",
    [(Weapons.Dagger(), 2), (Weapons.Handaxe(), 2), (Weapons.Longsword(), 0)],
)
def test_thrown_weapon_fighting_is_thrown_weapons_only(weapon, expected):
    assert _damage_bonus(_ledger_with(ThrownWeaponFighting()), weapon) == expected


@pytest.mark.parametrize(
    "weapon, expected",
    [
        (Weapons.Longbow(), 2),
        (Weapons.Shortbow(), 2),
        (MarksmansLongbow(), 2),  # a magic Longbow is still a Longbow
        (Weapons.LightCrossbow(), 0),
        (Weapons.Longsword(), 0),
    ],
)
def test_bracers_of_archery_are_longbow_and_shortbow_only(weapon, expected):
    assert _damage_bonus(_ledger_with(BracersOfArchery()), weapon) == expected


@pytest.mark.parametrize(
    "weapon, proficiency, expected",
    [
        (Weapons.Longbow(), WeaponProficiency.LONGBOW, True),
        (MarksmansLongbow(), WeaponProficiency.LONGBOW, True),
        (Weapons.Shortbow(), WeaponProficiency.LONGBOW, False),
        (Weapons.Shortbow(), WeaponProficiency.SHORTBOW, True),
        (Weapons.Scimitar(), WeaponProficiency.SCIMITAR, True),
        (Weapons.Longsword(), WeaponProficiency.SCIMITAR, False),
        (Weapons.Longsword(), WeaponProficiency.MARTIAL, True),
        (Weapons.Dagger(), WeaponProficiency.SIMPLE, True),
        (Weapons.Dagger(), WeaponProficiency.MARTIAL, False),
    ],
)
def test_weapon_proficiency_by_kind_and_category(weapon, proficiency, expected):
    assert weapon_matches_proficiency(weapon.traits, proficiency) is expected


def test_same_tool_from_two_sources_is_listed_once_and_sorted():
    training = EquipmentTraining()
    training.add_tool_proficiency(ThievesTools())
    training.add_tool_proficiency(HerbalismKit())
    training.add_tool_proficiency(ThievesTools())  # e.g. class and background
    assert [tool.name for tool in training.tool_proficiencies] == [
        "Herbalism Kit",
        "Thieves' Tools",
    ]


def test_tool_item_is_the_same_named_item():
    item = tool_item(ThievesTools())
    assert item is not None and item.name == "Thieves' Tools"
