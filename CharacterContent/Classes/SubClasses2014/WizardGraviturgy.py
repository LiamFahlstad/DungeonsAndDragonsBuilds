from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import WizardSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Wizard import (
    WizardGraviturgyFeatures,
)


@attr.dataclass
class WizardGraviturgyLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(WizardGraviturgyFeatures.AdjustDensity())
        return data


@attr.dataclass
class WizardGraviturgyLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(WizardGraviturgyFeatures.GravityWell())
        return data


@attr.dataclass
class WizardGraviturgyLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(WizardGraviturgyFeatures.ViolentAttraction())
        return data


@attr.dataclass
class WizardGraviturgyLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(WizardGraviturgyFeatures.EventHorizon())
        return data


class WizardGraviturgyCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass2014.GRAVITURGY.value,
            skills=skills,
        )


class WizardGraviturgyMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass2014.GRAVITURGY.value,
            replace_spells=replace_spells,
        )
