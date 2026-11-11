"""A monster's abilities as the combat UI uses them on its turn: to-hit bonus,
damage dice, save DC and how often it can be used, read from the stat block's
text, so that freeform abilities, structured ones and ones reloaded from a
saved fight (plain dicts) all work the same. An ability with combat effects
written on it (MonsterAbility.combat_effects) is taken at its word instead."""

import random
import re
from dataclasses import dataclass, field

from Core.Definitions import Condition, CreatureSize, DamageType
from Model.Content.CombatEffect import CombatEffect

# The stat blocks don't record this; nearly every legendary creature has 3.
LEGENDARY_ACTIONS_PER_ROUND = 3

# The sections of a stat block shown on a monster's turn, as (key, title).
ACTION_SECTIONS = (
    ("actions", "Actions"),
    ("bonus_actions", "Bonus Actions"),
    ("reactions", "Reactions"),
    ("legendary_actions", "Legendary Actions"),
)

DAMAGE_TYPE_NAMES = {t.value.lower(): t.value for t in DamageType}
_ATTACK = re.compile(r"Attack Roll:\s*([+-]\d+)")
_SAVE = re.compile(
    r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"
    r"\s+Saving Throw:\s*DC\s*(\d+)?"
)
_MINUS_SIGNS = "−–"
_DICE = rf"\d+d\d+(?:\s*[+{_MINUS_SIGNS}-]\s*\d+)?"
DAMAGE = re.compile(
    rf"(?:\d+\s*\(\s*(?P<dice>{_DICE})\s*\)|(?P<bare>{_DICE})|(?P<flat>\d+))"
    r"\s+(?:(?P<type>[A-Za-z]+)(?P<or>\s+or\s+[A-Za-z]+)?\s+)?damage"
)
JOINED = re.compile(r",?\s*(?:plus|and)\s+")
# One kind of die in a roll: "2d6" is (2, 6).
DIE = re.compile(r"(\d+)d(\d+)")
_CONDITIONAL = re.compile(r"\s+(?:if|while|when|unless|until|at the|on a)\b")
_RECHARGE = re.compile(r"\(Recharge\s+(\d)(?:\D\d)?\)")
_PER_DAY = re.compile(r"\((\d+)/Day")
_LEGENDARY_COST = re.compile(r"\(Costs\s+(\d+)\s+Actions?\)")
_START_OF_TURN = re.compile(r"start of (?:each of )?(?:its|the [\w -]+?'s) turns?")


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
    the end of its next turn", as EffectOption.until has it), whether it's
    once per turn, what only the GM can tell (`when`, said as what follows
    "if"), and a note for the badge ("Escape DC 13, from one of two
    claws.")."""

    text: str
    conditions: tuple[str, ...]
    largest_target: CreatureSize | None = None
    until: tuple[str, str] | None = None
    once_per_turn: bool = False
    when: str = ""
    note: str = ""


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


@dataclass(frozen=True)
class DamageRoll:
    dice: str  # "2d6 + 3", or "4" for a flat amount
    damage_type: str | None  # None when the monster chooses it as it attacks


@dataclass(frozen=True)
class MonsterAction:
    name: str
    description: str
    to_hit: int | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    half_on_save: bool = False
    damage: tuple[DamageRoll, ...] = field(default_factory=tuple)
    recharge_on: int | None = None  # the lowest d6 that brings it back
    per_day: int | None = None
    legendary_cost: int = 0
    rider: str = ""  # what its text says besides that damage, conditions apart
    # The conditions its hit gives in sentences of their own (hit_riders),
    # which the picker makes rows of, applied as it hits; not in `rider`.
    riders: tuple[HitRider, ...] = ()
    # What its stat block says using it does (MonsterAbility.combat_effects),
    # one per way to use it; () to read its text.
    effects: tuple[CombatEffect, ...] = ()

    @property
    def is_limited(self) -> bool:
        return self.recharge_on is not None or self.per_day is not None

    @property
    def is_rollable(self) -> bool:
        return self.to_hit is not None or bool(self.damage)

    @property
    def summary(self) -> str:
        """Its numbers, as they read on its button."""
        parts = []
        if self.to_hit is not None:
            parts.append(f"{self.to_hit:+d}")
        if self.save_ability is not None:
            parts.append(f"DC {self.save_dc or '?'} {self.save_ability[:3]}")
        parts += [
            f"{roll.dice} {roll.damage_type or '(type of its choice)'}"
            for roll in self.damage
        ]
        if self.half_on_save:
            parts.append("half on save")
        return "  ".join(parts)


def legendary_actions_left(char: dict) -> int:
    """How many legendary actions char can still use before its next turn."""
    if not char.get("legendary_actions"):
        return 0
    return char.get("legendary_actions_left", LEGENDARY_ACTIONS_PER_ROUND)


def is_spent(char: dict, action: MonsterAction) -> bool:
    """Whether char has used up a recharge or per-day action."""
    return char.get("spent_abilities", {}).get(action.name, 0) >= (action.per_day or 1)


def legendary_resistances_left(char: dict) -> int:
    return char.get("legendary_resistances_left", char.get("legendary_resistances", 0))


def ability_text(ability) -> tuple[str, str]:
    """(name, description) of a MonsterAbility, or of the dict it becomes in a
    saved combat log."""
    if isinstance(ability, dict):
        return ability.get("name", ""), ability.get("description", "")
    return ability.name, ability.description


def ability_effects(ability) -> tuple[CombatEffect, ...]:
    """The combat effects written on a MonsterAbility, or on the dict it
    becomes in a saved combat log."""
    if isinstance(ability, dict):
        return tuple(
            CombatEffect.from_dict(e) for e in ability.get("combat_effects", ())
        )
    return tuple(getattr(ability, "combat_effects", ()))


def parse_action(ability, legendary: bool = False) -> MonsterAction:
    """What an ability rolls and costs: from the combat effects written on it
    (its first, for the turn column's buttons), or else from its text. What it
    costs is in its name either way: a recharge, uses per day, a legendary
    action's cost."""
    name, description = ability_text(ability)
    recharge = _RECHARGE.search(name)
    per_day = _PER_DAY.search(name)
    cost = _LEGENDARY_COST.search(f"{name} {description}")
    recharge_on = int(recharge.group(1)) if recharge else None
    uses_per_day = int(per_day.group(1)) if per_day else None
    legendary_cost = (int(cost.group(1)) if cost else 1) if legendary else 0
    effects = ability_effects(ability)
    if effects:
        first = effects[0]
        return MonsterAction(
            name=name,
            description=description,
            to_hit=first.attack_bonus if first.roll == "attack" else None,
            save_ability=first.save_ability.value if first.save_ability else None,
            save_dc=first.dc,
            half_on_save=first.half_on_success,
            damage=tuple(
                DamageRoll(d.dice, d.damage_type.value if d.damage_type else None)
                for d in first.damage
            ),
            effects=effects,
            recharge_on=recharge_on,
            per_day=uses_per_day,
            legendary_cost=legendary_cost,
        )
    attack = _ATTACK.search(description)
    save = _SAVE.search(description)
    damage, rider = _damage_rolls(description, attack is not None)
    riders: tuple[HitRider, ...] = ()
    if attack is not None:
        riders, rider = hit_riders(rider)
    return MonsterAction(
        name=name,
        description=description,
        to_hit=int(attack.group(1)) if attack else None,
        save_ability=save.group(1) if save else None,
        save_dc=int(save.group(2)) if save and save.group(2) else None,
        half_on_save=bool(re.search(r"Success:\s*Half", description)),
        damage=damage,
        rider=rider,
        riders=riders,
        recharge_on=recharge_on,
        per_day=uses_per_day,
        legendary_cost=legendary_cost,
    )


def _damage_rolls(
    description: str, is_attack: bool
) -> tuple[tuple[DamageRoll, ...], str]:
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
    text = re.split(r"\b(?:Success|Failure or Success|Hit or Miss):", text)[0]
    rolls: list[DamageRoll] = []
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
        if match["or"]:
            damage_type = None  # "Necrotic or Radiant": the monster's choice
        dice = match["dice"] or match["bare"] or match["flat"]
        rolls.append(DamageRoll(tidy_dice(dice), damage_type))
        position = match.end()
    return tuple(rolls), text[position:].strip(" ,.")


def tidy_dice(dice: str) -> str:
    dice = re.sub(f"[{_MINUS_SIGNS}]", "-", dice)
    return re.sub(r"\s*([+-])\s*", r" \1 ", dice.strip())


def monster_actions(char: dict) -> list[tuple[str, list[MonsterAction]]]:
    """char's stat-block sections that have anything in them, parsed."""
    return [
        (
            title,
            [
                parse_action(ability, legendary=key == "legendary_actions")
                for ability in char[key]
            ],
        )
        for key, title in ACTION_SECTIONS
        if char.get(key)
    ]


def start_of_turn_traits(char: dict) -> list[tuple[str, str]]:
    """char's traits that do something at the start of its turn, as (name,
    the sentence saying what)."""
    found = []
    for trait in char.get("traits") or []:
        name, description = ability_text(trait)
        match = _START_OF_TURN.search(description)
        if match is None:
            continue
        sentences = re.split(r"(?<=[.!?])\s+", description)
        found.append(
            (name, next(s for s in sentences if _START_OF_TURN.search(s)).strip())
        )
    return found


def roll_dice(dice: str, critical: bool = False) -> int:
    """Roll "2d6 + 3" or a flat "4"; a critical hit rolls the dice twice over."""
    total = 0
    position = 0
    for match in DIE.finditer(dice):
        count, sides = int(match.group(1)), int(match.group(2))
        total += sum(
            random.randint(1, sides) for _ in range(count * (2 if critical else 1))
        )
        position = match.end()
    rest = dice[position:].replace(" ", "")
    return total + int(rest) if rest else total


def first_number(value) -> int | None:
    """The number an AC starts with: a monster's is a number, a player's a
    text like "18 (with Shield) and 16 (without Shield)"."""
    match = re.match(r"\s*(\d+)", str(value))
    return int(match.group(1)) if match else None
