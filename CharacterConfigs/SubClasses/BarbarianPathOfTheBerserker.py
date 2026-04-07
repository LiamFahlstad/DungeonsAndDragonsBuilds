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
class BarbarianBerserkerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.Frenzy())
        return data


@attr.dataclass
class BarbarianBerserkerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.MindlessRage())
        return data


@attr.dataclass
class BarbarianBerserkerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.Retaliation())
        return data


@attr.dataclass
class BarbarianBerserkerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.IntimidatingPresence())
        return data


class BarbarianBerserkerNonGenericStarterClassArgs(BarbarianNonGenericStarterClassArgs):
    def __init__(
        self,
        skills: BarbarianSkillsStatBlock,
    ):
        super().__init__(
            subclass=BarbarianSubclass.PATH_OF_THE_BERSERKER.value,
            skills=skills,
        )


class BarbarianBerserkerMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass.PATH_OF_THE_BERSERKER.value,
            replace_spells=replace_spells,
        )
