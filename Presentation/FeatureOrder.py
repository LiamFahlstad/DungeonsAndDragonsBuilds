"""The one order the sheet lists feature cards and nested extensions in -
never the order they were granted in."""

from Model.Character import Character
from Model.Content.Feature import Feature


def feature_sort_key(character: Character, feature: Feature) -> tuple:
    """Passive last, then by name, then by who granted it (GrantKind order,
    then the source's name)."""
    stamp = character.stamp_of(feature)
    return (
        feature.skippable_in_concise,
        feature.name,
        stamp.kind.sheet_rank,
        stamp.granted_by,
    )


def ordered_extensions(character: Character, feature: Feature) -> list[Feature]:
    """The extensions granted onto `feature`, by grant level, then in the
    sheet's order (feature_sort_key)."""

    def by_level_then_sheet_order(extension: Feature) -> tuple:
        level = character.stamp_of(extension).level
        return (level, feature_sort_key(character, extension))

    return sorted(character.extensions_of(feature), key=by_level_then_sheet_order)
