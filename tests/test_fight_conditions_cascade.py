"""What gaining or losing a condition sets off, without the combat window
(Combat/Fight/cascade.py, Notes/combat-ui-refactor-plan.md R34): logged
through a RecordingLogger, asked through a ScriptedAsker, and what the
window would redraw, say or save left in the Step's StepResult.

Expected values are the 2024 rules (SourceTexts/RulesGlossary/), and the
Druid's Wild Shape text (SourceTexts/ClassTexts/druid.txt)."""

from functools import cache

from Combat.Arena.arena import GRAPPLER_KEY, MOVED_KEY, POSITION_KEY
from Combat.Arena.speeds import ALTITUDE_KEY, FLY, MODE_KEY
from Combat.Definitions import Phase
from Combat.Effects.active_effects import link_concentration
from Combat.Fight.asker import ScriptedAsker
from Combat.Fight.cascade import (
    add_condition,
    heal_target,
    leave_wild_shape,
    remove_condition,
)
from Combat.Fight.fight import Fight
from Combat.Fight.logger import RecordingLogger
from Combat.Fight.spells import active_spell_record
from Combat.Fight.step import Step
from Combat.PlayerCombatant import combatant_from_character
from Combat.WildShape import assume_form, current_form, form_badge
from tests._snapshot_helpers import build

# Circle of the Moon Druid 3 (Wild Shape costs a Bonus Action).
MOON = "Y2024DruidMoonBriarWolfshadeCharacterBuilder"


@cache
def _sheet():
    return build(MOON)


def _creature(name: str, *conditions: str, hp: int = 20) -> dict:
    return {"name": name, "hp": hp, "max_hp": 20, "conditions": list(conditions)}


def _step(*chars: dict, phase: Phase = Phase.COMBAT, answers=()) -> Step:
    """A fight of chars in that order, on the first one's turn."""
    fight = Fight(characters=list(chars), initiative_order=list(chars), phase=phase)
    return Step(fight, RecordingLogger(), ScriptedAsker(list(answers)))


def _texts(step: Step) -> list[str]:
    logger = step.logger
    assert isinstance(logger, RecordingLogger)
    return logger.texts


def _in_form(druid: dict, form: str = "Brown Bear") -> dict:
    assume_form(druid, form)
    druid["conditions"].append(form_badge(form))
    return druid


# ---------------------------------------------------------------------------
# Concentration


def test_incapacitated_ends_concentration_and_what_it_held():
    """Concentration: "Your Concentration ends if you have the Incapacitated
    condition". Stunned gives Incapacitated, so Hold Person's Paralyzed
    comes off its target."""
    wizard, ogre = _creature("Wizard", "Concentrating"), _creature("Ogre", "Paralyzed")
    applied = [{"target": "Ogre", "condition": "Paralyzed"}]
    wizard["active_spells"] = [
        active_spell_record("Hold Person", 60, True, applied, None)
    ]
    link_concentration(ogre, "Paralyzed", "Wizard")
    step = _step(wizard, ogre)

    add_condition(step, wizard, "Stunned")

    assert wizard["conditions"] == ["Stunned"]
    assert wizard["active_spells"] == []
    assert ogre["conditions"] == []
    assert _texts(step) == [
        "Wizard gains Stunned",
        "Wizard loses Concentrating",
        "Wizard's Hold Person ends (concentration lost)",
        "Ogre loses Paralyzed",
    ]
    assert [c["name"] for c in step.result.changed] == ["Wizard", "Ogre"]


def test_a_condition_that_doesnt_incapacitate_leaves_concentration():
    wizard = _creature("Wizard", "Concentrating")
    step = _step(wizard)
    add_condition(step, wizard, "Poisoned")
    assert "Concentrating" in wizard["conditions"]


# ---------------------------------------------------------------------------
# Unconscious, Prone and standing up


def test_unconscious_ending_leaves_the_creature_prone():
    """Unconscious: "When this condition ends, you remain Prone." """
    fighter = _creature("Fighter", "Unconscious")
    step = _step(fighter)
    remove_condition(step, fighter, "Unconscious")
    assert fighter["conditions"] == ["Prone"]
    assert _texts(step) == ["Fighter loses Unconscious", "Fighter gains Prone"]


def test_standing_up_costs_half_its_speed_rounded_down():
    """Prone: "spend an amount of movement equal to half your Speed (round
    down) to right yourself". Only on its own turn, on the map."""
    monk, goblin = _creature("Monk", "Prone"), _creature("Goblin", "Prone")
    for char, cell in ((monk, [1, 1]), (goblin, [4, 4])):
        char["speed"] = 35
        char[POSITION_KEY] = cell
    step = _step(monk, goblin)  # the Monk's turn

    remove_condition(step, monk, "Prone")
    remove_condition(step, goblin, "Prone")

    assert monk[MOVED_KEY] == 17
    assert MOVED_KEY not in goblin, "not its turn: nothing spent"
    assert step.result.status == []


def test_with_a_speed_of_0_standing_up_is_warned_about():
    """Prone: "If your Speed is 0, you can't right yourself." The GM is
    told so on the status line."""
    monk = _creature("Monk", "Prone")
    monk["speed"], monk[POSITION_KEY] = 0, [1, 1]
    step = _step(monk)
    remove_condition(step, monk, "Prone")
    assert step.result.status == ["Monk has a Speed of 0 and can't stand up."]


# ---------------------------------------------------------------------------
# Grapples


def test_a_grapplers_incapacitated_ends_its_grapples_only():
    """Grappling: "The condition also ends if the grappler has the
    Incapacitated condition"; another grappler's hold stays."""
    fighter, goblin = _creature("Fighter"), _creature("Goblin")
    ogre, kobold = _creature("Ogre"), _creature("Kobold")
    step = _step(fighter, goblin, ogre, kobold)
    add_condition(step, goblin, "Grappled", fighter)
    add_condition(step, kobold, "Grappled", ogre)

    add_condition(step, fighter, "Unconscious")

    assert "Grappled" not in goblin["conditions"]
    assert GRAPPLER_KEY not in goblin
    assert kobold["conditions"] == ["Grappled"]
    assert _texts(step)[-1] == "Goblin loses Grappled from Fighter"


# ---------------------------------------------------------------------------
# Healing


def test_healing_at_0_hit_points_ends_unconscious():
    """Knocking Out a Creature: it "remains Unconscious until it regains any
    Hit Points"; and then it remains Prone (Unconscious)."""
    rogue, cleric = _creature("Rogue", "Unconscious", hp=0), _creature("Cleric")
    rogue["_is_player"] = True
    step = _step(rogue, cleric)

    assert heal_target(step, rogue, 5, cleric)

    assert rogue["hp"] == 5
    assert "Unconscious" not in rogue["conditions"]
    assert "Prone" in rogue["conditions"]
    assert _texts(step)[:2] == [
        "Rogue regains consciousness with 5 HP from Cleric",
        "Rogue loses Unconscious",
    ]
    # What the players saw of it is saved with the fight state.
    assert step.result.save


# ---------------------------------------------------------------------------
# Wild Shape


def test_a_form_ends_with_incapacitated_without_a_bonus_action():
    """Wild Shape: "You stay in that form ... until you ... have the
    Incapacitated condition"."""
    druid = _in_form(combatant_from_character(_sheet()))
    step = _step(druid)

    add_condition(step, druid, "Unconscious")

    assert current_form(druid) is None
    assert form_badge("Brown Bear") not in druid["conditions"]
    assert not druid.get("action_uses")
    assert "Briar Wolfshade leaves Brown Bear form (Unconscious)" in _texts(step)
    assert step.result.views


def test_leaving_early_with_the_bonus_action_used_asks_the_gm():
    """Wild Shape: "You can also leave the form early as a Bonus Action." With
    it spent this turn, the GM is asked; No keeps the form."""
    druid = _in_form(combatant_from_character(_sheet()))
    druid["action_uses"] = {"Bonus Action": 1}
    step = _step(druid, answers=[False])

    leave_wild_shape(step, druid)

    assert current_form(druid) == "Brown Bear"
    asker = step.asker
    assert isinstance(asker, ScriptedAsker)
    assert asker.asked == [
        (
            "Briar Wolfshade",
            "Leave Brown Bear form",
            ["Bonus Action: already used this turn"],
        )
    ]
    assert _texts(step) == []

    step = _step(druid, answers=[True])
    leave_wild_shape(step, druid)
    assert current_form(druid) is None
    assert druid["action_uses"] == {"Bonus Action": 2}
    assert step.result.spent == [(druid, "Bonus Action")]


def test_between_encounters_leaving_spends_no_action():
    druid = _in_form(combatant_from_character(_sheet()))
    step = _step(druid, phase=Phase.PARTY)
    remove_condition(step, druid, form_badge("Brown Bear"), druid)
    assert current_form(druid) is None
    assert not druid.get("action_uses")
    assert step.result.spent == []


def test_a_druid_aloft_falls_as_it_leaves_its_form():
    """Falling: "1d6 Bludgeoning damage ... for every 10 feet it fell". It
    falls where leaving the form brought the views up to date, before its
    grapple ends."""
    druid = _in_form(combatant_from_character(_sheet()))
    goblin = _creature("Goblin")
    druid[MODE_KEY], druid[ALTITUDE_KEY] = FLY, 30
    step = _step(druid, goblin)
    add_condition(step, goblin, "Grappled", druid)

    add_condition(step, druid, "Unconscious")

    texts = _texts(step)
    fall = next(i for i, t in enumerate(texts) if " falls 30 ft." in t)
    assert "3d6 Bludgeoning damage" in texts[fall]
    assert texts[fall - 1] == "Briar Wolfshade loses Wild Shape (Brown Bear)"
    assert texts[fall + 1] == "Goblin loses Grappled from Briar Wolfshade"
    assert ALTITUDE_KEY not in druid


# ---------------------------------------------------------------------------
# The StepResult


def test_a_line_logged_after_a_status_clears_it():
    """As the window's status line, which its next log line clears."""
    step = _step(_creature("Monk"))
    step.result.say("Not yet")
    step.log("Something happened")
    assert step.result.status == []
    step.result.say("Now")
    assert step.result.status == ["Now"]


def test_changed_keeps_each_combatant_once_by_identity():
    step = _step()
    one, twin = _creature("Twin"), _creature("Twin")
    for char in (one, one, twin):
        step.result.change(char)
    assert len(step.result.changed) == 2
    assert step.result.changed[0] is one and step.result.changed[1] is twin
