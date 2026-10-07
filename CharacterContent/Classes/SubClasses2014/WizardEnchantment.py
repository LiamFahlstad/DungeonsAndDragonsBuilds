from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import WizardSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Wizard import (
    WizardEnchantmentFeatures,
)


@attr.dataclass
class WizardEnchantmentLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardEnchantmentFeatures.EnchantmentSavant())
        data.add_feature(WizardEnchantmentFeatures.HypnoticGaze())


@attr.dataclass
class WizardEnchantmentLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardEnchantmentFeatures.InstinctiveCharm())


@attr.dataclass
class WizardEnchantmentLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardEnchantmentFeatures.SplitEnchantment())


@attr.dataclass
class WizardEnchantmentLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WizardEnchantmentFeatures.AlterMemories())


class WizardEnchantmentCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WizardSubclass2014.ENCHANTMENT.value,
            skills=skills,
        )


class WizardEnchantmentMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass2014.ENCHANTMENT.value,
            replace_spells=replace_spells,
        )
