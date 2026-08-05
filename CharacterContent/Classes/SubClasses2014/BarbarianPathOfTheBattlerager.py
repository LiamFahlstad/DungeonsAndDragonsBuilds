from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import BarbarianSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Barbarian import BarbarianPathOfTheBattleragerFeatures
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


@attr.dataclass
class BarbarianBattleragerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheBattleragerFeatures.BattleragerArmor())
        return data


@attr.dataclass
class BarbarianBattleragerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheBattleragerFeatures.RecklessAbandon())
        return data


@attr.dataclass
class BarbarianBattleragerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheBattleragerFeatures.BattleragerCharge())
        return data


@attr.dataclass
class BarbarianBattleragerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheBattleragerFeatures.SpikedRetribution())
        return data


class BarbarianBattleragerCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: BarbarianSkillsStatBlock,
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
