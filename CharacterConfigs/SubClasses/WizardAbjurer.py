from typing import Optional, TypeAlias

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WizardSubclass
from Features.ClassFeatures.Wizard import WizardAbjurerFeatures
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
)
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock

AbjurationSpellsUpTo2: TypeAlias = AbjurationLevel1Spells | AbjurationLevel2Spells

AbjurationSpellsUpTo3: TypeAlias = AbjurationSpellsUpTo2 | AbjurationLevel3Spells

AbjurationSpellsUpTo4: TypeAlias = AbjurationSpellsUpTo3 | AbjurationLevel4Spells

AbjurationSpellsUpTo5: TypeAlias = AbjurationSpellsUpTo4 | AbjurationLevel5Spells

AbjurationSpellsUpTo6: TypeAlias = AbjurationSpellsUpTo5 | AbjurationLevel6Spells

AbjurationSpellsUpTo7: TypeAlias = AbjurationSpellsUpTo6 | AbjurationLevel7Spells

AbjurationSpellsUpTo8: TypeAlias = AbjurationSpellsUpTo7 | AbjurationLevel8Spells

AbjurationSpellsUpTo9: TypeAlias = AbjurationSpellsUpTo8 | AbjurationLevel9Spells


@attr.dataclass
class AbjurerWizardLevel3(ClassBuilder.SubclassLevel3):
    spell_1: AbjurationSpellsUpTo2
    spell_2: AbjurationSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardAbjurerFeatures.AbjurationSavant())
        data.add_feature(WizardAbjurerFeatures.ArcaneWard())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class AbjurerWizardLevel5(ClassBuilder.SubclassLevel5):
    spell: AbjurationSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardAbjurerFeatures.ProjectedWard())
        return data


@attr.dataclass
class AbjurerWizardLevel7(ClassBuilder.SubclassLevel7):
    spell: AbjurationSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel9(ClassBuilder.SubclassLevel9):
    spell: AbjurationSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardAbjurerFeatures.SpellBreaker())
        data.add_spell(AbjurationLevel3Spells.COUNTERSPELL)
        data.add_spell(AbjurationLevel3Spells.DISPEL_MAGIC)
        return data


@attr.dataclass
class AbjurerWizardLevel11(ClassBuilder.SubclassLevel11):
    spell: AbjurationSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel13(ClassBuilder.SubclassLevel13):
    spell: AbjurationSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardAbjurerFeatures.SpellResistance())
        return data


@attr.dataclass
class AbjurerWizardLevel15(ClassBuilder.SubclassLevel15):
    spell: AbjurationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class AbjurerWizardLevel17(ClassBuilder.SubclassLevel17):
    spell: AbjurationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


class AbjurerWizardCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass.ABJURER.value,
            skills=skills,
        )


class AbjurerWizardMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.ABJURER.value,
            replace_spells=replace_spells,
        )
