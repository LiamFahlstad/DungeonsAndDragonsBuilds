from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import BardSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Bard import BardCreationFeatures
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardCreationLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardCreationFeatures.MoteOfPotential())
        data.add_feature(BardCreationFeatures.PerformanceOfCreation())
        return data


@attr.dataclass
class BardCreationLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardCreationFeatures.AnimatingPerformance())
        return data


@attr.dataclass
class BardCreationLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardCreationFeatures.CreativeCrescendo())
        return data


class BardCreationCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: BardSkillsStatBlock,
    ):
        super().__init__(
            subclass=BardSubclass2014.CREATION.value,
            skills=skills,
        )


class BardCreationMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.CREATION.value,
            replace_spells=replace_spells,
        )
