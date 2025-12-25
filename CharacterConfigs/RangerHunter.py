from typing import Optional
import attr
from CharacterConfigs.CharacterClasses.RangerBase import (
    RangerFeaturePerLevel,
    RangerSubclassLevel13,
    RangerSubclassLevel15,
    RangerSubclassLevel17,
    RangerSubclassLevel20,
    RangerSubclassLevel3,
    RangerSubclassLevel5,
    RangerSubclassLevel7,
    RangerSubclassLevel9,
)
from CharacterSheetCreator import CharacterSheetData
from Features.ClassFeatures import RangerFeatures
from Spells.Definitions import (
    BardLevel4Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel4Spells,
    RangerLevel1Spells,
    RangerLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class HunterRangerLevel3(RangerSubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.HuntersLore())
        data.add_feature(RangerFeatures.HuntersPrey())
        return data


@attr.dataclass
class HunterRangerLevel5(RangerSubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        data.add_spell(RangerLevel2Spells.MAGIC_WEAPON)
        return data


@attr.dataclass
class HunterRangerLevel7(RangerSubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: RangerFeatures.AuraOfProtection = data.get_features_by_type(
            RangerFeatures.AuraOfProtection
        )[0]
        aura_of_protection.add_feature(RangerFeatures.AuraOfAlacrity())
        return data


@attr.dataclass
class HunterRangerLevel9(RangerSubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class HunterRangerLevel13(RangerSubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class HunterRangerLevel15(RangerSubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.GloriousDefense())
        return data


@attr.dataclass
class HunterRangerLevel17(RangerSubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


@attr.dataclass
class HunterRangerLevel20(RangerSubclassLevel20):
    level: int = attr.field(init=False, default=20)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.LivingLegend())
        return data


@attr.dataclass
class HunterRangerFeaturePerLevel(RangerFeaturePerLevel):
    subclass_level_3: Optional[HunterRangerLevel3] = None
    subclass_level_5: Optional[HunterRangerLevel5] = None
    subclass_level_7: Optional[HunterRangerLevel7] = None
    subclass_level_9: Optional[HunterRangerLevel9] = None
    subclass_level_13: Optional[HunterRangerLevel13] = None
    subclass_level_15: Optional[HunterRangerLevel15] = None
    subclass_level_17: Optional[HunterRangerLevel17] = None
    subclass_level_20: Optional[HunterRangerLevel20] = None
