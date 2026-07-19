from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import SorcererSubclass
from Features.SubClassFeatures.Sorcerer import SorcererSpellfireFeatures
from Spells.SpellLists import (
    AbjurationLevel1Spells,
    AbjurationLevel2Spells,
    AbjurationLevel3Spells,
    AbjurationLevel5Spells,
    EvocationLevel1Spells,
    EvocationLevel5Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
)
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererSpellfireLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererSpellfireFeatures.SpellfireBurst())
        data.add_feature(SorcererSpellfireFeatures.SpellfireSpells())
        data.add_spell(AbjurationLevel1Spells.CURE_WOUNDS)
        data.add_spell(EvocationLevel1Spells.GUIDING_BOLT)
        data.add_spell(AbjurationLevel2Spells.LESSER_RESTORATION)
        data.add_spell(SorcererLevel2Spells.SCORCHING_RAY)
        return data


@attr.dataclass
class SorcererSpellfireLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(AbjurationLevel3Spells.AURA_OF_VITALITY)
        data.add_spell(SorcererLevel3Spells.DISPEL_MAGIC)
        return data


@attr.dataclass
class SorcererSpellfireLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.COUNTERSPELL)
        data.add_feature(SorcererSpellfireFeatures.AbsorbSpells())
        return data


@attr.dataclass
class SorcererSpellfireLevel7(ClassBuilder.SubclassLevel7):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel4Spells.FIRE_SHIELD)
        data.add_spell(SorcererLevel4Spells.WALL_OF_FIRE)
        return data


@attr.dataclass
class SorcererSpellfireLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(AbjurationLevel5Spells.GREATER_RESTORATION)
        data.add_spell(EvocationLevel5Spells.FLAME_STRIKE)
        return data


@attr.dataclass
class SorcererSpellfireLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererSpellfireFeatures.HonedSpellfire())
        return data


@attr.dataclass
class SorcererSpellfireLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererSpellfireFeatures.CrownOfSpellfire())
        return data


class SorcererSpellfireCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass.SPELLFIRE.value,
            skills=skills,
        )


class SorcererSpellfireMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.SPELLFIRE.value,
            replace_spells=replace_spells,
        )
