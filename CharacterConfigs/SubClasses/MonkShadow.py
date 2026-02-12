from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import MonkSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import MonkFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class ShadowMonkLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.add_feature(MonkFeatures.ShadowArts())
        return data


@attr.dataclass
class ShadowMonkLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.ShadowStep())
        return data


@attr.dataclass
class ShadowMonkLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        shadow_step: MonkFeatures.ShadowStep = data.get_features_by_type(
            MonkFeatures.ShadowStep
        )[0]
        shadow_step.add_feature(MonkFeatures.ImprovedShadowStep())
        return data


@attr.dataclass
class ShadowMonkLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.add_feature(MonkFeatures.CloakOfShadows())
        return data


class ShadowMonkStarterClassBuilder(MonkStarterClassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        abilities: AbilitiesStatBlock,
        monk_skills: MonkSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.SHADOW.value,
            abilities=abilities,
            monk_skills=monk_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class ShadowMonkMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.SHADOW.value,
            replace_spells=replace_spells,
        )
