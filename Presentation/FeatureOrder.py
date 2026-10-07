"""The one order the sheet lists feature cards and nested extensions in -
never the order they were granted in."""

from CharacterContent.Features.Core.BaseFeatures import Feature
from Model.Character import Character
from Model.Sources import GrantedFeature


def feature_sort_key(character: Character, feature: GrantedFeature) -> tuple:
    """Passive last, then by name, then by who granted it (GrantKind order,
    then the source's name)."""
    assert isinstance(feature, Feature)
    stamp = character.stamp_of(feature)
    return (
        feature.skippable_in_concise,
        feature.name,
        stamp.kind.sheet_rank,
        stamp.granted_by,
    )


def ordered_extensions(character: Character, feature: GrantedFeature) -> list[Feature]:
    """The extensions granted onto `feature`, by grant level, then in the
    sheet's order (feature_sort_key)."""

    def by_level_then_sheet_order(extension: Feature) -> tuple:
        level = character.stamp_of(extension).level
        return (level, feature_sort_key(character, extension))

    extensions = []
    for extension in character.extensions_of(feature):
        # The Model holds features as GrantedFeature (Model/Sources.py); an
        # extension of a Feature is always a Feature (Step 9 removes this).
        assert isinstance(extension, Feature)
        extensions.append(extension)
    return sorted(extensions, key=by_level_then_sheet_order)
