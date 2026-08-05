from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import Ability, MonkSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Monk import MonkLongDeathFeatures
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkLongDeathLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkLongDeathFeatures.TouchOfDeath())
        return data


@attr.dataclass
class MonkLongDeathLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkLongDeathFeatures.HourOfReaping())
        return data


@attr.dataclass
class MonkLongDeathLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkLongDeathFeatures.MasteryOfDeath())
        return data


@attr.dataclass
class MonkLongDeathLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkLongDeathFeatures.TouchOfTheLongDeath())
        return data


class MonkLongDeathCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: MonkSkillsStatBlock,
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass2014.LONG_DEATH.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkLongDeathMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass2014.LONG_DEATH.value,
            replace_spells=replace_spells,
        )
