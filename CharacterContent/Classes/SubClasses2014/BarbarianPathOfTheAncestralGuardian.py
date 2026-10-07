from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import BarbarianSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Barbarian import (
    BarbarianPathOfTheAncestralGuardianFeatures,
)
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures


@attr.dataclass
class BarbarianAncestralGuardianLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheAncestralGuardianFeatures.AncestralProtectors(),
            extends=BarbarianFeatures.Rage,
        )


@attr.dataclass
class BarbarianAncestralGuardianLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheAncestralGuardianFeatures.SpiritShield(),
            extends=BarbarianFeatures.Rage,
        )


@attr.dataclass
class BarbarianAncestralGuardianLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheAncestralGuardianFeatures.ConsultTheSpirits()
        )


@attr.dataclass
class BarbarianAncestralGuardianLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheAncestralGuardianFeatures.VengefulAncestors(),
            extends=BarbarianFeatures.Rage,
        )


class BarbarianAncestralGuardianCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass2014.PATH_OF_THE_ANCESTRAL_GUARDIAN.value,
            skills=skills,
        )


class BarbarianAncestralGuardianMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass2014.PATH_OF_THE_ANCESTRAL_GUARDIAN.value,
            replace_spells=replace_spells,
        )
