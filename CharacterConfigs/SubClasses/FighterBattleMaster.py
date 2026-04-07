from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterNonGenericStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import FighterSubclass
from Features import Maneuvers
from Features.ClassFeatures import FighterFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterBattleMasterLevel3(ClassBuilder.SubclassLevel3):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver
    maneuver_3: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice = FighterFeatures.SuperiorityDice()
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        superiority_dice.add_feature(self.maneuver_3)
        data.add_feature(superiority_dice)
        data.add_feature(FighterFeatures.StudentOfWar())
        return data


@attr.dataclass
class FighterBattleMasterLevel7(ClassBuilder.SubclassLevel7):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice: FighterFeatures.SuperiorityDice = data.get_features_by_type(
            FighterFeatures.SuperiorityDice
        )[0]
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        data.add_feature(FighterFeatures.KnowYourEnemy())
        return data


@attr.dataclass
class FighterBattleMasterLevel10(ClassBuilder.SubclassLevel10):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice: FighterFeatures.SuperiorityDice = data.get_features_by_type(
            FighterFeatures.SuperiorityDice
        )[0]
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        return data


@attr.dataclass
class FighterBattleMasterLevel15(ClassBuilder.SubclassLevel15):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice: FighterFeatures.SuperiorityDice = data.get_features_by_type(
            FighterFeatures.SuperiorityDice
        )[0]
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        superiority_dice.add_feature(FighterFeatures.Relentless())
        return data


@attr.dataclass
class FighterBattleMasterLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


class FighterBattleMasterNonGenericStarterClassArgs(FighterNonGenericStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass.BATTLE_MASTER.value,
            skills=skills,
        )


class FighterBattleMasterMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.BATTLE_MASTER.value,
            replace_spells=replace_spells,
        )
