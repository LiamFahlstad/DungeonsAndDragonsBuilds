from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ClericSubclass2014
from Features.SubClassFeatures2014.Cleric import ClericDeathFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericDeathLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericDeathFeatures.BonusProficiency())
        data.add_feature(ClericDeathFeatures.Reaper())
        data.add_feature(ClericDeathFeatures.DeathDomainSpells())
        data.add_feature(ClericDeathFeatures.TouchOfDeathChannelDivinity())
        return data


@attr.dataclass
class ClericDeathLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericDeathFeatures.InescapableDestruction())
        return data


@attr.dataclass
class ClericDeathLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericDeathFeatures.DivineStrike())
        return data


@attr.dataclass
class ClericDeathLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericDeathFeatures.ImprovedReaper())
        return data


class ClericDeathCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.DEATH.value,
            skills=skills,
        )


class ClericDeathMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.DEATH.value,
            replace_spells=replace_spells,
        )
