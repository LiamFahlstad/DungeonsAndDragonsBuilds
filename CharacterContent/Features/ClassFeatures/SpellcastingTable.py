"""The cantrips/prepared-spells track on a spellcasting class's Spellcasting
card. Level pages are printed once and kept, so the card shows the whole
progression rather than today's counts; the slots are left to the sheet's
spell-slot grid."""

from Core.Rules import MAX_LEVEL
from Model.Content.FeatureText import LevelTrack


def spellcasting_table(
    class_name: str,
    prepared: tuple[int, ...],
    cantrips: tuple[int, ...] | None = None,
) -> LevelTrack:
    """`prepared` and `cantrips` are the class table's Prepared Spells and
    Cantrips columns, one count per class level 1-20 (no `cantrips` for a
    class without them, e.g. Ranger)."""
    series = [] if cantrips is None else [("Cantrips", cantrips)]
    series.append(("Prepared spells", prepared))
    for label, values in series:
        if len(values) != MAX_LEVEL:
            raise ValueError(
                f"{class_name} {label} has {len(values)} levels, expected {MAX_LEVEL}"
            )
    return LevelTrack(
        f"{class_name} level",
        tuple(
            (label, tuple(str(value) for value in values)) for label, values in series
        ),
    )
