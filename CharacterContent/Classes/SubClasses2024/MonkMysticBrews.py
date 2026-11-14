from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import Ability, MonkSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Monk import MonkMysticBrewsFeatures
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures


@attr.dataclass
class MonkMysticBrewsLevel3(ClassBuilder.SubclassLevel3):
    # Performance, or a Monk skill if you already have Performance.
    bonus_skill: Skill = Skill.PERFORMANCE

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkMysticBrewsFeatures.BonusProficiencies(self.bonus_skill))
        data.add_feature(
            MonkMysticBrewsFeatures.DrunkenTechnique(),
            extends=MonkFeatures.MonksFocus,
        )


@attr.dataclass
class MonkMysticBrewsLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkMysticBrewsFeatures.TipsySway())
        data.add_feature(MonkMysticBrewsFeatures.MysticBrew())


@attr.dataclass
class MonkMysticBrewsLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            MonkMysticBrewsFeatures.WizenedBrewer(),
            extends=MonkMysticBrewsFeatures.MysticBrew,
        )


@attr.dataclass
class MonkMysticBrewsLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            MonkMysticBrewsFeatures.MasterBrewer(),
            extends=MonkMysticBrewsFeatures.MysticBrew,
        )
        data.add_feature(
            MonkMysticBrewsFeatures.IntoxicatedFrenzy(),
            extends=MonkFeatures.MonksFocus,
        )


class MonkMysticBrewsCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.MYSTIC_BREWS.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkMysticBrewsMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.MYSTIC_BREWS.value,
            replace_spells=replace_spells,
        )
