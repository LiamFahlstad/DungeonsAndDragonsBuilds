from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RangerSubclass
from Features.ClassFeatures import RangerFeatures
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class HunterRangerLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.HuntersLore())
        data.add_feature(RangerFeatures.HuntersPrey())
        return data


@attr.dataclass
class HunterRangerLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.DefensiveTactics())
        return data


@attr.dataclass
class HunterRangerLevel11(ClassBuilder.SubclassLevel11):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.SuperiorHuntersPrey())
        return data


@attr.dataclass
class HunterRangerLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.SuperiorHuntersDefense())
        return data


class RangerHunterCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass.HUNTER.value,
            skills=skills,
        )


class HunterRangerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.HUNTER.value,
            replace_spells=replace_spells,
        )
