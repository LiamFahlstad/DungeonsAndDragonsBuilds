from typing import Optional, cast

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ArtificerBase import (
    ArtificerMulticlassBuilder,
    ArtificerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import ArtificerSubclass
from CharacterContent.Features.SubClassFeatures.Artificer import ArtificerCartographerFeatures
from CharacterContent.Features.ClassFeatures.Artificer import ArtificerFeatures
from CharacterContent.Spells.SpellLists import (
    BardLevel3Spells,
    BardLevel5Spells,
    ClericLevel1Spells,
    ClericLevel4Spells,
    DivinationLevel2Spells,
    DivinationLevel4Spells,
    DivinationLevel5Spells,
    DruidLevel1Spells,
    DruidLevel3Spells,
)
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerCartographerLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerCartographerFeatures.CartographerToolsOfTheTrade())
        data.add_feature(ArtificerCartographerFeatures.CartographerSpells())
        data.add_feature(ArtificerCartographerFeatures.AdventurersAtlas())
        data.add_feature(ArtificerCartographerFeatures.MappingMagic())
        data.add_spell(DruidLevel1Spells.FAERIE_FIRE)
        data.add_spell(ClericLevel1Spells.GUIDING_BOLT)
        data.add_spell(ClericLevel1Spells.HEALING_WORD)
        return data


@attr.dataclass
class ArtificerCartographerLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        cartographer_spells: ArtificerCartographerFeatures.CartographerSpells = cast(
            ArtificerCartographerFeatures.CartographerSpells, data.get_features_by_type(
                ArtificerCartographerFeatures.CartographerSpells
            )[0]
        )
        cartographer_spells.extend_feature(ArtificerCartographerFeatures.GuidedPrecision())
        data.add_spell(DivinationLevel2Spells.LOCATE_OBJECT)
        data.add_spell(DivinationLevel2Spells.MIND_SPIKE)
        return data


@attr.dataclass
class ArtificerCartographerLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        flash_of_genius: ArtificerFeatures.FlashofGenius = cast(
            ArtificerFeatures.FlashofGenius, data.get_features_by_type(
                ArtificerFeatures.FlashofGenius
            )[0]
        )
        flash_of_genius.extend_feature(ArtificerCartographerFeatures.IngeniousMovement())
        data.add_spell(DruidLevel3Spells.CALL_LIGHTNING)
        data.add_spell(BardLevel3Spells.CLAIRVOYANCE)
        return data


@attr.dataclass
class ArtificerCartographerLevel13(ClassBuilder.SubclassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel4Spells.BANISHMENT)
        data.add_spell(DivinationLevel4Spells.LOCATE_CREATURE)
        return data


@attr.dataclass
class ArtificerCartographerLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        adventurers_atlas: ArtificerCartographerFeatures.AdventurersAtlas = cast(
            ArtificerCartographerFeatures.AdventurersAtlas, data.get_features_by_type(
                ArtificerCartographerFeatures.AdventurersAtlas
            )[0]
        )
        adventurers_atlas.extend_feature(ArtificerCartographerFeatures.SuperiorAtlas())
        return data


@attr.dataclass
class ArtificerCartographerLevel17(ClassBuilder.SubclassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DivinationLevel5Spells.SCRYING)
        data.add_spell(BardLevel5Spells.TELEPORTATION_CIRCLE)
        return data


class ArtificerCartographerCustomStarterClassArgs(ArtificerCustomStarterClassArgs):
    def __init__(
        self,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            subclass=ArtificerSubclass.CARTOGRAPHER.value,
            skills=skills,
        )


class ArtificerCartographerMulticlassBuilder(ArtificerMulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            artificer_level_features=artificer_level_features,
            artificer_level=artificer_level,
            subclass=ArtificerSubclass.CARTOGRAPHER.value,
            replace_spells=replace_spells,
        )
