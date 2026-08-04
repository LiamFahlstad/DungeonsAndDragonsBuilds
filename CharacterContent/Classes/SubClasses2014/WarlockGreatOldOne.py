from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WarlockSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Warlock import WarlockGreatOldOneFeatures
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class WarlockGreatOldOneLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.GreatOldOneExpandedSpells())
        data.add_feature(WarlockGreatOldOneFeatures.AwakenedMind())
        return data


@attr.dataclass
class WarlockGreatOldOneLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.EntropicWard())
        return data


@attr.dataclass
class WarlockGreatOldOneLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.ThoughtShield())
        return data


@attr.dataclass
class WarlockGreatOldOneLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.CreateThrall())
        return data


class WarlockGreatOldOneCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass2014.THE_GREAT_OLD_ONE.value,
            skills=skills,
        )


class WarlockGreatOldOneMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass2014.THE_GREAT_OLD_ONE.value,
            replace_spells=replace_spells,
        )
