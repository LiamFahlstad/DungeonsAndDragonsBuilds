from typing import Optional, TypeAlias

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, ApplyWhen, CharacterClass, Skill
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import BardFeatures, SpellSlots
from Spells.Definitions import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
    BardLevel5Spells,
    BardLevel6Spells,
    BardLevel7Spells,
    BardLevel8Spells,
    BardLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import BardSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock

BardSpellsUpTo2: TypeAlias = BardLevel1Spells | BardLevel2Spells

BardSpellsUpTo3: TypeAlias = BardSpellsUpTo2 | BardLevel3Spells

BardSpellsUpTo4: TypeAlias = BardSpellsUpTo3 | BardLevel4Spells

BardSpellsUpTo5: TypeAlias = BardSpellsUpTo4 | BardLevel5Spells

BardSpellsUpTo6: TypeAlias = BardSpellsUpTo5 | BardLevel6Spells

BardSpellsUpTo7: TypeAlias = BardSpellsUpTo6 | BardLevel7Spells

BardSpellsUpTo8: TypeAlias = BardSpellsUpTo7 | BardLevel8Spells

BardSpellsUpTo9: TypeAlias = BardSpellsUpTo8 | BardLevel9Spells


@attr.dataclass
class BardLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: BardLevel0Spells
    cantrip_2: BardLevel0Spells
    spell_1: BardLevel1Spells
    spell_2: BardLevel1Spells
    spell_3: BardLevel1Spells
    spell_4: BardLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardFeatures.Spellcasting())
        data.add_feature(BardFeatures.BardicInspiration())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        data.add_spell(self.spell_4)
        return data


@attr.dataclass
class BardLevel2(ClassBuilder.BaseClassLevel2):
    spell: BardLevel1Spells
    skill_1: Skill
    skill_2: Skill

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardFeatures.JackOfAllTrades(), apply_when=ApplyWhen.LAST)
        data.add_spell(self.spell)
        data.add_feature(
            BardFeatures.Expertise1(skill_1=self.skill_1, skill_2=self.skill_2),
            apply_when=ApplyWhen.LAST,
        )
        return data


@attr.dataclass
class BardLevel3(ClassBuilder.BaseClassLevel3):
    spell: BardSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: BardLevel0Spells
    spell: BardSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: BardSpellsUpTo3
    spell_2: BardSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        bardic_inspiration: BardFeatures.BardicInspiration = data.get_features_by_type(
            BardFeatures.BardicInspiration
        )[0]
        bardic_inspiration.add_feature(BardFeatures.FontOfInspiration())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class BardLevel6(ClassBuilder.BaseClassLevel6):
    spell: BardSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel7(ClassBuilder.BaseClassLevel7):
    spell: BardSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardFeatures.Countercharm())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: BardSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: BardSpellsUpTo5
    spell_2: BardSpellsUpTo5
    skill_1: Skill
    skill_2: Skill

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_feature(
            BardFeatures.Expertise1(skill_1=self.skill_1, skill_2=self.skill_2),
            apply_when=ApplyWhen.LAST,
        )
        return data


@attr.dataclass
class BardLevel10(ClassBuilder.BaseClassLevel10):
    cantrip: BardLevel0Spells
    spell: BardSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        data.add_feature(BardFeatures.MagicalSecrets())
        return data


@attr.dataclass
class BardLevel11(ClassBuilder.BaseClassLevel11):
    spell: BardSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BardLevel13(ClassBuilder.BaseClassLevel13):
    spell: BardSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BardLevel15(ClassBuilder.BaseClassLevel15):
    spell: BardSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BardLevel17(ClassBuilder.BaseClassLevel17):
    spell: BardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel18(ClassBuilder.BaseClassLevel18):
    spell: BardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        bardic_inspiration: BardFeatures.BardicInspiration = data.get_features_by_type(
            BardFeatures.BardicInspiration
        )[0]
        bardic_inspiration.add_feature(BardFeatures.SuperiorInspiration())

        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: BardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel20(ClassBuilder.BaseClassLevel20):
    spell: BardSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BardFeatures.WordsOfCreation())
        data.add_spell(self.spell)
        data.add_spell(BardLevel9Spells.POWER_WORD_HEAL)
        data.add_spell(BardLevel9Spells.POWER_WORD_KILL)
        return data


class BardStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        bard_skills: BardSkillsStatBlock,
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
            Weapons.Dagger(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.BARD,
            base_class_level_features=bard_level_features,
            base_class_level=bard_level,
            subclass=subclass,
            abilities=abilities,
            skills=bard_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=BardSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
            ],
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )


class BardMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.BARD,
            base_class_level_features=bard_level_features,
            base_class_level=bard_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
