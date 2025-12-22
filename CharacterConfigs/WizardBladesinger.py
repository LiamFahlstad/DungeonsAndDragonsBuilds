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
class BladesingerWizardLevel3(WizardSubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.Bladesong())
        data.add_feature(WizardFeatures.ArcaneWard())
        return data


@attr.dataclass
class BladesingerWizardLevel5(WizardSubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BladesingerWizardLevel6(WizardSubclassLevel6):
    level: int = attr.field(init=False, default=6)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.ExtraAttack())
        return data


@attr.dataclass
class BladesingerWizardLevel7(WizardSubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BladesingerWizardLevel9(WizardSubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BladesingerWizardLevel10(WizardSubclassLevel10):
    level: int = attr.field(init=False, default=10)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SongOfDefense())
        return data


@attr.dataclass
class BladesingerWizardLevel11(WizardSubclassLevel11):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BladesingerWizardLevel13(WizardSubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BladesingerWizardLevel14(WizardSubclassLevel14):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SongOfVictory())
        return data


@attr.dataclass
class BladesingerWizardLevel15(WizardSubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BladesingerWizardLevel17(WizardSubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BladesingerWizardFeaturePerLevel(WizardFeaturePerLevel):
    subclass_level_3: Optional[BladesingerWizardLevel3] = None
    subclass_level_5: Optional[BladesingerWizardLevel5] = None
    subclass_level_6: Optional[BladesingerWizardLevel6] = None
    subclass_level_7: Optional[BladesingerWizardLevel7] = None
    subclass_level_9: Optional[BladesingerWizardLevel9] = None
    subclass_level_10: Optional[BladesingerWizardLevel10] = None
    subclass_level_11: Optional[BladesingerWizardLevel11] = None
    subclass_level_13: Optional[BladesingerWizardLevel13] = None
    subclass_level_14: Optional[BladesingerWizardLevel14] = None
    subclass_level_15: Optional[BladesingerWizardLevel15] = None
    subclass_level_17: Optional[BladesingerWizardLevel17] = None
