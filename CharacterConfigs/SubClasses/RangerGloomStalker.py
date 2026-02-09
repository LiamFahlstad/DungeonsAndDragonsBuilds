from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RangerSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import RangerFeatures
from Spells.Definitions import (
    BardLevel4Spells,
    ClericLevel4Spells,
    IllusionLevel1Spells,
    TransmutationLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class GloomStalkerRangerLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.UmbralSight())
        data.add_spell(IllusionLevel1Spells.DISGUISE_SELF)
        return data


@attr.dataclass
class GloomStalkerRangerLevel5(ClassBuilder.SubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(TransmutationLevel2Spells.ROPE_TRICK)
        return data


@attr.dataclass
class GloomStalkerRangerLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: RangerFeatures.AuraOfProtection = data.get_features_by_type(
            RangerFeatures.AuraOfProtection
        )[0]
        aura_of_protection.add_feature(RangerFeatures.AuraOfAlacrity())
        return data


@attr.dataclass
class GloomStalkerRangerLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class GloomStalkerRangerLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class GloomStalkerRangerLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.GloriousDefense())
        return data


@attr.dataclass
class GloomStalkerRangerLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


@attr.dataclass
class GloomStalkerRangerLevel20(ClassBuilder.SubclassLevel20):
    level: int = attr.field(init=False, default=20)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.LivingLegend())
        return data


class GloomStalkerRangerStarterClassBuilder(RangerStarterClassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        abilities: AbilitiesStatBlock,
        ranger_skills: RangerSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.HUNTER.value,
            abilities=abilities,
            ranger_skills=ranger_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class GloomStalkerRangerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.HUNTER.value,
            replace_spells=replace_spells,
        )
