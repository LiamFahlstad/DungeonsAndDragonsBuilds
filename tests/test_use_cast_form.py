"""The Use / Cast dialog's readers of rolls typed at the table, and its Times
copies (Combat/CombatUIQt/use_cast/form.py), without Qt.

What a GM types is read the way the dialog's hint says: one roll per time,
comma separated, a blank one rolled; a save total, not a natural roll; an
attack roll as a total, a sum or "nat 20"."""

import pytest

from Combat.CombatUIQt.attack_rolls import AttackRoll
from Combat.CombatUIQt.saves import DAMAGE_AMOUNT, HEALING, CustomEffect
from Combat.CombatUIQt.use_cast.form import (
    FormError,
    nth,
    read_or_say,
    repeated,
    rolls_in,
    typed_attacks,
    typed_extras,
    typed_maximum,
    typed_totals,
)


def test_one_roll_per_time_and_no_more():
    assert rolls_in("17, 9", 3) == ["17", "9"]
    with pytest.raises(FormError, match="3 rolls for Times 2"):
        rolls_in("1, 2, 3", 2)


def test_save_totals_take_a_total_or_a_sum_and_leave_blanks_to_roll():
    assert typed_totals({1: "14", 2: "9+5", 3: "  "}, 1) == {1: [14], 2: [14]}
    assert typed_totals({1: "-1, , 12"}, 3) == {1: [-1, None, 12]}


def test_a_natural_roll_is_no_save_total():
    with pytest.raises(FormError, match="natural roll is nothing special"):
        typed_totals({1: "nat 20"}, 1)
    with pytest.raises(FormError, match="isn't a saving throw total"):
        typed_totals({1: "high"}, 1)


def test_attack_rolls_take_totals_sums_and_naturals():
    rolls = typed_attacks({1: "17, nat 20", 2: "12+5"}, 2)
    assert rolls[1] == [AttackRoll(total=17), AttackRoll(natural=20)]
    assert rolls[2] == [AttackRoll(total=17)]
    with pytest.raises(FormError, match="isn't an attack roll"):
        typed_attacks({1: "lots"}, 1)


def test_extra_damage_is_a_non_negative_amount_per_target_and_label():
    texts = {(1, "Hunter's Mark"): "4, 2+1", (2, "Hunter's Mark"): ""}
    assert typed_extras(texts, 2) == {1: {"Hunter's Mark": [4, 3]}}
    with pytest.raises(FormError, match="for Hunter's Mark"):
        typed_extras({(1, "Hunter's Mark"): "-3"}, 1)


def test_a_hit_point_maximum_is_one_for_all_or_one_each():
    assert typed_maximum("", [1, 2]) == {}
    assert typed_maximum("40", [1, 2]) == {1: 40, 2: 40}
    assert typed_maximum("40, 35", [1, 2]) == {1: 40, 2: 35}
    with pytest.raises(FormError, match="one for each of the 2 targets"):
        typed_maximum("1, 2, 3", [1, 2])
    with pytest.raises(FormError, match="isn't a Hit Point maximum"):
        typed_maximum("2d10", [1])


def test_each_time_takes_its_own_roll_and_rolls_the_blanks():
    typed = {1: [17, None, 9], 2: [5], 3: {"Mark": [None, 4]}}
    assert nth(typed, 0) == {1: 17, 2: 5}
    assert nth(typed, 1) == {3: {"Mark": 4}}
    assert nth(typed, 2) == {1: 9}


def test_read_or_say_passes_the_problem_on():
    said: list[str] = []

    def bad():
        raise FormError("no good")

    assert read_or_say(bad, said.append) is None
    assert said == ["no good"]
    assert read_or_say(lambda: 3, said.append) == 3


def test_times_copies_cost_once_and_take_their_own_rolls():
    effect = CustomEffect(
        name="Scorching Ray",
        damage=[(7, "Fire")],
        slot_level=2,
        action_cost="Action",
        concentration=True,
        attack_bonus=5,
        typed_attacks={1: AttackRoll(total=17)},
    )
    rolls = {
        "attacks": {1: [AttackRoll(total=17), AttackRoll(natural=1)]},
        "totals": {},
        "extras": {},
    }
    copies = repeated(
        effect,
        3,
        amount_text="7 fire",
        damage_type=None,
        kind=DAMAGE_AMOUNT,
        typed_rolls=rolls,
    )
    assert [c.name for c in copies] == [
        "Scorching Ray (1 of 3)",
        "Scorching Ray (2 of 3)",
        "Scorching Ray (3 of 3)",
    ]
    first, second, third = copies
    assert (first.slot_level, first.action_cost, first.concentration) == (
        2,
        "Action",
        True,
    )
    for copy in (second, third):
        assert (copy.slot_level, copy.action_cost, copy.concentration) == (
            None,
            None,
            False,
        )
        assert copy.damage == [(7, "Fire")]
        assert copy.critical_damage  # an attack's copy can crit too
    assert second.typed_attacks == {1: AttackRoll(natural=1)}
    assert third.typed_attacks == {}


def test_healing_copies_heal_and_deal_nothing():
    copies = repeated(
        CustomEffect(name="Heal", healing=5),
        2,
        amount_text="5",
        damage_type=None,
        kind=HEALING,
        typed_rolls={"attacks": {}, "totals": {}, "extras": {}},
    )
    assert copies[1].healing == 5 and copies[1].damage == []
