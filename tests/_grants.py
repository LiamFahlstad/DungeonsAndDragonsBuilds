"""A Grants scope for tests: builders grant through one (Model/Grants.py), so
a test granting a feature or spell to a bare Character does too."""

from Model.Character import Character
from Model.Records.GrantStamp import GrantKind
from Model.Grants import Grants


def grant(
    character: Character,
    level: int = 1,
    granted_by: str = "Test",
    kind: GrantKind = GrantKind.OTHER,
) -> Grants:
    return Grants(character, level, granted_by, kind)


def apply_level(level_builder, character: Character, granted_by: str = "Test") -> None:
    """Run one class or subclass level builder the way ClassBuilder does:
    through a Grants scope stamped with that builder's level."""
    level_builder.add_features(grant(character, level_builder.level, granted_by))
