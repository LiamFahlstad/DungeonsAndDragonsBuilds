from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WarlockSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import WarlockFeatures
from Spells.Definitions import (
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    SorcererLevel3Spells,
    WarlockLevel2Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class ArchfeyWarlockLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel2Spells.CALM_EMOTIONS)
        data.add_spell(WarlockLevel2Spells.MISTY_STEP)
        data.add_spell(BardLevel2Spells.PHANTASMAL_FORCE)
        data.add_spell(BardLevel1Spells.SLEEP)
        data.add_feature(WarlockFeatures.StepsOfTheFey())
        return data


@attr.dataclass
class ArchfeyWarlockLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.BLINK)
        data.add_spell(BardLevel3Spells.PLANT_GROWTH)
        return data


@attr.dataclass
class ArchfeyWarlockLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: WarlockFeatures.AuraOfProtection = (
            data.get_features_by_type(WarlockFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(WarlockFeatures.AuraOfAlacrity())
        return data


@attr.dataclass
class ArchfeyWarlockLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class ArchfeyWarlockLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class ArchfeyWarlockLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.GloriousDefense())
        return data


@attr.dataclass
class ArchfeyWarlockLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


class ArchfeyWarlockStarterClassBuilder(WarlockStarterClassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        abilities: AbilitiesStatBlock,
        warlock_skills: WarlockSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_ARCHFEY.value,
            abilities=abilities,
            warlock_skills=warlock_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class ArchfeyWarlockMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_ARCHFEY.value,
            replace_spells=replace_spells,
        )
