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
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericArcanaFeatures


@attr.dataclass
class ClericArcanaLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericArcanaFeatures.ArcaneInitiate())
        data.add_feature(ClericArcanaFeatures.ArcanaDomainSpells())
        data.add_feature(ClericArcanaFeatures.ArcaneAbjurationChannelDivinity())


@attr.dataclass
class ClericArcanaLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericArcanaFeatures.SpellBreaker())


@attr.dataclass
class ClericArcanaLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericArcanaFeatures.ArcaneMastery(),
            extends=ClericArcanaFeatures.ArcanaDomainSpells,
        )


class ClericArcanaCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass2014.ARCANA.value,
            skills=skills,
        )


class ClericArcanaMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.ARCANA.value,
            replace_spells=replace_spells,
        )
