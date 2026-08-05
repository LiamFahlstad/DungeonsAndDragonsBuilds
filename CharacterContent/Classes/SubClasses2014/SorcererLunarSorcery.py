from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import SorcererSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Sorcerer import SorcererLunarSorceryFeatures
from CharacterContent.Spells.SpellLists import (
    ClericLevel0Spells,
    SorcererLevel1Spells,
    ClericLevel2Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    WizardLevel3Spells,
    ClericLevel4Spells,
    SorcererLevel4Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
    SorcererLevel5Spells,
)
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererLunarSorceryLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererLunarSorceryFeatures.LunarEmbodiment())
        data.add_feature(SorcererLunarSorceryFeatures.MoonFire())
        data.add_cantrip(ClericLevel0Spells.SACRED_FLAME)
        data.add_spell(SorcererLevel1Spells.SHIELD)
        data.add_spell(SorcererLevel1Spells.RAY_OF_SICKNESS)
        data.add_spell(SorcererLevel1Spells.COLOR_SPRAY)
        data.add_spell(ClericLevel2Spells.LESSER_RESTORATION)
        data.add_spell(SorcererLevel2Spells.BLINDNESS_DEAFNESS)
        data.add_spell(SorcererLevel2Spells.ALTER_SELF)
        return data


@attr.dataclass
class SorcererLunarSorceryLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.DISPEL_MAGIC)
        data.add_spell(SorcererLevel3Spells.VAMPIRIC_TOUCH)
        data.add_spell(WizardLevel3Spells.PHANTOM_STEED)
        return data


@attr.dataclass
class SorcererLunarSorceryLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererLunarSorceryFeatures.LunarBoons())
        data.add_feature(SorcererLunarSorceryFeatures.WaxingAndWaning())
        return data


@attr.dataclass
class SorcererLunarSorceryLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel4Spells.DEATH_WARD)
        data.add_spell(SorcererLevel4Spells.CONFUSION)
        data.add_spell(WizardLevel4Spells.HALLUCINATORY_TERRAIN)
        return data


@attr.dataclass
class SorcererLunarSorceryLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.RARYS_TELEPATHIC_BOND)
        data.add_spell(SorcererLevel5Spells.HOLD_MONSTER)
        data.add_spell(WizardLevel5Spells.MISLEAD)
        return data


@attr.dataclass
class SorcererLunarSorceryLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererLunarSorceryFeatures.LunarEmpowerment())
        return data


@attr.dataclass
class SorcererLunarSorceryLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererLunarSorceryFeatures.LunarPhenomenon())
        return data


class SorcererLunarSorceryCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass2014.LUNAR_SORCERY.value,
            skills=skills,
        )


class SorcererLunarSorceryMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass2014.LUNAR_SORCERY.value,
            replace_spells=replace_spells,
        )
