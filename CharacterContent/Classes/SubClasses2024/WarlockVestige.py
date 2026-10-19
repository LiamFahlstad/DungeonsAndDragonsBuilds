from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import (
    Skill,
    WarlockSubclass,
    WarlockVestigeDomain,
    WarlockVestigeType,
)
from CharacterContent.Features.SubClassFeatures.Warlock import WarlockVestigeFeatures
from CharacterContent.Features.SubClassFeatures.Warlock.WarlockVestigeFeatures import (
    VESTIGE_DOMAIN_SPELLS,
)


def _add_domain_spells(data: Grants, domain: WarlockVestigeDomain, level: int) -> None:
    for spell in VESTIGE_DOMAIN_SPELLS[domain][level]:
        data.add_spell(spell, source="Vestige Spells")


@attr.dataclass
class WarlockVestigeLevel3(ClassBuilder.SubclassLevel3):
    vestige_type: WarlockVestigeType
    domain: WarlockVestigeDomain

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WarlockVestigeFeatures.VestigeCompanion(self.vestige_type))
        data.add_feature(WarlockVestigeFeatures.VestigeSpells(self.domain))
        _add_domain_spells(data, self.domain, 3)


@attr.dataclass
class WarlockVestigeLevel5(ClassBuilder.SubclassLevel5):
    domain: WarlockVestigeDomain

    def add_features(
        self,
        data: Grants,
    ) -> None:
        _add_domain_spells(data, self.domain, 5)


@attr.dataclass
class WarlockVestigeLevel6(ClassBuilder.SubclassLevel6):
    vestige_type: WarlockVestigeType

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            WarlockVestigeFeatures.VestigePower(self.vestige_type),
            extends=WarlockVestigeFeatures.VestigeCompanion,
        )


@attr.dataclass
class WarlockVestigeLevel7(ClassBuilder.SubclassLevel7):
    domain: WarlockVestigeDomain

    def add_features(
        self,
        data: Grants,
    ) -> None:
        _add_domain_spells(data, self.domain, 7)


@attr.dataclass
class WarlockVestigeLevel9(ClassBuilder.SubclassLevel9):
    domain: WarlockVestigeDomain

    def add_features(
        self,
        data: Grants,
    ) -> None:
        _add_domain_spells(data, self.domain, 9)


@attr.dataclass
class WarlockVestigeLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WarlockVestigeFeatures.VestigeRecovery())


@attr.dataclass
class WarlockVestigeLevel14(ClassBuilder.SubclassLevel14):
    vestige_type: WarlockVestigeType

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WarlockVestigeFeatures.SemblanceOfLife(self.vestige_type))


class WarlockVestigeCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_VESTIGE.value,
            skills=skills,
        )


class WarlockVestigeMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_VESTIGE.value,
            replace_spells=replace_spells,
        )
