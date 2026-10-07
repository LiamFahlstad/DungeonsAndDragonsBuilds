from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import WarlockSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Warlock import WarlockFiendFeatures
from CharacterContent.Spells.SpellLists import (
    BardLevel1Spells,
    BardLevel5Spells,
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    WarlockLevel2Spells,
)


@attr.dataclass
class WarlockFiendLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WarlockFiendFeatures.FiendSpells())
        data.add_feature(WarlockFiendFeatures.DarkOnesBlessing())
        data.add_spell(SorcererLevel1Spells.BURNING_HANDS)
        data.add_spell(BardLevel1Spells.COMMAND)
        data.add_spell(SorcererLevel2Spells.SCORCHING_RAY)
        data.add_spell(WarlockLevel2Spells.SUGGESTION)


@attr.dataclass
class WarlockFiendLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(SorcererLevel3Spells.FIREBALL)
        data.add_spell(SorcererLevel3Spells.STINKING_CLOUD)


@attr.dataclass
class WarlockFiendLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WarlockFiendFeatures.DarkOnesOwnLuck())


@attr.dataclass
class WarlockFiendLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(SorcererLevel4Spells.FIRE_SHIELD)
        data.add_spell(SorcererLevel4Spells.WALL_OF_FIRE)


@attr.dataclass
class WarlockFiendLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(BardLevel5Spells.GEAS)
        data.add_spell(SorcererLevel5Spells.INSECT_PLAGUE)


@attr.dataclass
class WarlockFiendLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WarlockFiendFeatures.FiendishResilience())


@attr.dataclass
class WarlockFiendLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(WarlockFiendFeatures.HurlThroughHell())


class WarlockFiendCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_FIEND.value,
            skills=skills,
        )


class WarlockFiendMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_FIEND.value,
            replace_spells=replace_spells,
        )
