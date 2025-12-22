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
    EvocationLevel1Spells,
    EvocationLevel2Spells,
    EvocationLevel3Spells,
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    EvocationLevel6Spells,
    EvocationLevel7Spells,
    EvocationLevel8Spells,
    EvocationLevel9Spells,
)

EvocationSpellsUpTo2: TypeAlias = EvocationLevel1Spells | EvocationLevel2Spells

EvocationSpellsUpTo3: TypeAlias = EvocationSpellsUpTo2 | EvocationLevel3Spells

EvocationSpellsUpTo4: TypeAlias = EvocationSpellsUpTo3 | EvocationLevel4Spells

EvocationSpellsUpTo5: TypeAlias = EvocationSpellsUpTo4 | EvocationLevel5Spells

EvocationSpellsUpTo6: TypeAlias = EvocationSpellsUpTo5 | EvocationLevel6Spells

EvocationSpellsUpTo7: TypeAlias = EvocationSpellsUpTo6 | EvocationLevel7Spells

EvocationSpellsUpTo8: TypeAlias = EvocationSpellsUpTo7 | EvocationLevel8Spells

EvocationSpellsUpTo9: TypeAlias = EvocationSpellsUpTo8 | EvocationLevel9Spells


@attr.dataclass
class EvokerWizardLevel3(WizardSubclassLevel3):
    level: int = attr.field(init=False, default=3)
    spell_1: EvocationSpellsUpTo2
    spell_2: EvocationSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.ImprovedIllusions())
        data.add_feature(WizardFeatures.IllusionSavant())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class EvokerWizardLevel5(WizardSubclassLevel5):
    level: int = attr.field(init=False, default=5)
    spell: EvocationSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel6(WizardSubclassLevel6):
    level: int = attr.field(init=False, default=6)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.PhantasmalCreatures())
        return data


@attr.dataclass
class EvokerWizardLevel7(WizardSubclassLevel7):
    level: int = attr.field(init=False, default=7)
    spell: EvocationSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel9(WizardSubclassLevel9):
    level: int = attr.field(init=False, default=9)
    spell: EvocationSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel10(WizardSubclassLevel10):
    level: int = attr.field(init=False, default=10)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.EmpoweredEvocation())
        return data


@attr.dataclass
class EvokerWizardLevel11(WizardSubclassLevel11):
    level: int = attr.field(init=False, default=11)
    spell: EvocationSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel13(WizardSubclassLevel13):
    level: int = attr.field(init=False, default=13)
    spell: EvocationSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel14(WizardSubclassLevel14):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.Overchannel())
        return data


@attr.dataclass
class EvokerWizardLevel15(WizardSubclassLevel15):
    level: int = attr.field(init=False, default=15)
    spell: EvocationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel17(WizardSubclassLevel17):
    level: int = attr.field(init=False, default=17)
    spell: EvocationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardFeaturePerLevel(WizardFeaturePerLevel):
    subclass_level_3: Optional[EvokerWizardLevel3] = None
    subclass_level_5: Optional[EvokerWizardLevel5] = None
    subclass_level_6: Optional[EvokerWizardLevel6] = None
    subclass_level_7: Optional[EvokerWizardLevel7] = None
    subclass_level_9: Optional[EvokerWizardLevel9] = None
    subclass_level_10: Optional[EvokerWizardLevel10] = None
    subclass_level_11: Optional[EvokerWizardLevel11] = None
    subclass_level_13: Optional[EvokerWizardLevel13] = None
    subclass_level_14: Optional[EvokerWizardLevel14] = None
    subclass_level_15: Optional[EvokerWizardLevel15] = None
    subclass_level_17: Optional[EvokerWizardLevel17] = None
