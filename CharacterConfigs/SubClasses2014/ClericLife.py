from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import ClericSubclass2014
from Features.SubClassFeatures2014.Cleric import ClericLifeFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericLifeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericLifeFeatures.BonusProficiency())
        data.add_feature(ClericLifeFeatures.DiscipleOfLife())
        data.add_feature(ClericLifeFeatures.LifeDomainSpells())
        data.add_feature(ClericLifeFeatures.PreserveLifeChannelDivinity())
        return data


@attr.dataclass
class ClericLifeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericLifeFeatures.BlessedHealer())
        return data


@attr.dataclass
class ClericLifeLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericLifeFeatures.DivineStrike())
        return data


@attr.dataclass
class ClericLifeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericLifeFeatures.SupremeHealing())
        return data


class ClericLifeCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.LIFE.value,
            skills=skills,
        )


class ClericLifeMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.LIFE.value,
            replace_spells=replace_spells,
        )
