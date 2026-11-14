from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import PaladinSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Paladin import PaladinHolyFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel3Spells,
    ClericLevel5Spells,
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
)


@attr.dataclass
class PaladinHolyLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinHolyFeatures.BeaconOfLight(),
            extends=PaladinFeatures.ChannelDivinity,
        )
        data.add_spell(PaladinLevel1Spells.CURE_WOUNDS)
        data.add_spell(ClericLevel1Spells.HEALING_WORD)


@attr.dataclass
class PaladinHolyLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(PaladinLevel2Spells.LESSER_RESTORATION)
        data.add_spell(PaladinLevel2Spells.PRAYER_OF_HEALING)


@attr.dataclass
class PaladinHolyLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinHolyFeatures.LightbringersAura(),
            extends=PaladinFeatures.AuraOfProtection,
        )


@attr.dataclass
class PaladinHolyLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(PaladinLevel3Spells.DISPEL_MAGIC)
        data.add_spell(ClericLevel3Spells.MASS_HEALING_WORD)


@attr.dataclass
class PaladinHolyLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(PaladinLevel4Spells.AURA_OF_LIFE)
        data.add_spell(PaladinLevel4Spells.DEATH_WARD)


@attr.dataclass
class PaladinHolyLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinHolyFeatures.InfusionOfLight(),
            extends=PaladinFeatures.LayOnHands,
        )


@attr.dataclass
class PaladinHolyLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(PaladinLevel5Spells.GREATER_RESTORATION)
        data.add_spell(ClericLevel5Spells.MASS_CURE_WOUNDS)


@attr.dataclass
class PaladinHolyLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinHolyFeatures.HolyDeliverance())


class PaladinHolyCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_THE_HOLY.value,
            skills=skills,
        )


class PaladinHolyMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_THE_HOLY.value,
            replace_spells=replace_spells,
        )
