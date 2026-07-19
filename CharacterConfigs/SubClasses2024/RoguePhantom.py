from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RogueSubclass
from Features.SubClassFeatures.Rogue import RoguePhantomFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RoguePhantomLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RoguePhantomFeatures.WailsFromTheGrave())
        data.add_feature(RoguePhantomFeatures.WhispersOfTheDead())
        return data


@attr.dataclass
class RoguePhantomLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RoguePhantomFeatures.TokensOfTheDeparted())
        data.add_feature(RoguePhantomFeatures.VoiceOfDeath())
        return data


@attr.dataclass
class RoguePhantomLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RoguePhantomFeatures.GhostWalk())
        return data


@attr.dataclass
class RoguePhantomLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RoguePhantomFeatures.DeathsFriend())
        return data


class RoguePhantomCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass.PHANTOM.value,
            skills=skills,
        )


class RoguePhantomMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.PHANTOM.value,
            replace_spells=replace_spells,
        )
