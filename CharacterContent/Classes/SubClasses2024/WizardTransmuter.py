from typing import Optional, TypeAlias

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import WizardSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Wizard import WizardTransmuterFeatures
from CharacterContent.Spells.SpellLists import (
    TransmutationLevel1Spells,
    TransmutationLevel2Spells,
    TransmutationLevel3Spells,
    TransmutationLevel4Spells,
    TransmutationLevel5Spells,
    TransmutationLevel6Spells,
    TransmutationLevel7Spells,
    TransmutationLevel8Spells,
    TransmutationLevel9Spells,
)

TransmutationSpellsUpTo2: TypeAlias = (
    TransmutationLevel1Spells | TransmutationLevel2Spells
)

TransmutationSpellsUpTo3: TypeAlias = (
    TransmutationSpellsUpTo2 | TransmutationLevel3Spells
)

TransmutationSpellsUpTo4: TypeAlias = (
    TransmutationSpellsUpTo3 | TransmutationLevel4Spells
)

TransmutationSpellsUpTo5: TypeAlias = (
    TransmutationSpellsUpTo4 | TransmutationLevel5Spells
)

TransmutationSpellsUpTo6: TypeAlias = (
    TransmutationSpellsUpTo5 | TransmutationLevel6Spells
)

TransmutationSpellsUpTo7: TypeAlias = (
    TransmutationSpellsUpTo6 | TransmutationLevel7Spells
)

TransmutationSpellsUpTo8: TypeAlias = (
    TransmutationSpellsUpTo7 | TransmutationLevel8Spells
)

TransmutationSpellsUpTo9: TypeAlias = (
    TransmutationSpellsUpTo8 | TransmutationLevel9Spells
)


@attr.dataclass
class WizardTransmuterLevel3(ClassBuilder.SubclassLevel3):
    spell_1: TransmutationSpellsUpTo2
    spell_2: TransmutationSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardTransmuterFeatures.TransmutationSavant())
        data.add_feature(WizardTransmuterFeatures.TransmutersStone())
        data.add_feature(WizardTransmuterFeatures.WondrousAlteration())
        data.add_spell(
            TransmutationLevel2Spells.ALTER_SELF,
            additional_ruling="Always prepared; cast once without a spell slot per Long Rest",
        )
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)


@attr.dataclass
class WizardTransmuterLevel5(ClassBuilder.SubclassLevel5):
    spell: TransmutationSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class WizardTransmuterLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardTransmuterFeatures.EmpoweredTransmutation())


@attr.dataclass
class WizardTransmuterLevel7(ClassBuilder.SubclassLevel7):
    spell: TransmutationSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class WizardTransmuterLevel9(ClassBuilder.SubclassLevel9):
    spell: TransmutationSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class WizardTransmuterLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            WizardTransmuterFeatures.PotentStone(),
            extends=WizardTransmuterFeatures.TransmutersStone,
        )
        data.add_feature(WizardTransmuterFeatures.ShapeShifter())
        data.add_spell(
            TransmutationLevel4Spells.POLYMORPH,
            additional_ruling="Always prepared; cast once without a spell slot per Long Rest",
        )


@attr.dataclass
class WizardTransmuterLevel11(ClassBuilder.SubclassLevel11):
    spell: TransmutationSpellsUpTo6

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class WizardTransmuterLevel13(ClassBuilder.SubclassLevel13):
    spell: TransmutationSpellsUpTo7

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class WizardTransmuterLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            WizardTransmuterFeatures.MasterTransmuter(),
            extends=WizardTransmuterFeatures.TransmutersStone,
        )


@attr.dataclass
class WizardTransmuterLevel15(ClassBuilder.SubclassLevel15):
    spell: TransmutationSpellsUpTo8

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class WizardTransmuterLevel17(ClassBuilder.SubclassLevel17):
    spell: TransmutationSpellsUpTo8

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


class WizardTransmuterCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass.TRANSMUTER.value,
            skills=skills,
        )


class WizardTransmuterMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.TRANSMUTER.value,
            replace_spells=replace_spells,
        )
