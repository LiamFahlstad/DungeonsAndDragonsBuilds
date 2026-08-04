from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import BarbarianStormEnvironment, BarbarianSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Barbarian import BarbarianPathOfTheStormHeraldFeatures
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


@attr.dataclass
class BarbarianStormHeraldLevel3(ClassBuilder.SubclassLevel3):
    environment: BarbarianStormEnvironment

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheStormHeraldFeatures.StormAura(environment=self.environment))
        return data


@attr.dataclass
class BarbarianStormHeraldLevel6(ClassBuilder.SubclassLevel6):
    environment: BarbarianStormEnvironment

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheStormHeraldFeatures.StormSoul(environment=self.environment))
        return data


@attr.dataclass
class BarbarianStormHeraldLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheStormHeraldFeatures.ShieldingStorm())
        return data


@attr.dataclass
class BarbarianStormHeraldLevel14(ClassBuilder.SubclassLevel14):
    environment: BarbarianStormEnvironment

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheStormHeraldFeatures.RagingStorm(environment=self.environment))
        return data


class BarbarianStormHeraldCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: BarbarianSkillsStatBlock,
    ):
        super().__init__(
            subclass=BarbarianSubclass2014.PATH_OF_THE_STORM_HERALD.value,
            skills=skills,
        )


class BarbarianStormHeraldMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass2014.PATH_OF_THE_STORM_HERALD.value,
            replace_spells=replace_spells,
        )
