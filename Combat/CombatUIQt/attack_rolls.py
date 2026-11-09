"""Attack rolls the GM types in for whoever's attacking: whether each one hits a
target's AC, and what the players learn from it. They know the number and the
result, so every roll narrows the AC down, and the Limited player view, which
hides the AC itself, keeps track of that for them (player_view.py). What's known
is kept in the target's public keys, so undo and a saved fight keep it too."""

import re
from dataclasses import dataclass

from Combat.Effects.modifiers import armor_class_bonus
from Model.Creatures.Combatants import Visibility
from .amounts import parse_amount

_NATURAL = re.compile(r"\s*nat(?:ural)?\s*(1|20)\s*", re.IGNORECASE)
_ALWAYS_HITS = 20
_ALWAYS_MISSES = 1
# What cover adds to a target's AC. Total Cover can't be targeted at all.
_COVER_BONUSES = {
    Visibility.HALF_COVER.value: 2,
    Visibility.THREE_QUARTERS_COVER.value: 5,
}


@dataclass(frozen=True)
class AttackRoll:
    total: int | None = None  # None for a natural roll, which is all that counts
    natural: int | None = None  # 20 or 1, when the GM typed one

    @property
    def text(self) -> str:
        return f"natural {self.natural}" if self.natural else str(self.total)

    @property
    def is_critical(self) -> bool:
        return self.natural == _ALWAYS_HITS

    def hits(self, armor: int | None) -> bool | None:
        """Whether it hits AC `armor`; a natural 20 always does and a natural 1
        never. None when it can't be told: the target has no AC."""
        if self.natural is not None:
            return self.is_critical
        return None if armor is None or self.total is None else self.total >= armor


def parse_attack_roll(text: str) -> AttackRoll | None:
    """What the Attack roll field says: a total or a sum, as in the other amount
    fields, or "nat 20" or "nat 1". None if it's neither."""
    natural = _NATURAL.fullmatch(text)
    if natural:
        return AttackRoll(natural=int(natural[1]))
    total = parse_amount(text)
    return None if total is None else AttackRoll(total=total)


def rolled_attack(d20: int, bonus: int) -> AttackRoll:
    """The attack roll a d20 and the attacker's bonus make."""
    if d20 in (_ALWAYS_HITS, _ALWAYS_MISSES):
        return AttackRoll(natural=d20)
    return AttackRoll(total=d20 + bonus)


def cover_bonus(char: dict) -> int:
    """What char's cover adds to its AC: only the most protective one counts."""
    states = char.get("visibility_states", [])
    return max((_COVER_BONUSES.get(state, 0) for state in states), default=0)


def armor_bonus(char: dict) -> int:
    """What char's AC has added to it now: its cover, and what its modifiers
    give (Combat/Effects)."""
    return cover_bonus(char) + armor_class_bonus(char)


def note_attack_roll(char: dict, roll: AttackRoll, hit: bool | None, bonus: int = 0):
    """Keep what `roll` showed about char's AC: at most the roll on a hit, above
    it on a miss. `bonus` is what the AC had added to it then (armor_bonus),
    which is taken off, so a note stays true when char leaves cover or the
    effect ends. A natural roll shows nothing, since it ignores the AC."""
    if roll.total is None or hit is None:
        return
    total = roll.total - bonus
    if hit:
        char["ac_at_most"] = min(total, char.get("ac_at_most", total))
    else:
        char["ac_above"] = max(total, char.get("ac_above", total))


def known_ac_text(char: dict) -> str:
    """What attack rolls have shown of char's AC: "AC > 10", "AC ≤ 17",
    "10 < AC ≤ 17" or, once they meet, "AC = 11". "" if nothing has."""
    above, at_most = char.get("ac_above"), char.get("ac_at_most")
    if above is None and at_most is None:
        return ""
    if at_most is None:
        return f"AC > {above}"
    if above is None:
        return f"AC ≤ {at_most}"
    if above + 1 == at_most:
        return f"AC = {at_most}"
    return f"{above} < AC ≤ {at_most}"
