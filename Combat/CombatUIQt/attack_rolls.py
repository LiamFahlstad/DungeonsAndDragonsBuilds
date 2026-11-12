"""Attack rolls the GM types in for whoever's attacking: whether each one hits a
target's AC, and what the players learn from it. They know the number and the
result, so every roll narrows the AC down, and the Limited player view, which
hides the AC itself, keeps track of that for them (player_view.py). What's known
is kept in the target's public keys, so undo and a saved fight keep it too."""

import re
from dataclasses import dataclass

from Combat.Effects.modifiers import (
    armor_class,
    armor_class_bonus,
    armor_class_text,
    cover_armor_bonus,
)
from .amounts import parse_amount
from .monster_actions import first_number

_NATURAL = re.compile(r"\s*nat(?:ural)?\s*(1|20)\s*", re.IGNORECASE)
_ALWAYS_HITS = 20
_ALWAYS_MISSES = 1

# True on a combatant with a Shield while it isn't wielding it (the Custom
# Effect dialog's Shield box): its AC is then the one its stored text gives
# "(without Shield)". A public key, so undo and a saved fight keep it.
SHIELD_OFF = "shield_off"
_WITHOUT_SHIELD = re.compile(r"(\d+)\s*\(without Shield\)")


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
    """What char's cover adds to its AC: only the most protective one counts.
    Total Cover can't be targeted at all."""
    return cover_armor_bonus(char)


def armor_without_shield(char: dict) -> int | None:
    """Char's AC without its Shield, from a player's stored "18 (with
    Shield) and 16 (without Shield)"; None for one without a Shield."""
    match = _WITHOUT_SHIELD.search(str(char.get("ac", "")))
    return int(match[1]) if match else None


def has_shield(char: dict) -> bool:
    """Whether char has a Shield it can wield or set down (a player's AC
    sentence says what it is without one)."""
    return armor_without_shield(char) is not None


def is_shield_off(char: dict) -> bool:
    """Whether char has a Shield and isn't wielding it now (SHIELD_OFF)."""
    return bool(char.get(SHIELD_OFF)) and has_shield(char)


def stored_armor(char: dict) -> int | None:
    """Char's AC before its effects and cover: its stored AC's first number,
    or its AC without its Shield while it isn't wielding it. None with no
    AC."""
    if is_shield_off(char):
        return armor_without_shield(char)
    return first_number(char.get("ac"))


def armor_bonus(char: dict) -> int:
    """What char's AC has added to it now: its cover, and what its lasting
    effects do to it (Shield of Faith's +2, Mage Armor's base AC, Barkskin's
    17 at least; Combat/Effects), as a number added to its stored AC
    (stored_armor)."""
    return armor_class_bonus(char, stored_armor(char))


def armor_in_use(char: dict) -> int | None:
    """The AC an attack against char has to meet now: its stored AC with its
    effects and cover. None with no AC."""
    stored = stored_armor(char)
    return None if stored is None else armor_class(char, stored)


def armor_text(char: dict) -> str:
    """Char's AC as its card and More Info show it: the stored text when
    nothing changes it (a player's "18 (with Shield) and 16 (without
    Shield)"), else the AC in use with what changes it, "17 (15; Shield of
    Faith +2)". Without its Shield: "16 (Shield set down)"."""
    stored = stored_armor(char)
    text = "" if stored is None else armor_class_text(char, stored)
    if stored is not None and text != str(stored):
        return f"{text}, Shield set down" if is_shield_off(char) else text
    return f"{stored} (Shield set down)" if is_shield_off(char) else str(char["ac"])


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
