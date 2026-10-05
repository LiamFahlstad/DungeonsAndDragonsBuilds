from typing import Optional

import attr

import CharacterContent.Spells.SpellLists as SpellDefinitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import ClericSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Cleric import ClericTrickeryFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures


@attr.dataclass
class ClericTrickeryLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(SpellDefinitions.EnchantmentLevel1Spells.CHARM_PERSON)
        data.add_spell(SpellDefinitions.IllusionLevel1Spells.DISGUISE_SELF)
        data.add_spell(SpellDefinitions.IllusionLevel2Spells.INVISIBILITY)
        data.add_spell(SpellDefinitions.AbjurationLevel2Spells.PASS_WITHOUT_TRACE)

        data.add_feature(
            ClericTrickeryFeatures.InvokeDuplicity(),
            extends=ClericFeatures.ChannelDivinity,
        )
        data.add_feature(ClericTrickeryFeatures.BlessingOfTheTrickster())
        return data


@attr.dataclass
class ClericTrickeryLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(SpellDefinitions.IllusionLevel3Spells.HYPNOTIC_PATTERN)
        data.add_spell(SpellDefinitions.AbjurationLevel3Spells.NONDETECTION)
        return data


@attr.dataclass
class ClericTrickeryLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            ClericTrickeryFeatures.TrickstersTransposition(),
            extends=ClericFeatures.ChannelDivinity,
        )
        return data


@attr.dataclass
class ClericTrickeryLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(SpellDefinitions.EnchantmentLevel4Spells.CONFUSION)
        data.add_spell(SpellDefinitions.ConjurationLevel4Spells.DIMENSION_DOOR)
        return data


@attr.dataclass
class ClericTrickeryLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(SpellDefinitions.EnchantmentLevel5Spells.DOMINATE_PERSON)
        data.add_spell(SpellDefinitions.EnchantmentLevel5Spells.MODIFY_MEMORY)
        return data


@attr.dataclass
class ClericTrickeryLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            ClericTrickeryFeatures.ImprovedDuplicity(),
            extends=ClericFeatures.ChannelDivinity,
        )
        return data


class ClericTrickeryCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
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
