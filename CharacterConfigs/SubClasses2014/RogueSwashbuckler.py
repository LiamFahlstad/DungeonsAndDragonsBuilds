from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import RogueSubclass2014
from Features.SubClassFeatures2014.Rogue import RogueSwashbucklerFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueSwashbucklerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSwashbucklerFeatures.FancyFootwork())
        data.add_feature(RogueSwashbucklerFeatures.RakishAudacity())
        return data


@attr.dataclass
class RogueSwashbucklerLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSwashbucklerFeatures.Panache())
        return data


@attr.dataclass
class RogueSwashbucklerLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSwashbucklerFeatures.ElegantManeuver())
        return data


@attr.dataclass
class RogueSwashbucklerLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSwashbucklerFeatures.MasterDuelist())
        return data


class RogueSwashbucklerCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass2014.SWASHBUCKLER.value,
            skills=skills,
        )


class RogueSwashbucklerMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass2014.SWASHBUCKLER.value,
            replace_spells=replace_spells,
        )
