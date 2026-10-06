from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import ClericSubclass2014, Skill
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericOrderFeatures
from Model.FeatureGrants import IfParentMissing


@attr.dataclass
class ClericOrderLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericOrderFeatures.BonusProficiencies())
        data.add_feature(ClericOrderFeatures.VoiceOfAuthority())
        data.add_feature(ClericOrderFeatures.OrderDomainSpells())
        data.add_feature(ClericOrderFeatures.OrdersDemandChannelDivinity())


@attr.dataclass
class ClericOrderLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericOrderFeatures.EmbodimentOfTheLaw())


@attr.dataclass
class ClericOrderLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # The 2024 base Cleric's Blessed Strikes replaces the 2014 domain's own
        # Divine Strike, so Order's Wrath rides on that when it was chosen.
        data.add_feature(
            ClericOrderFeatures.OrdersWrath(),
            extends=ClericFeatures.DivineStrike,
            if_missing=IfParentMissing.STANDALONE,
        )


class ClericOrderCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass2014.ORDER.value,
            skills=skills,
        )


class ClericOrderMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.ORDER.value,
            replace_spells=replace_spells,
        )
