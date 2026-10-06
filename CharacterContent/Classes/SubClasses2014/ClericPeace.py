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
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericPeaceFeatures


@attr.dataclass
class ClericPeaceLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericPeaceFeatures.ImplementOfPeace())
        data.add_feature(ClericPeaceFeatures.PeaceDomainSpells())
        data.add_feature(ClericPeaceFeatures.EmboldeningBond())
        data.add_feature(ClericPeaceFeatures.BalmOfPeaceChannelDivinity())


@attr.dataclass
class ClericPeaceLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericPeaceFeatures.ProtectiveBond(),
            extends=ClericPeaceFeatures.EmboldeningBond,
        )


@attr.dataclass
class ClericPeaceLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericPeaceFeatures.ExpansiveBond(),
            extends=ClericPeaceFeatures.EmboldeningBond,
        )


class ClericPeaceCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass2014.PEACE.value,
            skills=skills,
        )


class ClericPeaceMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.PEACE.value,
            replace_spells=replace_spells,
        )
