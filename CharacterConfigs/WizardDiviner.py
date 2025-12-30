from typing import Optional, TypeAlias

import attr

from CharacterSheetCreator import CharacterSheetData
from Features.ClassFeatures import WizardFeatures
from Spells.Definitions import (
    DivinationLevel1Spells,
    DivinationLevel2Spells,
    DivinationLevel3Spells,
    DivinationLevel4Spells,
    DivinationLevel5Spells,
    DivinationLevel6Spells,
    DivinationLevel7Spells,
    DivinationLevel8Spells,
    DivinationLevel9Spells,
)

DivinationSpellsUpTo2: TypeAlias = DivinationLevel1Spells | DivinationLevel2Spells

DivinationSpellsUpTo3: TypeAlias = DivinationSpellsUpTo2 | DivinationLevel3Spells

DivinationSpellsUpTo4: TypeAlias = DivinationSpellsUpTo3 | DivinationLevel4Spells

DivinationSpellsUpTo5: TypeAlias = DivinationSpellsUpTo4 | DivinationLevel5Spells

DivinationSpellsUpTo6: TypeAlias = DivinationSpellsUpTo5 | DivinationLevel6Spells

DivinationSpellsUpTo7: TypeAlias = DivinationSpellsUpTo6 | DivinationLevel7Spells

DivinationSpellsUpTo8: TypeAlias = DivinationSpellsUpTo7 | DivinationLevel8Spells

DivinationSpellsUpTo9: TypeAlias = DivinationSpellsUpTo8 | DivinationLevel9Spells


@attr.dataclass
class DivinerWizardLevel3(WizardSubclassLevel3):
    level: int = attr.field(init=False, default=3)
    spell_1: DivinationSpellsUpTo2
    spell_2: DivinationSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.DivinationSavant())
        data.add_feature(WizardFeatures.Portent())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class DivinerWizardLevel5(WizardSubclassLevel5):
    level: int = attr.field(init=False, default=5)
    spell: DivinationSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DivinerWizardLevel6(WizardSubclassLevel6):
    level: int = attr.field(init=False, default=6)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.ExpertDivination())
        return data


@attr.dataclass
class DivinerWizardLevel7(WizardSubclassLevel7):
    level: int = attr.field(init=False, default=7)
    spell: DivinationSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DivinerWizardLevel9(WizardSubclassLevel9):
    level: int = attr.field(init=False, default=9)
    spell: DivinationSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DivinerWizardLevel10(WizardSubclassLevel10):
    level: int = attr.field(init=False, default=10)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.TheThirdEye())
        return data


@attr.dataclass
class DivinerWizardLevel11(WizardSubclassLevel11):
    level: int = attr.field(init=False, default=11)
    spell: DivinationSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DivinerWizardLevel13(WizardSubclassLevel13):
    level: int = attr.field(init=False, default=13)
    spell: DivinationSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DivinerWizardLevel14(WizardSubclassLevel14):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.GreaterPortent())
        return data


@attr.dataclass
class DivinerWizardLevel15(WizardSubclassLevel15):
    level: int = attr.field(init=False, default=15)
    spell: DivinationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DivinerWizardLevel17(WizardSubclassLevel17):
    level: int = attr.field(init=False, default=17)
    spell: DivinationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DivinerWizardFeaturePerLevel(WizardFeaturePerLevel):
    subclass_level_3: Optional[DivinerWizardLevel3] = None
    subclass_level_5: Optional[DivinerWizardLevel5] = None
    subclass_level_6: Optional[DivinerWizardLevel6] = None
    subclass_level_7: Optional[DivinerWizardLevel7] = None
    subclass_level_9: Optional[DivinerWizardLevel9] = None
    subclass_level_10: Optional[DivinerWizardLevel10] = None
    subclass_level_11: Optional[DivinerWizardLevel11] = None
    subclass_level_13: Optional[DivinerWizardLevel13] = None
    subclass_level_14: Optional[DivinerWizardLevel14] = None
    subclass_level_15: Optional[DivinerWizardLevel15] = None
    subclass_level_17: Optional[DivinerWizardLevel17] = None
