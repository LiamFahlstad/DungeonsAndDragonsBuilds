"""The spellcasting table shared by the 2024 one-third casters (Eldritch
Knight, Arcane Trickster, Warrior of the Mystic Arts): prepared spells and
spell slots by class level, for their Spellcasting cards."""

from Core.Rules import MAX_LEVEL
from Core.SpellcastingRules import CasterType, get_spell_slots_for_level
from Model.Content.FeatureText import Table

# The Prepared Spells column, as {class level: count from that level on}.
PREPARED_SPELLS_GAINED_AT = {
    3: 3,
    4: 4,
    7: 5,
    8: 6,
    10: 7,
    11: 8,
    13: 9,
    14: 10,
    16: 11,
    19: 12,
    20: 13,
}

FIRST_LEVEL = 3
MAX_SLOT_LEVEL = 4
_ORDINALS = ("1st", "2nd", "3rd", "4th")


def prepared_spells(class_level: int) -> int:
    return max(
        (
            count
            for level, count in PREPARED_SPELLS_GAINED_AT.items()
            if level <= class_level
        ),
        default=0,
    )


def spell_slots(class_level: int) -> tuple[int, ...]:
    """Slots of spell levels 1-4 at a class level."""
    slots = get_spell_slots_for_level(class_level, CasterType.THIRD_CASTER)
    return tuple(slots[:MAX_SLOT_LEVEL])


def spellcasting_table(class_name: str) -> Table:
    """The subclass's Spellcasting table, with consecutive levels that share
    the same prepared spells and slots merged into one row."""
    rows: list[list] = []
    for level in range(FIRST_LEVEL, MAX_LEVEL + 1):
        values = (prepared_spells(level), *spell_slots(level))
        if rows and rows[-1][2] == values:
            rows[-1][1] = level
        else:
            rows.append([level, level, values])
    return Table(
        (f"{class_name} level", "Prepared spells", *_ORDINALS),
        tuple(
            (
                str(start) if start == end else f"{start}-{end}",
                *(str(value) if value else "-" for value in values),
            )
            for start, end, values in rows
        ),
    )
