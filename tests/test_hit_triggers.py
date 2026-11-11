"""What a hit triggers (Notes/combat-effects-plan.md, Phase 6, steps 6.1-6.3):
CombatTrigger as data, Combat/Effects/triggers.py's outcome_firings with
its gates and modes, and the combat window's three hit paths, the pop-up and
the setting.

Expected values come from Hill's Tumble (Goliath, Giant Ancestry): "When you
hit a Large or smaller creature with an attack roll and deal damage to it,
you can give that target the Prone condition. You can use the chosen benefit
a number of times equal to your Proficiency Bonus, and you regain all
expended uses when you finish a Long Rest." Kivi (Curse of the Lich, a Hill
Giant Goliath Monk) has a Proficiency Bonus of 2, so 2 uses. An Ogre is
Large; a Hill Giant is Huge."""

import json
import random
from dataclasses import asdict, replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder as Kivi,
)
from Combat.CombatUIQt.attack_rolls import parse_attack_roll
from Combat.CombatUIQt.effect_options import effect_options, triggered_rows
from Combat.CombatUIQt.monster_actions import HitRider, hit_riders, parse_action
from Combat.CombatUIQt.saves import CustomEffect
from Combat.CombatUIQt.trigger_prompt import TriggerPrompt
from Combat.Effects.triggers import (
    AttackOutcome,
    TriggerChoice,
    TriggerMode,
    TriggerRow,
    kind_fits,
    outcome_firings,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Combat.Monsters.CR_5.monsters import HillGiant
from Core.Definitions import Condition, CreatureSize, DamageType
from Model.Content.CombatEffect import CombatCondition, CombatEffect
from Model.Content.CombatModifiers import AttackKind, ExtraDamageOnHit
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent, trigger_problems
from tests._combat_ui import make_ui

TUMBLE = CombatTrigger(
    TriggerEvent.HIT, needs_damage=True, largest_target=CreatureSize.LARGE
)
TUMBLE_EFFECT = CombatEffect(
    name="Hill's Tumble",
    conditions=(CombatCondition(Condition.PRONE),),
    trigger=TUMBLE,
)

# ---------------------------------------------------------------------------
# As data (6.1)


def test_hills_tumble_says_when_it_is_used_not_a_note():
    sheet = Kivi().build()
    (feature,) = [
        f for f in sheet.iter_features_with_extensions() if f.name == "Giant Ancestry"
    ]
    (effect,) = feature.combat_effects(sheet) or []
    assert effect == TUMBLE_EFFECT
    assert effect.notes == ()


def test_a_trigger_reads_back_as_it_was_written():
    data = TUMBLE_EFFECT.to_dict()
    assert data["trigger"] == {
        "event": "hit",
        "largest_target": "Large",
        "needs_damage": True,
    }
    assert json.loads(json.dumps(data)) == data
    assert CombatEffect.from_dict(data) == TUMBLE_EFFECT


def test_a_trigger_with_every_field_reads_back():
    trigger = CombatTrigger(
        TriggerEvent.HIT,
        optional=False,
        after="Tree Club",
        attacks=AttackKind.MELEE,
        largest_target=CreatureSize.LARGE,
        needs_damage=True,
        critical_only=True,
        once_per_turn=True,
        reaction=True,
        when="it can see you",
    )
    effect = CombatEffect(name="Tree Club: Prone", trigger=trigger)
    assert CombatEffect.from_dict(effect.to_dict()) == effect


def test_an_effect_without_a_trigger_still_reads():
    """A log or file from before triggers has no "trigger" key; one that
    wrote every field (dataclasses.asdict) has it as None."""
    assert CombatEffect.from_dict({"name": "Hill's Tumble"}).trigger is None
    plain = CombatEffect(name="Hill's Tumble")
    assert CombatEffect.from_dict(asdict(plain)) == plain
    assert CombatEffect.from_dict(asdict(TUMBLE_EFFECT)) == TUMBLE_EFFECT


@pytest.mark.parametrize(
    "trigger",
    [
        {"needs_damage": True},  # no event
        {"event": "hits"},
        {"event": "hit", "largest_target": "Enormous"},
        {"event": "hit", "needs_damage": "yes"},
        {"event": "hit", "attacks": "any"},
        {"event": "hit", "range": 5},
        "hit",
    ],
)
def test_a_trigger_that_isnt_one_is_refused(trigger):
    with pytest.raises(ValueError, match="Invalid combat effect of Giant Ancestry"):
        CombatEffect.from_dict({"trigger": trigger}, "Giant Ancestry")


@pytest.mark.parametrize(
    "make, problem",
    [
        (
            lambda: CombatTrigger(
                TriggerEvent.BLOODIED, largest_target=CreatureSize.LARGE
            ),
            "largest_target",
        ),
        (lambda: CombatTrigger(TriggerEvent.MISS, needs_damage=True), "needs_damage"),
        (
            lambda: CombatTrigger(TriggerEvent.TAKES_DAMAGE, critical_only=True),
            "critical_only",
        ),
        (
            lambda: CombatTrigger(TriggerEvent.TAKES_DAMAGE, attacks=AttackKind.MELEE),
            "attacks",
        ),
        (lambda: CombatTrigger(TriggerEvent.BLOODIED, after="Tree Club"), "after"),
        (lambda: CombatTrigger(TriggerEvent.USES), "after="),
        (
            lambda: CombatTrigger("explodes"),  # pyright: ignore[reportArgumentType]
            "event",
        ),
        (
            lambda: CombatTrigger(
                TriggerEvent.HIT,
                attacks="melee attack",  # pyright: ignore[reportArgumentType]
            ),
            "AttackKind",
        ),
        (lambda: CombatTrigger(TriggerEvent.HIT, when=" if it can see you"), "spaces"),
        (
            lambda: CombatEffect(trigger="hit"),  # pyright: ignore[reportArgumentType]
            "CombatTrigger",
        ),
    ],
)
def test_invalid_combinations_raise(make, problem):
    with pytest.raises(ValueError, match=problem):
        make()


def test_an_after_must_name_another_row_of_the_source():
    club = CombatEffect(name="Tree Club")
    after_club = CombatTrigger(TriggerEvent.HIT, optional=False, after="Tree Club")
    rider = CombatEffect(name="Tree Club: Prone", trigger=after_club)
    assert trigger_problems("Tree Club", [club, rider]) == []
    # An unnamed row is the source's own.
    assert trigger_problems("Tree Club", [CombatEffect(), rider]) == []
    # Alone, it comes after nothing; nor can it come after itself.
    (problem,) = trigger_problems("Tree Club", [rider])
    assert "comes after 'Tree Club', which is no other row" in problem
    itself = replace(rider, name="Tree Club")
    assert trigger_problems("Tree Club", [itself]) != []
    stray = replace(rider, trigger=replace(after_club, after="Rock"))
    assert trigger_problems("Tree Club", [club, stray]) != []


def test_extra_damage_takes_only_the_kinds_hit_plan_reads():
    assert ExtraDamageOnHit("1d4", DamageType.RADIANT, AttackKind.WEAPON)
    with pytest.raises(ValueError, match="ANY or WEAPON"):
        ExtraDamageOnHit("1d4", DamageType.RADIANT, AttackKind.MELEE)


@pytest.mark.parametrize(
    "wanted, kind, fits",
    [
        (AttackKind.ANY, None, True),
        (AttackKind.WEAPON, AttackKind.WEAPON, True),
        (AttackKind.WEAPON, AttackKind.UNARMED, False),
        (AttackKind.WEAPON, None, None),
        (AttackKind.MELEE, AttackKind.UNARMED, True),
        (AttackKind.MELEE, AttackKind.WEAPON, None),  # a weapon may be ranged
        (AttackKind.RANGED, AttackKind.UNARMED, False),
        (AttackKind.UNARMED, AttackKind.SPELL, False),
    ],
)
def test_an_attacks_kind_fits_what_a_trigger_asks_for(wanted, kind, fits):
    assert kind_fits(wanted, kind) is fits


# ---------------------------------------------------------------------------
# The interpreter (6.2), on plain dicts

KIVI = {"name": "Kivi", "conditions": [], "hp": 27, "max_hp": 27, "_is_player": True}


def _row(uses=(2, 2), trigger=TUMBLE, costs=True) -> TriggerRow:
    return TriggerRow(
        name="Hill's Tumble",
        trigger=trigger,
        conditions=("Prone",),
        what="Prone",
        uses=uses,
        costs=costs,
    )


def _ogre(**changes) -> dict:
    return {
        "name": "Ogre",
        "size": "Large",
        "conditions": [],
        "hp": 60,
        "max_hp": 68,
        **changes,
    }


def _fire(*outcomes, row=None):
    row = row or _row()
    return outcome_firings(outcomes, lambda char: [row] if char is KIVI else [])


def _hit(target, dealt=7, **changes) -> AttackOutcome:
    return AttackOutcome(KIVI, target, True, damage_dealt=dealt, **changes)


def test_hills_tumble_on_a_large_target_asks():
    ogre = _ogre()
    (firing,), spent = _fire(_hit(ogre))
    assert (firing.target, firing.mode, firing.why, spent) == (
        ogre,
        TriggerMode.ASK,
        "",
        [],
    )
    assert firing.question == (
        "Kivi hits Ogre (Large): use Hill's Tumble? Prone. 2 of 2 uses left."
    )


@pytest.mark.parametrize("size", ["Tiny", "Small", "Medium", "Large"])
def test_large_or_smaller_creatures_can_be_tumbled(size):
    assert len(_fire(_hit(_ogre(size=size)))[0]) == 1


def test_on_a_huge_target_it_gives_nothing():
    assert _fire(_hit(_ogre(size="Huge"))) == ([], [])
    assert _fire(_hit(_ogre(size=CreatureSize.GARGANTUAN))) == ([], [])


def test_on_a_miss_it_gives_nothing():
    assert _fire(AttackOutcome(KIVI, _ogre(), False, damage_dealt=0)) == ([], [])


def test_with_no_damage_dealt_it_gives_nothing():
    """0 after Immunity: "and deal damage to it" didn't happen."""
    assert _fire(_hit(_ogre(), dealt=0)) == ([], [])


def test_with_no_uses_left_it_gives_nothing_and_says_so():
    assert _fire(_hit(_ogre()), row=_row(uses=(0, 2))) == (
        [],
        ["Hill's Tumble: no uses left"],
    )


def test_on_an_already_prone_target_it_gives_nothing():
    assert _fire(_hit(_ogre(conditions=["Prone"]))) == ([], [])


def test_on_a_dead_target_it_gives_nothing():
    assert _fire(_hit(_ogre(hp=0))) == ([], [])


def test_on_a_target_of_unknown_size_it_asks_with_the_reason():
    ogre = _ogre()
    del ogre["size"]
    (firing,), _ = _fire(_hit(ogre))
    assert (firing.mode, firing.why) == (TriggerMode.ASK, "Ogre's size isn't known")
    assert firing.question.endswith("Check: Ogre's size isn't known.")


def test_two_hits_on_one_target_ask_once():
    """Times 2, or Flurry of Blows' two strikes on one Ogre."""
    ogre = _ogre()
    assert len(_fire(_hit(ogre), _hit(ogre))[0]) == 1


def test_hits_on_two_targets_ask_about_each():
    assert len(_fire(_hit(_ogre()), _hit(_ogre(name="Orc")))[0]) == 2


def test_a_once_per_turn_row_is_offered_once():
    row = _row(trigger=replace(TUMBLE, once_per_turn=True))
    assert len(_fire(_hit(_ogre()), _hit(_ogre(name="Orc")), row=row)[0]) == 1
    used = outcome_firings(
        [_hit(_ogre())], lambda char: [row], used_this_turn={("Kivi", "Hill's Tumble")}
    )
    assert used == ([], [])


def test_what_happens_and_costs_nothing_is_automatic():
    """A monster's rider: "it has the Prone condition", no choice, no cost."""
    rider = _row(uses=None, costs=False, trigger=replace(TUMBLE, optional=False))
    (firing,), _ = _fire(_hit(_ogre()), row=rider)
    assert firing.mode is TriggerMode.AUTO
    unknown = _ogre()
    del unknown["size"]
    (firing,), _ = _fire(_hit(unknown), row=rider)
    assert firing.mode is TriggerMode.ASK


def test_a_row_after_another_comes_only_after_that_one():
    rider = _row(
        uses=None,
        costs=False,
        trigger=CombatTrigger(TriggerEvent.HIT, optional=False, after="Tree Club"),
    )
    assert _fire(_hit(_ogre(), row="Rock"), row=rider) == ([], [])
    (firing,), _ = _fire(_hit(_ogre(), row="Tree Club"), row=rider)
    assert firing.mode is TriggerMode.AUTO
    (firing,), _ = _fire(_hit(_ogre()), row=rider)  # a typed hit: which?
    assert (firing.mode, firing.why) == (TriggerMode.ASK, "if it was Tree Club")


def test_an_attack_of_unknown_kind_asks():
    """Q43: as hit_plan does, unknown never counts as automatic."""
    row = _row(trigger=replace(TUMBLE, attacks=AttackKind.UNARMED))
    (firing,), _ = _fire(_hit(_ogre()), row=row)
    assert firing.why == "if it was an unarmed strike"
    assert _fire(_hit(_ogre(), kind=AttackKind.WEAPON), row=row) == ([], [])


def test_kivis_rows_with_a_trigger():
    sheet = Kivi().build()
    from Combat.PlayerCombatant import combatant_from_character

    kivi = combatant_from_character(sheet)
    # Uncanny Metabolism comes with rolling Initiative (6.7) and Deflect
    # Attacks answers a hit on Kivi (6.5, tests/test_hit_by_triggers.py).
    rows = {r.name: r for r in triggered_rows(kivi)}
    assert sorted(rows) == ["Deflect Attacks", "Hill's Tumble", "Uncanny Metabolism"]
    row = rows["Hill's Tumble"]
    assert (row.name, row.trigger, row.conditions, row.uses, row.costs) == (
        "Hill's Tumble",
        TUMBLE,
        ("Prone",),
        (2, 2),
        True,
    )
    kivi["feature_uses_used"] = {"Giant Ancestry": 1}
    tumble = next(r for r in triggered_rows(kivi) if r.name == "Hill's Tumble")
    assert tumble.uses == (1, 2)


# ---------------------------------------------------------------------------
# In the window (6.3)


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


class Answers:
    """Stands in for the pop-up (TurnPanelMixin._ask_triggers): records
    each question and gives `answer` to it."""

    def __init__(self, answer: str = "apply"):
        self.answer = answer
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        if self.answer == "apply":
            return TriggerChoice(apply=tuple(firings))
        if self.answer == "edit":
            return TriggerChoice(edit=tuple(firings))
        return TriggerChoice()


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Kivi (20) against an Ogre (10, Large, AC 11, 68 HP) and a Hill Giant
    (5, Huge, AC 13, 105 HP), on Kivi's turn, with Kivi the source."""
    ui = make_ui(tmp_path, [Ogre(), HillGiant()], [Kivi().build()])
    kivi, ogre, giant = ui.characters
    for char, value in zip(ui.characters, (20, 10, 5)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(kivi)
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    return ui, kivi, ogre, giant, answers


def _events(ui) -> list[dict]:
    return [
        event
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def _lines(ui) -> list[str]:
    return [event["text"].split("] ", 1)[-1] for event in _events(ui)]


def _typed_hit(ui, target, roll="18", damage="7 bludgeoning"):
    """The main window: an attack roll and damage typed, one Enter."""
    ui._set_targets([target])
    ui.attack_roll_input.setText(roll)
    ui.damage_input.setText(damage)
    ui._apply_damage_checked()


def _unarmed(ui, kivi):
    (option,) = [
        o
        for _, options in effect_options(kivi, ())
        for o in options
        if o.name == "Unarmed Strike"
    ]
    return option


def _dialog_hit(ui, kivi, target, roll="18", times=1):
    """The Custom Effect dialog's Apply of Kivi's Unarmed Strike, as do_apply
    builds it (the attack roll typed in its target row)."""
    ui._set_targets([target])
    attack = parse_attack_roll(roll)
    assert attack is not None
    effect = CustomEffect(
        name="Unarmed Strike",
        damage=[(7, "Bludgeoning")],
        attack_bonus=6,
        typed_attacks={id(target): attack},
        pick=_unarmed(ui, kivi),
        weapon_attack=False,
    )
    if times == 1:
        ui._apply_custom_effect(effect)
    else:
        copies = [effect] + [
            replace(effect, name=f"Unarmed Strike ({i + 1} of {times})", pick=None)
            for i in range(1, times)
        ]
        ui._apply_custom_effects(copies)


def _uses_spent(kivi) -> int:
    return (kivi.get("feature_uses_used") or {}).get("Giant Ancestry", 0)


def test_a_typed_hit_on_an_ogre_asks_once_and_apply_tumbles_it(fight):
    ui, kivi, ogre, _, answers = fight
    _typed_hit(ui, ogre)
    assert answers.asked == [
        [
            f"{kivi['name']} hits Ogre (Large): use Hill's Tumble? Prone. 2 of 2 uses left."
        ]
    ]
    assert "Prone" in ogre["conditions"]
    assert "Hill's Tumble" in ogre["conditions"]  # its own badge (R126)
    assert _uses_spent(kivi) == 1
    lines = _lines(ui)
    assert lines[-4:] == [
        "Ogre takes 7 Bludgeoning damage from Kivi Jätti",
        "Kivi Jätti uses Giant Ancestry",
        "Ogre gains Prone from Kivi Jätti",
        "Ogre gains Hill's Tumble from Kivi Jätti",
    ]
    assert ui._status_label.text() == "Ogre: 18 vs AC 11, hit"


def test_an_attack_roll_entered_then_its_damage_asks_once(fight):
    ui, kivi, ogre, _, answers = fight
    ui._set_targets([ogre])
    ui.attack_roll_input.setText("18")
    ui._apply_attack_roll()
    assert answers.asked == []
    ui.damage_input.setText("7 bludgeoning")
    ui._apply_damage_checked()
    assert len(answers.asked) == 1
    assert "Prone" in ogre["conditions"]


def test_damage_typed_without_an_attack_roll_asks_nothing(fight):
    """It might be a spell's or a fall's: nothing says it was a hit."""
    ui, _, ogre, _, answers = fight
    ui._set_targets([ogre])
    ui.damage_input.setText("7 bludgeoning")
    ui._apply_damage_checked()
    assert answers.asked == []


def test_an_undone_attack_roll_no_longer_counts(fight):
    ui, _, ogre, _, answers = fight
    ui._set_targets([ogre])
    ui.attack_roll_input.setText("18")
    ui._apply_attack_roll()
    ui._undo_last()
    ui.attack_roll_input.clear()
    ui.damage_input.setText("7 bludgeoning")
    ui._apply_damage_checked()
    assert answers.asked == []


def test_a_monster_buttons_hit_asks_once(fight, monkeypatch):
    """The turn column's action button rolls the hit into the Damage field,
    and Enter deals it."""
    ui, kivi, ogre, _, answers = fight
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 15))
    ui._set_targets([ogre])
    slam = parse_action(
        {
            "name": "Slam",
            "description": "Melee Attack Roll: +6, reach 5 ft. Hit: 7 (1d6 + 4)"
            " Bludgeoning damage.",
        }
    )
    ui._roll_action(slam, kivi)
    assert ui.damage_input.text() == "10 Bludgeoning"
    ui._apply_damage_checked()
    assert len(answers.asked) == 1
    assert "Prone" in ogre["conditions"]


def test_the_dialogs_hit_asks_once(fight):
    ui, kivi, ogre, _, answers = fight
    _dialog_hit(ui, kivi, ogre)
    assert len(answers.asked) == 1
    assert "Prone" in ogre["conditions"]
    assert _uses_spent(kivi) == 1


def test_times_two_asks_once(fight):
    ui, kivi, ogre, _, answers = fight
    _dialog_hit(ui, kivi, ogre, times=2)
    assert len(answers.asked) == 1
    assert len(answers.asked[0]) == 1
    assert ogre["hp"] == 68 - 14
    assert _uses_spent(kivi) == 1


def test_a_huge_target_asks_nothing(fight):
    ui, kivi, _, giant, answers = fight
    _typed_hit(ui, giant)
    _dialog_hit(ui, kivi, giant)
    assert answers.asked == []
    assert "Prone" not in giant["conditions"]


def test_a_miss_asks_nothing(fight):
    ui, kivi, ogre, _, answers = fight
    _typed_hit(ui, ogre, roll="5")
    _dialog_hit(ui, kivi, ogre, roll="5")
    assert answers.asked == []


def test_no_damage_after_immunity_asks_nothing(fight):
    ui, kivi, ogre, _, answers = fight
    ogre["damage_immunities"] = [{"damage_types": ["Bludgeoning"]}]
    _typed_hit(ui, ogre)
    _dialog_hit(ui, kivi, ogre)
    assert ogre["hp"] == 68
    assert answers.asked == []


def test_no_uses_left_asks_nothing_and_says_so(fight):
    ui, kivi, ogre, _, answers = fight
    kivi["feature_uses_used"] = {"Giant Ancestry": 2}
    _typed_hit(ui, ogre)
    assert answers.asked == []
    assert ui._status_label.text() == (
        "Ogre: 18 vs AC 11, hit; Hill's Tumble: no uses left"
    )


def test_an_already_prone_target_asks_nothing(fight):
    ui, _, ogre, _, answers = fight
    ogre["conditions"].append("Prone")
    _typed_hit(ui, ogre)
    assert answers.asked == []


def test_a_target_of_unknown_size_asks_with_the_reason(fight):
    ui, kivi, ogre, _, answers = fight
    del ogre["size"]
    _typed_hit(ui, ogre)
    assert answers.asked == [
        [
            f"{kivi['name']} hits Ogre: use Hill's Tumble? Prone. 2 of 2 uses"
            " left. Check: Ogre's size isn't known."
        ]
    ]


def test_skip_changes_nothing_but_a_line_for_the_gm(fight):
    ui, kivi, ogre, _, answers = fight
    answers.answer = "skip"
    _typed_hit(ui, ogre)
    assert "Prone" not in ogre["conditions"]
    assert _uses_spent(kivi) == 0
    last = _events(ui)[-1]
    assert last["text"].endswith(f"{kivi['name']} didn't use Hill's Tumble on Ogre")
    assert not last.get("public")


def test_one_undo_takes_back_the_hit_and_the_prone(fight):
    ui, kivi, ogre, _, _ = fight
    before = len(ui.history)
    _typed_hit(ui, ogre)
    assert len(ui.history) == before + 1
    ui._undo_last()
    ogre = ui._find_character_by_name("Ogre")
    kivi = ui._find_character_by_name(kivi["name"])
    assert ogre["hp"] == 68
    assert "Prone" not in ogre["conditions"]
    assert _uses_spent(kivi) == 0
    assert not any("Prone" in line for line in _lines(ui))


def test_one_undo_takes_back_the_dialogs_hit_and_the_prone(fight):
    ui, kivi, ogre, _, _ = fight
    _dialog_hit(ui, kivi, ogre)
    ui._undo_last()
    ogre = ui._find_character_by_name("Ogre")
    assert (ogre["hp"], "Prone" in ogre["conditions"]) == (68, False)


def test_with_the_setting_off_nothing_is_asked(fight):
    """Off, the hits only leave a button in the turn column (Q40)."""
    ui, kivi, ogre, _, answers = fight
    ui.settings.ask_triggers = False
    _typed_hit(ui, ogre)
    _dialog_hit(ui, kivi, ogre)
    assert answers.asked == []
    assert ogre["hp"] == 68 - 14
    assert "Prone" not in ogre["conditions"]
    assert _uses_spent(kivi) == 0
    assert not any("didn't use" in line for line in _lines(ui))
    assert len(ui._hit_prompts) == 2  # one per Apply


def test_with_the_setting_off_it_asks_with_a_turn_column_button(fight, monkeypatch):
    ui, kivi, ogre, _, answers = fight
    ui.settings.ask_triggers = False
    _typed_hit(ui, ogre)
    assert answers.asked == []
    (prompt,) = ui._hit_prompts
    buttons = [
        ui._turn_prompts_layout.itemAt(i).widget().text()
        for i in range(ui._turn_prompts_layout.count())
    ]
    assert buttons == [prompt.prompt]
    assert prompt.prompt == f"Ogre: {kivi['name']}'s Hill's Tumble (on a hit)"
    opened: list[str] = []
    monkeypatch.setattr(
        ui, "_show_custom_condition_dialog", lambda pick="": opened.append(pick)
    )
    ui._use_turn_prompt(prompt)
    assert opened == ["Hill's Tumble"]
    assert ui._hit_prompts == ()
    assert ui.target_characters == [ogre]
    ui._advance_turn()
    assert ui._hit_prompts == ()


def test_edit_opens_the_dialog_with_the_row_picked(fight, monkeypatch):
    ui, kivi, ogre, giant, answers = fight
    answers.answer = "edit"
    seen = []
    monkeypatch.setattr(
        ui,
        "_show_custom_condition_dialog",
        lambda pick="": seen.append(
            (pick, ui.selected_character, list(ui.target_characters))
        ),
    )
    _typed_hit(ui, ogre)
    assert seen == [("Hill's Tumble", kivi, [ogre])]
    assert "Prone" not in ogre["conditions"]  # the dialog wasn't applied


def test_the_popup_gives_the_checked_rows(fight):
    ui, kivi, ogre, _, _ = fight
    firings, _ = outcome_firings(
        [
            AttackOutcome(kivi, ogre, True, damage_dealt=5),
            AttackOutcome(kivi, _ogre(name="Orc"), True, damage_dealt=5),
        ],
        triggered_rows,
    )
    prompt = TriggerPrompt(None, firings)
    assert [box.isChecked() for box in prompt.boxes] == [True, True]
    prompt.boxes[1].setChecked(False)
    prompt.apply_button.click()
    assert prompt.choice() == TriggerChoice(apply=(firings[0],))
    prompt = TriggerPrompt(None, firings)
    prompt.edit_button.click()
    assert prompt.choice() == TriggerChoice(edit=tuple(firings))
    prompt = TriggerPrompt(None, firings)
    prompt.skip_button.click()
    assert prompt.choice() == TriggerChoice()


# ---------------------------------------------------------------------------
# Monster riders (6.4): a condition a monster's hit gives, read from its text.
# The Hill Giant's Tree Club: "Hit: 18 (3d8 + 5) Bludgeoning damage. If the
# target is a Large or smaller creature, it has the Prone condition." Its
# Trash Lob: "Hit: 16 (2d10 + 5) Bludgeoning damage, and the target has the
# Poisoned condition until the end of its next turn."


def _tree_club_ability():
    return next(a for a in HillGiant().actions or [] if a.name == "Tree Club")


def _attack(hit: str) -> dict:
    return {"name": "Bite", "description": f"Melee Attack Roll: +5. Hit: {hit}"}


def test_tree_clubs_prone_is_a_row_of_its_own_that_comes_as_it_hits():
    giant = HillGiant()
    char = {"name": "Hill Giant", "actions": giant.actions, "size": "Huge"}
    (actions,) = [
        rows for title, rows in effect_options(char, ()) if title == "Actions"
    ]
    by_name = {o.name: o for o in actions}
    club = by_name["Tree Club"]
    assert (club.bonus, club.damage, club.condition, club.note) == (
        8,
        "3d8 + 5 Bludgeoning",
        "",  # the row below gives it, only to a Large or smaller target
        "",
    )
    prone = by_name["Tree Club: Prone"]
    assert prone.condition == "Prone"
    assert prone.trigger == CombatTrigger(
        TriggerEvent.HIT,
        optional=False,
        after="Tree Club",
        largest_target=CreatureSize.LARGE,
    )
    assert prone.row_text == "Tree Club: Prone  on a hit, Large or smaller"
    assert prone.monster_action is None  # it spends nothing: the attack did
    poisoned = by_name["Trash Lob: Poisoned"]
    assert (poisoned.condition, poisoned.until) == ("Poisoned", ("end", "target"))
    assert poisoned.trigger is not None
    assert poisoned.trigger.largest_target is None
    assert by_name["Trash Lob"].condition == ""
    assert [r.name for r in triggered_rows(char)] == [
        "Tree Club: Prone",
        "Trash Lob: Poisoned",
    ]


def test_the_turn_columns_also_line_no_longer_says_the_rider():
    club = parse_action(_tree_club_ability())
    assert club.rider == ""
    (rider,) = club.riders
    assert rider == HitRider(
        text="If the target is a Large or smaller creature, it has the Prone"
        " condition",
        conditions=("Prone",),
        largest_target=CreatureSize.LARGE,
    )


@pytest.mark.parametrize(
    "hit, conditions, largest, until, note",
    [
        (
            "4 (1d4 + 2) Piercing damage, and the target has the Poisoned"
            " condition until the start of the centipede's next turn.",
            ("Poisoned",),
            None,
            ("start", "source"),
            "",
        ),
        (
            "22 (2d12 + 9) Lightning damage, and the target has the Blinded and"
            " Deafened conditions until the start of the giant's next turn.",
            ("Blinded", "Deafened"),
            None,
            ("start", "source"),
            "",
        ),
        (
            "8 (1d8 + 4) Slashing damage. If the target is a Medium or smaller"
            " creature, it has the Grappled condition (escape DC 11) from one of"
            " two claws.",
            ("Grappled",),
            CreatureSize.MEDIUM,
            None,
            "Escape DC 11, from one of two claws.",
        ),
        (
            "22 (3d8 + 9) Piercing damage. If the target is a Large or smaller"
            " creature, it has the Grappled condition (escape DC 19), and it has"
            " the Restrained condition until the grapple ends.",
            ("Grappled", "Restrained"),
            CreatureSize.LARGE,
            None,
            "Escape DC 19. Restrained until the grapple ends.",
        ),
        (
            # A MeleeAttack's additional_ruling, as the crocodile's.
            "7 (1d10 + 2) Piercing damage. If the target is Medium or smaller,"
            " it has the Grappled condition (escape DC 12). While Grappled, the"
            " target has the Restrained condition.",
            ("Grappled", "Restrained"),
            CreatureSize.MEDIUM,
            None,
            "Escape DC 12. Restrained while Grappled.",
        ),
    ],
)
def test_a_rider_reads_its_conditions_size_duration_and_note(
    hit, conditions, largest, until, note
):
    action = parse_action(_attack(hit))
    (rider,) = action.riders
    assert (rider.conditions, rider.largest_target, rider.until, rider.note) == (
        conditions,
        largest,
        until,
        note,
    )
    assert (rider.when, rider.once_per_turn, action.rider) == ("", False, "")


def test_what_only_the_gm_can_tell_is_a_when():
    (rider,) = parse_action(
        _attack(
            "20 (3d8 + 7) Piercing damage. If the target is a Huge or smaller"
            " creature and the elephant moved 20+ feet straight toward it"
            " immediately before the hit, the target has the Prone condition."
        )
    ).riders
    assert (rider.largest_target, rider.when) == (
        CreatureSize.HUGE,
        "the elephant moved 20+ feet straight toward it immediately before the hit",
    )
    (rider,), _ = hit_riders(
        "Once per turn, if Mirelle had Advantage on the attack roll and the"
        " target is Medium or smaller, the target also has the Prone condition"
    )
    assert (rider.once_per_turn, rider.largest_target, rider.when) == (
        True,
        CreatureSize.MEDIUM,
        "Mirelle had Advantage on the attack roll",
    )


@pytest.mark.parametrize(
    "hit",
    [
        # Something more happens too, or it's a choice, or a save.
        "8 (1d8 + 4) Slashing damage. If the target is a Large or smaller"
        " creature and the allosaurus moved 30+ feet straight toward it"
        " immediately before the hit, the target has the Prone condition, and"
        " the allosaurus can make one Bite attack against it.",
        "1 Radiant damage, and the target has the Charmed or Poisoned condition"
        " (pixie's choice) until the start of the pixie's next turn.",
        "18 (3d6 + 8) Force damage. If the target is a Huge or smaller creature,"
        " the balor pulls the target up to 25 feet straight toward itself, and"
        " the target has the Prone condition.",
        "7 (1d8 + 3) Bludgeoning damage, and the target must succeed on a DC 12"
        " Strength saving throw or have the Prone condition.",
        "10 (2d6 + 3) Bludgeoning damage. If this damage reduces the target to 0"
        " Hit Points, the target becomes Stable, and it has the Poisoned"
        " condition for 1 hour.",
    ],
)
def test_a_sentence_that_says_more_is_no_rider(hit):
    action = parse_action(_attack(hit))
    assert action.riders == ()
    assert action.rider  # still there for the GM to read


def test_the_rest_of_the_text_stays_in_the_rider():
    action = parse_action(
        _attack(
            "9 (2d6 + 2) Piercing damage. If the target is a Medium or smaller"
            " creature, it has the Grappled condition (escape DC 12). Until the"
            " grapple ends, the kuo-toa can't make Pincer Staff attacks."
        )
    )
    assert len(action.riders) == 1
    assert action.rider == (
        "Until the grapple ends, the kuo-toa can't make Pincer Staff attacks"
    )


def _club_rows(giant: dict) -> list[TriggerRow]:
    return [r for r in triggered_rows(giant) if r.name == "Tree Club: Prone"]


def _giant_dict() -> dict:
    giant = HillGiant()
    return {"name": "Hill Giant", "actions": giant.actions, "conditions": []}


def test_tree_clubs_rider_on_a_large_target_is_automatic():
    giant = _giant_dict()
    hit = AttackOutcome(giant, _ogre(), True, row="Tree Club", damage_dealt=20)
    (firing,), _ = outcome_firings([hit], _club_rows)
    assert (firing.mode, firing.why) == (TriggerMode.AUTO, "")
    huge = replace(hit, target=_ogre(size="Huge"))
    assert outcome_firings([huge], _club_rows) == ([], [])
    assert outcome_firings([replace(hit, hit=False)], _club_rows) == ([], [])
    assert outcome_firings([replace(hit, row="Trash Lob")], _club_rows) == ([], [])
    unknown = _ogre()
    del unknown["size"]
    (firing,), _ = outcome_firings([replace(hit, target=unknown)], _club_rows)
    assert (firing.mode, firing.why) == (TriggerMode.ASK, "Ogre's size isn't known")


@pytest.fixture
def giants_turn(fight):
    """The Hill Giant the source, the Ogre (Large) its target."""
    ui, kivi, ogre, giant, answers = fight
    ui._select_character(giant)
    ui._set_targets([ogre])
    return ui, kivi, ogre, giant, answers


def _tree_club(giant):
    return parse_action(next(a for a in giant["actions"] if a.name == "Tree Club"))


def _club_option(giant):
    (option,) = [
        o
        for _, options in effect_options(giant, ())
        for o in options
        if o.name == "Tree Club"
    ]
    return option


def _dialog_club(ui, giant, target, roll="20", times=1):
    """The Custom Effect dialog's Apply of the giant's Tree Club, as do_apply
    builds it (the attack roll typed in its target row), and its Times
    copies as `repeated` does."""
    ui._set_targets([target])
    attack = parse_attack_roll(roll)
    assert attack is not None
    effect = CustomEffect(
        name="Tree Club",
        damage=[(18, "Bludgeoning")],
        attack_bonus=8,
        typed_attacks={id(target): attack},
        pick=_club_option(giant),
    )
    if times == 1:
        ui._apply_custom_effect(effect)
    else:
        copies = [effect] + [
            replace(
                effect,
                name=f"Tree Club ({i + 1} of {times})",
                pick=None,
                row="Tree Club",
            )
            for i in range(1, times)
        ]
        ui._apply_custom_effects(copies)


def test_the_giants_button_and_enter_knock_the_ogre_prone(giants_turn, monkeypatch):
    ui, _, ogre, giant, answers = giants_turn
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 15))
    ui._roll_action(_tree_club(giant), giant)
    ui._apply_damage_checked()
    assert answers.asked == []
    assert "Prone" in ogre["conditions"]
    assert _lines(ui)[-1] == "Ogre gains Prone from Hill Giant"


def test_the_giants_button_does_nothing_to_a_huge_target(giants_turn, monkeypatch):
    ui, _, ogre, giant, answers = giants_turn
    ogre["size"] = "Huge"
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 15))
    ui._roll_action(_tree_club(giant), giant)
    ui._apply_damage_checked()
    assert ogre["hp"] < 68
    assert (answers.asked, "Prone" in ogre["conditions"]) == ([], False)


def test_the_giants_miss_does_nothing(giants_turn, monkeypatch):
    ui, _, ogre, giant, answers = giants_turn
    monkeypatch.setattr(random, "randint", lambda a, b: 1)
    ui._roll_action(_tree_club(giant), giant)
    assert (answers.asked, "Prone" in ogre["conditions"]) == ([], False)


def test_the_dialogs_tree_club_knocks_the_ogre_prone(giants_turn):
    ui, _, ogre, giant, answers = giants_turn
    _dialog_club(ui, giant, ogre)
    assert answers.asked == []
    assert ogre["hp"] == 68 - 18
    assert "Prone" in ogre["conditions"]


def test_the_dialogs_tree_club_does_nothing_to_a_huge_target_or_on_a_miss(
    giants_turn,
):
    ui, _, ogre, giant, answers = giants_turn
    _dialog_club(ui, giant, ogre, roll="2")
    assert "Prone" not in ogre["conditions"]
    ogre["size"] = "Huge"
    _dialog_club(ui, giant, ogre)
    assert ogre["hp"] == 68 - 18
    assert (answers.asked, "Prone" in ogre["conditions"]) == ([], False)


def test_times_two_knows_both_were_tree_clubs(giants_turn):
    """The second copy has no pick, but keeps the row it was made with."""
    ui, _, ogre, giant, answers = giants_turn
    ogre["armor_class"] = 1  # the second copy rolls its own attack
    _dialog_club(ui, giant, ogre, times=2)
    assert answers.asked == []
    assert ogre["conditions"].count("Prone") == 1


def test_a_target_of_unknown_size_is_asked_about(giants_turn):
    ui, _, ogre, giant, answers = giants_turn
    del ogre["size"]
    _dialog_club(ui, giant, ogre)
    assert answers.asked == [
        [
            "Hill Giant hits Ogre: use Tree Club: Prone? Prone. Check: Ogre's"
            " size isn't known."
        ]
    ]
    assert "Prone" in ogre["conditions"]


def test_a_typed_hit_asks_which_attack_it_was(giants_turn):
    ui, _, ogre, _, answers = giants_turn
    _typed_hit(ui, ogre, roll="20", damage="18 bludgeoning")
    assert answers.asked == [
        [
            "Hill Giant hits Ogre (Large): use Tree Club: Prone? Prone. Check: if"
            " it was Tree Club.",
            "Hill Giant hits Ogre (Large): use Trash Lob: Poisoned? Poisoned."
            " Check: if it was Trash Lob.",
        ]
    ]


def test_one_undo_takes_back_the_giants_hit_and_the_prone(giants_turn):
    ui, _, ogre, giant, _ = giants_turn
    before = len(ui.history)
    _dialog_club(ui, giant, ogre)
    assert len(ui.history) == before + 1
    ui._undo_last()
    ogre = ui._find_character_by_name("Ogre")
    assert (ogre["hp"], "Prone" in ogre["conditions"]) == (68, False)


def test_a_grapples_escape_dc_goes_on_its_badge(giants_turn):
    ui, _, ogre, giant, _ = giants_turn
    giant["actions"] = [
        {
            "name": "Claw",
            "description": "Melee Attack Roll: +8, reach 5 ft. Hit: 8 (1d8 + 4)"
            " Slashing damage. If the target is a Large or smaller creature, it"
            " has the Grappled condition (escape DC 14) from one of two claws.",
        }
    ]
    (rider,) = triggered_rows(giant)
    assert rider.name == "Claw: Grappled"
    assert ui._apply_row(giant, ogre, rider.option)
    assert "Grappled" in ogre["conditions"]
    (record,) = [e for e in ogre["active_effects"] if e["name"] == "Grappled"]
    assert record["tooltip"].startswith("<i>Escape DC 14, from one of two claws.</i>")
