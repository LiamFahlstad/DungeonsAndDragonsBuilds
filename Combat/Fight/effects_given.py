"""What a Use / Cast effect gives each of its targets, Qt-free
(Notes/combat-ui-refactor-plan.md, step 5.4, R44): the conditions that land,
the picked spell's or feature's badge and the card its badges show, the
save it repeats, what a badge does while it's on, the uses it regains, a
Shield taken up or set down, a hit's extra damage, and the Concentration or
kept area that holds what it gave.

Each is a function of the operation's Step (Combat/Fight/step.py), as
cascade.py's are: it changes the fight, logs through the Step and puts what
the window must redraw, say or save in its StepResult. `source` is who uses
the effect: the window's selected card, else whose turn it is. The window's
ConditionsMixin keeps its methods of the same names as wrappers
(Combat/CombatUIQt/steps.py's run_step). What the effect deals (damage,
Temporary Hit Points), its rolls and what its hits trigger are still the
window's (ConditionsMixin._apply_effect_to_targets)."""

from dataclasses import replace
from html import escape

from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import AREA_KEY, find_area, record_end
from Combat.Definitions import Action, CombatStatus, ConditionRule
from Combat.Effects.active_effects import (
    CUSTOM,
    describe,
    duration_entry,
    find_effect,
    give_modifiers,
    is_linked,
    link_badge,
    link_concentration,
    note_origin,
    set_duration,
    set_repeat_save,
)
from Combat.Effects.modifiers import (
    hit_plan,
    hit_point_maximum,
    hit_point_maximum_notes,
    rolled_modifiers,
)
from Model.Content.CombatModifiers import HitPointMaximum, Modifier
from Model.Content.StandardActions import HIDDEN

from .attack_rolls import SHIELD_OFF, has_shield, is_shield_off
from .badge_text import (
    FEATURE_BADGE_COLOR,
    feature_condition_tooltip,
    spell_badge_color,
    spell_badge_description,
)
from .cascade import (
    add_condition,
    end_spell_effects,
    heal_target,
    holder_of,
    keep_hit_points_in_maximum,
)
from .effect_options import regained_uses
from .health import death_state, give_temp_hp
from .monster_actions import roll_dice
from .player_knowledge import note_condition_immunity
from .saves import (
    FEATURE,
    SPELL,
    CustomEffect,
    EffectOption,
    is_immune_to,
    roll_extra_damage,
    with_extra_damage,
)
from .spells import spell_called
from .step import Step

# How long a concentration effect runs with no time on it: the longest there is
# in general use, for the GM to end by hand or by losing concentration.
LONGEST_CONCENTRATION = 60 * 60


# ---- Conditions and badges ----


def add_custom_condition(
    step: Step,
    cond: str,
    duration: dict | None,
    notes: str,
    targets: list[dict],
    source: dict | None,
):
    """Give each of `targets` `cond`, any text (a rules condition or an
    effect like "Hexed" or "-2 AC"), attributed to `source`, for `duration`
    (see CUSTOM_CONDITION_DURATIONS) and with `notes` as its tooltip. Giving
    it again replaces its duration."""
    cond = cond.strip()
    if not cond or not targets:
        return
    source_name = source["name"] if source is not None else None
    turn = [c["name"] for c in step.fight.current_turn_group()]
    for target in list(targets):
        if notes.strip():
            describe(target, cond, notes.strip(), None, CUSTOM)
        add_condition(step, target, cond, source)
        set_duration(
            target,
            cond,
            duration_entry(duration, source_name, target["name"], turn),
        )
        # Its caster, unless it has one: re-adding Hanna's Hunter's Mark
        # by hand with the Pirate selected mustn't give the Pirate its
        # extra damage (DI-074).
        record = find_effect(target, cond)
        if record is None or not record.get("caster"):
            note_origin(target, cond, caster=source_name)
        step.result.change(target)
    step.result.save_begun = True


def give_effect_conditions(
    step: Step, target: dict, effect: CustomEffect, source: dict | None
) -> list[dict]:
    """Give target every condition of effect that lands (one it's immune
    to doesn't), its pick's badge and its repeat save: what the Use / Cast
    dialog does to a target it hit or that failed its save, and a
    monster's action button to the target its hit lands on. Returns the
    ({"target", "condition"}) rows a running effect now holds."""
    applied, linked = [], []
    for condition in effect.conditions:
        row = {"target": target["name"], "condition": condition}
        already_had = condition in target["conditions"]
        held_by_a_spell = holder_of(step.fight.characters, row) is not None
        held_by_a_badge = is_linked(target, condition)
        if give_effect_condition(step, target, effect, condition, source):
            if held_by_a_spell or not already_had:
                applied.append(row)
            if held_by_a_badge or not already_had:
                linked.append(condition)
    give_pick_badge(step, target, effect, linked, source)
    if effect.repeat_save and effect.ability is not None:
        track_repeat_save(target, effect)
    return applied


def give_effect_condition(
    step: Step,
    target: dict,
    effect: CustomEffect,
    condition: str,
    source: dict | None,
) -> bool:
    """Give target one of the effect's conditions, unless it's died of
    the effect or is immune. Returns whether it has it from this effect
    now."""
    if death_state(target) == "dead":
        return False
    if is_immune_to(target, condition):
        readable = step.log(
            f"{target['name']} is immune to {condition}",
            character=target["name"],
        )
        if readable:
            note_condition_immunity(target, condition)
        return False
    describe_effect_condition(target, effect, condition, source)
    duration = effect.duration
    if effect.pick is not None:
        duration = effect.pick.duration_for(condition, duration)
    add_custom_condition(step, condition, duration, effect.notes, [target], source)
    note_origin(target, condition, source=effect.name)
    if effect.pick is not None:
        # Who gave it, also on a record only its modifiers made: extra
        # damage from its caster's hits (Hunter's Mark) goes by it.
        levels_up = max(
            (effect.slot_level or effect.pick.spell_level) - effect.pick.spell_level,
            0,
        )
        give_badge_modifiers(
            step,
            target,
            condition,
            effect.pick.modifiers_for(condition),
            levels_up=levels_up,
            source=source,
            rolled_maximum=effect.typed_hit_point_maximum.get(id(target)),
        )
        if source is not None:
            note_origin(target, condition, source=effect.name, caster=source["name"])
    return True


def picked_feature(owner: dict, option: EffectOption):
    """owner's feature object for a picked feature row: the row's own
    feature (Hill's Tumble), else the one whose uses it spends."""
    features = owner.get("_feature_objects", [])
    for name in (option.name, option.feature_name):
        feature = next((f for f in features if f.name == name), None)
        if feature is not None:
            return feature
    return None


def give_pick_badge(
    step: Step,
    target: dict,
    effect: CustomEffect,
    conditions: list[str],
    source: dict | None,
):
    """Beside the rules conditions a picked spell or feature just gave
    target (Friends' Charmed, Turn Undead's Frightened), a badge of the
    spell's or feature's own name with its card, so the card says where
    they're from. It stands for `conditions`: it comes off with the last
    of them, and they come off with it (link_badge). None for a pick
    whose badge is its own name already (Bless), a weapon's or a
    monster's action (its rider is plain in the log), or conditions that
    aren't rules conditions (Hexed)."""
    option = effect.pick
    if option is None:
        return
    rules = [c for c in conditions if ConditionRule.from_name(c) is not None]
    if not rules:
        return
    if HIDDEN in effect.conditions and HIDDEN in target["conditions"]:
        # The Hide action's (or Cunning Action's): Hidden stands for the
        # Invisible it came with, so its next attack roll ends both.
        link_badge(target, HIDDEN, rules)
        return
    # A spell's badge, for a spell or a feature's use that casts one.
    badge = option.spell_name or (option.name if option.kind == SPELL else "")
    if badge:
        spell = spell_called(badge)
        if spell is not None and badge not in effect.conditions:
            describe(
                target,
                badge,
                spell_badge_description(spell),
                spell_badge_color(spell),
                SPELL,
            )
    elif option.kind == FEATURE:
        badge = option.name
        feature = picked_feature(source, option) if source is not None else None
        if (
            source is not None
            and feature is not None
            and badge not in effect.conditions
        ):
            describe(
                target,
                badge,
                feature_condition_tooltip(source, feature),
                FEATURE_BADGE_COLOR,
                FEATURE,
            )
    if not badge:
        return
    if badge in effect.conditions:
        # Its badge given by name beside them (Invisibility beside
        # Invisible, Silence beside Deafened): it stands for them all the
        # same, so they end together (plan step 9.6).
        if badge in target["conditions"]:
            link_badge(target, badge, rules)
        return
    add_condition(step, target, badge, source, counted=False)
    link_badge(target, badge, conditions)
    note_origin(
        target,
        badge,
        source=effect.name or badge,
        caster=source["name"] if source is not None else None,
    )


def track_repeat_save(target: dict, effect: CustomEffect):
    """The save target repeats at the end of each of its turns, ending
    every condition the effect gave it: one save for them all (Turn
    Undead's Frightened and Incapacitated)."""
    given = [c for c in effect.conditions if c in target["conditions"]]
    if not given or effect.ability is None:
        return
    first, *also = given
    set_repeat_save(
        target,
        first,
        effect.ability,
        effect.dc,
        effect.mode,
        effect.use_legendary_resistance,
        also,
    )
    note_origin(target, first, source=effect.name)


def describe_effect_condition(
    target: dict, effect: CustomEffect, cond: str, owner: dict | None
):
    """What target's badge for the effect's condition shows when clicked
    or hovered: the picked spell's card, as Cast Spell's badge has, the
    picked feature's (owner's), or the rules text of the attack or action
    picked. Notes typed in the dialog come first. Nothing for an effect
    typed in by hand, whose badge shows its notes, if any."""
    option = effect.pick
    if option is None:
        return
    notes = escape(effect.notes.strip(), quote=False)
    notes = f"<i>{notes}</i><br><br>" if notes else ""
    # A spell's card, for a spell or a feature's use that casts one.
    spell_name = option.spell_name or (option.name if option.kind == SPELL else "")
    if spell_name:
        spell = spell_called(spell_name)
        if spell is not None:
            describe(
                target,
                cond,
                notes + spell_badge_description(spell),
                spell_badge_color(spell),
                SPELL,
            )
            return
    if option.kind == FEATURE and owner is not None:
        feature = picked_feature(owner, option)
        if feature is not None:
            describe(
                target,
                cond,
                notes + feature_condition_tooltip(owner, feature),
                FEATURE_BADGE_COLOR,
                FEATURE,
            )
            return
    if option.tooltip:
        # A weapon's or a monster's action: its name and rules text.
        name = escape(option.row_name or option.name, quote=False)
        text = escape(option.tooltip, quote=False).replace("\n", "<br>")
        describe(
            target,
            cond,
            f"{notes}<b style='color:#c9a84c; font-size:14px;'>{name}</b>"
            f"<br><br>{text}",
            None,
            FEATURE,
        )


def give_badge_modifiers(
    step: Step,
    char: dict,
    name: str,
    modifiers,
    *,
    levels_up: int = 0,
    source: dict | None = None,
    rolled_maximum: int | None = None,
):
    """char's badge `name` gives `modifiers` while it's on, their dice
    rolled now (rolled_modifiers), or a Hit Point maximum's as
    `rolled_maximum`, rolled at the table (upcast and all; 8.6). One that raises its Hit Point maximum
    raises its current Hit Points by as much (Aid: "Hit Point maximum and
    current Hit Points increase by 5"), as Hit Points regained from
    `source`, so a creature at 0 HP comes to; one that lowers it leaves
    no more than the new maximum."""
    before = hit_point_maximum(char)
    if rolled_maximum is not None:
        modifiers = [
            (
                HitPointMaximum(str(rolled_maximum))
                if isinstance(m, HitPointMaximum) and not m.rolled
                else m
            )
            for m in modifiers
        ]
    kept: tuple[Modifier, ...] = rolled_modifiers(modifiers, levels_up, roll_dice)
    give_modifiers(char, name, kept)
    change = hit_point_maximum(char) - before
    if not change:
        return
    notes = ", ".join(hit_point_maximum_notes(char))
    step.log(
        f"{char['name']}'s Hit Point maximum is {hit_point_maximum(char)}"
        f" ({char['max_hp']}, {notes})",
        character=char["name"],
    )
    if change > 0:
        # heal_target sees to Bloodied by the new maximum.
        heal_target(step, char, change, source)
    else:
        keep_hit_points_in_maximum(step, char, name)


# ---- On each target, whatever its roll ----


def regain_feature_uses(step: Step, char: dict, option: EffectOption):
    """Give char back the expended feature uses option regains
    (Uncanny Metabolism's Focus Points), a logged line per use, as a rest
    logs them, so the party's history replays them."""
    used = char.setdefault("feature_uses_used", {})
    for regain in option.regains:
        for _ in range(regained_uses(char, regain)):
            used[regain.feature] = max(used.get(regain.feature, 0) - 1, 0)
            step.log(
                f"{char['name']} regains a use of {regain.feature}" f" ({option.name})",
                character=char["name"],
                action=Action.REGAIN_FEATURE_CHARGE,
                value=regain.feature,
            )
    step.result.change(char)


def set_shield(step: Step, char: dict, wielding: bool | None):
    """Have char wield its Shield or set it down (the attack rows' Shield
    box), with a log line when that changes it. None, or a char without
    a Shield, leaves it as it is. It stays so until changed again."""
    if wielding is None or not has_shield(char):
        return
    if wielding != is_shield_off(char):
        return
    if wielding:
        char.pop(SHIELD_OFF, None)
    else:
        char[SHIELD_OFF] = True
    did = "takes up" if wielding else "sets down"
    step.log(f"{char['name']} {did} a Shield", character=char["name"])
    step.result.change(char)


def with_hit_extras(
    step: Step,
    source: dict | None,
    target: dict,
    damage: list[tuple[int, str]],
    effect: CustomEffect,
    critical: bool,
) -> list[tuple[int, str]]:
    """A hit's damage with the extra damage that comes with it (Hunter's
    Mark's on its caster's hits, Divine Favor's on its caster's weapon
    hits), rolled after the attack's own dice, doubled for a Critical
    Hit. The log says what each adds, and what wasn't counted. One
    rolled at the table (its box under Damage) is added as typed, even
    to a typed damage total; a typed total gets none rolled here, as it
    was all rolled at the table (Decision 4)."""
    rolled = effect.typed_extras.get(id(target), {})
    plan = hit_plan(source, target, effect.weapon_attack, rolled)
    in_total: list[str] = []
    if effect.typed_damage:
        in_total = [
            f"{label}: not rolled, as the damage total typed has it"
            for label, _, _ in plan.extras
            if label not in plan.at_table
        ]
        plan = replace(
            plan,
            extras=tuple(e for e in plan.extras if e[0] in plan.at_table),
            notes=(),
        )
    extra, lines = roll_extra_damage(plan, critical)
    for line in (*lines, *plan.notes, *in_total):
        # After the hit's line, for the GM only: the player link joins a
        # hit's damage to its line, which a line between would stop.
        step.log(line, character=target["name"], public=False)
    return with_extra_damage(damage, extra)


# ---- What holds what it gave ----


def hold_concentration(
    step: Step, caster: dict, label: str, effect: CustomEffect, applied: list[dict]
):
    """Caster's concentration on the effect, tied to what it put on whom,
    and the area it keeps on the map, if any (arena step 11). If the
    effect itself just ended that concentration (the caster was among
    its targets), it's over already."""
    duration = effect.duration or {}
    seconds = duration.get("seconds", LONGEST_CONCENTRATION)
    turn = step.fight.current_turn_group()
    entry = {
        "name": label,
        "time_left": seconds,
        "duration": seconds,
        "concentration": True,
        "applied": applied,
        "ticks_on": turn[0]["name"] if turn else None,
        # With a turn for a duration, the conditions are what end first;
        # not while an area on the map lasts with the concentration.
        "ends_with_conditions": "until" in duration
        and bool(applied)
        and effect.area is None,
    }
    if effect.area is not None:
        entry[AREA_KEY] = effect.area
    if CombatStatus.CONCENTRATING.value not in caster["conditions"]:
        end_spell_effects(step, entry)
        return
    caster.setdefault("active_spells", []).append(entry)
    link_concentration_on(step, caster, applied)
    if effect.area is not None:
        log_area_kept(step, caster, label, effect.area)
    step.result.change(caster)


def hold_with_area(step: Step, key: str, applied: list[dict]):
    """What a kept area gave as it acted again (Web's Restrained), held
    by the area's active spell when its caster concentrates on it, so
    it comes off as the concentration ends, as what the cast gave does."""
    found = find_area(step.fight.characters, key)
    if found is None or not applied:
        return
    caster, entry = found
    if not entry.get("concentration"):
        return
    held = entry.setdefault("applied", [])
    new = [row for row in applied if row not in held]
    held.extend(new)
    link_concentration_on(step, caster, new)


def link_concentration_on(step: Step, caster: dict, applied: list[dict]):
    """Record on each effect in `applied` ({"target", "condition"} rows,
    as an active spell holds them) that caster concentrates on it."""
    for row in applied:
        target = next(
            (c for c in step.fight.characters if c.get("name") == row["target"]),
            None,
        )
        if target is not None:
            link_concentration(target, row["condition"], caster["name"])


def area_where(step: Step, record: dict) -> str:
    """Where a kept area is, for the log: "around its caster", or "at
    C7" (the cell it was aimed at)."""
    if record.get("follows"):
        return "around its caster"
    aim = record.get("aim")
    if aim is None:
        return ""
    shape = step.fight.arena_settings.distance_rule.shape
    end = record_end(record)
    if end is not None:
        return f"from {shape.cell_name(Cell.of(aim))} to {shape.cell_name(end)}"
    return f"at {shape.cell_name(Cell.of(aim))}"


def log_area_kept(step: Step, holder: dict, label: str, record: dict):
    """The GM-only log line for an area put on the map: "Clover's
    Moonbeam stays on the map at C7."."""
    where = area_where(step, record)
    step.log(
        f"{holder['name']}'s {label} stays on the map"
        + (f" {where}" if where else "")
        + ".",
        character=holder["name"],
        public=False,
    )


def grant_temp_hp(step: Step, target: dict, amount: int, source: dict | None):
    """Give target `amount` temporary Hit Points from source, counted in
    both their stats and logged. Temp HP and Wild Shape share it."""
    source_name = source["name"] if source is not None else None
    # Temporary Hit Points don't stack: it keeps the higher amount.
    old = give_temp_hp(target, amount, source)

    temp_hp_value = {
        "amount": amount,
        "source_name": source_name,
        "target_name": target["name"],
    }

    source_suffix = f" from {source_name}" if source_name else ""
    if amount > old:
        text = f"{target['name']} gains {amount} temp HP{source_suffix}"
        if old:
            text += f" (replacing {old})"
    else:
        text = (
            f"{target['name']} keeps {old} temp HP instead of "
            f"{amount}{source_suffix} (they don't stack)"
        )
    step.log(
        text,
        character=target["name"],
        action=Action.ADD_TEMP_HP,
        value=temp_hp_value,
    )
    step.result.change(target)
