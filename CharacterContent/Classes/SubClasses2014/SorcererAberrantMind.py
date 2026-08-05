from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import SorcererSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Sorcerer import SorcererAberrantMindFeatures
from CharacterContent.Spells.SpellLists import (
    ConjurationLevel1Spells,
    ConjurationLevel3Spells,
    ConjurationLevel4Spells,
    DivinationLevel2Spells,
    DivinationLevel3Spells,
    DivinationLevel5Spells,
    EnchantmentLevel0Spells,
    EnchantmentLevel1Spells,
    EnchantmentLevel2Spells,
    TransmutationLevel5Spells,
)
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererAberrantMindLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererAberrantMindFeatures.PsionicSpells())
        data.add_spell(ConjurationLevel1Spells.ARMS_OF_HADAR)
        data.add_spell(EnchantmentLevel1Spells.DISSONANT_WHISPERS)
        data.add_spell(EnchantmentLevel0Spells.MIND_SLIVER)
        data.add_spell(EnchantmentLevel2Spells.CALM_EMOTIONS)
        data.add_spell(DivinationLevel2Spells.DETECT_THOUGHTS)
        data.add_feature(SorcererAberrantMindFeatures.TelepathicSpeech())
        return data


@attr.dataclass
class SorcererAberrantMindLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel3Spells.HUNGER_OF_HADAR)
        data.add_spell(DivinationLevel3Spells.SENDING)
        return data


@attr.dataclass
class SorcererAberrantMindLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererAberrantMindFeatures.PsionicSorcery())
        data.add_feature(SorcererAberrantMindFeatures.PsychicDefenses())
        return data


@attr.dataclass
class SorcererAberrantMindLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel4Spells.EVARDS_BLACK_TENTACLES)
        data.add_spell(ConjurationLevel4Spells.SUMMON_ABERRATION)
        return data


@attr.dataclass
class SorcererAberrantMindLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DivinationLevel5Spells.RARYS_TELEPATHIC_BOND)
        data.add_spell(TransmutationLevel5Spells.TELEKINESIS)
        return data


@attr.dataclass
class SorcererAberrantMindLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererAberrantMindFeatures.RevelationInFlesh())
        return data


@attr.dataclass
class SorcererAberrantMindLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererAberrantMindFeatures.WarpingImplosion())
        return data


class SorcererAberrantMindCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass2014.ABERRANT_MIND.value,
            skills=skills,
        )


class SorcererAberrantMindMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass2014.ABERRANT_MIND.value,
            replace_spells=replace_spells,
        )
