from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianNonGenericStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import BarbarianSubclass
from Features.ClassFeatures import BarbarianFeatures
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


@attr.dataclass
class BarbarianWorldTreeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.VitalityOfTheTree())
        return data


@attr.dataclass
class BarbarianWorldTreeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.BranchesOfTheTree())
        return data


@attr.dataclass
class BarbarianWorldTreeLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.BatteringRoots())
        return data


@attr.dataclass
class BarbarianWorldTreeLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.BranchesOfTheTree())
        return data


class BarbarianWorldTreeNonGenericStarterClassArgs(BarbarianNonGenericStarterClassArgs):
    def __init__(
        self,
        skills: BarbarianSkillsStatBlock,
    ):
        super().__init__(
            subclass=BarbarianSubclass.PATH_OF_THE_WORLD_TREE.value,
            skills=skills,
        )


class BarbarianWorldTreeMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass.PATH_OF_THE_WORLD_TREE.value,
            replace_spells=replace_spells,
        )
