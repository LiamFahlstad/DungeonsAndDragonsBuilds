from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import BarbarianSubclass2014, Skill
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures
from CharacterContent.Features.SubClassFeatures2014.Barbarian import (
    BarbarianPathOfTheBattleragerFeatures,
)


@attr.dataclass
class BarbarianBattleragerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BarbarianPathOfTheBattleragerFeatures.BattleragerArmor())


@attr.dataclass
class BarbarianBattleragerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheBattleragerFeatures.RecklessAbandon(),
            extends=BarbarianFeatures.RecklessAttack,
        )


@attr.dataclass
class BarbarianBattleragerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheBattleragerFeatures.BattleragerCharge(),
            extends=BarbarianFeatures.Rage,
        )


@attr.dataclass
class BarbarianBattleragerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheBattleragerFeatures.SpikedRetribution(),
            extends=BarbarianPathOfTheBattleragerFeatures.BattleragerArmor,
        )


class BarbarianBattleragerCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass2014.PATH_OF_THE_BATTLERAGER.value,
            skills=skills,
        )


class BarbarianBattleragerMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass2014.PATH_OF_THE_BATTLERAGER.value,
            replace_spells=replace_spells,
        )
