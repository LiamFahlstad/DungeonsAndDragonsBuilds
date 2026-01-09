from typing import Optional, TypeAlias

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import ClericFeatures, SpellSlots
from Spells.Definitions import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    ClericLevel6Spells,
    ClericLevel7Spells,
    ClericLevel8Spells,
    ClericLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import ClericSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock

ClericSpellsUpTo2: TypeAlias = ClericLevel1Spells | ClericLevel2Spells

ClericSpellsUpTo3: TypeAlias = ClericSpellsUpTo2 | ClericLevel3Spells

ClericSpellsUpTo4: TypeAlias = ClericSpellsUpTo3 | ClericLevel4Spells

ClericSpellsUpTo5: TypeAlias = ClericSpellsUpTo4 | ClericLevel5Spells

ClericSpellsUpTo6: TypeAlias = ClericSpellsUpTo5 | ClericLevel6Spells

ClericSpellsUpTo7: TypeAlias = ClericSpellsUpTo6 | ClericLevel7Spells

ClericSpellsUpTo8: TypeAlias = ClericSpellsUpTo7 | ClericLevel8Spells

ClericSpellsUpTo9: TypeAlias = ClericSpellsUpTo8 | ClericLevel9Spells


@attr.dataclass
class ClericLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: ClericLevel0Spells
    cantrip_2: ClericLevel0Spells
    cantrip_3: ClericLevel0Spells
    spell_1: ClericLevel1Spells
    spell_2: ClericLevel1Spells
    spell_3: ClericLevel1Spells
    spell_4: ClericLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.Spellcasting())
        data.add_feature(ClericFeatures.DivineOrder())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_cantrip(self.cantrip_3)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        data.add_spell(self.spell_4)
        return data


@attr.dataclass
class ClericLevel2(ClassBuilder.BaseClassLevel2):
    spell: ClericLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.ChannelDivinity())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel3(ClassBuilder.BaseClassLevel3):
    spell: ClericSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: ClericLevel0Spells
    spell: ClericSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: ClericSpellsUpTo3
    spell_2: ClericSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.SearUndead())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ClericLevel6(ClassBuilder.BaseClassLevel6):
    spell: ClericSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel7(ClassBuilder.BaseClassLevel7):
    spell: ClericSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.BlessedStrikes())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: ClericSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: ClericSpellsUpTo5
    spell_2: ClericSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ClericLevel10(ClassBuilder.BaseClassLevel10):
    cantrip: ClericLevel0Spells
    spell: ClericSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        data.add_feature(ClericFeatures.DivineIntervention())
        return data


@attr.dataclass
class ClericLevel11(ClassBuilder.BaseClassLevel11):
    spell: ClericSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ClericLevel13(ClassBuilder.BaseClassLevel13):
    spell: ClericSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        blessed_strikes: ClericFeatures.BlessedStrikes = data.get_features_by_type(
            ClericFeatures.BlessedStrikes
        )[0]
        blessed_strikes.add_feature(ClericFeatures.ImprovedBlessedStrikes())
        return data


@attr.dataclass
class ClericLevel15(ClassBuilder.BaseClassLevel15):
    spell: ClericSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ClericLevel17(ClassBuilder.BaseClassLevel17):
    spell: ClericSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel18(ClassBuilder.BaseClassLevel18):
    spell: ClericSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: ClericSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class ClericLevel20(ClassBuilder.BaseClassLevel20):
    spell: ClericSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(ClericFeatures.GreaterDivineIntervention())
        data.add_spell(self.spell)
        return data


class ClericStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        subclass: str,
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
        default_equipment = [
            Armor.LeatherArmor(),
            Armor.ShieldArmor(),
            Weapons.Sickle(player_is_proficient=True),
            Weapons.Quarterstaff(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.CLERIC,
            base_class_level_features=cleric_level_features,
            base_class_level=cleric_level,
            subclass=subclass,
            abilities=abilities,
            skills=cleric_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=ClericSavingThrowsStatBlock(),
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


class ClericMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.CLERIC,
            base_class_level_features=cleric_level_features,
            base_class_level=cleric_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
