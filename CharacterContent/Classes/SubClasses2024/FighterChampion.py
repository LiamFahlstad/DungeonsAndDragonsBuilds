from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import FighterSubclass
from CharacterContent.Features.SubClassFeatures.Fighter import FighterChampionFeatures
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterChampionLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterChampionFeatures.ImprovedCritical())
        data.add_feature(FighterChampionFeatures.RemarkableAthlete())
        return data


@attr.dataclass
class FighterChampionLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        fighting_style: FighterFeatures.FightingStyle = data.get_features_by_type(
            FighterFeatures.FightingStyle
        )[0]
        fighting_style.extend_feature(FighterChampionFeatures.AdditionalFightingStyle())
        return data


@attr.dataclass
class FighterChampionLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterChampionFeatures.HeroicWarrior())
        return data


@attr.dataclass
class FighterChampionLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        improved_critical: FighterChampionFeatures.ImprovedCritical = (
            data.get_features_by_type(FighterChampionFeatures.ImprovedCritical)[0]
        )
        improved_critical.extend_feature(FighterChampionFeatures.SuperiorCritical())
        return data


@attr.dataclass
class FighterChampionLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterChampionFeatures.Survivor())
        return data


class FighterChampionCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass.CHAMPION.value,
            skills=skills,
        )


class FighterChampionMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.CHAMPION.value,
            replace_spells=replace_spells,
        )
