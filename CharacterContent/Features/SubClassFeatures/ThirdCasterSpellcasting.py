"""The spellcasting table shared by the 2024 one-third casters (Eldritch
Knight, Arcane Trickster, Warrior of the Mystic Arts): prepared spells and
spell slots by class level, for their Spellcasting cards."""

from Core.Rules import MAX_LEVEL
from Core.SpellcastingRules import CasterType, get_spell_slots_for_level
from Model.Content.FeatureText import LevelTrack

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


def spellcasting_table(class_name: str) -> LevelTrack:
    """The subclass's Spellcasting table as a level track: prepared spells
    and each slot level's count, from its first level to 20."""
    levels = range(FIRST_LEVEL, MAX_LEVEL + 1)
    slots = [spell_slots(level) for level in levels]
    return LevelTrack(
        f"{class_name} level",
        (
            ("Prepared spells", tuple(str(prepared_spells(level)) for level in levels)),
            *(
                (
                    f"{ordinal} slots",
                    tuple(str(row[index]) if row[index] else "-" for row in slots),
                )
                for index, ordinal in enumerate(_ORDINALS)
            ),
        ),
        first_level=FIRST_LEVEL,
    )
