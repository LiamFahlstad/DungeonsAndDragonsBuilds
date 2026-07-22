from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerMulticlassBuilder,
    ArtificerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ArtificerSubclass2014
from Features.SubClassFeatures2014.Artificer import ArtificerArmorerFeatures
from Spells.SpellLists import (
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
    DruidLevel4Spells,
    SorcererLevel1Spells,
    SorcererLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerArmorerLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArmorerFeatures.ArmorerToolsOfTheTrade())
        data.add_feature(ArtificerArmorerFeatures.ArmorerSpells())
        data.add_feature(ArtificerArmorerFeatures.ArcaneArmor())
        data.add_feature(ArtificerArmorerFeatures.ArmorModel())
        data.add_spell(SorcererLevel1Spells.MAGIC_MISSILE)
        data.add_spell(BardLevel1Spells.THUNDERWAVE)
        return data


@attr.dataclass
class ArtificerArmorerLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArmorerFeatures.ArmorerExtraAttack())
        data.add_spell(BardLevel2Spells.MIRROR_IMAGE)
        data.add_spell(BardLevel2Spells.SHATTER)
        return data


@attr.dataclass
class ArtificerArmorerLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArmorerFeatures.ArmorModifications())
        data.add_spell(BardLevel3Spells.HYPNOTIC_PATTERN)
        data.add_spell(SorcererLevel3Spells.LIGHTNING_BOLT)
        return data


@attr.dataclass
class ArtificerArmorerLevel13(ClassBuilder.SubclassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel4Spells.FIRE_SHIELD)
        data.add_spell(BardLevel4Spells.GREATER_INVISIBILITY)
        return data


@attr.dataclass
class ArtificerArmorerLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArmorerFeatures.PerfectedArmor())
        return data


@attr.dataclass
class ArtificerArmorerLevel17(ClassBuilder.SubclassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.PASSWALL)
        data.add_spell(WizardLevel5Spells.WALL_OF_FORCE)
        return data


class ArtificerArmorerCustomStarterClassArgs(ArtificerCustomStarterClassArgs):
    def __init__(
        self,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            subclass=ArtificerSubclass2014.ARMORER.value,
            skills=skills,
        )


class ArtificerArmorerMulticlassBuilder(ArtificerMulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            artificer_level_features=artificer_level_features,
            artificer_level=artificer_level,
            subclass=ArtificerSubclass2014.ARMORER.value,
            replace_spells=replace_spells,
        )
