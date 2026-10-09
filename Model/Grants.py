"""Grants: what a builder grants through.

A class level or a species doesn't write its grants into the CharacterSources
directly: it gets a Grants scope wrapping them, which stamps every feature
and spell with where the builder is - the class-relative level it's granted
at, the kind of source (species, background, class, ...) and which one
("Wizard", "Rock Gnome"). So that bookkeeping lives with the
builder, never as state on the Character, and every grant carries its own
level and origin instead of depending on what was granted before it.

The surface is exactly what level and species builders do. Anything else
(stat queries, evaluation) belongs to the Character, not to a builder.
"""

from typing import Optional

import Core.Definitions as Definitions
from Core.Definitions import Ability
from Model.CharacterSources import CharacterSources
from Model.FeatureGrants import IfParentMissing
from Model.Records.GrantStamp import GrantKind, GrantStamp
from Model.Content.Feature import Feature
from Model.Content.Weapon import AbstractWeapon
from Model.Content.FightingStyle import FightingStyle


class Grants:
    def __init__(
        self,
        sources: CharacterSources,
        level: int,
        granted_by: str,
        kind: GrantKind = GrantKind.OTHER,
    ):
        self.sources = sources
        self.level = level
        self.granted_by = granted_by
        self.kind: GrantKind = kind

    def for_origin_feat(self, feat: Feature) -> "Grants":
        """The scope an origin feat grants through, at this scope's level: the
        feat and its spells are listed under the feat, whether a background or
        a species (a Human's Versatile) grants it."""
        return Grants(self.sources, self.level, feat.name, GrantKind.ORIGIN_FEAT)

    # -- Features ---------------------------------------------------------------

    def add_feature(
        self,
        feature: Feature,
        extends: type | Feature | None = None,
        if_missing: IfParentMissing = IfParentMissing.ERROR,
    ) -> None:
        """Stamped with this scope's level, kind and grant."""
        self.sources.add_feature(
            feature,
            stamp=GrantStamp(self.level, self.kind, self.granted_by),
            extends=extends,
            if_missing=if_missing,
        )

    def add_fighting_style(self, fighting_style: FightingStyle) -> None:
        self.sources.add_fighting_style(fighting_style)

    def add_weapon_mastery(self, weapon: AbstractWeapon) -> None:
        self.sources.add_weapon_mastery(weapon)

    def add_invocation(self, invocation: str) -> None:
        self.sources.add_invocation(invocation)

    # -- Spells: stamped with this scope's level and grant -------------------------

    def add_spell(
        self,
        spell: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        self.sources.add_spell(
            spell,
            spell_casting_ability,
            additional_ruling,
            source,
            stamp=GrantStamp(self.level, self.kind, self.granted_by),
        )

    def add_cantrip(
        self,
        cantrip: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        self.add_spell(cantrip, spell_casting_ability, additional_ruling, source)

    # -- What a species sets -----------------------------------------------------

    @property
    def base_speed(self) -> Optional[int]:
        return self.sources.base_speed

    @base_speed.setter
    def base_speed(self, value: int) -> None:
        self.sources.base_speed = value

    @property
    def size(self) -> Optional[Definitions.CreatureSize]:
        return self.sources.size

    @size.setter
    def size(self, value: Definitions.CreatureSize) -> None:
        self.sources.size = value
