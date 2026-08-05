from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.DruidBase import (
    DruidMulticlassBuilder,
    DruidCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import DruidSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Druid import DruidShepherdFeatures
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class DruidShepherdLevel3(ClassBuilder.SubclassLevel3):
    """Note: the source text grants Speech of the Woods and Spirit Totem at 2nd level; they are
    folded into this 3rd-level grant because 2014-edition subclasses attach onto the shared,
    2024-unified base-class progression, which selects a subclass at 3rd level."""

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidShepherdFeatures.SpeechOfTheWoods())
        data.add_feature(DruidShepherdFeatures.SpiritTotem())
        return data


@attr.dataclass
class DruidShepherdLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidShepherdFeatures.MightySummoner())
        return data


@attr.dataclass
class DruidShepherdLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidShepherdFeatures.GuardianSpirit())
        return data


@attr.dataclass
class DruidShepherdLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidShepherdFeatures.FaithfulSummons())
        return data


class DruidShepherdCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass2014.SHEPHERD.value,
            skills=skills,
        )


class DruidShepherdMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass2014.SHEPHERD.value,
            replace_spells=replace_spells,
        )
