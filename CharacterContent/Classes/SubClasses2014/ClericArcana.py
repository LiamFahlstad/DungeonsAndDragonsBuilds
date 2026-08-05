from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import ClericSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericArcanaFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericArcanaLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericArcanaFeatures.ArcaneInitiate())
        data.add_feature(ClericArcanaFeatures.ArcanaDomainSpells())
        data.add_feature(ClericArcanaFeatures.ArcaneAbjurationChannelDivinity())
        return data


@attr.dataclass
class ClericArcanaLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericArcanaFeatures.SpellBreaker())
        return data


@attr.dataclass
class ClericArcanaLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericArcanaFeatures.PotentSpellcasting())
        return data


@attr.dataclass
class ClericArcanaLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericArcanaFeatures.ArcaneMastery())
        return data


class ClericArcanaCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.ARCANA.value,
            skills=skills,
        )


class ClericArcanaMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.ARCANA.value,
            replace_spells=replace_spells,
        )
