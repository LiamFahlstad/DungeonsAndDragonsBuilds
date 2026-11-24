"""What gaining or losing a condition sets off, Qt-free
(Notes/combat-ui-refactor-plan.md, step 5.4, R34).

A condition can end Concentration, which ends a spell's effects on others,
which takes conditions off them; Incapacitated ends a Wild Shape form and
the creature's grapples; Unconscious ending leaves it Prone, and standing up
spends movement; a badge's Hit Point maximum going holds its Hit Points to
the new one, which can change Bloodied. These call each other, so they're
here together, each a function of the operation's Step
(Combat/Fight/step.py): they change the fight, log through the Step, ask
through its Asker, and put what the window must redraw, say or save in its
StepResult. What a condition does to the combatant alone is conditions.py's
gain_condition and lose_condition; the window's ConditionsMixin,
DamageMixin, SpellsMixin and WildShapeMixin keep their methods of the same
names as wrappers (Combat/CombatUIQt/steps.py's run_step)."""

from Combat.Arena.arena import (
    DASHES_KEY,
    MOVED_KEY,
    dashes,
    grappled_by,
    movement_ft,
    movements,
    position,
    remaining_ft,
    stand_up_ft,
    walking_speed_ft,
)
from Combat.Definitions import Action, CombatStatus, Phase
from Combat.Effects.active_effects import (
    held_by_concentration,
    is_linked,
    link_concentration,
    unlink_concentration,
)
from Combat.Effects.modifiers import has_condition, hit_point_maximum, loses_dodge
from Combat.WildShape import current_form, form_badge, leave_form, wild_shape_feature
from Core.Definitions import Condition
from Model.Content.StandardActions import DASH, DODGE

from .conditions import gain_condition, incapacitates, lose_condition
from .effect_options import feature_action_cost
from .falling import land_fallers
from .health import DEAD, bloodied_change, death_state, regain_hit_points
from .health import resync_bloodied
from .player_knowledge import note_health
from .resources import counted_action_lack, go_ahead_anyway, use_action
from .saves import is_immune_to
from .step import Step

# ---- Conditions ----


def add_condition(
    step: Step,
    char: dict,
    cond: str,
    source: dict | None = None,
    *,
    counted: bool = True,
):
    """char gets `cond` from `source`, logged. Not `counted` in the fight's
    stats: a spell's badge beside the conditions it gave (Friends beside
    Charmed), which aren't one more condition."""
    if cond == DASH:
        # Each Dash this turn is its Speed again on the map, a second
        # one (Cunning Action's) too, which the badge it has can't say.
        take_dash(step, char)
    # Who grapples it, the condition and the statistics: gain_condition.
    if gain_condition(char, cond, source, counted=counted):
        source_name = source["name"] if source is not None else None
        cond_value = {
            "condition": cond,
            "source_name": source_name,
            "target_name": char["name"],
        }
        if not counted:
            # So replaying it doesn't count it either (stats.py's
            # is_counted_condition).
            cond_value["counted"] = False
        source_suffix = (
            f" from {source_name}"
            if source_name and source_name != char["name"]
            else ""
        )
        step.log(
            f"{char['name']} gains {cond}{source_suffix}",
            character=char["name"],
            action=Action.ADD_CONDITION,
            value=cond_value,
        )
        step.result.change(char)
        # Break concentration if an incapacitating condition is applied to a concentrating character
        if (
            incapacitates(cond)
            and cond != "Concentrating"
            and "Concentrating" in char.get("conditions", [])
        ):
            remove_condition(step, char, "Concentrating", source=char)
        # So does a Wild Shape form (which a knock-out's Unconscious ends too).
        if incapacitates(cond) and current_form(char):
            leave_wild_shape(step, char, reason=cond)
        # And its grapples (Rules Glossary, Grappling: "The condition also
        # ends if the grappler has the Incapacitated condition").
        if incapacitates(cond):
            for held in grappled_by(char, step.fight.characters):
                remove_condition(step, held, Condition.GRAPPLED.value, source=char)
        # The Dodge action's benefits are lost to Incapacitated or a
        # Speed of 0 (Grappled); they don't count from then on anyway.
        if cond != DODGE and DODGE in char["conditions"] and loses_dodge(char):
            remove_condition(step, char, DODGE)


def take_dash(step: Step, char: dict):
    """char takes the Dash action (or a feature's): as much movement
    again as its Speed, this turn, a GM-only log line."""
    char[DASHES_KEY] = dashes(char) + 1
    movement = movement_ft(char)
    if movement is not None:
        step.log(
            f"{char['name']} dashes: {movement} ft. of movement this turn",
            character=char["name"],
            public=False,
        )


def stand_up(step: Step, char: dict):
    """char rights itself from Prone, as Prone is taken off it on its own
    turn while it's on the map: that spends its movement (stand_up_ft:
    half its Speed, 5 ft. with Athlete's Hop Up), counted as moved, a
    GM-only log line. Prone ending on another's turn (the GM correcting
    a mistake, a feature standing it up) or off the map spends nothing.
    A Speed of 0, or too little movement left, is warned about, not
    refused, as a move past its Speed is."""
    if position(char) is None or not any(
        char is c for c in step.fight.current_turn_group()
    ):
        return
    cost = stand_up_ft(char)
    if cost is None:
        return
    name = char["name"]
    given = [s for s, m in movements(char) if m.stands_up_ft == cost]
    why = f" ({given[0]})" if given else ""
    left = remaining_ft(char)
    char[MOVED_KEY] = int(char.get(MOVED_KEY, 0)) + cost
    step.log(
        f"{name} stands up{why}: {cost} ft. of movement,"
        f" {remaining_ft(char)} ft. left this turn",
        character=name,
        public=False,
    )
    if walking_speed_ft(char) == 0:
        step.result.say(f"{name} has a Speed of 0 and can't stand up.")
    elif cost > left:
        step.result.say(
            f"{name} stands up with {left} ft. of movement left; it costs"
            f" {cost} ft."
        )


def keep_hit_points_in_maximum(step: Step, char: dict, reason: str):
    """char has no more Hit Points than its maximum, now that `reason`
    changed it (Aid ending), logged so the party's history replays it.
    Bloodied goes by the new maximum."""
    top = hit_point_maximum(char)
    if char["hp"] > top:
        lost = char["hp"] - top
        char["hp"] = top
        step.log(
            f"{char['name']} has {top} HP, the most its Hit Point maximum"
            f" allows without {reason}",
            character=char["name"],
            action=Action.LOSE_HIT_POINTS,
            value={
                "hp_delta": -lost,
                "reason": reason,
                "target_name": char["name"],
            },
        )
    apply_bloodied(step, char, source=char)


def remove_condition(step: Step, char: dict, cond: str, source: dict | None = None):
    """char loses `cond` (from `source`), logged, and what goes with it."""
    # Its lasting effect, a Dash's movement and who grappled it go with
    # it: lose_condition.
    lost = lose_condition(char, cond)
    if lost is None:
        return
    stands_for, emptied = lost.stands_for, lost.emptied
    # What it did to the Hit Point maximum (Aid) goes with it.
    if hit_point_maximum(char) != lost.maximum_before:
        keep_hit_points_in_maximum(step, char, cond)
    source_name = source["name"] if source is not None else None
    cond_value = {
        "condition": cond,
        "source_name": source_name,
        "target_name": char["name"],
    }
    source_suffix = (
        f" from {source_name}" if source_name and source_name != char["name"] else ""
    )
    step.log(
        f"{char['name']} loses {cond}{source_suffix}",
        character=char["name"],
        action=Action.REMOVE_CONDITION,
        value=cond_value,
    )
    if cond == Condition.PRONE.value:
        stand_up(step, char)
    if (
        cond == Condition.UNCONSCIOUS.value
        and not has_condition(char, Condition.PRONE)
        and not is_immune_to(char, Condition.PRONE.value)
        and death_state(char) != DEAD
    ):
        # Unconscious: "When this condition ends, you remain Prone."
        # Its own Prone went with it (held_conditions), so the
        # creature is given one, logged, which standing up ends.
        add_condition(step, char, Condition.PRONE.value, counted=False)
    forget_effect_on(step, char, cond)
    # A spell's badge and the conditions it stands for go together
    # (Friends and Charmed): those no other badge stands for, and a
    # badge left standing for none. Not Unconscious from 0 HP.
    for other in [*stands_for, *emptied]:
        if (
            other in char["conditions"]
            and not is_linked(char, other)
            and (other != Condition.UNCONSCIOUS.value or char["hp"] > 0)
        ):
            remove_condition(step, char, other, source=source)
    if cond == CombatStatus.CONCENTRATING.value:
        char.pop("concentration_checks", None)
        end_concentration_spells(step, char)
    # Taking the Wild Shape badge off is leaving the form early. The
    # badge is gone already, so the form goes too, without asking.
    form = current_form(char)
    if form is not None and cond == form_badge(form):
        leave_wild_shape(step, char, ask=False)
    step.result.change(char)


# ---- Hit Points ----


def apply_bloodied(step: Step, char: dict, source: dict | None = None):
    """Auto-apply/remove Bloodied condition based on HP threshold. Pass
    `source` (the damage dealer/healer) to log the change with a source,
    same as any other condition; omit it for silent resyncs (replay)."""
    if source is None:
        resync_bloodied(char)
        return
    change = bloodied_change(char)
    if change is True:
        add_condition(step, char, "Bloodied", source=source)
    elif change is False:
        remove_condition(step, char, "Bloodied", source=source)


def heal_target(step: Step, char: dict, heal: int, source: dict | None) -> bool:
    """char regains `heal` Hit Points from source, up to its maximum,
    counted in both their stats and logged; one at 0 HP comes to. Returns
    False for a dead creature, which can't regain Hit Points until it's
    revived (the card's Revive button)."""
    if death_state(char) == DEAD:
        return False
    source_name = source["name"] if source is not None else None
    regained = regain_hit_points(char, heal, source)
    actual_heal = regained.amount

    heal_value = {
        "heal": actual_heal,
        "source_name": source_name,
        "target_name": char["name"],
    }

    source_suffix = f" from {source_name}" if source_name else ""

    if regained.came_to:
        step.log(
            f"{char['name']} regains consciousness with {char['hp']} HP{source_suffix}",
            character=char["name"],
            action=Action.HEAL,
            value=heal_value,
        )
        # Regaining any Hit Points ends the Unconscious from 0 HP.
        remove_condition(step, char, Condition.UNCONSCIOUS.value)
    else:
        step.log(
            f"{char['name']} heals {actual_heal} HP{source_suffix}",
            character=char["name"],
            action=Action.HEAL,
            value=heal_value,
        )

    # Auto-apply bloodied condition, attributed to whoever healed
    apply_bloodied(step, char, source=source)
    note_health_change(step, char)
    step.result.change(char)
    return True


def note_health_change(step: Step, char: dict):
    """Note what the change of HP that's just over showed the players. The
    log was written before it was done, and a continued fight needs it, so
    the fight state is saved."""
    note_health(char)
    step.result.save = True


# ---- Wild Shape ----


def spend_action(step: Step, char: dict, action_type: str):
    """char uses its `action_type` (use_action, logged), unless it's
    between encounters, where there are no turns to spend it in."""
    if step.fight.phase == Phase.PARTY:
        return
    use_action(step, char, action_type)
    step.result.spent.append((char, action_type))


def leave_wild_shape(
    step: Step, char: dict, reason: str | None = None, *, ask: bool = True
):
    """char leaves its form: by choice (reason None), a Bonus Action, or
    because of `reason` ("Unconscious", "Wild Shape again"), no action.
    With its Bonus Action used already, the GM is asked whether to leave
    anyway, unless the form's badge is already off (ask=False)."""
    form_now = current_form(char)
    if form_now is None:
        return
    feature = wild_shape_feature(char)
    action_cost = feature_action_cost(feature) if feature is not None else None
    pays = reason is None and action_cost is not None
    if (
        pays
        and ask
        and not go_ahead_anyway(
            step.asker,
            char,
            f"Leave {form_now} form",
            [counted_action_lack(step.fight.phase, char, action_cost)],
        )
    ):
        return
    form = leave_form(char)
    if form is None:
        return
    if pays:
        assert action_cost is not None  # pays says so
        spend_action(step, char, action_cost)
    because = f" ({reason})" if reason else ""
    step.log(
        f"{char['name']} leaves {form} form{because}",
        character=char["name"],
        action=Action.LEAVE_WILD_SHAPE,
        value={"form": form},
    )
    remove_condition(step, char, form_badge(form), source=char)
    step.result.change(char)
    # The window brought its views up to date here, and whoever couldn't
    # stay aloft fell then, before the rest of the cascade.
    lines = land_fallers(step.fight, step)
    if lines:
        step.result.say(" ".join(lines))
    step.result.views = True


# ---- Concentration ----


def clear_concentration_if_unused(char: dict):
    """Remove Concentrating if no remaining active spell on char still needs it."""
    if any(e.get("concentration") for e in char.get("active_spells") or []):
        return
    char.pop("concentration_checks", None)
    conditions = char.get("conditions", [])
    if CombatStatus.CONCENTRATING.value in conditions:
        conditions.remove(CombatStatus.CONCENTRATING.value)


def end_concentration_spells(
    step: Step, char: dict, reason: str = "concentration lost"
):
    """End every active spell on char that requires concentration, and
    every effect still linked to char's concentration. Call this
    whenever Concentrating is removed by any path other than the spell's own
    duration expiring — a manual shortcut, a failed save, incapacitation,
    knockout, death, or char leaving the fight — so the effect doesn't keep
    ticking on the card after the character has stopped concentrating on it."""
    active_spells = char.get("active_spells") or []
    ended = [e for e in active_spells if e.get("concentration")]
    if ended:
        char["active_spells"] = [e for e in active_spells if not e.get("concentration")]
    for entry in ended:
        step.log(
            f"{char['name']}'s {entry['name']} ends ({reason})",
            note_turn=False,
            character=char["name"],
            value={"condition": entry["name"]},
        )
        end_spell_effects(step, entry)
    end_linked_effects(step, char)


def end_linked_effects(step: Step, char: dict):
    """char concentrates on nothing now, so every effect whose record
    still says it lasts while char concentrates ends: its badge comes
    off (not Unconscious from 0 HP). One another running effect holds
    stays, linked to that one's caster."""
    characters = step.fight.characters
    for target, effect in held_by_concentration(characters, char["name"]):
        condition = effect["name"]
        applied = {"target": target["name"], "condition": condition}
        holder = holder_of(characters, applied)
        if holder is not None:
            relink(characters, applied, *holder)
        elif condition in target["conditions"] and (
            condition != Condition.UNCONSCIOUS.value or target["hp"] > 0
        ):
            remove_condition(step, target, condition)
        else:
            unlink_concentration(target, condition)


def end_spell_effects(step: Step, entry: dict):
    """Take what a concentration spell put on its targets off them, now
    that it's ended: entry["applied"] says what and on whom. Not what
    another running effect also holds, and not Unconscious from 0 HP."""
    characters = step.fight.characters
    entry["ends_with_conditions"] = False
    for applied in list(entry.get("applied", [])):
        holder = holder_of(characters, applied, excluding=entry)
        if holder is not None:
            relink(characters, applied, *holder)
            continue
        condition = applied["condition"]
        for char in characters:
            if char["name"] != applied["target"]:
                continue
            if condition not in char["conditions"]:
                continue
            if condition != Condition.UNCONSCIOUS.value or char["hp"] > 0:
                remove_condition(step, char, condition)
            break


def holder_of(
    characters: list[dict], applied: dict, excluding: dict | None = None
) -> tuple[dict, dict] | None:
    """The caster and active spell, other than `excluding`, that put this
    condition on this target and still run, if any."""
    return next(
        (
            (char, entry)
            for char in characters
            for entry in char.get("active_spells") or []
            if entry is not excluding and applied in entry.get("applied", [])
        ),
        None,
    )


def relink(characters: list[dict], applied: dict, caster: dict, entry: dict):
    """The condition in `applied` stays on its target, held by caster's
    active spell `entry`: its record lasts while caster concentrates on
    it, if entry needs Concentration, and no longer on anyone's if not."""
    target = next((c for c in characters if c.get("name") == applied["target"]), None)
    condition = applied["condition"]
    if target is None or condition not in target["conditions"]:
        return
    if entry.get("concentration"):
        link_concentration(target, condition, caster["name"])
    else:
        unlink_concentration(target, condition)


def forget_effect_on(step: Step, target: dict, condition: str):
    """Target has lost condition, so no spell holds it any more. A spell
    that lasted only as long as its conditions is over with the last."""
    applied = {"target": target["name"], "condition": condition}
    for char in step.fight.characters:
        for entry in list(char.get("active_spells") or []):
            if applied not in entry.get("applied", []):
                continue
            entry["applied"].remove(applied)
            if entry.get("ends_with_conditions") and not entry["applied"]:
                char["active_spells"].remove(entry)
                step.log(
                    f"{char['name']}'s {entry['name']} ends",
                    note_turn=False,
                    character=char["name"],
                    value={"condition": entry["name"]},
                )
                clear_concentration_if_unused(char)
                step.result.change(char)
