from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features import (
    Armor,
    Backgrounds,
    FightingStyles,
    GeneralFeats,
    OriginFeats,
    Weapons,
)
from Features.ClassFeatures import PaladinFeatures, SpellSlots
from Spells.Definitions import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
    WarlockLevel2Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import PaladinSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class PaladinLevel1(ClassBuilder.BaseClassLevel1):
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    spell_1: PaladinLevel1Spells
    spell_2: PaladinLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        # Lay on Hands
        data.add_feature(PaladinFeatures.LayOnHands())

        # Add/Change prepared spells:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class PaladinLevel2(ClassBuilder.BaseClassLevel2):
    fighting_style: FightingStyles.FightingStyle
    spell: PaladinLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        # Choose one Fighting Style
        data.add_fighting_style(self.fighting_style)

        # Automatic feature
        data.add_feature(PaladinFeatures.PaladinsSmite())
        data.add_spell(PaladinLevel1Spells.DIVINE_SMITE)

        # Add prepared spells:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel3(ClassBuilder.BaseClassLevel3):
    spell: PaladinLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        channel_divinity_feature = PaladinFeatures.ChannelDivinity()
        channel_divinity_feature.add_spell("Divine Sense")
        data.add_feature(channel_divinity_feature)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    spell: PaladinLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel5(ClassBuilder.BaseClassLevel5):
    spell: PaladinLevel1Spells | PaladinLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        # Automatic feature
        data.add_feature(PaladinFeatures.ExtraAttack())
        data.add_feature(PaladinFeatures.FaithfulSteed())
        data.add_spell(PaladinLevel2Spells.FIND_STEED)

        # Oath of vengeance features
        data.add_spell(WarlockLevel2Spells.HOLD_PERSON)
        data.add_spell(WarlockLevel2Spells.MISTY_STEP)

        # Add/Change prepared spells:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.AuraOfProtection())
        return data


@attr.dataclass
class PaladinLevel7(ClassBuilder.BaseClassLevel7):
    spell: PaladinLevel1Spells | PaladinLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class PaladinLevel9(ClassBuilder.BaseClassLevel9):
    spell: PaladinLevel1Spells | PaladinLevel2Spells | PaladinLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: PaladinFeatures.ChannelDivinity = (
            data.get_features_by_type(PaladinFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.add_spell("Abjure Foes")
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: PaladinFeatures.AuraOfProtection = (
            data.get_features_by_type(PaladinFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(PaladinFeatures.AuraOfCourage())
        return data


@attr.dataclass
class PaladinLevel11(ClassBuilder.BaseClassLevel11):
    spell: PaladinLevel1Spells | PaladinLevel2Spells | PaladinLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.RadiantStrikes())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class PaladinLevel13(ClassBuilder.BaseClassLevel13):
    spell: (
        PaladinLevel1Spells
        | PaladinLevel2Spells
        | PaladinLevel3Spells
        | PaladinLevel4Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        lay_on_hands: PaladinFeatures.LayOnHands = data.get_features_by_type(
            PaladinFeatures.LayOnHands
        )[0]
        lay_on_hands.add_feature(PaladinFeatures.RestoringTouch())
        return data


@attr.dataclass
class PaladinLevel15(ClassBuilder.BaseClassLevel15):
    spell: (
        PaladinLevel1Spells
        | PaladinLevel2Spells
        | PaladinLevel3Spells
        | PaladinLevel4Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class PaladinLevel17(ClassBuilder.BaseClassLevel17):
    spell_1: (
        PaladinLevel1Spells
        | PaladinLevel2Spells
        | PaladinLevel3Spells
        | PaladinLevel4Spells
        | PaladinLevel5Spells
    )
    spell_2: (
        PaladinLevel1Spells
        | PaladinLevel2Spells
        | PaladinLevel3Spells
        | PaladinLevel4Spells
        | PaladinLevel5Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class PaladinLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: PaladinFeatures.AuraOfProtection = (
            data.get_features_by_type(PaladinFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(PaladinFeatures.AuraExpansion())
        return data


@attr.dataclass
class PaladinLevel19(ClassBuilder.BaseClassLevel19):
    spell: (
        PaladinLevel1Spells
        | PaladinLevel2Spells
        | PaladinLevel3Spells
        | PaladinLevel4Spells
        | PaladinLevel5Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


class PaladinStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        subclass: str,
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
        default_equipment = [
            Armor.ChainMailArmor(),
            Armor.ShieldArmor(),
            Weapons.Longsword(player_is_proficient=True),
            Weapons.Javelin(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.PALADIN,
            base_class_level_features=paladin_level_features,
            base_class_level=paladin_level,
            subclass=subclass,
            abilities=abilities,
            skills=paladin_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=PaladinSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )


class PaladinMulticlassBuilder(ClassBuilder.ClassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.PALADIN,
            base_class_level_features=paladin_level_features,
            base_class_level=paladin_level,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )
