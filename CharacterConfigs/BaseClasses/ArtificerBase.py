from typing import Optional, TypeAlias

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import ArtificerFeatures, SpellSlots
from Spells.Definitions import (
    ArtificerLevel0Spells,
    ArtificerLevel1Spells,
    ArtificerLevel2Spells,
    ArtificerLevel3Spells,
    ArtificerLevel4Spells,
    ArtificerLevel5Spells,
    ArtificerLevel6Spells,
    ArtificerLevel7Spells,
    ArtificerLevel8Spells,
    ArtificerLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import ArtificerSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock

ArtificerSpellsUpTo2: TypeAlias = ArtificerLevel1Spells | ArtificerLevel2Spells

ArtificerSpellsUpTo3: TypeAlias = ArtificerSpellsUpTo2 | ArtificerLevel3Spells

ArtificerSpellsUpTo4: TypeAlias = ArtificerSpellsUpTo3 | ArtificerLevel4Spells

ArtificerSpellsUpTo5: TypeAlias = ArtificerSpellsUpTo4 | ArtificerLevel5Spells

ArtificerSpellsUpTo6: TypeAlias = ArtificerSpellsUpTo5 | ArtificerLevel6Spells

ArtificerSpellsUpTo7: TypeAlias = ArtificerSpellsUpTo6 | ArtificerLevel7Spells

ArtificerSpellsUpTo8: TypeAlias = ArtificerSpellsUpTo7 | ArtificerLevel8Spells

ArtificerSpellsUpTo9: TypeAlias = ArtificerSpellsUpTo8 | ArtificerLevel9Spells


@attr.dataclass
class ArtificerLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: ArtificerLevel0Spells
    cantrip_2: ArtificerLevel0Spells
    spell_1: ArtificerLevel1Spells
    spell_2: ArtificerLevel1Spells
    spell_3: ArtificerLevel1Spells
    spell_4: ArtificerLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.Spellcasting())
        data.add_feature(ArtificerFeatures.Artificeric())
        data.add_feature(ArtificerFeatures.PrimalOrder())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        data.add_spell(self.spell_4)
        return data


@attr.dataclass
class ArtificerLevel2(ClassBuilder.BaseClassLevel2):
    spell: ArtificerLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.WildShape())
        data.add_feature(ArtificerFeatures.WildCompanion())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel3(ClassBuilder.BaseClassLevel3):
    spell: ArtificerSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: ArtificerLevel0Spells
    spell: ArtificerSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: ArtificerSpellsUpTo3
    spell_2: ArtificerSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.WildResurgence())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel6(ClassBuilder.BaseClassLevel6):
    spell: ArtificerSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel7(ClassBuilder.BaseClassLevel7):
    spell: ArtificerSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ElementalFury())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: ArtificerSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: ArtificerSpellsUpTo5
    spell_2: ArtificerSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel10(ClassBuilder.BaseClassLevel10):
    spell: ArtificerSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel11(ClassBuilder.BaseClassLevel11):
    spell: ArtificerSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ArtificerLevel13(ClassBuilder.BaseClassLevel13):
    spell: ArtificerSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel14(ClassBuilder.BaseClassLevel14):
    spell: ArtificerSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel15(ClassBuilder.BaseClassLevel15):
    spell: ArtificerSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ImprovedElementalFury())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat
    spell_1: ArtificerSpellsUpTo8
    spell_2: ArtificerSpellsUpTo8

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel17(ClassBuilder.BaseClassLevel17):
    spell: ArtificerSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel18(ClassBuilder.BaseClassLevel18):
    spell: ArtificerSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.BeastSpells())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: ArtificerSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel20(ClassBuilder.BaseClassLevel20):
    spell: ArtificerSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.Archartificer())
        data.add_spell(self.spell)
        return data


class ArtificerStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        artificer_skills: ArtificerSkillsStatBlock,
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
            base_class=CharacterClass.ARTIFICER,
            base_class_level_features=artificer_level_features,
            base_class_level=artificer_level,
            subclass=subclass,
            abilities=abilities,
            skills=artificer_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=ArtificerSavingThrowsStatBlock(),
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


class ArtificerMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.ARTIFICER,
            base_class_level_features=artificer_level_features,
            base_class_level=artificer_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
