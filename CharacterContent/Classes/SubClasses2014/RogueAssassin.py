from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import RogueSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Rogue import RogueAssassinFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueAssassinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueAssassinFeatures.BonusProficiencies())
        data.add_feature(RogueAssassinFeatures.Assassinate())
        return data


@attr.dataclass
class RogueAssassinLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueAssassinFeatures.InfiltrationExpertise())
        return data


@attr.dataclass
class RogueAssassinLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueAssassinFeatures.Impostor())
        return data


@attr.dataclass
class RogueAssassinLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueAssassinFeatures.DeathStrike())
        return data


class RogueAssassinCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass2014.ASSASSIN.value,
            skills=skills,
        )


class RogueAssassinMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass2014.ASSASSIN.value,
            replace_spells=replace_spells,
        )
