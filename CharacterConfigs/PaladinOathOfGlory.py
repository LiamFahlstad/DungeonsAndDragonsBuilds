from typing import Optional
import attr
from CharacterConfigs.CharacterClasses.PaladinBase import (
    PaladinFeaturePerLevel,
    PaladinSubclassLevel13,
    PaladinSubclassLevel15,
    PaladinSubclassLevel17,
    PaladinSubclassLevel20,
    PaladinSubclassLevel3,
    PaladinSubclassLevel5,
    PaladinSubclassLevel7,
    PaladinSubclassLevel9,
)
from CharacterSheetCreator import CharacterSheetData
from Features.ClassFeatures import PaladinFeatures
from Spells.Definitions import (
    BardLevel4Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel4Spells,
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class GloryPaladinLevel3(PaladinSubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: PaladinFeatures.ChannelDivinity = (
            data.get_features_by_type(PaladinFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.add_feature(PaladinFeatures.InspiringSmite())
        channel_divinity_feature.add_feature(PaladinFeatures.PeerlessAthlete())
        data.add_spell(ClericLevel1Spells.GUIDING_BOLT)
        data.add_spell(PaladinLevel1Spells.HEROISM)
        return data


@attr.dataclass
class GloryPaladinLevel5(PaladinSubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        data.add_spell(PaladinLevel2Spells.MAGIC_WEAPON)
        return data


@attr.dataclass
class GloryPaladinLevel7(PaladinSubclassLevel7):
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
class GloryPaladinLevel9(PaladinSubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class GloryPaladinLevel13(PaladinSubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class GloryPaladinLevel15(PaladinSubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.GloriousDefense())
        return data


@attr.dataclass
class GloryPaladinLevel17(PaladinSubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


@attr.dataclass
class GloryPaladinLevel20(PaladinSubclassLevel20):
    level: int = attr.field(init=False, default=20)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.LivingLegend())
        return data


@attr.dataclass
class GloryPaladinFeaturePerLevel(PaladinFeaturePerLevel):
    subclass_level_3: Optional[GloryPaladinLevel3] = None
    subclass_level_5: Optional[GloryPaladinLevel5] = None
    subclass_level_7: Optional[GloryPaladinLevel7] = None
    subclass_level_9: Optional[GloryPaladinLevel9] = None
    subclass_level_13: Optional[GloryPaladinLevel13] = None
    subclass_level_15: Optional[GloryPaladinLevel15] = None
    subclass_level_17: Optional[GloryPaladinLevel17] = None
    subclass_level_20: Optional[GloryPaladinLevel20] = None
