from typing import Optional

import attr

import CharacterContent.Spells.SpellLists as SpellDefinitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import ClericSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Cleric import ClericLightFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures


@attr.dataclass
class ClericLightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SpellDefinitions.EvocationLevel1Spells.BURNING_HANDS)
        data.add_spell(SpellDefinitions.EvocationLevel1Spells.FAERIE_FIRE)
        data.add_spell(SpellDefinitions.EvocationLevel2Spells.SCORCHING_RAY)
        data.add_spell(SpellDefinitions.SorcererLevel2Spells.SEE_INVISIBILITY)
        data.add_feature(
            ClericLightFeatures.RadianceOfTheDawn(),
            extends=ClericFeatures.ChannelDivinity,
        )
        data.add_feature(ClericLightFeatures.WardingFlare())
        return data


@attr.dataclass
class ClericLightLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SpellDefinitions.EvocationLevel3Spells.DAYLIGHT)
        data.add_spell(SpellDefinitions.EvocationLevel3Spells.FIREBALL)
        return data


@attr.dataclass
class ClericLightLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            ClericLightFeatures.ImprovedWardingFlare(),
            extends=ClericLightFeatures.WardingFlare,
        )
        return data


@attr.dataclass
class ClericLightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SpellDefinitions.DivinationLevel4Spells.ARCANE_EYE)
        data.add_spell(SpellDefinitions.EvocationLevel4Spells.WALL_OF_FIRE)
        return data


@attr.dataclass
class ClericLightLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SpellDefinitions.EvocationLevel5Spells.FLAME_STRIKE)
        data.add_spell(SpellDefinitions.DivinationLevel5Spells.SCRYING)
        return data


@attr.dataclass
class ClericLightLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(ClericLightFeatures.CoronaOfLight())
        return data


class ClericLightCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass.LIGHT.value,
            skills=skills,
        )


class ClericLightMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.LIGHT.value,
            replace_spells=replace_spells,
        )
