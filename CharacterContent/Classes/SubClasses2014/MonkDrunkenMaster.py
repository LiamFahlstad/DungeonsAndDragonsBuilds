from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import Ability, MonkSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Monk import MonkDrunkenMasterFeatures
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkDrunkenMasterLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkDrunkenMasterFeatures.BonusProficiencies())
        data.add_feature(MonkDrunkenMasterFeatures.DrunkenTechnique())
        return data


@attr.dataclass
class MonkDrunkenMasterLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkDrunkenMasterFeatures.TipsySway())
        return data


@attr.dataclass
class MonkDrunkenMasterLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkDrunkenMasterFeatures.DrunkardsLuck())
        return data


@attr.dataclass
class MonkDrunkenMasterLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkDrunkenMasterFeatures.IntoxicatedFrenzy())
        return data


class MonkDrunkenMasterCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: MonkSkillsStatBlock,
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass2014.DRUNKEN_MASTER.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkDrunkenMasterMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass2014.DRUNKEN_MASTER.value,
            replace_spells=replace_spells,
        )
