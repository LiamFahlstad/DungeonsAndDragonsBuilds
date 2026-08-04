from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import FighterSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Fighter import FighterEchoKnightFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterEchoKnightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEchoKnightFeatures.ManifestEcho())
        data.add_feature(FighterEchoKnightFeatures.UnleashIncarnation())
        return data


@attr.dataclass
class FighterEchoKnightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEchoKnightFeatures.EchoAvatar())
        return data


@attr.dataclass
class FighterEchoKnightLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEchoKnightFeatures.ShadowMartyr())
        return data


@attr.dataclass
class FighterEchoKnightLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEchoKnightFeatures.ReclaimPotential())
        return data


@attr.dataclass
class FighterEchoKnightLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEchoKnightFeatures.LegionOfOne())
        return data


class FighterEchoKnightCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass2014.ECHO_KNIGHT.value,
            skills=skills,
        )


class FighterEchoKnightMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.ECHO_KNIGHT.value,
            replace_spells=replace_spells,
        )
