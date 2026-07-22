from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import FighterSubclass2014
from Features.Combat import Maneuvers
from Features.SubClassFeatures2014.Fighter import FighterBattleMasterFeatures
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
        combat_superiority = FighterBattleMasterFeatures.CombatSuperiority()
        combat_superiority.extend_feature(self.maneuver_1)
        combat_superiority.extend_feature(self.maneuver_2)
        combat_superiority.extend_feature(self.maneuver_3)
        data.add_feature(combat_superiority)
        data.add_feature(FighterBattleMasterFeatures.StudentOfWar())
        return data


@attr.dataclass
class FighterBattleMasterLevel7(ClassBuilder.SubclassLevel7):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        combat_superiority: FighterBattleMasterFeatures.CombatSuperiority = data.get_features_by_type(
            FighterBattleMasterFeatures.CombatSuperiority
        )[0]
        combat_superiority.extend_feature(self.maneuver_1)
        combat_superiority.extend_feature(self.maneuver_2)
        data.add_feature(FighterBattleMasterFeatures.KnowYourEnemy())
        return data


@attr.dataclass
class FighterBattleMasterLevel10(ClassBuilder.SubclassLevel10):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        combat_superiority: FighterBattleMasterFeatures.CombatSuperiority = data.get_features_by_type(
            FighterBattleMasterFeatures.CombatSuperiority
        )[0]
        combat_superiority.extend_feature(self.maneuver_1)
        combat_superiority.extend_feature(self.maneuver_2)
        data.add_feature(FighterBattleMasterFeatures.ImprovedCombatSuperiority())
        return data


@attr.dataclass
class FighterBattleMasterLevel15(ClassBuilder.SubclassLevel15):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        combat_superiority: FighterBattleMasterFeatures.CombatSuperiority = data.get_features_by_type(
            FighterBattleMasterFeatures.CombatSuperiority
        )[0]
        combat_superiority.extend_feature(self.maneuver_1)
        combat_superiority.extend_feature(self.maneuver_2)
        combat_superiority.extend_feature(FighterBattleMasterFeatures.Relentless())
        return data


@attr.dataclass
class FighterBattleMasterLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterBattleMasterFeatures.GreaterCombatSuperiority())
        return data


class FighterBattleMasterCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass2014.BATTLE_MASTER.value,
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
            subclass=FighterSubclass2014.BATTLE_MASTER.value,
            replace_spells=replace_spells,
        )
