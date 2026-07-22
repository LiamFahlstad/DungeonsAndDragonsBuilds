from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import RogueSubclass
from Features.SubClassFeatures.Rogue import RogueThiefFeatures
from Features.ClassFeatures.Rogue import RogueFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueThiefLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueThiefFeatures.FastHands())
        data.add_feature(RogueThiefFeatures.SecondStoryWork())
        return data


@attr.dataclass
class RogueThiefLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.extend_feature(RogueThiefFeatures.SupremeSneak())
        return data


@attr.dataclass
class RogueThiefLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueThiefFeatures.UseMagicDevice())
        return data


@attr.dataclass
class RogueThiefLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueThiefFeatures.ThiefsReflexes())
        return data


class RogueThiefCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass.THIEF.value,
            skills=skills,
        )


class RogueThiefMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.THIEF.value,
            replace_spells=replace_spells,
        )
