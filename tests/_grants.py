"""A Grants scope for tests: builders grant through one (Model/Grants.py), so
a test granting a feature or spell to bare CharacterSources does too."""

from Model.CharacterSources import CharacterSources
from Model.Grants import Grants
from Model.Records.GrantStamp import GrantKind


def grant(
    sources: CharacterSources,
    level: int = 1,
    granted_by: str = "Test",
    kind: GrantKind = GrantKind.OTHER,
) -> Grants:
    return Grants(sources, level, granted_by, kind)


def apply_level(
    level_builder, sources: CharacterSources, granted_by: str = "Test"
) -> None:
    """Run one class or subclass level builder the way ClassBuilder does:
    through a Grants scope stamped with that builder's level."""
    level_builder.add_features(grant(sources, level_builder.level, granted_by))
