from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import ClericSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericOrderFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericOrderLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericOrderFeatures.BonusProficiencies())
        data.add_feature(ClericOrderFeatures.VoiceOfAuthority())
        data.add_feature(ClericOrderFeatures.OrderDomainSpells())
        data.add_feature(ClericOrderFeatures.OrdersDemandChannelDivinity())
        return data


@attr.dataclass
class ClericOrderLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericOrderFeatures.EmbodimentOfTheLaw())
        return data


@attr.dataclass
class ClericOrderLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericOrderFeatures.DivineStrike())
        return data


@attr.dataclass
class ClericOrderLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericOrderFeatures.OrdersWrath())
        return data


class ClericOrderCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.ORDER.value,
            skills=skills,
        )


class ClericOrderMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.ORDER.value,
            replace_spells=replace_spells,
        )
