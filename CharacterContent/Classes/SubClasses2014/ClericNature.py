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
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericNatureFeatures


@attr.dataclass
class ClericNatureLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericNatureFeatures.AcolyteOfNature())
        data.add_feature(ClericNatureFeatures.BonusProficiency())
        data.add_feature(ClericNatureFeatures.NatureDomainSpells())
        data.add_feature(ClericNatureFeatures.CharmAnimalsAndPlantsChannelDivinity())


@attr.dataclass
class ClericNatureLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericNatureFeatures.DampenElements())


@attr.dataclass
class ClericNatureLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericNatureFeatures.MasterOfNature(),
            extends=ClericNatureFeatures.CharmAnimalsAndPlantsChannelDivinity,
        )


class ClericNatureCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass2014.NATURE.value,
            skills=skills,
        )


class ClericNatureMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.NATURE.value,
            replace_spells=replace_spells,
        )
