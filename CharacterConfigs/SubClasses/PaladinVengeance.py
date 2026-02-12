from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import PaladinSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import PaladinFeatures
from Spells.Definitions import (
    BardLevel4Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel4Spells,
    PaladinLevel2Spells,
    RangerLevel1Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class VengeancePaladinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.VowOfEnmity())
        data.add_spell(ClericLevel1Spells.BANE)
        data.add_spell(RangerLevel1Spells.HUNTERS_MARK)
        return data


@attr.dataclass
class VengeancePaladinLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        data.add_spell(PaladinLevel2Spells.MAGIC_WEAPON)
        return data


@attr.dataclass
class VengeancePaladinLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: PaladinFeatures.AuraOfProtection = (
            data.get_features_by_type(PaladinFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(PaladinFeatures.AuraOfAlacrity())
        return data


@attr.dataclass
class VengeancePaladinLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class VengeancePaladinLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class VengeancePaladinLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.GloriousDefense())
        return data


@attr.dataclass
class VengeancePaladinLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


@attr.dataclass
class VengeancePaladinLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.LivingLegend())
        return data


class VengeancePaladinStarterClassBuilder(PaladinStarterClassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        abilities: AbilitiesStatBlock,
        paladin_skills: PaladinSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_VENGEANCE.value,
            abilities=abilities,
            paladin_skills=paladin_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class VengeancePaladinMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_VENGEANCE.value,
            replace_spells=replace_spells,
        )
