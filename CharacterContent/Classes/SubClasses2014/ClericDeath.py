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
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericDeathFeatures


@attr.dataclass
class ClericDeathLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericDeathFeatures.BonusProficiency())
        data.add_feature(ClericDeathFeatures.Reaper())
        data.add_feature(ClericDeathFeatures.DeathDomainSpells())
        data.add_feature(ClericDeathFeatures.TouchOfDeathChannelDivinity())


@attr.dataclass
class ClericDeathLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericDeathFeatures.InescapableDestruction(),
            extends=ClericDeathFeatures.TouchOfDeathChannelDivinity,
        )


@attr.dataclass
class ClericDeathLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericDeathFeatures.ImprovedReaper(), extends=ClericDeathFeatures.Reaper
        )


class ClericDeathCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass2014.DEATH.value,
            skills=skills,
        )


class ClericDeathMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.DEATH.value,
            replace_spells=replace_spells,
        )
