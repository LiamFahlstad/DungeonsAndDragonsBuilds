from typing import Optional

import attr

from Model.Character import Character
from Model.Grants import Grants
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkCustomStarterClassArgs,
    MonkMulticlassBuilder,
)
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.SubClassFeatures.Monk import MonkElementsFeatures
from CharacterContent.Spells.SpellLists import DruidLevel0Spells
from Core.Definitions import Ability, MonkSubclass, Skill


@attr.dataclass
class MonkElementsLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            MonkElementsFeatures.ElementalAttunement(), extends=MonkFeatures.MonksFocus
        )
        data.add_feature(MonkElementsFeatures.ManipulateElements())
        data.add_cantrip(DruidLevel0Spells.ELEMENTALISM, Ability.WISDOM)
        return data


@attr.dataclass
class MonkElementsLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            MonkElementsFeatures.ElementalBurst(), extends=MonkFeatures.MonksFocus
        )
        return data


@attr.dataclass
class MonkElementsLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            MonkElementsFeatures.StrideOfTheElements(), extends=MonkFeatures.MonksFocus
        )
        return data


@attr.dataclass
class MonkElementsLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            MonkElementsFeatures.ElementalEpitome(), extends=MonkFeatures.MonksFocus
        )
        return data


class MonkElementsCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.ELEMENTS.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkElementsMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.ELEMENTS.value,
            replace_spells=replace_spells,
        )
