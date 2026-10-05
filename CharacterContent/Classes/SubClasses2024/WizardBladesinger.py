from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import Skill, WizardSubclass
from CharacterContent.Features.SubClassFeatures.Wizard import WizardBladesingerFeatures


@attr.dataclass
class WizardBladesingerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WizardBladesingerFeatures.Bladesong())
        data.add_feature(
            WizardBladesingerFeatures.TrainingInWarAndSong(Skill.ATHLETICS)
        )
        return data


@attr.dataclass
class WizardBladesingerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WizardBladesingerFeatures.ExtraAttack())
        return data


@attr.dataclass
class WizardBladesingerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            WizardBladesingerFeatures.SongOfDefense(),
            extends=WizardBladesingerFeatures.Bladesong,
        )
        return data


@attr.dataclass
class WizardBladesingerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WizardBladesingerFeatures.SongOfVictory())
        return data


class WizardBladesingerCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass.BLADESINGER.value,
            skills=skills,
        )


class WizardBladesingerMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.BLADESINGER.value,
            replace_spells=replace_spells,
        )
