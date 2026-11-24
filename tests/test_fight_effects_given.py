"""What a Use / Cast effect gives its targets and what using it spends,
without the combat window (Combat/Fight/effects_given.py and resources.py,
Notes/combat-ui-refactor-plan.md R44): logged through a RecordingLogger,
asked through a ScriptedAsker, and what the window would redraw, say or
save left in the Step's StepResult.

Expected values are the 2024 rules (SourceTexts/RulesGlossary/), the spells'
own text and the Druid's (SourceTexts/ClassTexts/druid.txt)."""

from functools import cache

from Combat.Definitions import Phase
from Combat.Effects.active_effects import held_by_concentration, link_concentration
from Combat.Effects.modifiers import hit_point_maximum
from Combat.Fight.asker import ScriptedAsker
from Combat.Fight.cascade import start_concentration
from Combat.Fight.effects_given import (
    give_badge_modifiers,
    give_effect_conditions,
    hold_concentration,
)
from Combat.Fight.fight import Fight
from Combat.Fight.logger import RecordingLogger
from Combat.Fight.resources import effect_lacks
from Combat.Fight.saves import CustomEffect
from Combat.Fight.spells import active_spell_record
from Combat.Fight.step import Step
from Combat.Fight.wild_shape import can_cast_or_say
from Combat.PlayerCombatant import combatant_from_character
from Combat.WildShape import assume_form, form_badge
from Model.Content.CombatModifiers import HitPointMaximum
from tests._snapshot_helpers import build

# Circle of the Moon Druid 3: Moonbeam is one of its Circle of the Moon Spells.
MOON = "Y2024DruidMoonBriarWolfshadeCharacterBuilder"


@cache
def _sheet():
    return build(MOON)


def _creature(name: str, *conditions: str, hp: int = 20) -> dict:
    return {"name": name, "hp": hp, "max_hp": 20, "conditions": list(conditions)}


def _step(*chars: dict, phase: Phase = Phase.COMBAT) -> Step:
    """A fight of chars in that order, on the first one's turn."""
    fight = Fight(characters=list(chars), initiative_order=list(chars), phase=phase)
    return Step(fight, RecordingLogger(), ScriptedAsker())


def _texts(step: Step) -> list[str]:
    logger = step.logger
    assert isinstance(logger, RecordingLogger)
    return logger.texts


def test_a_condition_it_is_immune_to_doesnt_land():
    """Immunity: "If you have Immunity to a damage type or a condition, it
    doesn't affect you in any way." The log says so instead."""
    caster, ghoul = _creature("Cleric"), _creature("Ghoul")
    ghoul["condition_immunities"] = ["Frightened"]
    step = _step(caster, ghoul)

    held = give_effect_conditions(
        step, ghoul, CustomEffect("Fear", "Frightened"), caster
    )

    assert held == []
    assert "Frightened" not in ghoul["conditions"]
    assert _texts(step) == ["Ghoul is immune to Frightened"]


def test_a_condition_that_lands_is_drawn_and_saved():
    caster, ogre = _creature("Wizard"), _creature("Ogre")
    step = _step(caster, ogre)

    held = give_effect_conditions(
        step, ogre, CustomEffect("Hold Person", "Paralyzed"), caster
    )

    assert "Paralyzed" in ogre["conditions"]
    assert held == [{"target": "Ogre", "condition": "Paralyzed"}]
    assert any(c is ogre for c in step.result.changed)
    assert step.result.save_begun


def test_aid_raises_the_maximum_and_current_hit_points_by_5():
    """Aid: "Each target's Hit Point maximum and current Hit Points
    increase by 5 for the duration." """
    fighter = _creature("Fighter", "Aid", hp=12)
    step = _step(fighter)

    give_badge_modifiers(step, fighter, "Aid", [HitPointMaximum("5")])

    assert hit_point_maximum(fighter) == 25
    assert fighter["hp"] == 17


def test_concentration_holds_what_the_effect_gave():
    """What a concentration spell put on its target lasts while its caster
    concentrates (Concentration), so it's tied to the caster."""
    wizard, ogre = _creature("Wizard", "Concentrating"), _creature("Ogre", "Paralyzed")
    applied = [{"target": "Ogre", "condition": "Paralyzed"}]
    step = _step(wizard, ogre)
    effect = CustomEffect("Hold Person", "Paralyzed", concentration=True)

    hold_concentration(step, wizard, "Hold Person", effect, applied)

    [entry] = wizard["active_spells"]
    assert entry["concentration"] and entry["applied"] == applied
    assert [char for char, _ in held_by_concentration([ogre], "Wizard")] == [ogre]


def test_a_new_concentration_ends_the_old_one():
    """Concentration: "You lose Concentration on an effect the moment you
    start casting a spell that requires Concentration". Bless's badge comes
    off the Fighter it was on."""
    cleric, fighter = _creature("Cleric", "Concentrating"), _creature(
        "Fighter", "Bless"
    )
    applied = [{"target": "Fighter", "condition": "Bless"}]
    cleric["active_spells"] = [active_spell_record("Bless", 60, True, applied, None)]
    link_concentration(fighter, "Bless", "Cleric")
    step = _step(cleric, fighter)

    start_concentration(step, cleric, "Hold Person")

    assert cleric["active_spells"] == []
    assert "Bless" not in fighter["conditions"]
    assert "Concentrating" in cleric["conditions"]
    assert (
        "Cleric's Bless ends (concentration broken by casting Hold Person)"
        in _texts(step)
    )


def test_a_druid_in_a_beast_form_casts_only_its_circle_spells():
    """Wild Shape: "No Spellcasting. You can't cast spells"; Circle of the
    Moon Spells may be cast in a Wild Shape form."""
    druid = combatant_from_character(_sheet())
    assume_form(druid, "Brown Bear")
    druid["conditions"].append(form_badge("Brown Bear"))
    step = _step(druid)

    assert can_cast_or_say(step, druid, "Moonbeam")
    assert not can_cast_or_say(step, druid, "Thunderwave")
    assert step.result.status == [
        f"No spell cast: {druid['name']} can't cast Thunderwave in Brown Bear form."
    ]


def test_between_encounters_an_effect_spends_no_action():
    """The Action is one per turn, and between encounters there are no
    turns, so a used one doesn't stop an effect there."""
    cleric = _creature("Cleric")
    cleric["action_uses"] = {"Action": 1}
    effect = CustomEffect("Cure Wounds", action_cost="Action")

    assert effect_lacks(Phase.PARTY, cleric, effect) == [None]
    assert effect_lacks(Phase.COMBAT, cleric, effect)[0]
