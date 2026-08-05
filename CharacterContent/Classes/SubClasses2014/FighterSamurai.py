from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import FighterSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Fighter import FighterSamuraiFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterSamuraiLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterSamuraiFeatures.BonusProficiency())
        data.add_feature(FighterSamuraiFeatures.FightingSpirit())
        return data


@attr.dataclass
class FighterSamuraiLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterSamuraiFeatures.ElegantCourtier())
        return data


@attr.dataclass
class FighterSamuraiLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterSamuraiFeatures.TirelessSpirit())
        return data


@attr.dataclass
class FighterSamuraiLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterSamuraiFeatures.RapidStrike())
        return data


@attr.dataclass
class FighterSamuraiLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterSamuraiFeatures.StrengthBeforeDeath())
        return data


class FighterSamuraiCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass2014.SAMURAI.value,
            skills=skills,
        )


class FighterSamuraiMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.SAMURAI.value,
            replace_spells=replace_spells,
        )
