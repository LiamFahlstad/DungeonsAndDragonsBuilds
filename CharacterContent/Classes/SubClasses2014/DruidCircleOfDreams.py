from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.DruidBase import (
    DruidMulticlassBuilder,
    DruidCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import DruidSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Druid import DruidDreamsFeatures
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class DruidDreamsLevel3(ClassBuilder.SubclassLevel3):
    """Note: the source text grants Balm of the Summer Court at 2nd level; it is folded into this
    3rd-level grant because 2014-edition subclasses attach onto the shared, 2024-unified base-class
    progression, which selects a subclass at 3rd level."""

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidDreamsFeatures.BalmOfTheSummerCourt())
        return data


@attr.dataclass
class DruidDreamsLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidDreamsFeatures.HearthOfMoonlightAndShadow())
        return data


@attr.dataclass
class DruidDreamsLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidDreamsFeatures.HiddenPaths())
        return data


@attr.dataclass
class DruidDreamsLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidDreamsFeatures.WalkerInDreams())
        return data


class DruidDreamsCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass2014.DREAMS.value,
            skills=skills,
        )


class DruidDreamsMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass2014.DREAMS.value,
            replace_spells=replace_spells,
        )
