from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import Ability, MonkSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Monk import MonkMercyFeatures


@attr.dataclass
class MonkMercyLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkMercyFeatures.HandOfHarm())
        data.add_feature(MonkMercyFeatures.HandOfHealing())
        data.add_feature(MonkMercyFeatures.ImplementsOfMercy())
        return data


@attr.dataclass
class MonkMercyLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            MonkMercyFeatures.PhysiciansTouch(), extends=MonkMercyFeatures.HandOfHarm
        )
        return data


@attr.dataclass
class MonkMercyLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkMercyFeatures.FlurryOfHealingAndHarm())
        return data


@attr.dataclass
class MonkMercyLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(MonkMercyFeatures.HandOfUltimateMercy())
        return data


class MonkMercyCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.MERCY.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkMercyMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.MERCY.value,
            replace_spells=replace_spells,
        )
