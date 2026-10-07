from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import Ability, MonkSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Monk import MonkShadowFeatures
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Spells.SpellLists import (
    EvocationLevel2Spells,
    IllusionLevel0Spells,
)


@attr.dataclass
class MonkShadowLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            MonkShadowFeatures.ShadowArts(), extends=MonkFeatures.MonksFocus
        )
        data.add_spell(
            EvocationLevel2Spells.DARKNESS,
            Ability.WISDOM,
            additional_ruling="Cast by expending 1 Focus Point instead of a spell slot",
        )
        data.add_cantrip(IllusionLevel0Spells.MINOR_ILLUSION, Ability.WISDOM)


@attr.dataclass
class MonkShadowLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkShadowFeatures.ShadowStep())


@attr.dataclass
class MonkShadowLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            MonkShadowFeatures.ImprovedShadowStep(),
            extends=MonkShadowFeatures.ShadowStep,
        )


@attr.dataclass
class MonkShadowLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            MonkShadowFeatures.CloakOfShadows(), extends=MonkFeatures.MonksFocus
        )


class MonkShadowCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.SHADOW.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkShadowMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.SHADOW.value,
            replace_spells=replace_spells,
        )
