from typing import Optional, TypeAlias

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WizardSubclass
from Features.ClassFeatures import WizardEvokerFeatures
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
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock

EvocationSpellsUpTo2: TypeAlias = EvocationLevel1Spells | EvocationLevel2Spells

EvocationSpellsUpTo3: TypeAlias = EvocationSpellsUpTo2 | EvocationLevel3Spells

EvocationSpellsUpTo4: TypeAlias = EvocationSpellsUpTo3 | EvocationLevel4Spells

EvocationSpellsUpTo5: TypeAlias = EvocationSpellsUpTo4 | EvocationLevel5Spells

EvocationSpellsUpTo6: TypeAlias = EvocationSpellsUpTo5 | EvocationLevel6Spells

EvocationSpellsUpTo7: TypeAlias = EvocationSpellsUpTo6 | EvocationLevel7Spells

EvocationSpellsUpTo8: TypeAlias = EvocationSpellsUpTo7 | EvocationLevel8Spells

EvocationSpellsUpTo9: TypeAlias = EvocationSpellsUpTo8 | EvocationLevel9Spells


@attr.dataclass
class EvokerWizardLevel3(ClassBuilder.SubclassLevel3):
    spell_1: EvocationSpellsUpTo2
    spell_2: EvocationSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvokerFeatures.EvocationSavant())
        data.add_feature(WizardEvokerFeatures.PotentCantrip())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class EvokerWizardLevel5(ClassBuilder.SubclassLevel5):
    spell: EvocationSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvokerFeatures.SculptSpells())
        return data


@attr.dataclass
class EvokerWizardLevel7(ClassBuilder.SubclassLevel7):
    spell: EvocationSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel9(ClassBuilder.SubclassLevel9):
    spell: EvocationSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvokerFeatures.EmpoweredEvocation())
        return data


@attr.dataclass
class EvokerWizardLevel11(ClassBuilder.SubclassLevel11):
    spell: EvocationSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel13(ClassBuilder.SubclassLevel13):
    spell: EvocationSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvokerFeatures.Overchannel())
        return data


@attr.dataclass
class EvokerWizardLevel15(ClassBuilder.SubclassLevel15):
    spell: EvocationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class EvokerWizardLevel17(ClassBuilder.SubclassLevel17):
    spell: EvocationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


class EvokerWizardCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass.EVOKER.value,
            skills=skills,
        )


class EvokerWizardMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.EVOKER.value,
            replace_spells=replace_spells,
        )
