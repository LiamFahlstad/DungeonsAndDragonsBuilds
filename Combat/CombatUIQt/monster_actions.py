"""A monster's abilities as the combat UI uses them on its turn: to-hit bonus,
damage dice, save DC and how often it can be used, read from the stat block's
text, so that freeform abilities, structured ones and ones reloaded from a
saved fight (plain dicts) all work the same."""

import random
import re
from dataclasses import dataclass, field

from Core.Definitions import DamageType

# The stat blocks don't record this; nearly every legendary creature has 3.
LEGENDARY_ACTIONS_PER_ROUND = 3

# The sections of a stat block shown on a monster's turn, as (key, title).
ACTION_SECTIONS = (
    ("actions", "Actions"),
    ("bonus_actions", "Bonus Actions"),
    ("reactions", "Reactions"),
    ("legendary_actions", "Legendary Actions"),
)

_DAMAGE_TYPE_NAMES = {t.value.lower(): t.value for t in DamageType}
_ATTACK = re.compile(r"Attack Roll:\s*([+-]\d+)")
_SAVE = re.compile(
    r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)"
    r"\s+Saving Throw:\s*DC\s*(\d+)?"
)
_MINUS_SIGNS = "−–"
_DICE = rf"\d+d\d+(?:\s*[+{_MINUS_SIGNS}-]\s*\d+)?"
_DAMAGE = re.compile(
    rf"(?:\d+\s*\(\s*(?P<dice>{_DICE})\s*\)|(?P<bare>{_DICE})|(?P<flat>\d+))"
    r"\s+(?:(?P<type>[A-Za-z]+)(?P<or>\s+or\s+[A-Za-z]+)?\s+)?damage"
)
_JOINED = re.compile(r",?\s*(?:plus|and)\s+")
_CONDITIONAL = re.compile(r"\s+(?:if|while|when|unless|until|at the|on a)\b")
_RECHARGE = re.compile(r"\(Recharge\s+(\d)(?:\D\d)?\)")
_PER_DAY = re.compile(r"\((\d+)/Day")
_LEGENDARY_COST = re.compile(r"\(Costs\s+(\d+)\s+Actions?\)")
_START_OF_TURN = re.compile(r"start of (?:each of )?(?:its|the [\w -]+?'s) turns?")


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


def legendary_resistances_left(char: dict) -> int:
    return char.get("legendary_resistances_left", char.get("legendary_resistances", 0))


def ability_text(ability) -> tuple[str, str]:
    """(name, description) of a MonsterAbility, or of the dict it becomes in a
    saved combat log."""
    if isinstance(ability, dict):
        return ability.get("name", ""), ability.get("description", "")
    return ability.name, ability.description


def parse_action(ability, legendary: bool = False) -> MonsterAction:
    name, description = ability_text(ability)
    attack = _ATTACK.search(description)
    save = _SAVE.search(description)
    recharge = _RECHARGE.search(name)
    per_day = _PER_DAY.search(name)
    cost = _LEGENDARY_COST.search(f"{name} {description}")
    damage, rider = _damage_rolls(description, attack is not None)
    return MonsterAction(
        name=name,
        description=description,
        to_hit=int(attack.group(1)) if attack else None,
        save_ability=save.group(1) if save else None,
        save_dc=int(save.group(2)) if save and save.group(2) else None,
        half_on_save=bool(re.search(r"Success:\s*Half", description)),
        damage=damage,
        rider=rider,
        recharge_on=int(recharge.group(1)) if recharge else None,
        per_day=int(per_day.group(1)) if per_day else None,
        legendary_cost=(int(cost.group(1)) if cost else 1) if legendary else 0,
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
    for match in _DAMAGE.finditer(text):
        between = text[position : match.start()]
        if rolls:
            if not _JOINED.fullmatch(between) or _CONDITIONAL.match(text, match.end()):
                break
        elif ". " in between:
            break  # the first sentence has none: it's an effect's, for later
        word = match["type"]
        damage_type = _DAMAGE_TYPE_NAMES.get(word.lower()) if word else None
        if word and damage_type is None and not match["or"]:
            break  # "1 extra damage": not a type, not a roll of its own
        if match["or"]:
            damage_type = None  # "Necrotic or Radiant": the monster's choice
        dice = match["dice"] or match["bare"] or match["flat"]
        rolls.append(DamageRoll(_tidy_dice(dice), damage_type))
        position = match.end()
    return tuple(rolls), text[position:].strip(" ,.")


def _tidy_dice(dice: str) -> str:
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
    for match in re.finditer(r"(\d+)d(\d+)", dice):
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
