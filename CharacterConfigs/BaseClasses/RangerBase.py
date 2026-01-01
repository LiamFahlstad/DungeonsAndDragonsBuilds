from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass, Skill
from Features import (
    Armor,
    Backgrounds,
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
    WarlockLevel2Spells,
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

        data.add_feature(RangerFeatures.RegainingSpellSlots())
        data.add_feature(RangerFeatures.ReplacingSpells())
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
        data.add_feature(RangerFeatures.DeftExplorerExpertise(self.skill))
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

        # Automatic feature
        data.add_feature(RangerFeatures.ExtraAttack())
        data.add_feature(RangerFeatures.FaithfulSteed())
        data.add_spell(RangerLevel2Spells.FIND_STEED)

        # Oath of vengeance features
        data.add_spell(WarlockLevel2Spells.HOLD_PERSON)
        data.add_spell(WarlockLevel2Spells.MISTY_STEP)

        # Add/Change prepared spells:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RangerFeatures.AuraOfProtection())
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
    spell: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: RangerFeatures.ChannelDivinity = (
            data.get_features_by_type(RangerFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.add_spell("Abjure Foes")
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: RangerFeatures.AuraOfProtection = data.get_features_by_type(
            RangerFeatures.AuraOfProtection
        )[0]
        aura_of_protection.add_feature(RangerFeatures.AuraOfCourage())
        return data


@attr.dataclass
class RangerLevel11(ClassBuilder.BaseClassLevel11):
    spell: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.RadiantStrikes())
        data.add_spell(self.spell)
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
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        lay_on_hands: RangerFeatures.LayOnHands = data.get_features_by_type(
            RangerFeatures.LayOnHands
        )[0]
        lay_on_hands.add_feature(RangerFeatures.RestoringTouch())
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
        return data


@attr.dataclass
class RangerLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: RangerFeatures.AuraOfProtection = data.get_features_by_type(
            RangerFeatures.AuraOfProtection
        )[0]
        aura_of_protection.add_feature(RangerFeatures.AuraExpansion())
        return data


@attr.dataclass
class RangerLevel19(ClassBuilder.BaseClassLevel19):
    spell: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
        | RangerLevel5Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
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
            Weapons.Shortbow(player_is_proficient=True),
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
