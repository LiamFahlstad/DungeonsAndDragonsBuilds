from typing import Optional, TypeAlias

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.Equipment import Armor, Weapons
from Features.ClassFeatures import SpellSlots
from Features.ClassFeatures.Artificer import ArtificerFeatures
from Features.Items import Items
from Spells.Definitions import (
    ArtificerLevel0Spells,
    ArtificerLevel1Spells,
    ArtificerLevel2Spells,
    ArtificerLevel3Spells,
    ArtificerLevel4Spells,
    ArtificerLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import ArtificerSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock

# Artificer is a half-caster whose spell slots never exceed 5th level.
ArtificerSpellsUpTo2: TypeAlias = ArtificerLevel1Spells | ArtificerLevel2Spells

ArtificerSpellsUpTo3: TypeAlias = ArtificerSpellsUpTo2 | ArtificerLevel3Spells

ArtificerSpellsUpTo4: TypeAlias = ArtificerSpellsUpTo3 | ArtificerLevel4Spells

ArtificerSpellsUpTo5: TypeAlias = ArtificerSpellsUpTo4 | ArtificerLevel5Spells


@attr.dataclass
class ArtificerLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: ArtificerLevel0Spells
    cantrip_2: ArtificerLevel0Spells
    spell_1: ArtificerLevel1Spells
    spell_2: ArtificerLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.Spellcasting())
        data.add_feature(ArtificerFeatures.TinkersMagic())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel2(ClassBuilder.BaseClassLevel2):
    spell: ArtificerLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ReplicateMagicItem())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel3(ClassBuilder.BaseClassLevel3):
    spell: ArtificerLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    spell: ArtificerLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel5(ClassBuilder.BaseClassLevel5):
    spell: ArtificerSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.MagicItemTinker())
        return data


@attr.dataclass
class ArtificerLevel7(ClassBuilder.BaseClassLevel7):
    spell: ArtificerSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.FlashofGenius())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ArtificerLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: ArtificerSpellsUpTo3
    spell_2: ArtificerSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel10(ClassBuilder.BaseClassLevel10):
    cantrip: ArtificerLevel0Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.MagicItemAdept())
        data.add_cantrip(self.cantrip)
        return data


@attr.dataclass
class ArtificerLevel11(ClassBuilder.BaseClassLevel11):
    spell: ArtificerSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.SpellStoringItem())
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
    spell: ArtificerSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel14(ClassBuilder.BaseClassLevel14):
    cantrip: ArtificerLevel0Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.AdvancedArtifice())
        data.add_cantrip(self.cantrip)
        return data


@attr.dataclass
class ArtificerLevel15(ClassBuilder.BaseClassLevel15):
    spell: ArtificerSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ArtificerLevel17(ClassBuilder.BaseClassLevel17):
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
class ArtificerLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.MagicItemMaster())
        return data


@attr.dataclass
class ArtificerLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: ArtificerSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.epic_boon)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.SoulOfArtifice())
        return data


class ArtificerCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            base_class=CharacterClass.ARTIFICER,
            subclass=subclass,
            saving_throws=ArtificerSavingThrowsStatBlock(),
            default_equipment=[
                Armor.StuddedLeatherArmor(),
                Weapons.Dagger(player_is_proficient=True),
            ],
            skills=skills,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.MEDIUM,
                Definitions.ArmorType.SHIELD,
            ],
            spell_casting_ability=Ability.INTELLIGENCE,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )


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
        items: Optional[list[tuple[Items.Item, int]]] = None,
    ):
        default_equipment = [
            Armor.StuddedLeatherArmor(),
            Weapons.Dagger(player_is_proficient=True),
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
                Definitions.ArmorType.MEDIUM,
                Definitions.ArmorType.SHIELD,
            ],
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.INTELLIGENCE,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
            items=items,
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
            spell_casting_ability=Ability.INTELLIGENCE,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )
