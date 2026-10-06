from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import BarbarianSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Barbarian import (
    BarbarianPathOfTheZealotFeatures,
)
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures


@attr.dataclass
class BarbarianZealotLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheZealotFeatures.DivineFury(),
            extends=BarbarianFeatures.Rage,
        )
        data.add_feature(BarbarianPathOfTheZealotFeatures.WarriorOfTheGods())


@attr.dataclass
class BarbarianZealotLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheZealotFeatures.FanaticalFocus(),
            extends=BarbarianFeatures.Rage,
        )


@attr.dataclass
class BarbarianZealotLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BarbarianPathOfTheZealotFeatures.ZealousPresence())


@attr.dataclass
class BarbarianZealotLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheZealotFeatures.RageOfTheGods(),
            extends=BarbarianFeatures.Rage,
        )


class BarbarianZealotCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass.PATH_OF_THE_ZEALOT.value,
            skills=skills,
        )


class BarbarianZealotMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass.PATH_OF_THE_ZEALOT.value,
            replace_spells=replace_spells,
        )
