from typing import Optional, TypeAlias

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import DruidFeatures, SpellSlots
from Spells.Definitions import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    DruidLevel6Spells,
    DruidLevel7Spells,
    DruidLevel8Spells,
    DruidLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import DruidSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock

DruidSpellsUpTo2: TypeAlias = DruidLevel1Spells | DruidLevel2Spells

DruidSpellsUpTo3: TypeAlias = DruidSpellsUpTo2 | DruidLevel3Spells

DruidSpellsUpTo4: TypeAlias = DruidSpellsUpTo3 | DruidLevel4Spells

DruidSpellsUpTo5: TypeAlias = DruidSpellsUpTo4 | DruidLevel5Spells

DruidSpellsUpTo6: TypeAlias = DruidSpellsUpTo5 | DruidLevel6Spells

DruidSpellsUpTo7: TypeAlias = DruidSpellsUpTo6 | DruidLevel7Spells

DruidSpellsUpTo8: TypeAlias = DruidSpellsUpTo7 | DruidLevel8Spells

DruidSpellsUpTo9: TypeAlias = DruidSpellsUpTo8 | DruidLevel9Spells


@attr.dataclass
class DruidLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: DruidLevel0Spells
    cantrip_2: DruidLevel0Spells
    spell_1: DruidLevel1Spells
    spell_2: DruidLevel1Spells
    spell_3: DruidLevel1Spells
    spell_4: DruidLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.Spellcasting())
        data.add_feature(DruidFeatures.Druidic())
        data.add_feature(DruidFeatures.PrimalOrder())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        data.add_spell(self.spell_4)
        return data


@attr.dataclass
class DruidLevel2(ClassBuilder.BaseClassLevel2):
    spell: DruidLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.WildShape())
        data.add_feature(DruidFeatures.WildCompanion())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel3(ClassBuilder.BaseClassLevel3):
    spell: DruidSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: DruidLevel0Spells
    spell: DruidSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: DruidSpellsUpTo3
    spell_2: DruidSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.WildResurgence())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class DruidLevel6(ClassBuilder.BaseClassLevel6):
    spell: DruidSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel7(ClassBuilder.BaseClassLevel7):
    spell: DruidSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.ElementalFury())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: DruidSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: DruidSpellsUpTo5
    spell_2: DruidSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class DruidLevel10(ClassBuilder.BaseClassLevel10):
    spell: DruidSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel11(ClassBuilder.BaseClassLevel11):
    spell: DruidSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class DruidLevel13(ClassBuilder.BaseClassLevel13):
    spell: DruidSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel14(ClassBuilder.BaseClassLevel14):
    spell: DruidSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel15(ClassBuilder.BaseClassLevel15):
    spell: DruidSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.ImprovedElementalFury())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat
    spell_1: DruidSpellsUpTo8
    spell_2: DruidSpellsUpTo8

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class DruidLevel17(ClassBuilder.BaseClassLevel17):
    spell: DruidSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel18(ClassBuilder.BaseClassLevel18):
    spell: DruidSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.BeastSpells())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: DruidSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class DruidLevel20(ClassBuilder.BaseClassLevel20):
    spell: DruidSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(DruidFeatures.Archdruid())
        data.add_spell(self.spell)
        return data


class DruidStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        druid_skills: DruidSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Armor.LeatherArmor(),
            Armor.ShieldArmor(),
            Weapons.Sickle(player_is_proficient=True),
            Weapons.Quarterstaff(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.DRUID,
            base_class_level_features=druid_level_features,
            base_class_level=druid_level,
            subclass=subclass,
            abilities=abilities,
            skills=druid_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=DruidSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.SHIELD,
            ],
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )


class DruidMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.DRUID,
            base_class_level_features=druid_level_features,
            base_class_level=druid_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
