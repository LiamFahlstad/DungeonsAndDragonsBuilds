from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ClericSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import ClericFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class LightClericLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity: ClericFeatures.ChannelDivinity = data.get_features_by_type(
            ClericFeatures.ChannelDivinity
        )[0]
        channel_divinity.add_feature(ClericFeatures.RadianceOfTheDawn())
        data.add_feature(ClericFeatures.WardingFlare())
        return data


@attr.dataclass
class LightClericLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.WardingFlare())
        return data


@attr.dataclass
class LightClericLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.CoronaOfLight())
        return data


class LightClericStarterClassBuilder(ClericStarterClassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        abilities: AbilitiesStatBlock,
        cleric_skills: ClericSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.LIGHT.value,
            abilities=abilities,
            cleric_skills=cleric_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class LightClericMulticlassBuilder(ClericMulticlassBuilder):

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
