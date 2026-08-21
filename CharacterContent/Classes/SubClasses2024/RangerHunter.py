from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import RangerSubclass
from CharacterContent.Features.SubClassFeatures.Ranger import RangerHunterFeatures
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class ColossusSlayerChoice:
    pass


@attr.dataclass
class HordeBreakerChoice:
    pass


@attr.dataclass
class EscapeTheHordeChoice:
    pass


@attr.dataclass
class MultiattackDefenseChoice:
    pass


@attr.dataclass
class RangerHunterLevel3(ClassBuilder.SubclassLevel3):
    hunters_prey: ColossusSlayerChoice | HordeBreakerChoice

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHunterFeatures.HuntersLore())
        if isinstance(self.hunters_prey, HordeBreakerChoice):
            data.add_feature(RangerHunterFeatures.HordeBreaker())
        else:
            data.add_feature(RangerHunterFeatures.ColossusSlayer())
        return data


@attr.dataclass
class RangerHunterLevel7(ClassBuilder.SubclassLevel7):
    defensive_tactics: EscapeTheHordeChoice | MultiattackDefenseChoice

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        if isinstance(self.defensive_tactics, MultiattackDefenseChoice):
            data.add_feature(RangerHunterFeatures.MultiattackDefense())
        else:
            data.add_feature(RangerHunterFeatures.EscapeTheHorde())
        return data


@attr.dataclass
class RangerHunterLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHunterFeatures.SuperiorHuntersPrey())
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
            subclass=RangerSubclass.HUNTER.value,
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
            subclass=RangerSubclass.HUNTER.value,
            replace_spells=replace_spells,
        )
