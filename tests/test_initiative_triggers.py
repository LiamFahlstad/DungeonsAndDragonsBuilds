"""What rolling Initiative triggers (Notes/combat-effects-plan.md, step 6.7):
ROLLS_INITIATIVE rows, given or asked about once as the fight starts, and
CombatEffect.regains, the expended feature uses a row gives back.

Expected values come from the rules text:
- Uncanny Metabolism (Monk 2): "When you roll Initiative, you can regain all
  expended Focus Points. When you do so, roll your Martial Arts die, and
  regain a number of Hit Points equal to your Monk level plus the number
  rolled. Once you use this feature, you can't use it again until you finish
  a Long Rest." Kivi (Monk 4, Martial Arts die 1d6) has 4 Focus Points.
- Perfect Focus (Monk 15): "... you regain expended Focus Points until you
  have 4 if you have 3 or fewer."
- Superior Inspiration (Bard 18): "When you roll Initiative, you regain
  expended uses of Bardic Inspiration until you have two if you have fewer
  than that."
- Evergreen Wild Shape (Archdruid, Druid 20): "Whenever you roll Initiative
  and have no uses of Wild Shape left, you regain one expended use of it."
- Ever-Ready Shot (Arcane Archer 10): "When you roll Initiative, you can
  regain one expended use of Arcane Shot."
- Persistent Rage (Barbarian 15): "When you roll Initiative, you can regain
  all expended uses of Rage."

Clover (a Valor Bard) is given Superior Inspiration for these tests."""

from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder as Clover,
)
from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder as Kivi,
)
from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
    PersistentRage,
)
from CharacterContent.Features.ClassFeatures.Bard.BardFeatures import (
    SuperiorInspiration,
)
from CharacterContent.Features.ClassFeatures.Druid.DruidFeatures import Archdruid
from CharacterContent.Features.ClassFeatures.Monk.MonkFeatures import (
    PerfectFocus,
    UncannyMetabolism,
)
from CharacterContent.Features.SubClassFeatures.Fighter.FighterArcaneArcherFeatures import (
    EverReadyShot,
)
from Combat.CombatUIQt.effect_options import (
    effect_options,
    regained_uses,
    triggered_rows,
)
from Combat.Effects.triggers import (
    InitiativeOutcome,
    TriggerChoice,
    TriggerMode,
    outcome_firings,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Model.Content.CombatEffect import CombatEffect, CombatRegain
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from tests._combat_ui import make_ui

FOCUS = "Monk's Focus"
INITIATIVE = CombatTrigger(TriggerEvent.ROLLS_INITIATIVE)
IT_HAPPENS = CombatTrigger(TriggerEvent.ROLLS_INITIATIVE, optional=False)

# ---------------------------------------------------------------------------
# As data


def test_regains_read_back_as_they_were_written():
    effect = CombatEffect(
        targets_self=True,
        regains=(CombatRegain(FOCUS), CombatRegain("Bardic Inspiration", up_to=2)),
        trigger=INITIATIVE,
    )
    data = effect.to_dict()
    assert data["regains"] == [
        {"feature": FOCUS},
        {"feature": "Bardic Inspiration", "up_to": 2},
    ]
    assert CombatEffect.from_dict(data) == effect


@pytest.mark.parametrize(
    "make",
    [
        lambda: CombatEffect(regains=(CombatRegain(FOCUS),)),  # not targets_self
        lambda: CombatEffect(
            targets_self=True, regains=(CombatRegain(FOCUS), CombatRegain(FOCUS))
        ),
        lambda: CombatRegain(""),
        lambda: CombatRegain(FOCUS, up_to=0),
        lambda: CombatRegain(FOCUS, count=True),
    ],
)
def test_regains_go_on_the_user_and_count_from_1(make):
    with pytest.raises(ValueError):
        make()


def test_the_features_say_what_rolling_initiative_gives():
    sheet = Kivi().build()
    (metabolism,) = UncannyMetabolism().combat_effects(sheet)
    assert metabolism.trigger == INITIATIVE
    assert metabolism.regains == (CombatRegain(FOCUS),)
    assert metabolism.healing is not None
    assert metabolism.healing.dice == "1d6 + 4"
    (focus,) = PerfectFocus().combat_effects(sheet)
    assert (focus.trigger, focus.regains) == (IT_HAPPENS, (CombatRegain(FOCUS, 4),))
    (inspiration,) = SuperiorInspiration().combat_effects(sheet)
    assert (inspiration.trigger, inspiration.regains) == (
        IT_HAPPENS,
        (CombatRegain("Bardic Inspiration", up_to=2),),
    )
    evergreen, _ = Archdruid().combat_effects(sheet)
    assert (evergreen.trigger, evergreen.regains, evergreen.spends_use) == (
        IT_HAPPENS,
        (CombatRegain("Wild Shape", up_to=1),),
        False,
    )
    (shot,) = EverReadyShot().combat_effects(sheet)
    assert (shot.trigger, shot.regains) == (
        INITIATIVE,
        (CombatRegain("Arcane Shot", count=1),),
    )
    (rage,) = PersistentRage().combat_effects(sheet)
    assert (rage.trigger, rage.regains) == (INITIATIVE, (CombatRegain("Rage"),))


# ---------------------------------------------------------------------------
# The interpreter


@pytest.fixture
def kivi():
    from Combat.PlayerCombatant import combatant_from_character

    return combatant_from_character(Kivi().build())


@pytest.mark.parametrize(
    "used, regain, back",
    [
        (3, CombatRegain(FOCUS), 3),
        (0, CombatRegain(FOCUS), 0),
        (3, CombatRegain(FOCUS, up_to=4), 3),  # 1 left: until 4
        (1, CombatRegain(FOCUS, up_to=2), 0),  # 3 left: already 2 or more
        (3, CombatRegain(FOCUS, count=1), 1),
        (3, CombatRegain("Rage"), 0),  # Kivi has no Rage
    ],
)
def test_regained_uses(kivi, used, regain, back):
    kivi["feature_uses_used"] = {FOCUS: used}
    assert regained_uses(kivi, regain) == back


def _initiative_firings(char):
    found, _ = outcome_firings([InitiativeOutcome(char)], triggered_rows)
    return found


def test_with_nothing_to_regain_nothing_is_asked(kivi):
    assert _initiative_firings(kivi) == []


def test_uncanny_metabolism_asks_when_focus_is_spent(kivi):
    kivi["feature_uses_used"] = {FOCUS: 3}
    (firing,) = _initiative_firings(kivi)
    assert firing.mode is TriggerMode.ASK
    assert firing.owner is kivi and firing.target is kivi
    assert firing.question == (
        f"{kivi['name']} rolls Initiative: use Uncanny Metabolism? 1d6 + 4 Hit"
        f" Points, every expended use of {FOCUS}. 1 of 1 uses left."
    )
    assert (
        firing.prompt == f"{kivi['name']}: Uncanny Metabolism (on rolling Initiative)"
    )


def test_hurt_with_full_focus_it_still_asks(kivi):
    kivi["hp"] = kivi["max_hp"] - 6
    assert len(_initiative_firings(kivi)) == 1


def test_used_today_it_isnt_asked(kivi):
    kivi["feature_uses_used"] = {FOCUS: 3, "Uncanny Metabolism": 1}
    assert _initiative_firings(kivi) == []


def test_the_picker_row_says_what_it_regains(kivi):
    (row,) = [
        o
        for _, options in effect_options(kivi)
        for o in options
        if o.name == "Uncanny Metabolism"
    ]
    assert "Its user regains every expended use of Monk's Focus." in row.note
    assert "reset them by hand" not in row.note


# ---------------------------------------------------------------------------
# In the window


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


class Answers:
    """Stands in for the pop-up: records each question, gives `answer`."""

    def __init__(self, answer: str = "apply"):
        self.answer = answer
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        if self.answer == "apply":
            return TriggerChoice(apply=tuple(firings))
        return TriggerChoice()


@pytest.fixture
def window(tmp_path, monkeypatch):
    """Clover (with Superior Inspiration), Kivi and an Ogre, before the
    fight starts; start() starts it."""
    ui = make_ui(tmp_path, [Ogre()], [Clover().build(), Kivi().build()])
    clover, kivi, ogre = ui.characters
    clover["_feature_objects"] = [*clover["_feature_objects"], SuperiorInspiration()]
    for char, value in zip(ui.characters, (5, 3, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    return ui, clover, kivi, ogre, answers


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def test_a_rested_party_is_asked_nothing(window):
    ui, _, _, _, answers = window
    ui._start_combat()
    assert answers.asked == []


def test_kivi_regains_his_focus_and_hit_points_as_the_fight_starts(window):
    ui, _, kivi, _, answers = window
    kivi["feature_uses_used"] = {FOCUS: 3}
    kivi["hp"] = hp = kivi["max_hp"] - 20
    ui._start_combat()
    assert len(answers.asked) == 1
    assert answers.asked[0][0].startswith(f"{kivi['name']} rolls Initiative:")
    assert kivi["feature_uses_used"][FOCUS] == 0
    assert kivi["feature_uses_used"]["Uncanny Metabolism"] == 1
    assert hp + 5 <= kivi["hp"] <= hp + 10  # 1d6 + 4
    lines = _lines(ui)
    assert (
        lines.count(f"{kivi['name']} regains a use of {FOCUS} (Uncanny Metabolism)")
        == 3
    )


def test_skip_leaves_everything_as_it_was(window):
    ui, _, kivi, _, answers = window
    answers.answer = "skip"
    kivi["feature_uses_used"] = {FOCUS: 3}
    ui._start_combat()
    assert kivi["feature_uses_used"] == {FOCUS: 3}


def test_superior_inspiration_is_given_without_asking(window):
    ui, clover, _, _, answers = window
    most = next(
        f for f in clover["_feature_objects"] if f.name == "Bardic Inspiration"
    ).number_of_uses(clover["_stat_block"])
    assert most >= 2
    clover["feature_uses_used"] = {"Bardic Inspiration": most}
    ui._start_combat()
    assert answers.asked == []
    assert clover["feature_uses_used"]["Bardic Inspiration"] == most - 2


def test_with_the_setting_off_it_is_a_turn_column_button(window):
    ui, _, kivi, _, answers = window
    ui.settings = replace(ui.settings, ask_triggers=False)
    kivi["feature_uses_used"] = {FOCUS: 3}
    ui._start_combat()
    assert answers.asked == []
    assert [p.prompt for p in ui._hit_prompts] == [
        f"{kivi['name']}: Uncanny Metabolism (on rolling Initiative)"
    ]
    (firing,) = ui._hit_prompts
    ui._use_trigger(firing, [])
    assert kivi["feature_uses_used"][FOCUS] == 0
