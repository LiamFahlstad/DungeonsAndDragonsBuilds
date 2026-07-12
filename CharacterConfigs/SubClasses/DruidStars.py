from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidCustomStarterClassArgs,
    DruidMulticlassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import DruidSubclass
from Features.ClassFeatures.Druid import DruidStarsFeatures
from Spells.Definitions import DruidLevel0Spells, EvocationLevel1Spells
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class DruidStarsLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidStarsFeatures.StarMap())
        data.add_feature(DruidStarsFeatures.StarryForm())
        data.add_spell(DruidLevel0Spells.GUIDANCE)
        data.add_spell(EvocationLevel1Spells.GUIDING_BOLT)
        return data


@attr.dataclass
class DruidStarsLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidStarsFeatures.CosmicOmen())
        return data


@attr.dataclass
class DruidStarsLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidStarsFeatures.TwinklingConstellations())
        return data


@attr.dataclass
class DruidStarsLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidStarsFeatures.FullOfStars())
        return data


class DruidStarsCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass.STARS.value,
            skills=skills,
        )


class DruidStarsMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass.STARS.value,
            replace_spells=replace_spells,
        )
