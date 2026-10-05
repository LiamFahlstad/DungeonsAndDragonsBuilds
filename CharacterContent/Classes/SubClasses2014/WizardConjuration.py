from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import WizardSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Wizard import (
    WizardConjurationFeatures,
)


@attr.dataclass
class WizardConjurationLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WizardConjurationFeatures.ConjurationSavant())
        data.add_feature(WizardConjurationFeatures.MinorConjuration())
        return data


@attr.dataclass
class WizardConjurationLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WizardConjurationFeatures.BenignTransportation())
        return data


@attr.dataclass
class WizardConjurationLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WizardConjurationFeatures.FocusedConjuration())
        return data


@attr.dataclass
class WizardConjurationLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WizardConjurationFeatures.DurableSummons())
        return data


class WizardConjurationCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass2014.CONJURATION.value,
            skills=skills,
        )


class WizardConjurationMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass2014.CONJURATION.value,
            replace_spells=replace_spells,
        )
