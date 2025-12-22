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
    IllusionLevel0Spells,
    IllusionLevel1Spells,
    IllusionLevel2Spells,
    IllusionLevel3Spells,
    IllusionLevel4Spells,
    IllusionLevel5Spells,
    IllusionLevel6Spells,
    IllusionLevel7Spells,
    IllusionLevel8Spells,
    IllusionLevel9Spells,
    WizardLevel9Spells,
)

IllusionSpellsUpTo2: TypeAlias = IllusionLevel1Spells | IllusionLevel2Spells

IllusionSpellsUpTo3: TypeAlias = IllusionSpellsUpTo2 | IllusionLevel3Spells

IllusionSpellsUpTo4: TypeAlias = IllusionSpellsUpTo3 | IllusionLevel4Spells

IllusionSpellsUpTo5: TypeAlias = IllusionSpellsUpTo4 | IllusionLevel5Spells

IllusionSpellsUpTo6: TypeAlias = IllusionSpellsUpTo5 | IllusionLevel6Spells

IllusionSpellsUpTo7: TypeAlias = IllusionSpellsUpTo6 | IllusionLevel7Spells

IllusionSpellsUpTo8: TypeAlias = IllusionSpellsUpTo7 | IllusionLevel8Spells

IllusionSpellsUpTo9: TypeAlias = IllusionSpellsUpTo8 | IllusionLevel9Spells


@attr.dataclass
class IllusionistWizardLevel3(WizardSubclassLevel3):
    level: int = attr.field(init=False, default=3)
    spell_1: IllusionSpellsUpTo2
    spell_2: IllusionSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.IllusionSavant())
        data.add_feature(WizardFeatures.ImprovedIllusions())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_cantrip(IllusionLevel0Spells.MINOR_ILLUSION)
        return data


@attr.dataclass
class IllusionistWizardLevel5(WizardSubclassLevel5):
    level: int = attr.field(init=False, default=5)
    spell: IllusionSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel6(WizardSubclassLevel6):
    level: int = attr.field(init=False, default=6)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SculptSpells())
        data.add_spell(ConjurationLevel2Spells.SUMMON_BEAST)
        data.add_spell(ConjurationLevel3Spells.SUMMON_FEY)
        return data


@attr.dataclass
class IllusionistWizardLevel7(WizardSubclassLevel7):
    level: int = attr.field(init=False, default=7)
    spell: IllusionSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel9(WizardSubclassLevel9):
    level: int = attr.field(init=False, default=9)
    spell: IllusionSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel10(WizardSubclassLevel10):
    level: int = attr.field(init=False, default=10)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.IllusorySelf())
        return data


@attr.dataclass
class IllusionistWizardLevel11(WizardSubclassLevel11):
    level: int = attr.field(init=False, default=11)
    spell: IllusionSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel13(WizardSubclassLevel13):
    level: int = attr.field(init=False, default=13)
    spell: IllusionSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel14(WizardSubclassLevel14):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.IllusoryReality())
        return data


@attr.dataclass
class IllusionistWizardLevel15(WizardSubclassLevel15):
    level: int = attr.field(init=False, default=15)
    spell: IllusionSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel17(WizardSubclassLevel17):
    level: int = attr.field(init=False, default=17)
    spell: IllusionSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardFeaturePerLevel(WizardFeaturePerLevel):
    subclass_level_3: Optional[IllusionistWizardLevel3] = None
    subclass_level_5: Optional[IllusionistWizardLevel5] = None
    subclass_level_6: Optional[IllusionistWizardLevel6] = None
    subclass_level_7: Optional[IllusionistWizardLevel7] = None
    subclass_level_9: Optional[IllusionistWizardLevel9] = None
    subclass_level_10: Optional[IllusionistWizardLevel10] = None
    subclass_level_11: Optional[IllusionistWizardLevel11] = None
    subclass_level_13: Optional[IllusionistWizardLevel13] = None
    subclass_level_14: Optional[IllusionistWizardLevel14] = None
    subclass_level_15: Optional[IllusionistWizardLevel15] = None
    subclass_level_17: Optional[IllusionistWizardLevel17] = None
