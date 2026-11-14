from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import ClericSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Cleric import ClericDisciplineFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Spells.SpellLists import (
    AbjurationLevel2Spells,
    ClericLevel1Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    EvocationLevel5Spells,
    PaladinLevel2Spells,
    DruidLevel4Spells,
)


@attr.dataclass
class ClericDisciplineLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(AbjurationLevel2Spells.ARCANE_VIGOR)
        data.add_spell(ClericLevel1Spells.GUIDING_BOLT)
        data.add_spell(PaladinLevel2Spells.MAGIC_WEAPON)
        data.add_spell(ClericLevel1Spells.SHIELD_OF_FAITH)
        data.add_feature(ClericDisciplineFeatures.DisciplineDomainSpells())
        data.add_feature(
            ClericDisciplineFeatures.HolyBolt(),
            extends=ClericFeatures.ChannelDivinity,
        )
        data.add_feature(ClericDisciplineFeatures.Atonement())


@attr.dataclass
class ClericDisciplineLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ClericLevel3Spells.PRAYER_OF_MENDING)
        data.add_spell(ClericLevel3Spells.PROTECTION_FROM_ENERGY)


@attr.dataclass
class ClericDisciplineLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericDisciplineFeatures.LuminousBarrier(),
            extends=ClericFeatures.ChannelDivinity,
        )


@attr.dataclass
class ClericDisciplineLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ClericLevel4Spells.GUARDIAN_OF_FAITH)
        data.add_spell(DruidLevel4Spells.STONESKIN)


@attr.dataclass
class ClericDisciplineLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ClericLevel5Spells.CIRCLE_OF_POWER)
        data.add_spell(EvocationLevel5Spells.DESTRUCTIVE_WAVE)


@attr.dataclass
class ClericDisciplineLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # Holy Bolt is a Channel Divinity extension, which a type parent can't
        # match, so its upgrade is granted on its own.
        data.add_feature(ClericDisciplineFeatures.UltimatePenitence())


class ClericDisciplineCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass.DISCIPLINE.value,
            skills=skills,
        )


class ClericDisciplineMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.DISCIPLINE.value,
            replace_spells=replace_spells,
        )
