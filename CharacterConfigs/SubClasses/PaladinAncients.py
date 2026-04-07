from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinNonGenericStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import PaladinSubclass
from Features.ClassFeatures import PaladinFeatures
from Spells.Definitions import (
    BardLevel4Spells,
    ClericLevel2Spells,
    ClericLevel4Spells,
    ConjurationLevel1Spells,
    DivinationLevel1Spells,
    PaladinLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class AncientsPaladinLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: PaladinFeatures.ChannelDivinity = (
            data.get_features_by_type(PaladinFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.add_feature(PaladinFeatures.NaturesWrath())
        data.add_spell(ConjurationLevel1Spells.ENSNARING_STRIKE)
        data.add_spell(DivinationLevel1Spells.SPEAK_WITH_ANIMALS)
        return data


@attr.dataclass
class AncientsPaladinLevel5(ClassBuilder.SubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        data.add_spell(PaladinLevel2Spells.MAGIC_WEAPON)
        return data


@attr.dataclass
class AncientsPaladinLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: PaladinFeatures.AuraOfProtection = (
            data.get_features_by_type(PaladinFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(PaladinFeatures.AuraOfAlacrity())
        return data


@attr.dataclass
class AncientsPaladinLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class AncientsPaladinLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class AncientsPaladinLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.GloriousDefense())
        return data


@attr.dataclass
class AncientsPaladinLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


@attr.dataclass
class AncientsPaladinLevel20(ClassBuilder.SubclassLevel20):
    level: int = attr.field(init=False, default=20)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.LivingLegend())
        return data


class PaladinAncientsNonGenericStarterClassArgs(PaladinNonGenericStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_THE_ANCIENTS.value,
            skills=skills,
        )


class AncientsPaladinMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_THE_ANCIENTS.value,
            replace_spells=replace_spells,
        )
