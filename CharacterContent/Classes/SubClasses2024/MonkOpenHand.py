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
from CharacterContent.Features.SubClassFeatures.Monk import MonkOpenHandFeatures


@attr.dataclass
class MonkOpenHandLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkOpenHandFeatures.OpenHandTechnique())


@attr.dataclass
class MonkOpenHandLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkOpenHandFeatures.WholenessOfBody())


@attr.dataclass
class MonkOpenHandLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkOpenHandFeatures.FleetStep())


@attr.dataclass
class MonkOpenHandLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkOpenHandFeatures.QuiveringPalm())


class MonkOpenHandCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.OPEN_HAND.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkOpenHandMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.OPEN_HAND.value,
            replace_spells=replace_spells,
        )
