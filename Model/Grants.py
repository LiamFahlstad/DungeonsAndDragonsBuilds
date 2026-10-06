"""Grants: what a builder grants through.

A class level or a species doesn't hand its grants to the Character directly:
it gets a Grants scope wrapping the Character, which stamps every feature
and spell with where the builder is - the class-relative level it's granted
at, the kind of source (species, background, class, ...) and which one
("Wizard", "Rock Gnome"). So that bookkeeping lives with the
builder, never as state on the Character, and every grant carries its own
level and origin instead of depending on what was granted before it.

The surface is exactly what level and species builders do. Anything else
(stat queries, evaluation) belongs to the Character, not to a builder.
"""

from typing import Literal, Optional

import Core.Definitions as Definitions
from Core.Definitions import Ability
from Model.Character import Character, GrantKind
from Model.Sources import Effect, Gear, GrantedFeature


class Grants:
    def __init__(
        self,
        character: Character,
        level: int,
        granted_by: str,
        kind: GrantKind = "other",
    ):
        self.character = character
        self.level = level
        self.granted_by = granted_by
        self.kind: GrantKind = kind

    # -- Features ---------------------------------------------------------------

    def add_feature(
        self,
        feature: GrantedFeature,
        extends: type | GrantedFeature | None = None,
        if_missing: Literal["error", "drop", "standalone"] = "error",
        kind: Optional[GrantKind] = None,
        granted_by: Optional[str] = None,
    ) -> None:
        """Stamped with this scope's level, kind and grant; `kind` and
        `granted_by` override them (an origin feat a species grants is still
        an origin feat)."""
        self.character.add_feature(
            feature,
            extends=extends,
            if_missing=if_missing,
            level=self.level,
            kind=kind or self.kind,
            granted_by=granted_by or self.granted_by,
        )

    def add_fighting_style(self, fighting_style: Effect) -> None:
        self.character.add_fighting_style(fighting_style)

    def add_weapon_mastery(self, weapon: Gear) -> None:
        self.character.add_weapon_mastery(weapon)

    def add_invocation(self, invocation: str) -> None:
        self.character.add_invocation(invocation)

    # -- Spells: stamped with this scope's level and grant -------------------------

    def add_spell(
        self,
        spell: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
        granted_by: Optional[str] = None,
    ) -> None:
        """`granted_by` overrides this scope's (an origin feat granted by a
        species lists its spells under the feat)."""
        self.character.add_spell(
            spell,
            spell_casting_ability,
            additional_ruling,
            source=source,
            grant_level=self.level,
            granted_by=granted_by or self.granted_by,
        )

    def add_cantrip(
        self,
        cantrip: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
        granted_by: Optional[str] = None,
    ) -> None:
        self.add_spell(
            cantrip,
            spell_casting_ability,
            additional_ruling,
            source=source,
            granted_by=granted_by,
        )

    # -- What a species sets -----------------------------------------------------

    @property
    def base_speed(self) -> Optional[int]:
        return self.character.base_speed

    @base_speed.setter
    def base_speed(self, value: int) -> None:
        self.character.base_speed = value

    @property
    def size(self) -> Optional[Definitions.CreatureSize]:
        return self.character.size

    @size.setter
    def size(self, value: Definitions.CreatureSize) -> None:
        self.character.size = value
