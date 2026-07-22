from typing import Optional, TypeAlias

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import WizardSubclass
from Features.SubClassFeatures.Wizard import WizardIllusionistFeatures
from Spells.SpellLists import (
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
)
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock

IllusionSpellsUpTo2: TypeAlias = IllusionLevel1Spells | IllusionLevel2Spells

IllusionSpellsUpTo3: TypeAlias = IllusionSpellsUpTo2 | IllusionLevel3Spells

IllusionSpellsUpTo4: TypeAlias = IllusionSpellsUpTo3 | IllusionLevel4Spells

IllusionSpellsUpTo5: TypeAlias = IllusionSpellsUpTo4 | IllusionLevel5Spells

IllusionSpellsUpTo6: TypeAlias = IllusionSpellsUpTo5 | IllusionLevel6Spells

IllusionSpellsUpTo7: TypeAlias = IllusionSpellsUpTo6 | IllusionLevel7Spells

IllusionSpellsUpTo8: TypeAlias = IllusionSpellsUpTo7 | IllusionLevel8Spells

IllusionSpellsUpTo9: TypeAlias = IllusionSpellsUpTo8 | IllusionLevel9Spells


@attr.dataclass
class IllusionistWizardLevel3(ClassBuilder.SubclassLevel3):
    spell_1: IllusionSpellsUpTo2
    spell_2: IllusionSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardIllusionistFeatures.IllusionSavant())
        data.add_feature(WizardIllusionistFeatures.ImprovedIllusions())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_cantrip(IllusionLevel0Spells.MINOR_ILLUSION)
        return data


@attr.dataclass
class IllusionistWizardLevel5(ClassBuilder.SubclassLevel5):
    spell: IllusionSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardIllusionistFeatures.PhantasmalCreatures())
        data.add_spell(ConjurationLevel2Spells.SUMMON_BEAST)
        data.add_spell(ConjurationLevel3Spells.SUMMON_FEY)
        return data


@attr.dataclass
class IllusionistWizardLevel7(ClassBuilder.SubclassLevel7):
    spell: IllusionSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel9(ClassBuilder.SubclassLevel9):
    spell: IllusionSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardIllusionistFeatures.IllusorySelf())
        return data


@attr.dataclass
class IllusionistWizardLevel11(ClassBuilder.SubclassLevel11):
    spell: IllusionSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel13(ClassBuilder.SubclassLevel13):
    spell: IllusionSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardIllusionistFeatures.IllusoryReality())
        return data


@attr.dataclass
class IllusionistWizardLevel15(ClassBuilder.SubclassLevel15):
    spell: IllusionSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class IllusionistWizardLevel17(ClassBuilder.SubclassLevel17):
    spell: IllusionSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


class IllusionistWizardCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass.ILLUSIONIST.value,
            skills=skills,
        )


class IllusionistWizardMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.ILLUSIONIST.value,
            replace_spells=replace_spells,
        )
