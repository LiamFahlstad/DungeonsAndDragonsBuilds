from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import FighterSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Fighter import FighterArcaneArcherFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterArcaneArcherLevel3(ClassBuilder.SubclassLevel3):
    skill: Skill
    cantrip: str

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterArcaneArcherFeatures.ArcaneArcherLore(self.skill, self.cantrip))
        data.add_feature(FighterArcaneArcherFeatures.ArcaneShot())
        return data


@attr.dataclass
class FighterArcaneArcherLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterArcaneArcherFeatures.MagicArrow())
        data.add_feature(FighterArcaneArcherFeatures.CurvingShot())
        return data


@attr.dataclass
class FighterArcaneArcherLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        arcane_shot: FighterArcaneArcherFeatures.ArcaneShot = data.get_features_by_type(
            FighterArcaneArcherFeatures.ArcaneShot
        )[0]
        arcane_shot.extend_feature(FighterArcaneArcherFeatures.EverReadyShot())
        return data


class FighterArcaneArcherCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass2014.ARCANE_ARCHER.value,
            skills=skills,
        )


class FighterArcaneArcherMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.ARCANE_ARCHER.value,
            replace_spells=replace_spells,
        )
