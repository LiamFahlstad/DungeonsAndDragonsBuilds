from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RogueSubclass
from Features.ClassFeatures.Rogue import RogueAssassinFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueAssassinLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueAssassinFeatures.Assassinate())
        data.add_feature(RogueAssassinFeatures.AssassinsTools())
        return data


@attr.dataclass
class RogueAssassinLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueAssassinFeatures.InfiltrationExpertise())
        return data


@attr.dataclass
class RogueAssassinLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueAssassinFeatures.SneakAttack = data.get_features_by_type(
            RogueAssassinFeatures.SneakAttack
        )[0]
        sneak_attack_feature.extend_feature(RogueAssassinFeatures.CunningStrike())
        data.add_feature(RogueAssassinFeatures.EnvenomWeapons())
        return data


@attr.dataclass
class RogueAssassinLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueAssassinFeatures.SneakAttack = data.get_features_by_type(
            RogueAssassinFeatures.SneakAttack
        )[0]
        sneak_attack_feature.extend_feature(RogueAssassinFeatures.CunningStrike())
        data.add_feature(RogueAssassinFeatures.DeathStrike())
        return data


class RogueAssassinCustomStarterClassArgs(RogueCustomStarterClassArgs):
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
