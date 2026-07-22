from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import BarbarianSubclass2014
from Features.SubClassFeatures2014.Barbarian import BarbarianPathOfTheTotemWarriorFeatures
from Features.ClassFeatures.Barbarian import BarbarianFeatures
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


@attr.dataclass
class BarbarianTotemWarriorLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheTotemWarriorFeatures.SpiritSeeker())
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(BarbarianPathOfTheTotemWarriorFeatures.TotemSpirit())
        return data


@attr.dataclass
class BarbarianTotemWarriorLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheTotemWarriorFeatures.AspectOfTheBeast())
        return data


@attr.dataclass
class BarbarianTotemWarriorLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheTotemWarriorFeatures.SpiritWalker())
        return data


@attr.dataclass
class BarbarianTotemWarriorLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(BarbarianPathOfTheTotemWarriorFeatures.TotemicAttunement())
        return data


class BarbarianTotemWarriorCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: BarbarianSkillsStatBlock,
    ):
        super().__init__(
            subclass=BarbarianSubclass2014.PATH_OF_THE_TOTEM_WARRIOR.value,
            skills=skills,
        )


class BarbarianTotemWarriorMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass2014.PATH_OF_THE_TOTEM_WARRIOR.value,
            replace_spells=replace_spells,
        )
