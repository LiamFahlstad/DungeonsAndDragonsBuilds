from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, ApplyWhen, CharacterClass, Skill
from Features import (
    Armor,
    Backgrounds,
    EpicBoon,
    FightingStyles,
    GeneralFeats,
    OriginFeats,
    Weapons,
)
from Features.ClassFeatures import RangerFeatures, SpellSlots
from Spells.Definitions import (
    RangerLevel1Spells,
    RangerLevel2Spells,
    RangerLevel3Spells,
    RangerLevel4Spells,
    RangerLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import RangerSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerLevel1(ClassBuilder.BaseClassLevel1):
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    spell_1: RangerLevel1Spells
    spell_2: RangerLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(RangerFeatures.SpellCasting())
        data.add_feature(RangerFeatures.ReplacingWeaponMasteries())
        data.add_feature(RangerFeatures.FavoredEnemy())

        # Add/Change prepared spells:
        data.add_spell(RangerLevel1Spells.HUNTERS_MARK)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class RangerLevel2(ClassBuilder.BaseClassLevel2):
    skill: Skill
    fighting_style: FightingStyles.FightingStyle
    spell: RangerLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RangerFeatures.DeftExplorerLanguages())
        data.add_feature(
            RangerFeatures.DeftExplorerExpertise(self.skill), apply_when=ApplyWhen.LAST
        )
        data.add_fighting_style(self.fighting_style)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel3(ClassBuilder.BaseClassLevel3):
    spell: RangerLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    spell: RangerLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel5(ClassBuilder.BaseClassLevel5):
    spell: RangerLevel1Spells | RangerLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RangerFeatures.ExtraAttack())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RangerLevel7(ClassBuilder.BaseClassLevel7):
    spell: RangerLevel1Spells | RangerLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RangerLevel9(ClassBuilder.BaseClassLevel9):
    skill_1: Skill
    skill_2: Skill
    spell: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RangerFeatures.Expertise(self.skill_1, self.skill_2))
        return data


@attr.dataclass
class RangerLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.Tireless())
        return data


@attr.dataclass
class RangerLevel11(ClassBuilder.BaseClassLevel11):
    spell: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class RangerLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RangerLevel13(ClassBuilder.BaseClassLevel13):
    spell: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        favored_enemy: RangerFeatures.FavoredEnemy = data.get_features_by_type(
            RangerFeatures.FavoredEnemy
        )[0]
        favored_enemy.add_feature(RangerFeatures.RelentlessHunter())
        return data


@attr.dataclass
class RangerLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.NaturesVeil())
        return data


@attr.dataclass
class RangerLevel15(ClassBuilder.BaseClassLevel15):
    spell: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RangerLevel17(ClassBuilder.BaseClassLevel17):
    spell_1: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
        | RangerLevel5Spells
    )
    spell_2: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
        | RangerLevel5Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        favored_enemy: RangerFeatures.FavoredEnemy = data.get_features_by_type(
            RangerFeatures.FavoredEnemy
        )[0]
        favored_enemy.add_feature(RangerFeatures.PreciseHunter())

        return data


@attr.dataclass
class RangerLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.FeralSenses())
        return data


@attr.dataclass
class RangerLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoonCharacterFeature | EpicBoon.EpicBoonTextFeature
    spell: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
        | RangerLevel5Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.epic_boon)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        favored_enemy: RangerFeatures.FavoredEnemy = data.get_features_by_type(
            RangerFeatures.FavoredEnemy
        )[0]
        favored_enemy.add_feature(RangerFeatures.FoeSlayer())
        return data


class RangerStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        subclass: str,
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
        default_equipment = [
            Armor.StuddedLeatherArmor(),
            Weapons.Scimitar(player_is_proficient=True),
            Weapons.Shortsword(player_is_proficient=True),
            Weapons.Longbow(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.RANGER,
            base_class_level_features=ranger_level_features,
            base_class_level=ranger_level,
            subclass=subclass,
            abilities=abilities,
            skills=ranger_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=RangerSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )


class RangerMulticlassBuilder(ClassBuilder.ClassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.RANGER,
            base_class_level_features=ranger_level_features,
            base_class_level=ranger_level,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )
