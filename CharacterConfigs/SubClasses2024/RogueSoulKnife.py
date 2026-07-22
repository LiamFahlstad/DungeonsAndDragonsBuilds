from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import RogueSubclass
from Features.SubClassFeatures.Rogue import RogueSoulKnifeFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueSoulKnifeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSoulKnifeFeatures.PsionicPower())
        data.add_feature(RogueSoulKnifeFeatures.PsychicBlades())
        return data


@attr.dataclass
class RogueSoulKnifeLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSoulKnifeFeatures.SoulBlades())
        return data


@attr.dataclass
class RogueSoulKnifeLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSoulKnifeFeatures.PsychicVeil())
        return data


@attr.dataclass
class RogueSoulKnifeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueSoulKnifeFeatures.RendMind())
        return data


class RogueSoulKnifeCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass.SOUL_KNIFE.value,
            skills=skills,
        )


class RogueSoulKnifeMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.SOUL_KNIFE.value,
            replace_spells=replace_spells,
        )
