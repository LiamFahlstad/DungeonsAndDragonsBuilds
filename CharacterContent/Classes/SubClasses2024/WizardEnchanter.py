from typing import Optional, TypeAlias

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import WizardSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Wizard import WizardEnchanterFeatures
from CharacterContent.Spells.SpellLists import (
    EnchantmentLevel1Spells,
    EnchantmentLevel2Spells,
    EnchantmentLevel3Spells,
    EnchantmentLevel4Spells,
    EnchantmentLevel5Spells,
    EnchantmentLevel6Spells,
    EnchantmentLevel7Spells,
    EnchantmentLevel8Spells,
    EnchantmentLevel9Spells,
)
from Model.CharacterSources import SpellSource

EnchantmentSpellsUpTo2: TypeAlias = EnchantmentLevel1Spells | EnchantmentLevel2Spells

EnchantmentSpellsUpTo3: TypeAlias = EnchantmentSpellsUpTo2 | EnchantmentLevel3Spells

EnchantmentSpellsUpTo4: TypeAlias = EnchantmentSpellsUpTo3 | EnchantmentLevel4Spells

EnchantmentSpellsUpTo5: TypeAlias = EnchantmentSpellsUpTo4 | EnchantmentLevel5Spells

EnchantmentSpellsUpTo6: TypeAlias = EnchantmentSpellsUpTo5 | EnchantmentLevel6Spells

EnchantmentSpellsUpTo7: TypeAlias = EnchantmentSpellsUpTo6 | EnchantmentLevel7Spells

EnchantmentSpellsUpTo8: TypeAlias = EnchantmentSpellsUpTo7 | EnchantmentLevel8Spells

EnchantmentSpellsUpTo9: TypeAlias = EnchantmentSpellsUpTo8 | EnchantmentLevel9Spells


@attr.dataclass
class WizardEnchanterLevel3(ClassBuilder.SubclassLevel3):
    skill: Skill
    spell_1: EnchantmentSpellsUpTo2
    spell_2: EnchantmentSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            WizardEnchanterFeatures.EnchantingConversationalist(self.skill)
        )
        data.add_feature(WizardEnchanterFeatures.EnchantmentSavant())
        data.add_feature(WizardEnchanterFeatures.HypnoticPresence())
        data.add_spell(self.spell_1, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_2, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardEnchanterLevel5(ClassBuilder.SubclassLevel5):
    spell: EnchantmentSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardEnchanterLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardEnchanterFeatures.SplitEnchantment())


@attr.dataclass
class WizardEnchanterLevel7(ClassBuilder.SubclassLevel7):
    spell: EnchantmentSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardEnchanterLevel9(ClassBuilder.SubclassLevel9):
    spell: EnchantmentSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardEnchanterLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardEnchanterFeatures.InstinctiveCharm())


@attr.dataclass
class WizardEnchanterLevel11(ClassBuilder.SubclassLevel11):
    spell: EnchantmentSpellsUpTo6

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardEnchanterLevel13(ClassBuilder.SubclassLevel13):
    spell: EnchantmentSpellsUpTo7

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardEnchanterLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardEnchanterFeatures.AlterMemories())


@attr.dataclass
class WizardEnchanterLevel15(ClassBuilder.SubclassLevel15):
    spell: EnchantmentSpellsUpTo8

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardEnchanterLevel17(ClassBuilder.SubclassLevel17):
    spell: EnchantmentSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


class WizardEnchanterCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass.ENCHANTER.value,
            skills=skills,
        )


class WizardEnchanterMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.ENCHANTER.value,
            replace_spells=replace_spells,
        )
