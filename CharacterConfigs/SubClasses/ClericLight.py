from typing import Optional

import attr

import Spells.SpellLists as SpellDefinitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ClericSubclass
from Features.ClassFeatures.Cleric import ClericLightFeatures, ClericFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericLightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.EvocationLevel1Spells.BURNING_HANDS)
        data.add_spell(SpellDefinitions.EvocationLevel1Spells.FAERIE_FIRE)
        data.add_spell(SpellDefinitions.EvocationLevel2Spells.SCORCHING_RAY)
        data.add_spell(SpellDefinitions.SorcererLevel2Spells.SEE_INVISIBILITY)
        channel_divinity: ClericFeatures.ChannelDivinity = data.get_features_by_type(
            ClericFeatures.ChannelDivinity
        )[0]
        channel_divinity.extend_feature(ClericLightFeatures.RadianceOfTheDawn())
        data.add_feature(ClericLightFeatures.WardingFlare())
        return data


@attr.dataclass
class ClericLightLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.EvocationLevel3Spells.DAYLIGHT)
        data.add_spell(SpellDefinitions.EvocationLevel3Spells.FIREBALL)
        return data


@attr.dataclass
class ClericLightLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        warding_flare: ClericLightFeatures.WardingFlare = data.get_features_by_type(
            ClericLightFeatures.WardingFlare
        )[0]
        warding_flare.extend_feature(ClericLightFeatures.ImprovedWardingFlare())
        return data


@attr.dataclass
class ClericLightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.DivinationLevel4Spells.ARCANE_EYE)
        data.add_spell(SpellDefinitions.EvocationLevel4Spells.WALL_OF_FIRE)
        return data


@attr.dataclass
class ClericLightLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.EvocationLevel5Spells.FLAME_STRIKE)
        data.add_spell(SpellDefinitions.DivinationLevel5Spells.SCRYING)
        return data


@attr.dataclass
class ClericLightLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericLightFeatures.CoronaOfLight())
        return data


class ClericLightCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
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
