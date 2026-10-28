from typing import Optional, TypeAlias

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import WizardSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Wizard import WizardNecromancerFeatures
from CharacterContent.Spells.SpellLists import (
    NecromancyLevel1Spells,
    NecromancyLevel2Spells,
    NecromancyLevel3Spells,
    NecromancyLevel4Spells,
    NecromancyLevel5Spells,
    NecromancyLevel6Spells,
    NecromancyLevel7Spells,
    NecromancyLevel8Spells,
    NecromancyLevel9Spells,
)
from Model.CharacterSources import SpellSource

NecromancySpellsUpTo2: TypeAlias = NecromancyLevel1Spells | NecromancyLevel2Spells

NecromancySpellsUpTo3: TypeAlias = NecromancySpellsUpTo2 | NecromancyLevel3Spells

NecromancySpellsUpTo4: TypeAlias = NecromancySpellsUpTo3 | NecromancyLevel4Spells

NecromancySpellsUpTo5: TypeAlias = NecromancySpellsUpTo4 | NecromancyLevel5Spells

NecromancySpellsUpTo6: TypeAlias = NecromancySpellsUpTo5 | NecromancyLevel6Spells

NecromancySpellsUpTo7: TypeAlias = NecromancySpellsUpTo6 | NecromancyLevel7Spells

NecromancySpellsUpTo8: TypeAlias = NecromancySpellsUpTo7 | NecromancyLevel8Spells

NecromancySpellsUpTo9: TypeAlias = NecromancySpellsUpTo8 | NecromancyLevel9Spells


@attr.dataclass
class WizardNecromancerLevel3(ClassBuilder.SubclassLevel3):
    spell_1: NecromancySpellsUpTo2
    spell_2: NecromancySpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardNecromancerFeatures.NecromancySavant())
        data.add_feature(WizardNecromancerFeatures.NecromancySpellbook())
        data.add_spell(self.spell_1, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_2, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardNecromancerLevel5(ClassBuilder.SubclassLevel5):
    spell: NecromancySpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardNecromancerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardNecromancerFeatures.GravePower())
        data.add_feature(WizardNecromancerFeatures.UndeadThralls())


@attr.dataclass
class WizardNecromancerLevel7(ClassBuilder.SubclassLevel7):
    spell: NecromancySpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardNecromancerLevel9(ClassBuilder.SubclassLevel9):
    spell: NecromancySpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardNecromancerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardNecromancerFeatures.HarvestUndead())


@attr.dataclass
class WizardNecromancerLevel11(ClassBuilder.SubclassLevel11):
    spell: NecromancySpellsUpTo6

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardNecromancerLevel13(ClassBuilder.SubclassLevel13):
    spell: NecromancySpellsUpTo7

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardNecromancerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardNecromancerFeatures.DeathsMaster())


@attr.dataclass
class WizardNecromancerLevel15(ClassBuilder.SubclassLevel15):
    spell: NecromancySpellsUpTo8

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardNecromancerLevel17(ClassBuilder.SubclassLevel17):
    spell: NecromancySpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


class WizardNecromancerCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass.NECROMANCER.value,
            skills=skills,
        )


class WizardNecromancerMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.NECROMANCER.value,
            replace_spells=replace_spells,
        )
