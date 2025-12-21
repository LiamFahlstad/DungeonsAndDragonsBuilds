from typing import Optional
import attr
from CharacterConfigs.Bases.BarbarianBase import (
    BarbarianFeaturePerLevel,
    BarbarianSubclassLevel13,
    BarbarianSubclassLevel15,
    BarbarianSubclassLevel17,
    BarbarianSubclassLevel20,
    BarbarianSubclassLevel3,
    BarbarianSubclassLevel5,
    BarbarianSubclassLevel7,
    BarbarianSubclassLevel9,
)
from CharacterSheetCreator import CharacterSheetData
from Features.ClassFeatures import BarbarianFeatures


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel3(BarbarianSubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.Frenzy())
        data.add_feature(BarbarianFeatures.MindlessRage())
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel5(BarbarianSubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        data.add_spell(BarbarianLevel2Spells.MAGIC_WEAPON)
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel7(BarbarianSubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: BarbarianFeatures.AuraOfProtection = (
            data.get_features_by_type(BarbarianFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(BarbarianFeatures.AuraOfAlacrity())
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel9(BarbarianSubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel13(BarbarianSubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel15(BarbarianSubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.GloriousDefense())
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel17(BarbarianSubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianLevel20(BarbarianSubclassLevel20):
    level: int = attr.field(init=False, default=20)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.LivingLegend())
        return data


@attr.dataclass
class PathOfTheBerserkerBarbarianFeaturePerLevel(BarbarianFeaturePerLevel):
    subclass_level_3: Optional[PathOfTheBerserkerBarbarianLevel3] = None
    subclass_level_5: Optional[PathOfTheBerserkerBarbarianLevel5] = None
    subclass_level_7: Optional[PathOfTheBerserkerBarbarianLevel7] = None
    subclass_level_9: Optional[PathOfTheBerserkerBarbarianLevel9] = None
    subclass_level_13: Optional[PathOfTheBerserkerBarbarianLevel13] = None
    subclass_level_15: Optional[PathOfTheBerserkerBarbarianLevel15] = None
    subclass_level_17: Optional[PathOfTheBerserkerBarbarianLevel17] = None
    subclass_level_20: Optional[PathOfTheBerserkerBarbarianLevel20] = None
