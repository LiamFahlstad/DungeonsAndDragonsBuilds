from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import BarbarianSubclass2014
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures
from CharacterContent.Features.SubClassFeatures2014.Barbarian import BarbarianPathOfTheBattleragerFeatures
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


@attr.dataclass
class BarbarianBattleragerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheBattleragerFeatures.BattleragerArmor())
        return data


@attr.dataclass
class BarbarianBattleragerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        reckless_attack: BarbarianFeatures.RecklessAttack = data.get_features_by_type(
            BarbarianFeatures.RecklessAttack
        )[0]
        reckless_attack.extend_feature(BarbarianPathOfTheBattleragerFeatures.RecklessAbandon())
        return data


@attr.dataclass
class BarbarianBattleragerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(BarbarianPathOfTheBattleragerFeatures.BattleragerCharge())
        return data


@attr.dataclass
class BarbarianBattleragerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        battlerager_armor: BarbarianPathOfTheBattleragerFeatures.BattleragerArmor = (
            data.get_features_by_type(
                BarbarianPathOfTheBattleragerFeatures.BattleragerArmor
            )[0]
        )
        battlerager_armor.extend_feature(BarbarianPathOfTheBattleragerFeatures.SpikedRetribution())
        return data


class BarbarianBattleragerCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: BarbarianSkillsStatBlock,
    ):
        super().__init__(
            subclass=BarbarianSubclass2014.PATH_OF_THE_BATTLERAGER.value,
            skills=skills,
        )


class BarbarianBattleragerMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass2014.PATH_OF_THE_BATTLERAGER.value,
            replace_spells=replace_spells,
        )
