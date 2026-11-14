from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import BarbarianSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Barbarian import (
    BarbarianPathOfTheSpiritualGuardianFeatures,
)
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures


@attr.dataclass
class BarbarianSpiritualGuardianLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheSpiritualGuardianFeatures.SpiritualProtectors(),
            extends=BarbarianFeatures.Rage,
        )


@attr.dataclass
class BarbarianSpiritualGuardianLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheSpiritualGuardianFeatures.SpiritShield(),
            extends=BarbarianFeatures.Rage,
        )


@attr.dataclass
class BarbarianSpiritualGuardianLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheSpiritualGuardianFeatures.ConsultTheSpirits()
        )


@attr.dataclass
class BarbarianSpiritualGuardianLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BarbarianPathOfTheSpiritualGuardianFeatures.SpiritsFury())


class BarbarianSpiritualGuardianCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass.PATH_OF_THE_SPIRITUAL_GUARDIAN.value,
            skills=skills,
        )


class BarbarianSpiritualGuardianMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass.PATH_OF_THE_SPIRITUAL_GUARDIAN.value,
            replace_spells=replace_spells,
        )
