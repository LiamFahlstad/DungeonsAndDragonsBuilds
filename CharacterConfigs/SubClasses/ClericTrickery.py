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
from Features.ClassFeatures.Cleric import ClericTrickeryFeatures, ClericFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericTrickeryLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.EnchantmentLevel1Spells.CHARM_PERSON)
        data.add_spell(SpellDefinitions.IllusionLevel1Spells.DISGUISE_SELF)
        data.add_spell(SpellDefinitions.IllusionLevel2Spells.INVISIBILITY)
        data.add_spell(SpellDefinitions.AbjurationLevel2Spells.PASS_WITHOUT_TRACE)

        channel_divinity: ClericFeatures.ChannelDivinity = data.get_features_by_type(
            ClericFeatures.ChannelDivinity
        )[0]
        channel_divinity.extend_feature(ClericTrickeryFeatures.InvokeDuplicity())
        data.add_feature(ClericTrickeryFeatures.BlessingOfTheTrickster())
        return data


@attr.dataclass
class ClericTrickeryLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.IllusionLevel3Spells.HYPNOTIC_PATTERN)
        data.add_spell(SpellDefinitions.AbjurationLevel3Spells.NONDETECTION)
        return data


@attr.dataclass
class ClericTrickeryLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericTrickeryFeatures.TrickstersTransposition())
        return data


@attr.dataclass
class ClericTrickeryLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.EnchantmentLevel4Spells.CONFUSION)
        data.add_spell(SpellDefinitions.ConjurationLevel4Spells.DIMENSION_DOOR)
        return data


@attr.dataclass
class ClericTrickeryLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.EnchantmentLevel5Spells.DOMINATE_PERSON)
        data.add_spell(SpellDefinitions.EnchantmentLevel5Spells.MODIFY_MEMORY)
        return data


@attr.dataclass
class ClericTrickeryLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericTrickeryFeatures.ImprovedDuplicity())
        return data


class ClericTrickeryCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass.TRICKERY.value,
            skills=skills,
        )


class ClericTrickeryMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.TRICKERY.value,
            replace_spells=replace_spells,
        )
