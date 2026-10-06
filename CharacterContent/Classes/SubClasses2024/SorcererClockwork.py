from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import SorcererSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Sorcerer import (
    SorcererClockworkFeatures,
)
from CharacterContent.Spells.SpellLists import (
    AbjurationLevel1Spells,
    AbjurationLevel2Spells,
    AbjurationLevel4Spells,
    AbjurationLevel5Spells,
    ConjurationLevel4Spells,
    EvocationLevel5Spells,
    SorcererLevel3Spells,
)


@attr.dataclass
class SorcererClockworkLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(SorcererClockworkFeatures.ClockworkSpells())
        data.add_spell(AbjurationLevel2Spells.AID)
        data.add_spell(AbjurationLevel1Spells.ALARM)
        data.add_spell(AbjurationLevel2Spells.LESSER_RESTORATION)
        data.add_spell(AbjurationLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD)
        data.add_feature(SorcererClockworkFeatures.RestoreBalance())


@attr.dataclass
class SorcererClockworkLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(SorcererLevel3Spells.DISPEL_MAGIC)
        data.add_spell(SorcererLevel3Spells.PROTECTION_FROM_ENERGY)


@attr.dataclass
class SorcererClockworkLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(SorcererClockworkFeatures.BastionOfLaw())


@attr.dataclass
class SorcererClockworkLevel7(ClassBuilder.SubclassLevel7):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(AbjurationLevel4Spells.FREEDOM_OF_MOVEMENT)
        data.add_spell(ConjurationLevel4Spells.SUMMON_CONSTRUCT)


@attr.dataclass
class SorcererClockworkLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(AbjurationLevel5Spells.GREATER_RESTORATION)
        data.add_spell(EvocationLevel5Spells.WALL_OF_FORCE)


@attr.dataclass
class SorcererClockworkLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(SorcererClockworkFeatures.TranceOfOrder())


@attr.dataclass
class SorcererClockworkLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(SorcererClockworkFeatures.ClockworkCavalcade())


class SorcererClockworkCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=SorcererSubclass.CLOCKWORK.value,
            skills=skills,
        )


class SorcererClockworkMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.CLOCKWORK.value,
            replace_spells=replace_spells,
        )
