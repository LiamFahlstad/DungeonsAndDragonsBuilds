"""One hit dealt and what it sets off, without the combat window
(Combat/Fight/damage.py's deal_damage, summons.py's vanish_at_zero_hp and
effects_given.py's grant_temp_hp; Notes/combat-ui-refactor-plan.md R45):
logged through a RecordingLogger, and what the window must still do (a
Concentration save, the hit's triggers) handed back in its DamageDealt.

Expected values are the 2024 rules: the Rules Glossary
(SourceTexts/RulesGlossary/) and the "Playing the Game" chapter's Damage
and Healing it points to."""

from Combat.Definitions import Phase
from Combat.Effects.triggers import BloodiedOutcome, DamageOutcome, KnockoutOutcome
from Combat.Fight.asker import ScriptedAsker
from Combat.Fight.damage import bloodied_outcomes, deal_damage
from Combat.Fight.effects_given import grant_temp_hp
from Combat.Fight.fight import Fight
from Combat.Fight.logger import RecordingLogger
from Combat.Fight.step import Step
from Combat.Summons import ON_ZERO_HP_KEY, SUMMON_OF_KEY
from Model.Content.Summons import OnZeroHp


def _creature(name: str, *conditions: str, hp: int = 20, **keys) -> dict:
    return {
        "name": name,
        "hp": hp,
        "max_hp": 20,
        "temp_hp": 0,
        "conditions": list(conditions),
        **keys,
    }


def _step(*chars: dict) -> Step:
    """A fight of chars in that order, on the first one's turn."""
    fight = Fight(
        characters=list(chars), initiative_order=list(chars), phase=Phase.COMBAT
    )
    return Step(fight, RecordingLogger(), ScriptedAsker())


def _hit(step, target, amount, source=None, *, critical=False, state="alive"):
    return deal_damage(
        step,
        target,
        [(amount, "Slashing")],
        source,
        False,
        False,
        critical=critical,
        state_before=state,
        drops_to=0,
        ask_concentration=True,
    )


def test_damage_while_concentrating_owes_a_constitution_save():
    """Concentration: "If you take damage, you must succeed on a
    Constitution saving throw to maintain Concentration." The window asks
    it, after the hit."""
    ogre, wizard = _creature("Ogre"), _creature("Wizard", "Concentrating")
    step = _step(ogre, wizard)

    dealt = _hit(step, wizard, 7, ogre)

    assert dealt.taken == 7 and wizard["hp"] == 13
    assert dealt.concentration_save
    assert "Wizard takes 7 Slashing damage from Ogre" in step.logger.texts


def test_dropping_to_0_knocks_a_player_out_and_ends_concentration():
    """At 0 Hit Points a player character falls Unconscious (and makes
    Death Saving Throws); Unconscious is Incapacitated, which ends
    Concentration, so no save is owed. The one who did it learns of the
    damage and of the knockout (its triggers)."""
    ogre = _creature("Ogre")
    wizard = _creature("Wizard", "Concentrating", hp=5, _is_player=True)
    step = _step(ogre, wizard)

    dealt = _hit(step, wizard, 9, ogre)

    assert wizard["hp"] == 0
    assert "Unconscious" in wizard["conditions"]
    assert "Concentrating" not in wizard["conditions"]
    assert not dealt.concentration_save
    assert [type(o) for o in dealt.outcomes] == [DamageOutcome, KnockoutOutcome]


def test_damage_at_0_hit_points_is_a_failed_death_save_two_on_a_critical():
    """Damage at 0 Hit Points: any damage is a Death Saving Throw failure,
    two if it's from a Critical Hit."""
    for critical, fails in ((False, 1), (True, 2)):
        wizard = _creature("Wizard", "Unconscious", hp=0, _is_player=True)
        step = _step(wizard)

        _hit(step, wizard, 3, critical=critical, state="dying")

        assert wizard["death_saves_fail"] == fails


def test_a_summon_that_vanishes_at_0_leaves_the_fight():
    """A drake (its spec's OnZeroHp.VANISHES) is gone at 0 Hit Points, out
    of the turn order and off the window's screens (StepResult.removed)."""
    ranger = _creature("Ranger", _is_player=True)
    drake = _creature(
        "Drake",
        hp=4,
        **{SUMMON_OF_KEY: "Ranger", ON_ZERO_HP_KEY: OnZeroHp.VANISHES.value},
    )
    ogre = _creature("Ogre")
    step = _step(ranger, drake, ogre)

    _hit(step, drake, 10, ogre)

    assert drake not in step.fight.characters
    assert drake not in step.fight.initiative_order
    assert step.result.removed == [drake]
    assert "Drake drops to 0 HP and vanishes" in step.logger.texts


def test_temporary_hit_points_dont_stack():
    """Temporary Hit Points don't stack: given more while it has some, a
    creature keeps whichever is more."""
    fighter = _creature("Fighter", temp_hp=8)
    step = _step(fighter)

    grant_temp_hp(step, fighter, 5, None)
    assert fighter["temp_hp"] == 8
    grant_temp_hp(step, fighter, 10, None)
    assert fighter["temp_hp"] == 10


def test_a_hit_that_leaves_it_bloodied_triggers_that():
    """Bloodied: "A creature is Bloodied while it has half its Hit Points
    or fewer remaining." What being left Bloodied triggers is judged after
    the hit (and its Concentration save)."""
    ogre, orc = _creature("Ogre"), _creature("Orc")
    step = _step(ogre, orc)

    dealt = _hit(step, orc, 12, ogre)

    assert orc["hp"] == 8 and "Bloodied" in orc["conditions"]
    assert [type(o) for o in bloodied_outcomes(dealt, orc, ogre)] == [BloodiedOutcome]
    assert bloodied_outcomes(_hit(step, orc, 1, ogre), orc, ogre) == []
