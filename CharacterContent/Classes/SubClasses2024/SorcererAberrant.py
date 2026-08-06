from typing import Optional

import attr

from Builds.CharacterSheetAccumulator import CharacterSheetData
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.SorcererBase import (
    SorcererCustomStarterClassArgs,
    SorcererMulticlassBuilder,
)
from CharacterContent.Features.SubClassFeatures.Sorcerer import SorcererAberrantFeatures
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
from Core.Definitions import SorcererSubclass
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererAberrantLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererAberrantFeatures.PsionicSpells())
        data.add_spell(ConjurationLevel1Spells.ARMS_OF_HADAR)
        data.add_spell(EnchantmentLevel2Spells.CALM_EMOTIONS)
        data.add_spell(DivinationLevel2Spells.DETECT_THOUGHTS)
        data.add_spell(EnchantmentLevel1Spells.DISSONANT_WHISPERS)
        data.add_spell(EnchantmentLevel0Spells.MIND_SLIVER)
        data.add_feature(SorcererAberrantFeatures.TelepathicSpeech())
        return data


@attr.dataclass
class SorcererAberrantLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel3Spells.HUNGER_OF_HADAR)
        data.add_spell(DivinationLevel3Spells.SENDING)
        return data


@attr.dataclass
class SorcererAberrantLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        psionic_spells: SorcererAberrantFeatures.PsionicSpells = (
            data.get_features_by_type(SorcererAberrantFeatures.PsionicSpells)[0]
        )
        psionic_spells.extend_feature(SorcererAberrantFeatures.PsionicSorcery())
        data.add_feature(SorcererAberrantFeatures.PsychicDefenses())
        return data


@attr.dataclass
class SorcererAberrantLevel7(ClassBuilder.SubclassLevel7):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel4Spells.EVARDS_BLACK_TENTACLES)
        data.add_spell(ConjurationLevel4Spells.SUMMON_ABERRATION)
        return data


@attr.dataclass
class SorcererAberrantLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DivinationLevel5Spells.RARYS_TELEPATHIC_BOND)
        data.add_spell(TransmutationLevel5Spells.TELEKINESIS)
        return data


@attr.dataclass
class SorcererAberrantLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererAberrantFeatures.RevelationInFlesh())
        return data


@attr.dataclass
class SorcererAberrantLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererAberrantFeatures.WarpingImplosion())
        return data


class SorcererAberrantCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass.ABERRANT.value,
            skills=skills,
        )


class SorcererAberrantMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.ABERRANT.value,
            replace_spells=replace_spells,
        )
