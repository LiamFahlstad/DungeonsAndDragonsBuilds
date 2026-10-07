from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import ClericSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericTempestFeatures


@attr.dataclass
class ClericTempestLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericTempestFeatures.BonusProficiencies())
        data.add_feature(ClericTempestFeatures.WrathOfTheStorm())
        data.add_feature(ClericTempestFeatures.TempestDomainSpells())
        data.add_feature(ClericTempestFeatures.DestructiveWrathChannelDivinity())


@attr.dataclass
class ClericTempestLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericTempestFeatures.ThunderousStrike())


@attr.dataclass
class ClericTempestLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericTempestFeatures.Stormborn())


class ClericTempestCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass2014.TEMPEST.value,
            skills=skills,
        )


class ClericTempestMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.TEMPEST.value,
            replace_spells=replace_spells,
        )
