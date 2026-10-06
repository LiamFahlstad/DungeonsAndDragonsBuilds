from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import FighterSubclass, Skill
from CharacterContent.Features.CombatFeatures import Maneuvers
from CharacterContent.Features.SubClassFeatures.Fighter import (
    FighterBattleMasterFeatures,
)


@attr.dataclass
class FighterBattleMasterLevel3(ClassBuilder.SubclassLevel3):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver
    maneuver_3: Maneuvers.Maneuver

    def add_features(
        self,
        data: Grants,
    ) -> None:
        superiority_dice = FighterBattleMasterFeatures.SuperiorityDice()
        data.add_feature(self.maneuver_1, extends=superiority_dice)
        data.add_feature(self.maneuver_2, extends=superiority_dice)
        data.add_feature(self.maneuver_3, extends=superiority_dice)
        data.add_feature(superiority_dice)
        data.add_feature(FighterBattleMasterFeatures.StudentOfWar())


@attr.dataclass
class FighterBattleMasterLevel7(ClassBuilder.SubclassLevel7):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            self.maneuver_1, extends=FighterBattleMasterFeatures.SuperiorityDice
        )
        data.add_feature(
            self.maneuver_2, extends=FighterBattleMasterFeatures.SuperiorityDice
        )
        data.add_feature(FighterBattleMasterFeatures.KnowYourEnemy())


@attr.dataclass
class FighterBattleMasterLevel10(ClassBuilder.SubclassLevel10):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            self.maneuver_1, extends=FighterBattleMasterFeatures.SuperiorityDice
        )
        data.add_feature(
            self.maneuver_2, extends=FighterBattleMasterFeatures.SuperiorityDice
        )
        data.add_feature(
            FighterBattleMasterFeatures.ImprovedCombatSuperiority(),
            extends=FighterBattleMasterFeatures.SuperiorityDice,
        )


@attr.dataclass
class FighterBattleMasterLevel15(ClassBuilder.SubclassLevel15):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            self.maneuver_1, extends=FighterBattleMasterFeatures.SuperiorityDice
        )
        data.add_feature(
            self.maneuver_2, extends=FighterBattleMasterFeatures.SuperiorityDice
        )
        data.add_feature(
            FighterBattleMasterFeatures.Relentless(),
            extends=FighterBattleMasterFeatures.SuperiorityDice,
        )


@attr.dataclass
class FighterBattleMasterLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterBattleMasterFeatures.UltimateCombatSuperiority(),
            extends=FighterBattleMasterFeatures.SuperiorityDice,
        )


class FighterBattleMasterCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
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
