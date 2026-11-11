"""A spell's later steps, asked as its first one lands (Notes/combat-effects-plan.md,
step 6.7): `after=` on a spell's rows, the USES event (after a row picked and
applied in the Custom Effect dialog) and CombatTrigger.aim, who a triggered
row goes on.

Expected values come from the rules text:
- Ice Knife: "You create a shard of ice and fling it at one creature within
  range. Make a ranged spell attack against the target. On a hit, the target
  takes 1d10 Piercing damage. Hit or miss, the shard then explodes. The
  target and each creature within 5 feet of it must succeed on a Dexterity
  saving throw or take 2d6 Cold damage."
- Green-Flame Blade: "On a hit, the target suffers the weapon attack's normal
  effects, and you can cause green fire to leap from the target to a
  different creature of your choice that you can see within 5 feet of it.
  The second creature takes Fire damage equal to your spellcasting ability
  modifier." (Clover is below level 5: her modifier, 4.)

Clover (Curse of the Lich) knows Green-Flame Blade and is given Ice Knife."""

import random

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder as Clover,
)
from CharacterContent.Spells.SpellClasses.Cantrips import GreenFlameBlade
from CharacterContent.Spells.SpellClasses.Level1 import IceKnife
from Combat.CombatUIQt.effect_options import effect_options, triggered_rows
from Combat.Effects.triggers import (
    AttackOutcome,
    TriggerChoice,
    TriggerMode,
    UsesOutcome,
    outcome_firings,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatTriggers import (
    CombatTrigger,
    TriggerAim,
    TriggerEvent,
    trigger_problems,
)
from tests._combat_ui import make_ui

# ---------------------------------------------------------------------------
# As data


def test_aim_reads_back_and_needs_another_creature():
    trigger = CombatTrigger(
        TriggerEvent.USES, after="Ice Knife: shard", aim=TriggerAim.ALSO_OTHERS
    )
    effect = CombatEffect(name="Ice Knife: explosion", trigger=trigger)
    assert effect.to_dict()["trigger"] == {
        "event": "uses",
        "after": "Ice Knife: shard",
        "aim": "also others",
    }
    assert CombatEffect.from_dict(effect.to_dict()) == effect
    with pytest.raises(ValueError):
        CombatTrigger(TriggerEvent.ROLLS_INITIATIVE, aim=TriggerAim.ANOTHER)


def test_the_spells_say_when_their_later_steps_come():
    shard, explosion = IceKnife().combat_effects()
    assert shard.notes == ()  # "pick Ice Knife: explosion next" is gone
    assert explosion.trigger == CombatTrigger(
        TriggerEvent.USES,
        optional=False,
        after="Ice Knife: shard",
        aim=TriggerAim.ALSO_OTHERS,
    )
    _, fire = GreenFlameBlade().combat_effects()
    assert fire.trigger == CombatTrigger(
        TriggerEvent.HIT,
        optional=False,
        after="Green-Flame Blade",
        aim=TriggerAim.ANOTHER,
    )
    for spell in (IceKnife(), GreenFlameBlade()):
        assert trigger_problems(spell.name, spell.combat_effects()) == []


# ---------------------------------------------------------------------------
# The interpreter


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Clover (with Ice Knife) and two Ogres, on Clover's turn."""
    ui = make_ui(tmp_path, [Ogre(), Ogre()], [Clover().build()])
    clover, ogre, other = ui.characters
    clover["_spell_objects"] = {**clover["_spell_objects"], "Ice Knife": IceKnife()}
    for char, value in zip(ui.characters, (20, 5, 3)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(clover)
    return ui, clover, ogre, other


def _fire_rows(found):
    return [f for f in found if f.row.name == "Green-Flame Blade: leaping fire"]


def test_the_fire_leaps_only_after_a_green_flame_blade_hit(fight):
    _, clover, ogre, _ = fight
    hit = AttackOutcome(clover, ogre, True, row="Green-Flame Blade")
    (firing,) = _fire_rows(outcome_firings([hit], triggered_rows)[0])
    assert firing.mode is TriggerMode.ASK
    assert firing.question == (
        "Clover hits Ogre (Large): use Green-Flame Blade: leaping fire? 4 Fire."
        " It goes on another creature near Ogre: pick it."
    )
    # Not after another row, a miss, or a hit typed in (its row not known).
    for outcome in (
        AttackOutcome(clover, ogre, True, row="Booming Blade"),
        AttackOutcome(clover, ogre, False, row="Green-Flame Blade"),
        AttackOutcome(clover, ogre, True),
    ):
        assert _fire_rows(outcome_firings([outcome], triggered_rows)[0]) == []


def test_the_explosion_comes_after_the_shard_is_used(fight):
    _, clover, ogre, _ = fight
    found, _ = outcome_firings(
        [UsesOutcome(clover, ogre, "Ice Knife: shard")], triggered_rows
    )
    (firing,) = [f for f in found if f.row.name == "Ice Knife: explosion"]
    assert firing.mode is TriggerMode.ASK
    assert firing.question == (
        "Clover uses Ice Knife: shard on Ogre: use Ice Knife: explosion? 2d6"
        " Cold. On Ogre, and any creature near it you add."
    )
    assert (
        firing.prompt == "Ogre: Clover's Ice Knife: explosion (after Ice Knife: shard)"
    )
    found, _ = outcome_firings(
        [UsesOutcome(clover, ogre, "Ice Knife: explosion")], triggered_rows
    )
    assert [f for f in found if f.row.name == "Ice Knife: explosion"] == []


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
    """Stands in for the pop-up: records what it's asked and who each firing
    could go on, applies them all, aimed at `pick` (a function of the
    firing's others)."""

    def __init__(self, pick=lambda others: others):
        self.pick = pick
        self.asked: list[list[str]] = []
        self.others: list[list[list[dict]]] = []

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        self.others.append([list(f.others) for f in firings])
        return TriggerChoice(
            apply=tuple(firings),
            aimed=tuple((f, tuple(self.pick(f.others))) for f in firings),
        )


def _row(char, name):
    return next(
        o for _, options in effect_options(char) for o in options if o.name == name
    )


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def test_green_flame_blades_fire_goes_on_the_creature_picked(fight, monkeypatch):
    ui, clover, ogre, other = fight
    answers = Answers(pick=lambda others: others[:1])
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 15))  # 15 + 6 hits
    hp, other_hp = ogre["hp"], other["hp"]
    assert ui._apply_row(clover, ogre, _row(clover, "Green-Flame Blade"))
    assert len(answers.asked) == 1
    # Anyone else alive but Clover and the Ogre hit: the other Ogre.
    assert answers.others == [[[other]]]
    assert other["hp"] == other_hp - 4
    assert ogre["hp"] == hp  # the attack row has no damage of its own here


def test_with_no_creature_picked_the_fire_goes_nowhere(fight, monkeypatch):
    ui, clover, ogre, other = fight
    monkeypatch.setattr(ui, "_ask_triggers", Answers(pick=lambda others: ()))
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 15))
    other_hp, hp = other["hp"], ogre["hp"]
    ui._apply_row(clover, ogre, _row(clover, "Green-Flame Blade"))
    assert (other["hp"], ogre["hp"]) == (other_hp, hp)
    assert "no creature picked" in ui._status_label.text()


@pytest.mark.parametrize("roll", [1, 15])  # a miss and a hit: it explodes anyway
def test_the_shard_explodes_on_its_target_and_those_added(fight, monkeypatch, roll):
    ui, clover, ogre, other = fight
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, roll))
    ui._apply_row(clover, ogre, _row(clover, "Ice Knife: shard"))
    explosions = [q for asked in answers.asked for q in asked if "explosion" in q]
    assert len(explosions) == 1
    saves = [line for line in _lines(ui) if "save against Ice Knife: explosion" in line]
    assert len(saves) == 2  # the target and the other Ogre added
    # Part of the same casting: one slot spent, by the shard.
    assert sum(1 for line in _lines(ui) if line == "Clover casts Ice Knife") == 1
