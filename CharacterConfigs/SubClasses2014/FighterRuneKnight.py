from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import FighterSubclass2014
from Features.SubClassFeatures2014.Fighter import FighterRuneKnightFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterRuneKnightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterRuneKnightFeatures.BonusProficiencies())
        data.add_feature(FighterRuneKnightFeatures.RuneCarver())
        data.add_feature(FighterRuneKnightFeatures.GiantsMight())
        return data


@attr.dataclass
class FighterRuneKnightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterRuneKnightFeatures.RunicShield())
        return data


@attr.dataclass
class FighterRuneKnightLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterRuneKnightFeatures.GreatStature())
        return data


@attr.dataclass
class FighterRuneKnightLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterRuneKnightFeatures.MasterOfRunes())
        return data


@attr.dataclass
class FighterRuneKnightLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterRuneKnightFeatures.RunicJuggernaut())
        return data


class FighterRuneKnightCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass2014.RUNE_KNIGHT.value,
            skills=skills,
        )


class FighterRuneKnightMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.RUNE_KNIGHT.value,
            replace_spells=replace_spells,
        )
