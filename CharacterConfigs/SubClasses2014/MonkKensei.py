from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import Ability, MonkSubclass2014
from Features.SubClassFeatures2014.Monk import MonkKenseiFeatures
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkKenseiLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkKenseiFeatures.KenseiWeapons())
        data.add_feature(MonkKenseiFeatures.AgileParry())
        data.add_feature(MonkKenseiFeatures.KenseiShot())
        data.add_feature(MonkKenseiFeatures.WayOfTheBrush())
        return data


@attr.dataclass
class MonkKenseiLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkKenseiFeatures.MagicKenseiWeapons())
        data.add_feature(MonkKenseiFeatures.DeftStrike())
        return data


@attr.dataclass
class MonkKenseiLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkKenseiFeatures.SharpenTheBlade())
        return data


@attr.dataclass
class MonkKenseiLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkKenseiFeatures.UnearringAccuracy())
        return data


class MonkKenseiCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: MonkSkillsStatBlock,
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass2014.KENSEI.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkKenseiMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass2014.KENSEI.value,
            replace_spells=replace_spells,
        )
