"""What the combat UI's amount fields understand (amounts.py), and how a
monster's abilities are read from its stat block (monster_actions.py), run
over every monster in the game so a new wording shows up here."""

import importlib
import inspect
import pkgutil

import pytest

import Combat.Monsters
from Combat.CombatUIQt.amounts import (
    AmountError,
    damage_type_from_text,
    parse_amount,
    parse_damage,
)
from Combat.CombatUIQt.monster_actions import (
    DamageRoll,
    first_number,
    monster_actions,
    parse_action,
    roll_dice,
    start_of_turn_traits,
)
from Combat.Monsters.CR_0.monsters import GoblinWarrior, Stirge
from Core.Definitions import DamageType
from Model.Creatures.Combatants import BasicCombatantData
from Model.Creatures.MonsterAbilities import (
    DiceType,
    MeleeAttack,
    MonsterAbility,
    SavingThrowEffect,
)
from Core.Definitions import Ability


@pytest.mark.parametrize(
    "text, amount",
    [
        ("7", 7),
        ("0", 0),
        (" 7 ", 7),
        ("+5", 5),
        ("8+5", 13),
        ("12 - 2", 10),
        ("1+2+3", 6),
        ("10-3+1", 8),
        ("24/2", 12),
        ("25/2", 12),  # half damage rounds down
        ("24 / 2", 12),
        ("8+6/2", 11),
        ("3-5", None),
        ("-5", None),
        ("", None),
        ("   ", None),
        ("abc", None),
        ("2d6", None),
        ("2d6+3", None),
        ("5+", None),
        ("1.5", None),
        ("5/0", None),
        ("12 fire", None),  # healing has no damage type
    ],
)
def test_parse_amount(text, amount):
    assert parse_amount(text) == amount


FIRE = DamageType.FIRE.value
FORCE = DamageType.FORCE.value
PIERCING = DamageType.PIERCING.value
POISON = DamageType.POISON.value
PSYCHIC = DamageType.PSYCHIC.value
SLASHING = DamageType.SLASHING.value


@pytest.mark.parametrize(
    "word, damage_type",
    [
        ("fire", FIRE),
        ("FIRE", FIRE),
        ("fi", FIRE),
        ("f", FIRE),
        ("fo", FORCE),
        ("p", PIERCING),
        ("pi", PIERCING),
        ("po", POISON),
        ("ps", PSYCHIC),
        ("sl", SLASHING),
        ("s", SLASHING),
        ("zz", None),
        ("", None),
    ],
)
def test_damage_type_from_text(word, damage_type):
    assert damage_type_from_text(word) == damage_type


def test_every_damage_type_has_a_short_form_and_its_full_name():
    for damage_type in DamageType:
        assert damage_type_from_text(damage_type.value) == damage_type.value
        assert damage_type_from_text(damage_type.value[:2]) == damage_type.value


@pytest.mark.parametrize(
    "text, parts",
    [
        ("12", [(12, None)]),
        ("12 fi", [(12, FIRE)]),
        ("12f", [(12, FIRE)]),
        ("12 fire", [(12, FIRE)]),
        ("  12   Fire ", [(12, FIRE)]),
        ("8+5 fi", [(13, FIRE)]),
        ("8 fi + 5", [(13, FIRE)]),
        ("24/2 fi", [(12, FIRE)]),
        ("24 fi/2", [(12, FIRE)]),
        ("7 pi + 3 fi", [(7, PIERCING), (3, FIRE)]),
        ("7 pi + 3 + 2 fi", [(7, PIERCING), (5, FIRE)]),
        ("7 pi + 3 fi + 2 pi", [(9, PIERCING), (3, FIRE)]),
        ("10 - 2 fi", [(8, FIRE)]),
        ("0 fi", [(0, FIRE)]),
    ],
)
def test_parse_damage(text, parts):
    assert parse_damage(text) == parts


@pytest.mark.parametrize(
    "text, message",
    [
        ("", "no amount"),
        ("12 zz", "'zz' isn't a damage type"),
        ("2d6", "'2d6' isn't an amount"),
        ("fire", "'fire' isn't an amount"),
        ("12 fi fi", "'12 fi fi' isn't an amount"),
        ("3 - 5 fi", "'3 - 5 fi' comes to less than 0"),
        ("-5", "'-5' isn't an amount"),
    ],
)
def test_parse_damage_says_whats_wrong(text, message):
    with pytest.raises(AmountError) as error:
        parse_damage(text)
    assert str(error.value) == message


# ---------------------------------------------------------------------------
# Monster abilities


def _ability(name: str, description: str) -> MonsterAbility:
    return MonsterAbility(name=name, description=description)


def test_an_attack():
    action = parse_action(
        _ability(
            "Talons",
            "Melee Attack Roll: +4, reach 5 ft. Hit: 4 (1d4 + 2) Slashing damage,"
            " or 9 (3d4 + 2) Slashing damage if the aarakocra moved 30+ feet.",
        )
    )
    assert action.to_hit == 4
    assert action.damage == (DamageRoll("1d4 + 2", SLASHING),)
    assert action.save_dc is None


def test_an_attack_of_two_damage_types():
    action = parse_action(
        _ability(
            "Wind Javelin",
            "Melee or Ranged Attack Roll: +4, reach 5 ft. or range 30/120 ft."
            " Hit: 5 (1d6 + 2) Piercing damage plus 2 (1d4) Thunder damage."
            " Hit or Miss: The javelin magically returns.",
        )
    )
    assert action.damage == (
        DamageRoll("1d6 + 2", PIERCING),
        DamageRoll("1d4", DamageType.THUNDER.value),
    )


def test_a_real_minus_sign_in_the_dice():
    action = parse_action(
        _ability(
            "Bite",
            "Melee Attack Roll: +1, reach 5 ft. Hit: 1 (1d4 − 1)" " Piercing damage.",
        )
    )
    assert action.damage == (DamageRoll("1d4 - 1", PIERCING),)


@pytest.mark.parametrize(
    "hit",
    [
        "6 (1d6 + 3) damage of a type chosen by the kobold: Acid, Cold or Fire.",
        "6 (1d6 + 3) Necrotic or Radiant damage (empyrean's choice).",
    ],
)
def test_a_damage_type_the_monster_chooses_is_left_open(hit):
    action = parse_action(
        _ability("Spittle", f"Ranged Attack Roll: +5, range 30 ft. Hit: {hit}")
    )
    assert action.damage == (DamageRoll("1d6 + 3", None),)
    assert "(type of its choice)" in action.summary


def test_a_save_dc_set_by_the_summoner():
    action = parse_action(
        _ability(
            "Fell Glare",
            "Wisdom Saving Throw: DC equals your spell save DC, one creature."
            " Failure: 2d6 damage of a type of your choice.",
        )
    )
    assert (action.save_ability, action.save_dc) == ("Wisdom", None)
    assert action.damage == (DamageRoll("2d6", None),)
    assert action.summary.startswith("DC ? Wis")


def test_flat_damage():
    action = parse_action(
        _ability("Prick", "Melee Attack Roll: +3, reach 5 ft. Hit: 1 Piercing damage.")
    )
    assert action.damage == (DamageRoll("1", PIERCING),)


def test_damage_on_a_failed_save():
    action = parse_action(
        _ability(
            "Fire Breath (Recharge 5\N{EN DASH}6)",
            "Dexterity Saving Throw: DC 14, each creature in a 30-foot Cone."
            " Failure: 27 (5d10) Fire damage. Success: Half damage.",
        )
    )
    assert (action.save_ability, action.save_dc) == ("Dexterity", 14)
    assert action.damage == (DamageRoll("5d10", FIRE),)
    assert action.half_on_save
    assert action.recharge_on == 5
    assert action.is_limited
    assert action.summary == "DC 14 Dex  5d10 Fire  half on save"


def test_a_save_with_no_damage():
    action = parse_action(
        _ability(
            "Blinding Breath (Recharge 6)",
            "Dexterity Saving Throw: DC 10, each creature in a 15-foot Cone."
            " Failure: The target has the Blinded condition.",
        )
    )
    assert action.damage == ()
    assert action.recharge_on == 6
    assert not action.is_rollable


def test_success_damage_isnt_read_as_failure_damage():
    action = parse_action(
        _ability(
            "Blast",
            "Wisdom Saving Throw: DC 12, one creature. Failure: 10 (3d6) Psychic"
            " damage. Success: 3 (1d6) Psychic damage.",
        )
    )
    assert action.damage == (DamageRoll("3d6", PSYCHIC),)
    assert not action.half_on_save


def test_per_day_and_legendary_cost():
    assert parse_action(_ability("Fetid Cloud (1/Day)", "text")).per_day == 1
    assert parse_action(_ability("Lash", "text"), legendary=True).legendary_cost == 1
    wing = parse_action(_ability("Wing (Costs 2 Actions)", "text"), legendary=True)
    assert wing.legendary_cost == 2
    assert parse_action(_ability("Lash", "text")).legendary_cost == 0


def test_structured_abilities_read_the_same():
    attack = parse_action(
        MeleeAttack(
            name="Bite",
            attack_bonus=5,
            dice_count=2,
            dice_type=DiceType.D6,
            damage_bonus=3,
            damage_type=DamageType.PIERCING,
        )
    )
    assert attack.to_hit == 5
    assert attack.damage == (DamageRoll("2d6 + 3", PIERCING),)

    save = parse_action(
        SavingThrowEffect(
            name="Spit",
            ability=Ability.DEXTERITY,
            dc=13,
            target="one creature",
            dice_count=2,
            dice_type=DiceType.D6,
            damage_type=DamageType.ACID,
        )
    )
    assert (save.save_ability, save.save_dc) == ("Dexterity", 13)
    assert save.damage == (DamageRoll("2d6", DamageType.ACID.value),)


def test_a_saved_fights_dicts_read_the_same():
    text = "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Slashing damage."
    assert parse_action({"name": "Claw", "description": text}) == parse_action(
        _ability("Claw", text)
    )


def test_sections_and_legendary_marking():
    char = {
        "actions": [_ability("Claw", "text")],
        "bonus_actions": [],
        "legendary_actions": [_ability("Lash", "text")],
    }
    sections = monster_actions(char)
    assert [title for title, _ in sections] == ["Actions", "Legendary Actions"]
    assert sections[0][1][0].legendary_cost == 0
    assert sections[1][1][0].legendary_cost == 1


def test_start_of_turn_traits():
    char = {
        "traits": [
            _ability(
                "Regeneration",
                "The troll regains 15 Hit Points at the start of each of its turns."
                " If it takes Fire damage, this doesn't work.",
            ),
            _ability(
                "Aura",
                "It glows. At the start of the wight's turn, shadows gather.",
            ),
            _ability("Keen Sight", "It sees far."),
        ]
    }
    assert start_of_turn_traits(char) == [
        (
            "Regeneration",
            "The troll regains 15 Hit Points at the start of each of its turns.",
        ),
        ("Aura", "At the start of the wight's turn, shadows gather."),
    ]


@pytest.mark.parametrize(
    "dice, low, high",
    [("4", 4, 4), ("1d4", 1, 4), ("2d6 + 3", 5, 15), ("1d4 - 1", 0, 3), ("3d4", 3, 12)],
)
def test_roll_dice_stays_in_range(dice, low, high):
    rolls = [roll_dice(dice) for _ in range(200)]
    assert low <= min(rolls) and max(rolls) <= high


def test_a_critical_rolls_the_dice_twice_over_but_not_the_bonus():
    rolls = [roll_dice("1d4 + 3", critical=True) for _ in range(300)]
    assert min(rolls) == 5 and max(rolls) == 11


def test_first_number():
    assert first_number(13) == 13
    assert first_number("18 (with Shield) and 16 (without Shield)") == 18
    assert first_number("no idea") is None


def _all_monsters():
    for info in pkgutil.walk_packages(Combat.Monsters.__path__, "Combat.Monsters."):
        if info.ispkg:
            continue
        module = importlib.import_module(info.name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__ and issubclass(
                cls, BasicCombatantData
            ):
                yield cls()


def test_real_stat_blocks_roll_only_what_every_hit_deals():
    """Extra damage that waits on something must never be rolled in: the
    Goblin Warrior's needs Advantage, the Stirge's comes turns later."""
    scimitar, *_ = GoblinWarrior().actions
    action = parse_action(scimitar)
    assert action.damage == (DamageRoll("1d6 + 2", SLASHING),)
    assert action.rider.endswith("if the attack roll had Advantage")

    action = parse_action(Stirge().actions[0])
    assert action.damage == (DamageRoll("1d6 + 3", PIERCING),)


def test_every_monsters_attacks_can_be_read():
    """Each attack or damaging save in the game gives a to-hit or a DC, and
    damage when its text has the usual "N (XdY) Type damage". A new wording in
    a stat block fails here instead of showing a dead button at the table."""
    checked = 0
    unread = []
    for monster in _all_monsters():
        for key in ("actions", "bonus_actions", "reactions", "legendary_actions"):
            for ability in getattr(monster, key, None) or []:
                action = parse_action(ability)
                text = ability.description
                if "Attack Roll: +" in text:
                    checked += 1
                    assert action.to_hit is not None, (monster, text)
                    if "Hit:" in text and " damage" in text.split("Hit:")[1][:60]:
                        if not action.damage:
                            unread.append((type(monster).__name__, ability.name))
                if " Saving Throw: DC " in text and action.save_ability is None:
                    unread.append((type(monster).__name__, ability.name))
    assert checked > 500
    assert unread == []
