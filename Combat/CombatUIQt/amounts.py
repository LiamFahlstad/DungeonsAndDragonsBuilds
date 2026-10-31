"""What the GM types in the combat UI's amount fields. Everywhere a number,
a sum ("8+5") or a halving ("24/2"); the Damage field also takes damage types,
spelled out or cut short ("12 fire", "12 fi", "12f"), even more than one for a
hit of two types ("7 pi + 3 fi")."""

import re

from Core.Definitions import DamageType

# One letter is enough for the common damage types; where several start with
# it, the most common one wins and the others take two letters ("fo", "po").
_ONE_LETTER_DAMAGE_TYPES = {
    "a": DamageType.ACID,
    "b": DamageType.BLUDGEONING,
    "c": DamageType.COLD,
    "f": DamageType.FIRE,
    "l": DamageType.LIGHTNING,
    "n": DamageType.NECROTIC,
    "p": DamageType.PIERCING,
    "r": DamageType.RADIANT,
    "s": DamageType.SLASHING,
    "t": DamageType.THUNDER,
}

# A sum's term: a number, maybe halved, maybe with a damage type (the halving
# reads as well on either side of it: "24/2 fi", "24 fi/2").
_TERM = re.compile(
    r"\s*(?P<sign>[+-]?)\s*(?P<number>\d+)\s*"
    r"(?:/\s*(?P<divisor>\d+))?\s*"
    r"(?P<word>[^\W\d_]*)\s*"
    r"(?:/\s*(?P<late_divisor>\d+))?\s*"
)


class AmountError(ValueError):
    """Why what was typed can't be applied, in words for the status line."""


def damage_type_from_text(word: str) -> str | None:
    """The damage type a word names, in full or cut short: its one letter
    (see above), or as many letters as tell it from the others."""
    word = word.strip().lower()
    if word in _ONE_LETTER_DAMAGE_TYPES:
        return _ONE_LETTER_DAMAGE_TYPES[word].value
    matches = [t.value for t in DamageType if t.value.lower().startswith(word)]
    return matches[0] if word and len(matches) == 1 else None


def parse_damage(text: str) -> list[tuple[int, str | None]]:
    """What the Damage field says, as (amount, damage type) for each type
    named, in the order typed; a single (amount, None) with no type in it. A
    number with no type of its own takes the next one named ("8+5 fire" is 13
    fire), or the last if none follows. Raises AmountError if it can't."""
    terms = _parse_terms(text)
    typed = [word for _, word in terms if word]
    if not typed:
        total = sum(amount for amount, _ in terms)
        if total < 0:
            raise AmountError(f"'{text.strip()}' comes to less than 0")
        return [(total, None)]

    totals: dict[str, int] = {}
    upcoming = list(typed)
    for amount, word in terms:
        damage_type = word or (upcoming[0] if upcoming else typed[-1])
        if word:
            upcoming.pop(0)
        totals[damage_type] = totals.get(damage_type, 0) + amount
    if any(total < 0 for total in totals.values()):
        raise AmountError(f"'{text.strip()}' comes to less than 0")
    return [(total, damage_type) for damage_type, total in totals.items()]


def parse_amount(text: str) -> int | None:
    """The whole number typed in an amount field with no damage type to it,
    or None if it isn't one or comes to less than 0."""
    try:
        parts = parse_damage(text)
    except AmountError:
        return None
    if len(parts) != 1 or parts[0][1] is not None:
        return None
    return parts[0][0]


def _parse_terms(text: str) -> list[tuple[int, str | None]]:
    """text's terms as (signed amount, damage type or None)."""
    if not text.strip():
        raise AmountError("no amount")
    if re.search(r"\d\s*d\s*\d", text):
        raise AmountError(_not_an_amount(text))  # dice, not a total
    terms = []
    position = 0
    while position < len(text):
        match = _TERM.match(text, position)
        if match is None or match.end() == position:
            raise AmountError(_not_an_amount(text))
        sign = match["sign"]
        if bool(sign) == (position == 0) and sign != "+":
            # Only the first term goes without a sign, and it can't be "-".
            raise AmountError(_not_an_amount(text))
        amount = int(match["number"])
        for divisor in (match["divisor"], match["late_divisor"]):
            if divisor is not None:
                if int(divisor) == 0:
                    raise AmountError(_not_an_amount(text))
                amount //= int(divisor)
        damage_type = None
        if match["word"]:
            damage_type = damage_type_from_text(match["word"])
            if damage_type is None:
                raise AmountError(f"'{match['word']}' isn't a damage type")
        terms.append((-amount if sign == "-" else amount, damage_type))
        position = match.end()
    return terms


def _not_an_amount(text: str) -> str:
    return f"'{text.strip()}' isn't an amount"
