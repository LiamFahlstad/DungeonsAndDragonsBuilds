"""What Hit Points reaching 0 triggers (Notes/combat-effects-plan.md, step
6.6): DROPS_TO_ZERO rows asked as damage would drop their owner to 0, before
it does (Relentless Endurance, Relentless Rage), REDUCES_TO_ZERO rows of the
creature that did it (Dark One's Blessing), CombatEffect.drops_to and the
trigger's enemy_only gate.

Expected values come from the rules text:
- Relentless Endurance (Orc): "When you are reduced to 0 Hit Points but not
  killed outright, you can drop to 1 Hit Point instead. Once you use this
  trait, you can't do so again until you finish a Long Rest."
- Dark One's Blessing (Fiend Patron 3): "When you reduce an enemy to 0 Hit
  Points, you gain Temporary Hit Points equal to your Charisma modifier plus
  your Warlock level (minimum of 1 Temporary Hit Point)." Wrenna (Warlock 3,
  CHA +3) gets 6.
- Relentless Rage (Barbarian 11): "If you drop to 0 Hit Points while your
  Rage is active and don't die outright, you can make a DC 10 Constitution
  saving throw. If you succeed, your Hit Points instead change to a number
  equal to twice your Barbarian level."
- Instant Death (Playing the Game): damage that reduces you to 0 Hit Points
  with a remainder at least your Hit Point maximum kills you outright.
- Knocking Out a Creature / Dropping to 0 Hit Points: a creature at 0 Hit
  Points has the Unconscious condition, which ends its Concentration.

Ymira (an Orc Berserker Barbarian 4) has Relentless Endurance. Wrenna (an
Archfey Warlock 3) is given Dark One's Blessing for these tests."""

from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Barbarian_Berserker_YmiraSkullcrusher import (
    Y2024BarbarianBerserkerYmiraSkullcrusherCharacterBuilder as Ymira,
)
from Builds.Examples.Y2024_Wizard_Necromancy_MordecaiAshgrave import (
    Y2024WizardNecromancyMordecaiAshgraveCharacterBuilder as Mordecai,
)
from Builds.Characters.Y2024_Warlock_Archfey_WrennaThornpact import (
    Y2024WarlockArchfeyWrennaThornpactCharacterBuilder as Wrenna,
)
from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
    RelentlessRage,
)
from CharacterContent.Features.SpeciesFeatures.OrcFeatures import (
    RelentlessEndurance,
)
from CharacterContent.Features.SubClassFeatures.Warlock.WarlockFiendFeatures import (
    DarkOnesBlessing,
)
from CharacterContent.Features.SubClassFeatures.Wizard.WizardNecromancerFeatures import (
    HarvestUndead,
)
from Combat.CombatUIQt.effect_options import effect_options, triggered_rows
from Combat.Effects.triggers import (
    BloodiedOutcome,
    DropOutcome,
    KnockoutOutcome,
    TriggerChoice,
    TriggerMode,
    drop_firings,
    outcome_firings,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Core.Definitions import CharacterClass
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from tests._combat_ui import make_ui

# ---------------------------------------------------------------------------
# As data


def test_drops_to_reads_back_as_it_was_written():
    effect = CombatEffect(trigger=CombatTrigger(TriggerEvent.DROPS_TO_ZERO), drops_to=1)
    data = effect.to_dict()
    assert data == {"trigger": {"event": "drops to 0"}, "drops_to": 1}
    assert CombatEffect.from_dict(data) == effect


@pytest.mark.parametrize(
    "make",
    [
        lambda: CombatEffect(drops_to=1),
        lambda: CombatEffect(drops_to=1, trigger=CombatTrigger(TriggerEvent.HIT)),
        lambda: CombatEffect(
            drops_to=-1, trigger=CombatTrigger(TriggerEvent.DROPS_TO_ZERO)
        ),
        lambda: CombatEffect(
            drops_to=True, trigger=CombatTrigger(TriggerEvent.DROPS_TO_ZERO)
        ),
    ],
)
def test_drops_to_is_hit_points_with_a_drops_to_0_trigger(make):
    with pytest.raises(ValueError):
        make()


def test_enemy_only_reads_back_and_needs_another_creature():
    trigger = CombatTrigger(TriggerEvent.REDUCES_TO_ZERO, enemy_only=True)
    effect = CombatEffect(trigger=trigger)
    assert CombatEffect.from_dict(effect.to_dict()) == effect
    with pytest.raises(ValueError):
        CombatTrigger(TriggerEvent.DROPS_TO_ZERO, enemy_only=True)


def test_relentless_endurance_drops_its_owner_to_1_instead():
    (effect,) = RelentlessEndurance().combat_effects(Ymira().build())
    assert effect.trigger == CombatTrigger(TriggerEvent.DROPS_TO_ZERO)
    assert effect.drops_to == 1
    assert effect.targets_self


def test_dark_ones_blessing_gives_cha_plus_warlock_level_at_once():
    sheet = Wrenna().build()
    (effect,) = DarkOnesBlessing().combat_effects(sheet)
    expected = sheet.get_charisma_modifier() + sheet.get_class_level(
        CharacterClass.WARLOCK
    )
    assert expected == 6
    assert effect.temp_hp is not None and effect.temp_hp.dice == "6"
    assert effect.targets_self
    assert effect.trigger == CombatTrigger(
        TriggerEvent.REDUCES_TO_ZERO, optional=False, enemy_only=True
    )


def test_relentless_rage_changes_hit_points_to_twice_the_barbarian_level():
    sheet = Ymira().build()
    (effect,) = RelentlessRage().combat_effects(sheet)
    level = sheet.get_class_level(CharacterClass.BARBARIAN)
    assert effect.drops_to == 2 * level
    assert effect.trigger is not None
    assert effect.trigger.event is TriggerEvent.DROPS_TO_ZERO
    assert "DC 10 Constitution saving throw" in effect.trigger.when


# ---------------------------------------------------------------------------
# The interpreter


@pytest.fixture
def party(tmp_path):
    """Ymira, Wrenna (with Dark One's Blessing) and an Ogre, in a fight, on
    the Ogre's turn."""
    ui = make_ui(tmp_path, [Ogre()], [Ymira().build(), Wrenna().build()])
    ymira, wrenna, ogre = ui.characters
    wrenna["_feature_objects"] = [*wrenna["_feature_objects"], DarkOnesBlessing()]
    for char, value in zip(ui.characters, (5, 3, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(ogre)
    return ui, ymira, wrenna, ogre


def _drop(ymira, ogre, damage=13, left_over=0) -> DropOutcome:
    return DropOutcome(ymira, ogre, damage, left_over)


def test_relentless_endurance_asks_as_ymira_would_drop(party):
    _, ymira, _, ogre = party
    found, spent = drop_firings(_drop(ymira, ogre), triggered_rows, maximum=45)
    assert spent == []
    (firing,) = found
    assert firing.mode is TriggerMode.ASK
    assert firing.owner is ymira and firing.target is ymira
    assert firing.question == (
        f"Ogre's 13 damage would drop {ymira['name']} to 0 Hit Points: use"
        " Relentless Endurance? Drops to 1 Hit Point instead. 1 of 1 uses left."
    )
    assert (
        firing.prompt == f"{ymira['name']}: Relentless Endurance (dropped to 0 by Ogre)"
    )


def test_killed_outright_nothing_is_asked(party):
    _, ymira, _, ogre = party
    outcome = _drop(ymira, ogre, damage=80, left_over=45)
    found, spent = drop_firings(outcome, triggered_rows, maximum=45)
    assert found == []
    assert spent == [
        "Relentless Endurance: not when killed outright (45 damage past 0,"
        " Hit Point maximum 45)"
    ]
    # One short of the maximum past 0 isn't outright.
    outcome = _drop(ymira, ogre, damage=79, left_over=44)
    assert len(drop_firings(outcome, triggered_rows, maximum=45)[0]) == 1


def test_once_used_it_waits_for_a_long_rest(party):
    _, ymira, _, ogre = party
    ymira["feature_uses_used"] = {"Relentless Endurance": 1}
    found, spent = drop_firings(_drop(ymira, ogre), triggered_rows, maximum=45)
    assert found == []
    assert spent == ["Relentless Endurance: no uses left"]


def test_dark_ones_blessing_is_given_for_an_enemy_reduced_to_0(party):
    _, ymira, wrenna, ogre = party
    ogre["hp"] = 0  # dead: a knockout's target may be
    found, _ = outcome_firings([KnockoutOutcome(wrenna, ogre)], triggered_rows)
    (firing,) = found
    assert firing.mode is TriggerMode.AUTO
    assert firing.owner is wrenna and firing.target is ogre
    assert firing.question == (
        f"{wrenna['name']} reduces Ogre to 0 Hit Points: use Dark One's Blessing?"
        " 6 Temporary Hit Points."
    )
    # Not for an ally.
    assert outcome_firings([KnockoutOutcome(wrenna, ymira)], triggered_rows)[0] == []


def test_the_picker_row_says_when_its_used(party):
    _, ymira, _, _ = party
    (row,) = [
        o
        for _, options in effect_options(ymira)
        for o in options
        if o.name == "Relentless Endurance"
    ]
    assert row.drops_to == 1
    assert row.note.startswith(
        "Its user drops to 1 Hit Point instead of 0, asked as damage would drop"
        " them to 0;"
    )


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
def fight(party, monkeypatch):
    ui, ymira, wrenna, ogre = party
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    return ui, ymira, wrenna, ogre, answers


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def _typed_damage(ui, target, damage):
    ui._set_targets([target])
    ui.damage_input.setText(damage)
    ui._apply_damage_checked()


def _uses_spent(char) -> int:
    return (char.get("feature_uses_used") or {}).get("Relentless Endurance", 0)


def test_ymira_drops_to_1_instead_and_isnt_knocked_out(fight):
    ui, ymira, _, _, answers = fight
    ymira["hp"] = 10
    _typed_damage(ui, ymira, "13 bludgeoning")
    assert answers.asked == [
        [
            f"Ogre's 13 damage would drop {ymira['name']} to 0 Hit Points: use"
            " Relentless Endurance? Drops to 1 Hit Point instead. 1 of 1 uses left."
        ]
    ]
    assert ymira["hp"] == 1
    assert "Unconscious" not in ymira["conditions"]
    assert _uses_spent(ymira) == 1
    lines = _lines(ui)
    assert f"{ymira['name']} takes 13 Bludgeoning damage from Ogre" in lines
    assert lines[-1] == f"{ymira['name']} drops to 1 Hit Point instead of 0"
    damage = [
        e["value"]
        for events in ui._read_log().values()
        if isinstance(events, list)
        for e in events
        if isinstance(e, dict) and e.get("action") == "damage"
    ]
    assert damage[-1]["knockout"] is False
    assert damage[-1]["hp_delta"] == -9


def test_skip_drops_her_to_0(fight):
    ui, ymira, _, _, answers = fight
    answers.answer = "skip"
    ymira["hp"] = 10
    _typed_damage(ui, ymira, "13 bludgeoning")
    assert ymira["hp"] == 0
    assert "Unconscious" in ymira["conditions"]
    assert _uses_spent(ymira) == 0
    assert f"{ymira['name']} didn't use Relentless Endurance on {ymira['name']}" in (
        _lines(ui)
    )


def test_one_undo_takes_back_the_hit_and_the_use(fight):
    ui, ymira, _, _, _ = fight
    ymira["hp"] = 10
    _typed_damage(ui, ymira, "13 bludgeoning")
    ui._undo_last()
    ymira = ui._find_character_by_name(ymira["name"])
    assert ymira["hp"] == 10
    assert _uses_spent(ymira) == 0


def test_the_next_drop_that_day_asks_nothing(fight):
    ui, ymira, _, _, answers = fight
    ymira["hp"] = 10
    _typed_damage(ui, ymira, "13 bludgeoning")
    _typed_damage(ui, ymira, "5 bludgeoning")
    assert len(answers.asked) == 1
    assert ymira["hp"] == 0
    assert "Relentless Endurance: no uses left" in ui._status_label.text()


def test_damage_that_leaves_her_standing_asks_nothing(fight):
    ui, ymira, _, _, answers = fight
    ymira["hp"] = 10
    _typed_damage(ui, ymira, "9 bludgeoning")
    assert answers.asked == []
    assert ymira["hp"] == 1


def test_temporary_hit_points_count_first(fight):
    ui, ymira, _, _, answers = fight
    ymira["hp"], ymira["temp_hp"] = 10, 5
    _typed_damage(ui, ymira, "14 bludgeoning")
    assert answers.asked == []
    assert ymira["hp"] == 1 and ymira["temp_hp"] == 0


def test_a_hit_of_two_types_asks_once_and_leaves_her_at_1(fight):
    ui, ymira, _, _, answers = fight
    ymira["hp"] = 10
    _typed_damage(ui, ymira, "6 bludgeoning + 7 fire")
    assert len(answers.asked) == 1
    assert answers.asked[0][0].startswith("Ogre's 13 damage would drop")
    assert ymira["hp"] == 1


def test_resistance_counts_in_whether_she_would_drop(fight):
    """Raging, Ymira has Resistance to Bludgeoning: 18 is 9, and she stands."""
    ui, ymira, _, _, answers = fight
    ymira["hp"] = 10
    ymira["damage_resistances"] = [{"damage_types": ["Bludgeoning"]}]
    _typed_damage(ui, ymira, "18 bludgeoning")
    assert answers.asked == []
    assert ymira["hp"] == 1


def test_with_the_setting_off_it_is_a_button_and_picked_late_she_comes_back(fight):
    ui, ymira, _, _, answers = fight
    ui.settings = replace(ui.settings, ask_triggers=False)
    ymira["hp"] = 10
    _typed_damage(ui, ymira, "13 bludgeoning")
    assert answers.asked == []
    assert ymira["hp"] == 0
    assert [p.prompt for p in ui._hit_prompts] == [
        f"{ymira['name']}: Relentless Endurance (dropped to 0 by Ogre)"
    ]
    (firing,) = ui._hit_prompts
    ui._use_trigger(firing, [])
    assert ymira["hp"] == 1
    assert "Unconscious" not in ymira["conditions"]
    assert _uses_spent(ymira) == 1


def test_wrenna_reducing_the_ogre_to_0_gets_6_temporary_hit_points(fight):
    ui, _, wrenna, ogre, answers = fight
    ui._select_character(wrenna)
    ogre["hp"] = 5
    _typed_damage(ui, ogre, "10 fire")
    assert answers.asked == []
    assert ogre["hp"] == 0
    assert wrenna["temp_hp"] == 6
    name = wrenna["name"]
    ui._undo_last()
    wrenna = ui._find_character_by_name(name)
    assert wrenna["temp_hp"] == 0


def test_a_hit_that_leaves_the_ogre_standing_gives_nothing(fight):
    ui, _, wrenna, ogre, _ = fight
    ui._select_character(wrenna)
    ogre["hp"] = 15
    _typed_damage(ui, ogre, "10 fire")
    assert wrenna["temp_hp"] == 0


def test_dropping_an_ally_gives_nothing(fight):
    ui, ymira, wrenna, _, answers = fight
    answers.answer = "skip"  # Ymira keeps her Relentless Endurance
    ui._select_character(wrenna)
    ymira["hp"] = 5
    _typed_damage(ui, ymira, "10 fire")
    assert ymira["hp"] == 0
    assert wrenna["temp_hp"] == 0


# ---------------------------------------------------------------------------
# Left Bloodied (BLOODIED)
#
# Harvest Undead (Necromancer 10): "Immediately after you become Bloodied but
# aren't reduced to 0 Hit Points from taking damage, you can take a Reaction to
# reduce an Undead creature under your control that you can see to 0 Hit
# Points. You then immediately regain a number of Hit Points equal to your
# Wizard level." Mordecai is a Necromancer Wizard 20.


@pytest.fixture
def necromancer(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Ogre()], [Mordecai().build()])
    mordecai, ogre = ui.characters
    for char, value in zip(ui.characters, (5, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(ogre)
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    return ui, mordecai, ogre, answers


def test_harvest_undead_heals_the_wizard_level():
    (effect,) = HarvestUndead().combat_effects(Mordecai().build())
    assert effect.healing is not None and effect.healing.dice == "20"
    assert effect.targets_self
    assert effect.trigger is not None
    assert effect.trigger.event is TriggerEvent.BLOODIED
    assert effect.trigger.when


def test_harvest_undead_asks_as_damage_leaves_the_wizard_bloodied(necromancer):
    _, mordecai, ogre, _ = necromancer
    found, _ = outcome_firings([BloodiedOutcome(mordecai, ogre)], triggered_rows)
    (firing,) = [f for f in found if f.row.name == "Harvest Undead"]
    assert firing.owner is mordecai and firing.target is mordecai
    assert firing.mode is TriggerMode.ASK
    assert firing.question.startswith(
        f"Ogre's damage leaves {mordecai['name']} Bloodied: use Harvest Undead?"
        " 20 Hit Points. Check: if an Undead"
    )
    assert firing.prompt.startswith(
        f"{mordecai['name']}: Harvest Undead (Bloodied by Ogre; if an Undead"
    )


def _harvest_asked(answers) -> int:
    return sum(1 for asked in answers.asked for q in asked if "Harvest Undead" in q)


def test_in_the_window_it_heals_once_he_is_bloodied(necromancer):
    ui, mordecai, _, answers = necromancer
    top = mordecai["max_hp"]
    hp = top // 2 + 5
    mordecai["hp"] = hp
    _typed_damage(ui, mordecai, "10 slashing")
    assert _harvest_asked(answers) == 1
    assert mordecai["hp"] == min(hp - 10 + 20, top)
    assert mordecai["action_uses"]["Reaction"] == 1


def test_already_bloodied_or_dropped_to_0_it_isnt_asked(necromancer):
    ui, mordecai, _, answers = necromancer
    answers.answer = "skip"
    mordecai["hp"] = mordecai["max_hp"] // 2 + 5
    _typed_damage(ui, mordecai, "10 slashing")  # Bloodied now: asked, skipped
    _typed_damage(ui, mordecai, "3 slashing")  # still Bloodied
    assert _harvest_asked(answers) == 1
    _typed_damage(ui, mordecai, f"{mordecai['hp']} slashing")  # to 0
    assert _harvest_asked(answers) == 1
