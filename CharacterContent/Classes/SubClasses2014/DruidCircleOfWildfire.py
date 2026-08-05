from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.DruidBase import (
    DruidMulticlassBuilder,
    DruidCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import DruidSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Druid import DruidWildfireFeatures
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class DruidWildfireLevel3(ClassBuilder.SubclassLevel3):
    """Note: the source text grants Circle Spells and Summon Wildfire Spirit at 2nd level; they are
    folded into this 3rd-level grant because 2014-edition subclasses attach onto the shared,
    2024-unified base-class progression, which selects a subclass at 3rd level."""

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidWildfireFeatures.CircleSpells())
        data.add_feature(DruidWildfireFeatures.SummonWildfireSpirit())
        return data


@attr.dataclass
class DruidWildfireLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidWildfireFeatures.EnhancedBond())
        return data


@attr.dataclass
class DruidWildfireLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidWildfireFeatures.CauterizingFlames())
        return data


@attr.dataclass
class DruidWildfireLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidWildfireFeatures.BlazingRevival())
        return data


class DruidWildfireCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass2014.WILDFIRE.value,
            skills=skills,
        )


class DruidWildfireMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass2014.WILDFIRE.value,
            replace_spells=replace_spells,
        )
