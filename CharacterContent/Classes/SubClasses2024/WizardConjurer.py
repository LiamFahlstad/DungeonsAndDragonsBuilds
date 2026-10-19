from typing import Optional, TypeAlias

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import WizardSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Wizard import WizardConjurerFeatures
from CharacterContent.Spells.SpellLists import (
    ConjurationLevel1Spells,
    ConjurationLevel2Spells,
    ConjurationLevel3Spells,
    ConjurationLevel4Spells,
    ConjurationLevel5Spells,
    ConjurationLevel6Spells,
    ConjurationLevel7Spells,
    ConjurationLevel8Spells,
    ConjurationLevel9Spells,
)
from Model.CharacterSources import SpellSource

ConjurationSpellsUpTo2: TypeAlias = ConjurationLevel1Spells | ConjurationLevel2Spells

ConjurationSpellsUpTo3: TypeAlias = ConjurationSpellsUpTo2 | ConjurationLevel3Spells

ConjurationSpellsUpTo4: TypeAlias = ConjurationSpellsUpTo3 | ConjurationLevel4Spells

ConjurationSpellsUpTo5: TypeAlias = ConjurationSpellsUpTo4 | ConjurationLevel5Spells

ConjurationSpellsUpTo6: TypeAlias = ConjurationSpellsUpTo5 | ConjurationLevel6Spells

ConjurationSpellsUpTo7: TypeAlias = ConjurationSpellsUpTo6 | ConjurationLevel7Spells

ConjurationSpellsUpTo8: TypeAlias = ConjurationSpellsUpTo7 | ConjurationLevel8Spells

ConjurationSpellsUpTo9: TypeAlias = ConjurationSpellsUpTo8 | ConjurationLevel9Spells


@attr.dataclass
class WizardConjurerLevel3(ClassBuilder.SubclassLevel3):
    spell_1: ConjurationSpellsUpTo2
    spell_2: ConjurationSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardConjurerFeatures.BenignTransposition())
        data.add_feature(WizardConjurerFeatures.ConjurationSavant())
        data.add_spell(self.spell_1, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_2, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardConjurerLevel5(ClassBuilder.SubclassLevel5):
    spell: ConjurationSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardConjurerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            WizardConjurerFeatures.DistantTransposition(),
            extends=WizardConjurerFeatures.BenignTransposition,
        )
        data.add_feature(WizardConjurerFeatures.DurableSummons())


@attr.dataclass
class WizardConjurerLevel7(ClassBuilder.SubclassLevel7):
    spell: ConjurationSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardConjurerLevel9(ClassBuilder.SubclassLevel9):
    spell: ConjurationSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardConjurerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardConjurerFeatures.FocusedConjuration())


@attr.dataclass
class WizardConjurerLevel11(ClassBuilder.SubclassLevel11):
    spell: ConjurationSpellsUpTo6

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardConjurerLevel13(ClassBuilder.SubclassLevel13):
    spell: ConjurationSpellsUpTo7

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardConjurerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardConjurerFeatures.SplinteredSummons())


@attr.dataclass
class WizardConjurerLevel15(ClassBuilder.SubclassLevel15):
    spell: ConjurationSpellsUpTo8

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class WizardConjurerLevel17(ClassBuilder.SubclassLevel17):
    spell: ConjurationSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


class WizardConjurerCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass.CONJURER.value,
            skills=skills,
        )


class WizardConjurerMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.CONJURER.value,
            replace_spells=replace_spells,
        )
