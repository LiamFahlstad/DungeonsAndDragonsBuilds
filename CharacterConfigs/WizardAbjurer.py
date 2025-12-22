from typing import Optional, TypeAlias
import attr
from CharacterConfigs.Bases.WizardBase import (
    WizardFeaturePerLevel,
    WizardSubclassLevel10,
    WizardSubclassLevel11,
    WizardSubclassLevel13,
    WizardSubclassLevel14,
    WizardSubclassLevel15,
    WizardSubclassLevel17,
    WizardSubclassLevel3,
    WizardSubclassLevel5,
    WizardSubclassLevel6,
    WizardSubclassLevel7,
    WizardSubclassLevel9,
)
from CharacterSheetCreator import CharacterSheetData
from Features.ClassFeatures import WizardFeatures
from Spells.Definitions import (
    ConjurationLevel2Spells,
    ConjurationLevel3Spells,
    AbjurationLevel0Spells,
    AbjurationLevel1Spells,
    AbjurationLevel2Spells,
    AbjurationLevel3Spells,
    AbjurationLevel4Spells,
    AbjurationLevel5Spells,
    AbjurationLevel6Spells,
    AbjurationLevel7Spells,
    AbjurationLevel8Spells,
    AbjurationLevel9Spells,
    WizardLevel9Spells,
)

AbjurationSpellsUpTo2: TypeAlias = AbjurationLevel1Spells | AbjurationLevel2Spells

AbjurationSpellsUpTo3: TypeAlias = AbjurationSpellsUpTo2 | AbjurationLevel3Spells

AbjurationSpellsUpTo4: TypeAlias = AbjurationSpellsUpTo3 | AbjurationLevel4Spells

AbjurationSpellsUpTo5: TypeAlias = AbjurationSpellsUpTo4 | AbjurationLevel5Spells

AbjurationSpellsUpTo6: TypeAlias = AbjurationSpellsUpTo5 | AbjurationLevel6Spells

AbjurationSpellsUpTo7: TypeAlias = AbjurationSpellsUpTo6 | AbjurationLevel7Spells

AbjurationSpellsUpTo8: TypeAlias = AbjurationSpellsUpTo7 | AbjurationLevel8Spells

AbjurationSpellsUpTo9: TypeAlias = AbjurationSpellsUpTo8 | AbjurationLevel9Spells


@attr.dataclass
class AbjurerWizardLevel3(WizardSubclassLevel3):
    level: int = attr.field(init=False, default=3)
    spell_1: AbjurationSpellsUpTo2
    spell_2: AbjurationSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.AbjurationSavant())
        data.add_feature(WizardFeatures.ArcaneWard())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class AbjurerWizardLevel5(WizardSubclassLevel5):
    level: int = attr.field(init=False, default=5)
    spell: AbjurationSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel6(WizardSubclassLevel6):
    level: int = attr.field(init=False, default=6)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.ProjectedWard())
        return data


@attr.dataclass
class AbjurerWizardLevel7(WizardSubclassLevel7):
    level: int = attr.field(init=False, default=7)
    spell: AbjurationSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel9(WizardSubclassLevel9):
    level: int = attr.field(init=False, default=9)
    spell: AbjurationSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel10(WizardSubclassLevel10):
    level: int = attr.field(init=False, default=10)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SpellBreaker())
        data.add_spell(AbjurationLevel3Spells.COUNTERSPELL)
        data.add_spell(AbjurationLevel3Spells.DISPEL_MAGIC)
        return data


@attr.dataclass
class AbjurerWizardLevel11(WizardSubclassLevel11):
    level: int = attr.field(init=False, default=11)
    spell: AbjurationSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel13(WizardSubclassLevel13):
    level: int = attr.field(init=False, default=13)
    spell: AbjurationSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel14(WizardSubclassLevel14):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SpellResistance())
        return data


@attr.dataclass
class AbjurerWizardLevel15(WizardSubclassLevel15):
    level: int = attr.field(init=False, default=15)
    spell: AbjurationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel17(WizardSubclassLevel17):
    level: int = attr.field(init=False, default=17)
    spell: AbjurationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardFeaturePerLevel(WizardFeaturePerLevel):
    subclass_level_3: Optional[AbjurerWizardLevel3] = None
    subclass_level_5: Optional[AbjurerWizardLevel5] = None
    subclass_level_6: Optional[AbjurerWizardLevel6] = None
    subclass_level_7: Optional[AbjurerWizardLevel7] = None
    subclass_level_9: Optional[AbjurerWizardLevel9] = None
    subclass_level_10: Optional[AbjurerWizardLevel10] = None
    subclass_level_11: Optional[AbjurerWizardLevel11] = None
    subclass_level_13: Optional[AbjurerWizardLevel13] = None
    subclass_level_14: Optional[AbjurerWizardLevel14] = None
    subclass_level_15: Optional[AbjurerWizardLevel15] = None
    subclass_level_17: Optional[AbjurerWizardLevel17] = None
