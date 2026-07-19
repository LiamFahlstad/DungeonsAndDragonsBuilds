from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import FighterSubclass
from Features.SubClassFeatures.Fighter import FighterPsiWarriorFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterPsiWarriorLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.PsionicPower())
        return data


@attr.dataclass
class FighterPsiWarriorLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.TelekineticAdept())
        return data


@attr.dataclass
class FighterPsiWarriorLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.GuardedMind())
        return data


@attr.dataclass
class FighterPsiWarriorLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.BulwarkofForce())
        return data


@attr.dataclass
class FighterPsiWarriorLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.TelekineticMaster())
        return data


class FighterPsiWarriorCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass.PSI_WARRIOR.value,
            skills=skills,
        )


class FighterPsiWarriorMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.PSI_WARRIOR.value,
            replace_spells=replace_spells,
        )
