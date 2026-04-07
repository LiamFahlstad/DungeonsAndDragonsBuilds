from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueNonGenericStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RogueSubclass
from Features.ClassFeatures import RogueFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueAssassinLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueFeatures.Assassinate())
        data.add_feature(RogueFeatures.AssassinsTools())
        return data


@attr.dataclass
class RogueAssassinLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueFeatures.InfiltrationExpertise())
        return data


@attr.dataclass
class RogueAssassinLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.EnvenomWeapons())
        return data


@attr.dataclass
class RogueAssassinLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.DeathStrike())
        return data


class RogueAssassinNonGenericStarterClassArgs(RogueNonGenericStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass.ASSASSIN.value,
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
            subclass=RogueSubclass.ASSASSIN.value,
            replace_spells=replace_spells,
        )
