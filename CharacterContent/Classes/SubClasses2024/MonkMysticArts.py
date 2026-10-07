from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import Ability, MonkSubclass, Skill
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.SubClassFeatures.Monk import MonkMysticArtsFeatures


@attr.dataclass
class MonkMysticArtsLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkMysticArtsFeatures.MysticArtsSpellcasting())


@attr.dataclass
class MonkMysticArtsLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkMysticArtsFeatures.MysticFightingStyle())
        data.add_feature(
            MonkMysticArtsFeatures.MysticFocus(), extends=MonkFeatures.MonksFocus
        )


@attr.dataclass
class MonkMysticArtsLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkMysticArtsFeatures.FocusedStrike())


@attr.dataclass
class MonkMysticArtsLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            MonkMysticArtsFeatures.ImprovedMysticFightingStyle(),
            extends=MonkMysticArtsFeatures.MysticFightingStyle,
        )


class MonkMysticArtsCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.MYSTIC_ARTS.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )


class MonkMysticArtsMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.MYSTIC_ARTS.value,
            replace_spells=replace_spells,
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )
