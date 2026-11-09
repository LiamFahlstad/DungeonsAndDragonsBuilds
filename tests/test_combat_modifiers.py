"""The rules conditions as data (Model/Content/RulesConditions.py) and what the
combat simulator makes of them (Combat/Effects/modifiers.py): the roll modes,
automatic failures, Critical Hits, AC, Resistance and immunities they give.
Expected values come from the 2024 Rules Glossary's condition entries
(SourceTexts/RulesGlossary/Conditions/), not from the table itself."""

import pytest

from Combat.Effects.modifiers import (
    armor_class_bonus,
    attack_plan,
    combine_modes,
    has_condition,
    held_conditions,
    hit_notes,
    immune_to_condition,
    resists,
    resists_all_damage,
    rules_condition,
    save_plan,
)
from Core.Definitions import Ability, Condition, DamageType
from Model.Content import RulesConditions
from Model.Content.CombatModifiers import (
    ArmorClass,
    AutoFail,
    D20Bonus,
    D20Mode,
    D20Test,
    RollMode,
)
from Model.Content.RulesConditions import (
    CONDITION_RULES,
    conditions_given_by,
    conditions_with,
)

ADVANTAGE, DISADVANTAGE, NEUTRAL = "Advantage", "Disadvantage", "Neutral"


def _with(*conditions: str, name: str = "Tiger") -> dict:
    return {"name": name, "conditions": list(conditions)}


# ---------------------------------------------------------------------------
# The table


def test_every_rules_condition_has_its_rules():
    assert set(CONDITION_RULES) == set(Condition)


@pytest.mark.parametrize(
    "condition, given",
    [
        (Condition.PARALYZED, [Condition.PARALYZED, Condition.INCAPACITATED]),
        (Condition.PETRIFIED, [Condition.PETRIFIED, Condition.INCAPACITATED]),
        (Condition.STUNNED, [Condition.STUNNED, Condition.INCAPACITATED]),
        # "You have the Incapacitated and Prone conditions."
        (
            Condition.UNCONSCIOUS,
            [Condition.UNCONSCIOUS, Condition.INCAPACITATED, Condition.PRONE],
        ),
        (Condition.RESTRAINED, [Condition.RESTRAINED]),
    ],
)
def test_the_conditions_a_condition_gives(condition, given):
    assert conditions_given_by(condition) == given


def test_what_incapacitates():
    assert conditions_with(Condition.INCAPACITATED) == {
        Condition.INCAPACITATED,
        Condition.PARALYZED,
        Condition.PETRIFIED,
        Condition.STUNNED,
        Condition.UNCONSCIOUS,
    }


@pytest.mark.parametrize(
    "make",
    [
        lambda: D20Mode((), RollMode.ADVANTAGE),
        lambda: D20Mode(
            (D20Test.ATTACK_ROLL,), RollMode.ADVANTAGE, (Ability.DEXTERITY,)
        ),
        lambda: AutoFail((D20Test.INITIATIVE,), (Ability.DEXTERITY,)),
        lambda: D20Bonus((D20Test.SAVING_THROW,), ""),
        lambda: D20Bonus((D20Test.SAVING_THROW,), "-"),
    ],
)
def test_a_modifier_that_cant_be_true_is_refused(make):
    with pytest.raises(ValueError):
        make()


# ---------------------------------------------------------------------------
# Which conditions a combatant has


@pytest.mark.parametrize(
    "name, condition",
    [
        ("Restrained", Condition.RESTRAINED),
        ("Restrained by vines", Condition.RESTRAINED),
        ("Restrainedish", None),
        ("Bless", None),
    ],
)
def test_a_longer_name_is_the_rules_condition(name, condition):
    assert rules_condition(name) is condition


def test_a_condition_given_by_another_is_held_once():
    char = _with("Unconscious", "Prone")
    assert held_conditions(char) == [
        Condition.UNCONSCIOUS,
        Condition.INCAPACITATED,
        Condition.PRONE,
    ]
    assert has_condition(_with("Stunned"), Condition.INCAPACITATED)
    assert not has_condition(_with("Bless"), Condition.INCAPACITATED)


# ---------------------------------------------------------------------------
# The rules, condition by condition: attack rolls against it and by it

# "Attack rolls against you have Advantage."
_ATTACKED_WITH_ADVANTAGE = {
    Condition.BLINDED,
    Condition.PARALYZED,
    Condition.PETRIFIED,
    Condition.RESTRAINED,
    Condition.STUNNED,
    Condition.UNCONSCIOUS,
}
# "You have Disadvantage on attack rolls" (Frightened's and Grappled's only
# sometimes, Invisible's Advantage only sometimes: see below).
_ATTACKS_WITH_DISADVANTAGE = {
    Condition.BLINDED,
    Condition.POISONED,
    Condition.PRONE,
    Condition.RESTRAINED,
}


@pytest.mark.parametrize("condition", list(Condition))
def test_attack_rolls_against_each_condition(condition):
    plan = attack_plan(_with(name="Pirate"), _with(condition.value), NEUTRAL)
    expected = ADVANTAGE if condition in _ATTACKED_WITH_ADVANTAGE else NEUTRAL
    if condition == Condition.UNCONSCIOUS:
        # Its Prone's Disadvantage from farther than 5 feet is the GM's call.
        expected = ADVANTAGE
    assert plan.mode == expected


@pytest.mark.parametrize("condition", list(Condition))
def test_attack_rolls_by_each_condition(condition):
    plan = attack_plan(_with(condition.value, name="Pirate"), _with(), NEUTRAL)
    expected = DISADVANTAGE if condition in _ATTACKS_WITH_DISADVANTAGE else NEUTRAL
    if condition == Condition.UNCONSCIOUS:
        expected = DISADVANTAGE  # it's Prone too
    assert plan.mode == expected


# "You automatically fail Strength and Dexterity saving throws."
_FAILS_STRENGTH_AND_DEXTERITY = {
    Condition.PARALYZED,
    Condition.PETRIFIED,
    Condition.STUNNED,
    Condition.UNCONSCIOUS,
}


@pytest.mark.parametrize("condition", list(Condition))
@pytest.mark.parametrize("ability", ["STR", "DEX", "CON", "INT", "WIS", "CHA"])
def test_saving_throws_with_each_condition(condition, ability):
    plan = save_plan(_with(condition.value), ability, NEUTRAL)
    fails = condition in _FAILS_STRENGTH_AND_DEXTERITY and ability in ("STR", "DEX")
    assert bool(plan.auto_fail) is fails
    # Restrained: "You have Disadvantage on Dexterity saving throws."
    restrained_dex = condition == Condition.RESTRAINED and ability == "DEX"
    assert plan.mode == (DISADVANTAGE if restrained_dex else NEUTRAL)


def test_prone_depends_on_where_the_attacker_is():
    """ "An attack roll against you has Advantage if the attacker is within 5
    feet of you. Otherwise, that attack roll has Disadvantage." The simulator
    doesn't know where anyone is, so it counts neither and says both."""
    plan = attack_plan(_with(name="Pirate"), _with("Prone"), NEUTRAL)
    assert plan.mode == NEUTRAL
    (note,) = plan.notes
    assert note.startswith("Tiger is Prone (not counted): Advantage if the attacker")
    assert "Disadvantage if the attacker is farther than 5 feet" in note


@pytest.mark.parametrize(
    "attacker, target, says",
    [
        # "Attack rolls against you have Disadvantage, and your attack rolls
        # have Advantage. If a creature can somehow see you, you don't gain
        # this benefit against that creature."
        ("Invisible", "", "Pirate is Invisible (not counted): Advantage"),
        ("", "Invisible", "Tiger is Invisible (not counted): Disadvantage"),
        # "... while the source of fear is within line of sight."
        ("Frightened", "", "Pirate is Frightened (not counted): Disadvantage"),
        # "... against any target other than the grappler."
        ("Grappled", "", "Pirate is Grappled (not counted): Disadvantage"),
    ],
)
def test_what_depends_on_sight_or_the_grappler_is_only_noted(attacker, target, says):
    plan = attack_plan(
        _with(*filter(None, [attacker]), name="Pirate"),
        _with(*filter(None, [target])),
        NEUTRAL,
    )
    assert plan.mode == NEUTRAL
    assert any(note.startswith(says) for note in plan.notes), plan.notes


@pytest.mark.parametrize("condition", ["Paralyzed", "Unconscious"])
def test_a_hit_from_within_5_feet_is_a_critical_hit(condition):
    """ "Any attack roll that hits you is a Critical Hit if the attacker is
    within 5 feet of you": noted on a hit, for the GM to judge."""
    (note,) = hit_notes(_with(condition))
    assert f"Tiger is {condition}: a Critical Hit if the attacker is within 5" in note
    assert hit_notes(_with("Stunned")) == []


def test_exhaustion_is_noted_on_every_d20_test():
    """ "When you make a D20 Test, the roll is reduced by 2 times your
    Exhaustion level." Its level isn't tracked, so it's a note."""
    assert save_plan(_with("Exhaustion"), "WIS", NEUTRAL).notes == (
        "Exhaustion (not counted): -2 a level",
    )
    attack = attack_plan(_with("Exhaustion", name="Pirate"), _with(), NEUTRAL)
    assert attack.notes == ("Pirate's Exhaustion (not counted): -2 a level",)


def test_petrified_resists_all_damage_and_is_immune_to_poisoned():
    petrified = _with("Petrified")
    assert resists_all_damage(petrified)
    assert resists(petrified, DamageType.FIRE.value)
    assert immune_to_condition(petrified, "Poisoned")
    assert not immune_to_condition(petrified, "Prone")
    assert not resists(_with("Stunned"), DamageType.FIRE.value)


# ---------------------------------------------------------------------------
# Advantage and Disadvantage together


def test_advantage_and_disadvantage_cancel_out():
    """Poisoned attacker, Restrained target: "If multiple situations affect a
    roll and each one grants Advantage or imposes Disadvantage, you don't roll
    more than one additional d20"; one of each cancels out."""
    plan = attack_plan(_with("Poisoned", name="Pirate"), _with("Restrained"), NEUTRAL)
    assert plan.mode == NEUTRAL
    assert plan.notes == (
        "Pirate is Poisoned: Disadvantage",
        "Tiger is Restrained: Advantage",
        "Advantage and Disadvantage cancel out",
    )


@pytest.mark.parametrize(
    "asked, given, mode",
    [
        (NEUTRAL, [], NEUTRAL),
        (ADVANTAGE, [], ADVANTAGE),
        (NEUTRAL, [RollMode.ADVANTAGE, RollMode.ADVANTAGE], ADVANTAGE),
        (ADVANTAGE, [RollMode.ADVANTAGE], ADVANTAGE),
        (ADVANTAGE, [RollMode.DISADVANTAGE], NEUTRAL),
        (DISADVANTAGE, [RollMode.ADVANTAGE, RollMode.ADVANTAGE], NEUTRAL),
        (NEUTRAL, [RollMode.ADVANTAGE, RollMode.DISADVANTAGE], NEUTRAL),
    ],
)
def test_combine_modes(asked, given, mode):
    combined, _ = combine_modes(
        asked, [(f"Source {i}", m) for i, m in enumerate(given)]
    )
    assert combined == mode


def test_a_cancelled_mode_says_what_cancelled_it():
    plan = save_plan(_with("Restrained"), "DEX", ADVANTAGE)
    assert plan.notes == ("Restrained: Disadvantage, cancelling Advantage",)


def test_a_typed_total_gets_only_its_automatic_failure():
    """A total rolled at the table was rolled as the GM saw fit."""
    assert (
        save_plan(_with("Restrained", "Exhaustion"), "DEX", NEUTRAL, True).notes == ()
    )
    assert save_plan(_with("Stunned"), "DEX", NEUTRAL, True).auto_fail
    assert attack_plan(None, _with("Prone"), NEUTRAL, typed=True).notes == ()


def test_an_unknown_attacker_counts_only_the_target():
    plan = attack_plan(None, _with("Blinded"), NEUTRAL)
    assert plan.mode == ADVANTAGE
    assert plan.notes == ("Tiger is Blinded: Advantage",)


# ---------------------------------------------------------------------------
# AC


def test_ac_reads_the_modifiers(monkeypatch):
    """No rules condition changes AC; a modifier that does counts (Shield of
    Faith's +2, step 3.3)."""
    assert armor_class_bonus(_with("Restrained")) == 0
    monkeypatch.setitem(
        RulesConditions.CONDITION_RULES, Condition.DEAFENED, (ArmorClass(2),)
    )
    assert armor_class_bonus(_with("Deafened")) == 2


# ---------------------------------------------------------------------------
# What the rules-checker found (2026-11-09)


def test_an_unconscious_target_from_afar_is_a_straight_roll_and_says_so():
    """Unconscious gives Advantage and Prone; Prone's "Otherwise, that attack
    roll has Disadvantage" would cancel it, which the note has to say."""
    plan = attack_plan(_with(name="Pirate"), _with("Unconscious"), NEUTRAL)
    assert plan.mode == ADVANTAGE
    (prone,) = [n for n in plan.notes if "Prone" in n]
    assert (
        "Disadvantage if the attacker is farther than 5 feet, a straight roll then"
        in prone
    )
    assert "within 5 feet of it, a straight roll" not in prone


def test_an_attackers_own_conditions_count_without_a_target():
    plan = attack_plan(_with("Poisoned", name="Pirate"), None, NEUTRAL)
    assert plan.mode == DISADVANTAGE


def test_petrified_means_a_poisoned_it_had_does_nothing():
    """Immunity: "it doesn't affect you in any way"."""
    assert Condition.POISONED not in held_conditions(_with("Petrified", "Poisoned"))
    plan = attack_plan(_with("Petrified", "Poisoned", name="Pirate"), _with(), NEUTRAL)
    assert "Poisoned" not in " ".join(plan.notes)
