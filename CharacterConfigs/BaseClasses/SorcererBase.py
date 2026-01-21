from typing import Optional, TypeAlias

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import SorcererFeatures, SpellSlots
from Spells.Definitions import (
    SorcererLevel0Spells,
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    SorcererLevel6Spells,
    SorcererLevel7Spells,
    SorcererLevel8Spells,
    SorcererLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import SorcererSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock

SorcererSpellsUpTo2: TypeAlias = SorcererLevel1Spells | SorcererLevel2Spells

SorcererSpellsUpTo3: TypeAlias = SorcererSpellsUpTo2 | SorcererLevel3Spells

SorcererSpellsUpTo4: TypeAlias = SorcererSpellsUpTo3 | SorcererLevel4Spells

SorcererSpellsUpTo5: TypeAlias = SorcererSpellsUpTo4 | SorcererLevel5Spells

SorcererSpellsUpTo6: TypeAlias = SorcererSpellsUpTo5 | SorcererLevel6Spells

SorcererSpellsUpTo7: TypeAlias = SorcererSpellsUpTo6 | SorcererLevel7Spells

SorcererSpellsUpTo8: TypeAlias = SorcererSpellsUpTo7 | SorcererLevel8Spells

SorcererSpellsUpTo9: TypeAlias = SorcererSpellsUpTo8 | SorcererLevel9Spells


@attr.dataclass
class SorcererLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: SorcererLevel0Spells
    cantrip_2: SorcererLevel0Spells
    cantrip_3: SorcererLevel0Spells
    cantrip_4: SorcererLevel0Spells
    spell_1: SorcererLevel1Spells
    spell_2: SorcererLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.Spellcasting())
        data.add_feature(SorcererFeatures.InnateSorcery())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_cantrip(self.cantrip_3)
        data.add_cantrip(self.cantrip_4)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class SorcererLevel2(ClassBuilder.BaseClassLevel2):
    spell_1: SorcererLevel1Spells
    spell_2: SorcererLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.FontOfMagic())
        data.add_feature(SorcererFeatures.WildCompanion())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class SorcererLevel3(ClassBuilder.BaseClassLevel3):
    spell: SorcererSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: SorcererLevel0Spells
    spell: SorcererSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: SorcererSpellsUpTo3
    spell_2: SorcererSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.WildResurgence())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class SorcererLevel6(ClassBuilder.BaseClassLevel6):
    spell: SorcererSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel7(ClassBuilder.BaseClassLevel7):
    spell: SorcererSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.ElementalFury())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: SorcererSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: SorcererSpellsUpTo5
    spell_2: SorcererSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class SorcererLevel10(ClassBuilder.BaseClassLevel10):
    spell: SorcererSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel11(ClassBuilder.BaseClassLevel11):
    spell: SorcererSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class SorcererLevel13(ClassBuilder.BaseClassLevel13):
    spell: SorcererSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel14(ClassBuilder.BaseClassLevel14):
    spell: SorcererSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel15(ClassBuilder.BaseClassLevel15):
    spell: SorcererSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.ImprovedElementalFury())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat
    spell_1: SorcererSpellsUpTo8
    spell_2: SorcererSpellsUpTo8

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class SorcererLevel17(ClassBuilder.BaseClassLevel17):
    spell: SorcererSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel18(ClassBuilder.BaseClassLevel18):
    spell: SorcererSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.BeastSpells())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: SorcererSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class SorcererLevel20(ClassBuilder.BaseClassLevel20):
    spell: SorcererSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.Archsorcerer())
        data.add_spell(self.spell)
        return data


class SorcererStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        sorcerer_skills: SorcererSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
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
            base_class=CharacterClass.SORCERER,
            base_class_level_features=sorcerer_level_features,
            base_class_level=sorcerer_level,
            subclass=subclass,
            abilities=abilities,
            skills=sorcerer_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=SorcererSavingThrowsStatBlock(),
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


class SorcererMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.SORCERER,
            base_class_level_features=sorcerer_level_features,
            base_class_level=sorcerer_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
