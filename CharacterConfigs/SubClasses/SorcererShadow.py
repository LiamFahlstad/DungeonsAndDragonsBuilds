from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import SorcererSubclass
from Features.ClassFeatures.Sorcerer import SorcererShadowFeatures
from Spells.SpellLists import (
    AbjurationLevel2Spells,
    AbjurationLevel3Spells,
    ConjurationLevel3Spells,
    EnchantmentLevel1Spells,
    IllusionLevel4Spells,
    NecromancyLevel1Spells,
    NecromancyLevel5Spells,
    SorcererLevel2Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
)
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererShadowLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererShadowFeatures.ShadowSpells())
        data.add_spell(EnchantmentLevel1Spells.BANE)
        data.add_spell(SorcererLevel2Spells.DARKNESS)
        data.add_spell(NecromancyLevel1Spells.INFLICT_WOUNDS)
        data.add_spell(AbjurationLevel2Spells.PASS_WITHOUT_TRACE)
        data.add_feature(SorcererShadowFeatures.PowerOfShadow())
        return data


@attr.dataclass
class SorcererShadowLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel3Spells.HUNGER_OF_HADAR)
        data.add_spell(AbjurationLevel3Spells.NONDETECTION)
        return data


@attr.dataclass
class SorcererShadowLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererShadowFeatures.BeastsOfIllOmen())
        return data


@attr.dataclass
class SorcererShadowLevel7(ClassBuilder.SubclassLevel7):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel4Spells.GREATER_INVISIBILITY)
        data.add_spell(IllusionLevel4Spells.PHANTASMAL_KILLER)
        return data


@attr.dataclass
class SorcererShadowLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(NecromancyLevel5Spells.CONTAGION)
        data.add_spell(SorcererLevel5Spells.CREATION)
        return data


@attr.dataclass
class SorcererShadowLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererShadowFeatures.ShadowWalk())
        return data


@attr.dataclass
class SorcererShadowLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererShadowFeatures.UmbralForm())
        return data


class SorcererShadowCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass.SHADOW.value,
            skills=skills,
        )


class SorcererShadowMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.SHADOW.value,
            replace_spells=replace_spells,
        )
