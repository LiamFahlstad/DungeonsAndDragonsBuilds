from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import ClericSubclass2014
from Features.SubClassFeatures2014.Cleric import ClericForgeFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericForgeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericForgeFeatures.BonusProficiencies())
        data.add_feature(ClericForgeFeatures.BlessingOfTheForge())
        data.add_feature(ClericForgeFeatures.ForgeDomainSpells())
        data.add_feature(ClericForgeFeatures.ArtisansBlessingChannelDivinity())
        return data


@attr.dataclass
class ClericForgeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericForgeFeatures.SoulOfTheForge())
        return data


@attr.dataclass
class ClericForgeLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericForgeFeatures.DivineStrike())
        return data


@attr.dataclass
class ClericForgeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericForgeFeatures.SaintOfForgeAndFire())
        return data


class ClericForgeCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.FORGE.value,
            skills=skills,
        )


class ClericForgeMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.FORGE.value,
            replace_spells=replace_spells,
        )
