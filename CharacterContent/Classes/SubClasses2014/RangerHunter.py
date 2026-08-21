from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import RangerSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Ranger import RangerHunterFeatures
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class VolleyChoice:
    pass


@attr.dataclass
class WhirlwindAttackChoice:
    pass


@attr.dataclass
class RangerHunterLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHunterFeatures.HuntersPrey())
        return data


@attr.dataclass
class RangerHunterLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHunterFeatures.DefensiveTactics())
        return data


@attr.dataclass
class RangerHunterLevel11(ClassBuilder.SubclassLevel11):
    multiattack: VolleyChoice | WhirlwindAttackChoice

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        if isinstance(self.multiattack, WhirlwindAttackChoice):
            data.add_feature(RangerHunterFeatures.WhirlwindAttack())
        else:
            data.add_feature(RangerHunterFeatures.Volley())
        return data


@attr.dataclass
class RangerHunterLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHunterFeatures.SuperiorHuntersDefense())
        return data


class RangerHunterCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass2014.HUNTER.value,
            skills=skills,
        )


class RangerHunterMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass2014.HUNTER.value,
            replace_spells=replace_spells,
        )
