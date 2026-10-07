from typing import Optional

import attr

import CharacterContent.Spells.SpellLists as SpellDefinitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import ClericSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Cleric import ClericWarFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures


@attr.dataclass
class ClericWarLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(SpellDefinitions.ClericLevel1Spells.GUIDING_BOLT)
        data.add_spell(SpellDefinitions.TransmutationLevel2Spells.MAGIC_WEAPON)
        data.add_spell(SpellDefinitions.ClericLevel1Spells.SHIELD_OF_FAITH)
        data.add_spell(SpellDefinitions.ClericLevel2Spells.SPIRITUAL_WEAPON)

        data.add_feature(
            ClericWarFeatures.GuidedStrike(), extends=ClericFeatures.ChannelDivinity
        )
        data.add_feature(ClericWarFeatures.WarPriest())


@attr.dataclass
class ClericWarLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(SpellDefinitions.EvocationLevel3Spells.CRUSADERS_MANTLE)
        data.add_spell(SpellDefinitions.ClericLevel3Spells.SPIRIT_GUARDIANS)


@attr.dataclass
class ClericWarLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            ClericWarFeatures.WarGodsBlessing(), extends=ClericFeatures.ChannelDivinity
        )


@attr.dataclass
class ClericWarLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(SpellDefinitions.EvocationLevel4Spells.FIRE_SHIELD)
        data.add_spell(SpellDefinitions.ClericLevel4Spells.FREEDOM_OF_MOVEMENT)


@attr.dataclass
class ClericWarLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(SpellDefinitions.EnchantmentLevel5Spells.HOLD_MONSTER)
        data.add_spell(SpellDefinitions.ConjurationLevel5Spells.STEEL_WIND_STRIKE)


@attr.dataclass
class ClericWarLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericWarFeatures.AvatarOfBattle())


class ClericWarCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass.WAR.value,
            skills=skills,
        )


class ClericWarMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.WAR.value,
            replace_spells=replace_spells,
        )
