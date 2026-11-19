"""A stat-block ability's text read into the CombatEffects the combat UI acts
on (Notes/explicit-attributes-plan.md, Phase 4.3): its attack or save, the
damage a hit or failed save deals, the condition it gives and how long for,
the Hit Points it gives, its area, an attack's reach and range (Phase
4.5), and a HIT-triggered effect for each
condition its hit gives in a sentence of its own and for a save its hit
forces.

This is read where content is written: by generate_monsters.py
(monster_enum_format.format_ability_list), once for the stat block files
written before the effects existed, and once as a saved fight loads, for an
ability logged before them (monster_actions.upgrade_ability_keys). The fight
itself reads the effects (MonsterAbility.combat_effects), never this text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from Combat.CombatUIQt.effect_options import (
    _REPEATS_THE_SAVE,
    _inflicted_condition,
    _read_gain,
)
from Combat.CombatUIQt.monster_actions import (
    ACTION_SECTIONS,
    DAMAGE,
    DAMAGE_TYPE_NAMES,
    JOINED,
    ability_effects,
    ability_text,
    picker_names,
    tidy_dice,
)
from Combat.CombatUIQt.saves import CONDITION_JOINER
from Core.Definitions import Ability, Condition, CreatureSize, DamageType
from Model.Content.CombatAreaText import read_combat_area
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from Model.Creatures.MonsterAbilities import ability_field
from Model.Creatures.MonsterAbilityText import name_alone, read_ability

# The sections whose abilities the picker lists (a trait only with effects
# written on it by hand): only they get effects read from their text.
EFFECT_SECTIONS = tuple(key for key, _ in ACTION_SECTIONS)

_ATTACK = re.compile(r"Attack Roll:\s*([+-]\d+)")
# An attack's reach and range, in what comes before its "Hit:" ("Melee
# Attack Roll: +6, reach 10 ft.", "range 80/320 ft.", "reach 5 feet").
_REACH = re.compile(r"\breach (\d+) ?(?:ft\b|feet\b)", re.IGNORECASE)
_RANGE = re.compile(r"\brange (\d+)(?:/(\d+))? ?(?:ft\b|feet\b)", re.IGNORECASE)
_SAVE = re.compile(
    r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"
    r"\s+Saving Throw:\s*DC\s*(\d+)?"
)
_HALF = re.compile(r"Success:\s*Half")
_OUTCOME_LABELS = re.compile(r"\b(?:Success|Failure or Success|Hit or Miss):")
_CHOSEN_FROM = re.compile(r" of a type chosen by [^:]+: (?P<types>[A-Za-z ,]+)")
_TYPE_LIST = re.compile(r",? or |, ")
_CONDITIONAL = re.compile(r"\s+(?:if|while|when|unless|until|at the|on a)\b")
# Where a monster's hit stops and a save it forces begins.
_HIT_ENDS = re.compile(r"\b\w+ Saving Throw:|\bFailure:")
# "If the target is a creature that isn't an Undead or elf, it is subjected
# to the following effect.": what the save its hit forces waits on.
_SAVE_GATE = re.compile(
    r"\bIf (?P<gate>[^,.]+), (?:it|the target) is subjected to the following effect"
)
_ANY_CREATURE = "the target is a creature"

# A condition an attack's hit gives, in one sentence of its Hit: text
# (Notes/combat-effects-plan.md, 6.4). Read strictly: a sentence that says
# anything more ("and the allosaurus can make one Bite attack against it",
# "the balor pulls the target", "(pixie's choice)") isn't one, and stays in
# the rider for the GM to read.
_CONDITION = "|".join(c.value for c in Condition)
_SIZE = "|".join(s.value for s in CreatureSize)
_SIZE_GATE = (
    rf"(?:the )?target is (?:a |an )?(?P<size>{_SIZE}) or smaller(?: creature)?"
)
_GIVES = (
    rf"(?:has|have) the (?P<first>{_CONDITION})(?: and (?P<second>{_CONDITION}))?"
    r" conditions?"
    r"(?: \(escape DC (?P<escape>\d+)\))?"
    r"(?: (?P<holds>from [^,.]+?))?"
    rf"(?:, and (?:it|the target) has the (?P<grapple>{_CONDITION}) condition"
    r" until the grapple ends)?"
    r"(?: until the (?P<edge>start|end) of"
    r" (?P<whose>its|their|the [\w -]+?['’]s) next turn)?"
)
# "..., and the target has the Poisoned condition until the end of its next
# turn": joined onto the damage, so the rider starts with "and".
_JOINED_RIDER = re.compile(rf"and (?:the target|it) (?:also )?{_GIVES}")
# "If the target is a Large or smaller creature, it has the Prone
# condition."; with what only the GM can tell ("and the elephant moved 20+
# feet straight toward it immediately before the hit"), or "Once per turn".
_IF_RIDER = re.compile(
    r"(?P<once>Once per turn, )?[Ii]f (?P<gates>[^,]+),"
    rf" (?:it|the target) (?:also )?{_GIVES}"
)
_GATES = (
    re.compile(rf"{_SIZE_GATE}(?: and (?P<when>.+))?"),
    re.compile(rf"(?P<when>.+?) and {_SIZE_GATE}"),
)
# "The target has the Grappled condition (escape DC 15) from one of ten
# tentacles, ...": a sentence of its own, with no gate.
_PLAIN_RIDER = re.compile(rf"The target (?:also )?{_GIVES}")
# "While Grappled, the target has the Restrained condition.", right after
# the rider that grapples.
_WHILE_GRAPPLED = re.compile(
    rf"While (?P<held>{_CONDITION}), the target (?:also )?has the"
    rf" (?P<also>{_CONDITION}) condition"
)
_RIDER_SENTENCE = re.compile(r"(?<=[.!?])\s+")
_THE_TARGETS_TURN = re.compile(r"its|their|the (?:target|creature)['’]s")


@dataclass(frozen=True)
class HitRider:
    """A condition an attack's hit gives, read from one sentence of its
    Hit: text (`text`, as it was in the rider): the conditions, the largest
    target it lands on ("If the target is a Large or smaller creature"),
    how long the first lasts if that's a turn (("end", "target") for "until
    the end of its next turn"), whether it's once per turn, what only the GM
    can tell (`when`, said as what follows "if"), and a note for the badge
    ("Escape DC 13, from one of two claws.")."""

    text: str
    conditions: tuple[str, ...]
    largest_target: CreatureSize | None = None
    until: tuple[str, str] | None = None
    once_per_turn: bool = False
    when: str = ""
    note: str = ""


@dataclass(frozen=True)
class AbilityReading:
    """What an ability's text says it rolls and does: its attack bonus or
    save, the damage of a hit or failed save, the conditions its hit gives
    in sentences of their own (`riders`) and what else its outcome says
    (`rider`), for the GM."""

    to_hit: int | None
    save_ability: str | None
    save_dc: int | None
    half_on_save: bool
    damage: tuple[CombatDamage, ...]
    rider: str
    riders: tuple[HitRider, ...]

    @property
    def has_own_roll(self) -> bool:
        return (
            self.to_hit is not None
            or bool(self.damage)
            or self.save_ability is not None
        )


def hit_riders(rider: str) -> tuple[tuple[HitRider, ...], str]:
    """The conditions an attack's hit gives that its `rider` text (what its
    Hit: text says after the damage) says in a sentence of their own, and
    the rest of the rider, without those sentences."""
    riders: list[HitRider] = []
    rest: list[str] = []
    for sentence in _RIDER_SENTENCE.split(rider):
        sentence = sentence.rstrip(".").strip()
        if not sentence:
            continue
        found = _read_rider(sentence)
        if found is not None:
            riders.append(found)
            continue
        also = _WHILE_GRAPPLED.fullmatch(sentence)
        if also is not None and riders and also["held"] in riders[-1].conditions:
            last = riders[-1]
            note = f"{also['also']} while {also['held']}."
            riders[-1] = HitRider(
                text=f"{last.text}. {sentence}",
                conditions=(*last.conditions, also["also"]),
                largest_target=last.largest_target,
                until=last.until,
                once_per_turn=last.once_per_turn,
                when=last.when,
                note=f"{last.note} {note}".strip(),
            )
            continue
        rest.append(sentence)
    if not riders:
        return (), rider
    return tuple(riders), ". ".join(rest)


def _read_rider(sentence: str) -> HitRider | None:
    """The rider one sentence is, if it's nothing but one."""
    match = _JOINED_RIDER.fullmatch(sentence) or _PLAIN_RIDER.fullmatch(sentence)
    size: str | None = None
    when = ""
    once = False
    if match is None:
        match = _IF_RIDER.fullmatch(sentence)
        if match is None:
            return None
        once = bool(match["once"])
        gates = match["gates"]
        for pattern in _GATES:
            gate = pattern.fullmatch(gates)
            if gate is not None:
                size, when = gate["size"], gate["when"] or ""
                break
        else:
            when = gates
    conditions = tuple(
        c for c in (match["first"], match["second"], match["grapple"]) if c
    )
    until = None
    if match["edge"]:
        whose = "target" if _THE_TARGETS_TURN.fullmatch(match["whose"]) else "source"
        until = (match["edge"], whose)
    notes = []
    if match["escape"]:
        holds = f", {match['holds']}" if match["holds"] else ""
        notes.append(f"Escape DC {match['escape']}{holds}.")
    if match["grapple"]:
        notes.append(f"{match['grapple']} until the grapple ends.")
    return HitRider(
        text=sentence,
        conditions=conditions,
        largest_target=CreatureSize(size) if size else None,
        until=until,
        once_per_turn=once,
        when=when.strip(),
        note=" ".join(notes),
    )


def _damage_rolls(
    description: str, is_attack: bool
) -> tuple[tuple[CombatDamage, ...], str]:
    """The damage every hit or failed save deals, and the text after it. Only
    the first sentence's first damage counts, plus any joined straight onto
    it. What's left waits on something ("if the attack roll had Advantage", "at
    the start of each of its turns", "or 9 (3d4 + 2) if it charged"), so it's
    for the GM to read, not to go on the hit by itself."""
    label = "Hit:" if is_attack else "Failure:"
    start = description.find(label)
    if start < 0:
        return (), ""
    text = description[start + len(label) :]
    text = _OUTCOME_LABELS.split(text)[0]
    rolls: list[CombatDamage] = []
    position = 0
    for match in DAMAGE.finditer(text):
        between = text[position : match.start()]
        if rolls:
            if not JOINED.fullmatch(between) or _CONDITIONAL.match(text, match.end()):
                break
        elif ". " in between:
            break  # the first sentence has none: it's an effect's, for later
        word = match["type"]
        damage_type = DAMAGE_TYPE_NAMES.get(word.lower()) if word else None
        if word and damage_type is None and not match["or"]:
            break  # "1 extra damage": not a type, not a roll of its own
        dice = tidy_dice(match["dice"] or match["bare"] or match["flat"])
        if match["or"]:
            # "Necrotic or Radiant": the monster's choice.
            other = DAMAGE_TYPE_NAMES.get(match["or"].split()[-1].lower())
            choices = tuple(
                DamageType(t) for t in (damage_type, other) if t is not None
            )
            rolls.append(CombatDamage(dice, None, choices=choices))
        elif damage_type is None:
            # "6 (1d6 + 3) damage of a type chosen by the kobold: Acid, Cold or
            # Fire": the monster's choice of those; of any when it lists none.
            listed = _CHOSEN_FROM.match(text, match.end())
            names = _TYPE_LIST.split(listed["types"]) if listed else []
            choices = tuple(
                DamageType(DAMAGE_TYPE_NAMES[n.lower()])
                for n in names
                if n.lower() in DAMAGE_TYPE_NAMES
            )
            if len(choices) < 2:
                choices = tuple(DamageType)
            rolls.append(CombatDamage(dice, None, choices=choices))
        else:
            rolls.append(CombatDamage(dice, DamageType(damage_type)))
        position = match.end()
    return tuple(rolls), text[position:].strip(" ,.")


def read_reach_and_range(
    description: str,
) -> tuple[int | None, int | None, int | None]:
    """(reach_ft, range_ft, long_range_ft) an attack's text states before
    its "Hit:", a None for each it doesn't."""
    head = description.split("Hit:", 1)[0]
    reach = _REACH.search(head)
    ranged = _RANGE.search(head)
    return (
        int(reach[1]) if reach else None,
        int(ranged[1]) if ranged else None,
        int(ranged[2]) if ranged and ranged[2] else None,
    )


def read_text(description: str) -> AbilityReading:
    """What `description` says the ability rolls and deals."""
    attack = _ATTACK.search(description)
    save = _SAVE.search(description)
    damage, rider = _damage_rolls(description, attack is not None)
    riders: tuple[HitRider, ...] = ()
    if attack is not None:
        riders, rider = hit_riders(rider)
    return AbilityReading(
        to_hit=int(attack.group(1)) if attack else None,
        save_ability=save.group(1) if save else None,
        save_dc=int(save.group(2)) if save and save.group(2) else None,
        half_on_save=bool(_HALF.search(description)),
        damage=damage,
        rider=rider,
        riders=riders,
    )


def _outcome_condition(
    description: str, is_attack: bool, riders: tuple[HitRider, ...]
) -> tuple[str, tuple[str, str] | None]:
    """The condition its Hit: or Failure: text gives, and how long for if
    that's a turn. A hit's text stops where a save it forces begins: that
    save's condition is only for who fails it, so it's the save's own
    effect. Neither is what "Failure or Success:" gives, whatever the roll:
    that's in the rider."""
    label = "Hit:" if is_attack else "Failure:"
    start = description.find(label)
    if start < 0:
        return "", None
    text = description[start + len(label) :]
    text = _OUTCOME_LABELS.split(text)[0]
    if is_attack:
        text = _HIT_ENDS.split(text)[0]
    for rider in riders:
        # Its own effect gives it, as the attack hits.
        text = text.replace(rider.text, "")
    condition, _, until, _ = _inflicted_condition(text)
    return condition, until


def _condition(name: str, until: tuple[str, str] | None) -> CombatCondition:
    return CombatCondition(
        name,
        until=(TurnEdge(until[0]), TurnOf(until[1])) if until is not None else None,
    )


def _save_effect(name: str, description: str, save: re.Match) -> CombatEffect:
    """The save an attack's hit forces ("Constitution Saving Throw: DC 10.
    Failure: The target has the Paralyzed condition until the end of its
    next turn."), rolled as that attack hits (or after it, hit or miss, when
    its text says "Hit or Miss:"), with what its Failure: text deals and
    gives, and its own area; asked first when its text says what it waits
    on ("If the target is a creature that isn't an Undead or elf")."""
    text = description[save.start() :]
    before = description[: save.start()]
    reading = read_text(text)
    condition, until = _outcome_condition(text, False, ())
    gate = _SAVE_GATE.search(before)
    when = gate["gate"] if gate is not None else ""
    event = TriggerEvent.USES if "Hit or Miss:" in before else TriggerEvent.HIT
    notes = (f"Also: {reading.rider}",) if reading.rider else ()
    return CombatEffect(
        name=f"{name_alone(name)}: {reading.save_ability} save",
        roll=EffectRoll.SAVE,
        save_ability=Ability(reading.save_ability),
        dc=reading.save_dc,
        half_on_success=reading.half_on_save,
        repeat_save=bool(_REPEATS_THE_SAVE.search(text)),
        damage=reading.damage,
        conditions=(_condition(condition, until),) if condition else (),
        spends_use=False,
        notes=notes,
        trigger=CombatTrigger(
            event,
            optional=False,
            after=name,
            when="" if when == _ANY_CREATURE else when,
        ),
        area=read_combat_area(text),
    )


def _rider_effect(name: str, rider: HitRider) -> CombatEffect:
    """A condition the attack's hit gives in a sentence of its own ("Tree
    Club: Prone"), which the simulator applies as that attack hits
    (Notes/combat-effects-plan.md, 6.4), asking first about what it can't
    check: a size it doesn't know, a `when`. It spends nothing: the attack
    did."""
    first, *others = rider.conditions
    return CombatEffect(
        name=f"{name_alone(name)}: {CONDITION_JOINER.join(rider.conditions)}",
        conditions=(
            _condition(first, rider.until),
            *(CombatCondition(c) for c in others),
        ),
        spends_use=False,
        notes=(rider.note,) if rider.note else (),
        trigger=CombatTrigger(
            TriggerEvent.HIT,
            optional=False,
            after=name,
            largest_target=rider.largest_target,
            once_per_turn=rider.once_per_turn,
            when=rider.when,
        ),
    )


def read_effects(name: str, description: str) -> tuple[CombatEffect, ...]:
    """The combat effects an ability's text says it has: its own (its attack
    or save, damage, condition, Hit Points, area), then one per condition
    its hit gives in a sentence of its own and one for a save its hit
    forces. () when the text says nothing to apply (Multiattack)."""
    reading = read_text(description)
    is_attack = reading.to_hit is not None
    is_save = not is_attack and reading.save_ability is not None
    condition, until = _outcome_condition(description, is_attack, reading.riders)
    gain = None
    if not (reading.has_own_roll):
        gain = _read_gain(description, ())
    forced = _SAVE.search(description) if is_attack else None
    # A save its hit forces has its own area (the Dao's Earth Burst).
    area = read_combat_area(
        description[: forced.start()] if forced is not None else description
    )
    notes = []
    if forced is not None and reading.save_ability is not None:
        notes.append(
            f"Its {reading.save_ability} save is a row of its own, rolled as it hits."
        )
    if reading.rider:
        notes.append(f"Also: {reading.rider}")
    if not (reading.has_own_roll or condition or gain or area or notes):
        return ()
    if name.startswith("Multiattack"):
        notes.insert(0, "Pick each of its attacks in turn.")
    roll = EffectRoll.NONE
    if is_attack:
        roll = EffectRoll.ATTACK
    elif is_save:
        roll = EffectRoll.SAVE
    own = CombatEffect(
        roll=roll,
        save_ability=Ability(reading.save_ability) if is_save else None,
        dc=reading.save_dc if is_save else None,
        half_on_success=is_save and reading.half_on_save,
        repeat_save=is_save and bool(_REPEATS_THE_SAVE.search(description)),
        attack_bonus=reading.to_hit,
        damage=reading.damage,
        healing=(
            CombatHitPoints(gain.dice)
            if gain is not None and not gain.temporary
            else None
        ),
        temp_hp=(
            CombatHitPoints(gain.dice) if gain is not None and gain.temporary else None
        ),
        conditions=(_condition(condition, until),) if condition else (),
        notes=tuple(notes),
        area=area,
        **(_reach_and_range_fields(description) if is_attack else {}),
    )
    effects = [own, *(_rider_effect(name, r) for r in reading.riders)]
    if forced is not None:
        effects.append(_save_effect(name, description, forced))
    return tuple(effects)


def _reach_and_range_fields(description: str) -> dict:
    """An attack effect's reach_ft, range_ft and long_range_ft keywords, the
    ones its text states."""
    reach, normal, far = read_reach_and_range(description)
    found = {"reach_ft": reach, "range_ft": normal, "long_range_ft": far}
    return {key: feet for key, feet in found.items() if feet is not None}


def reads_effects(ability, section: str) -> bool:
    """Whether `ability`, one of a stat block's `section`, has its combat
    effects read from its text: an action section's ability without effects
    written by hand, that casts no spell and isn't another ability's use
    (the picker makes those rows from its `casts` and `uses_ability`)."""
    return (
        section in EFFECT_SECTIONS
        and not ability_effects(ability)
        and not ability_field(ability, "casts")
        and not ability_field(ability, "uses_ability")
    )


def read_ability_effects(ability, section: str) -> tuple[CombatEffect, ...]:
    """The combat effects `ability`'s text gives it, as one of a stat
    block's `section` (reads_effects); () for one that isn't read."""
    if not reads_effects(ability, section):
        return ()
    name, description = ability_text(ability)
    return read_effects(name, description)


def read_ability_fields(char, ability, section: str) -> dict:
    """What `ability`'s name and text say its MonsterAbility fields are
    (Model/Creatures/MonsterAbilityText.py), as one of char's `section`:
    only the ones it gives. `char` is a combat dict or a stat block."""
    name, description = ability_text(ability)
    effects = ability_effects(ability)
    if effects:
        first = effects[0]
        has_own_roll = (
            (first.roll == EffectRoll.ATTACK and first.attack_bonus is not None)
            or bool(first.damage)
            or first.save_ability is not None
        )
    else:
        has_own_roll = read_text(description).has_own_roll
    return read_ability(
        name,
        description,
        names=picker_names(char),
        has_own_roll=has_own_roll,
        is_trait=section == "traits",
    )


def main(argv: list[str]) -> int:
    """Print the combat effects an ability's text gives, as Python, for a
    hand-written stat block to start from."""
    import sys

    from CharacterContent.Spells.SpellClassConverter import source_of

    if len(argv) != 2:
        print(
            'usage: python -m Combat.Tools.monster_effect_text "<name>" "<description>"',
            file=sys.stderr,
        )
        return 2
    effects = read_effects(*argv)
    print(f"combat_effects={source_of(effects)}," if effects else "(nothing to apply)")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
