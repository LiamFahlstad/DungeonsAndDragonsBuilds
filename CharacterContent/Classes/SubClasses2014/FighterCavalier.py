from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import FighterSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Fighter import FighterCavalierFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterCavalierLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterCavalierFeatures.BonusProficiency())
        data.add_feature(FighterCavalierFeatures.BornToTheSaddle())
        data.add_feature(FighterCavalierFeatures.UnwaveringMark())
        return data


@attr.dataclass
class FighterCavalierLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterCavalierFeatures.WardingManeuver())
        return data


@attr.dataclass
class FighterCavalierLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterCavalierFeatures.HoldTheLine())
        return data


@attr.dataclass
class FighterCavalierLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterCavalierFeatures.FerociousCharger())
        return data


@attr.dataclass
class FighterCavalierLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterCavalierFeatures.VigilantDefender())
        return data


class FighterCavalierCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass2014.CAVALIER.value,
            skills=skills,
        )


class FighterCavalierMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.CAVALIER.value,
            replace_spells=replace_spells,
        )
