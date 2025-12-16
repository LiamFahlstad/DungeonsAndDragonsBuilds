from abc import ABC, abstractmethod
from typing import Optional
import attr
from Definitions import Ability, CharacterClass, PaladinSubclass
from Features import GeneralFeats, OriginFeats
from CharacterSheetCreator import CharacterSheetData
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import PaladinFeatures, SpellSlots
from StatBlocks.AbilitiesStatBlock import (
    AbilitiesStatBlock,
)
from StatBlocks.SavingThrowsStatBlock import PaladinSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock
from Spells.Definitions import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
    WarlockLevel2Spells,
)


@attr.dataclass
class ClassLevelBase(ABC):
    level: int = attr.field(init=False)

    @abstractmethod
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        pass


@attr.dataclass
class PaladinSubclassLevel3(ClassLevelBase):
    pass


@attr.dataclass
class PaladinSubclassLevel5(ClassLevelBase):
    pass


@attr.dataclass
class PaladinSubclassLevel7(ClassLevelBase):
    pass


@attr.dataclass
class PaladinSubclassLevel9(ClassLevelBase):
    pass


@attr.dataclass
class PaladinSubclassLevel13(ClassLevelBase):
    pass


@attr.dataclass
class PaladinSubclassLevel15(ClassLevelBase):
    pass


@attr.dataclass
class PaladinSubclassLevel17(ClassLevelBase):
    pass


@attr.dataclass
class PaladinSubclassLevel20(ClassLevelBase):
    pass


@attr.dataclass
class PaladinLevel1(ClassLevelBase):
    level: int = attr.field(init=False, default=1)
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
class PaladinLevel2(ClassLevelBase):
    level: int = attr.field(init=False, default=2)
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
class PaladinLevel3(ClassLevelBase):
    level: int = attr.field(init=False, default=3)
    spell: PaladinLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        channel_divinity_feature = PaladinFeatures.ChannelDivinity()
        channel_divinity_feature.add_spell("Divine Sense")
        data.add_feature(channel_divinity_feature)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel4(ClassLevelBase):
    level: int = attr.field(init=False, default=4)
    general_feat: GeneralFeats.GeneralFeat
    spell: PaladinLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel5(ClassLevelBase):
    level: int = attr.field(init=False, default=5)
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
class PaladinLevel6(ClassLevelBase):
    level: int = attr.field(init=False, default=6)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.AuraOfProtection())
        return data


@attr.dataclass
class PaladinLevel7(ClassLevelBase):
    level: int = attr.field(init=False, default=7)
    spell: PaladinLevel1Spells | PaladinLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel8(ClassLevelBase):
    level: int = attr.field(init=False, default=8)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class PaladinLevel9(ClassLevelBase):
    level: int = attr.field(init=False, default=9)
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
class PaladinLevel10(ClassLevelBase):
    level: int = attr.field(init=False, default=10)

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
class PaladinLevel11(ClassLevelBase):
    level: int = attr.field(init=False, default=11)
    spell: PaladinLevel1Spells | PaladinLevel2Spells | PaladinLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.RadiantStrikes())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class PaladinLevel12(ClassLevelBase):
    level: int = attr.field(init=False, default=12)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class PaladinLevel13(ClassLevelBase):
    level: int = attr.field(init=False, default=13)
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
class PaladinLevel14(ClassLevelBase):
    level: int = attr.field(init=False, default=14)

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
class PaladinLevel15(ClassLevelBase):
    level: int = attr.field(init=False, default=15)
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
class PaladinLevel16(ClassLevelBase):
    level: int = attr.field(init=False, default=16)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class PaladinLevel17(ClassLevelBase):
    level: int = attr.field(init=False, default=17)
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
class PaladinLevel18(ClassLevelBase):
    level: int = attr.field(init=False, default=18)

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
class PaladinLevel19(ClassLevelBase):
    level: int = attr.field(init=False, default=19)
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
class PaladinLevel20(ClassLevelBase):
    level: int = attr.field(init=False, default=20)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


class PaladinBase:

    def __init__(
        self,
        paladin_level: int,
        subclass: PaladinSubclass,
        abilities: AbilitiesStatBlock,
        skills: PaladinSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        paladin_level_1: Optional[PaladinLevel1] = None,
        paladin_level_2: Optional[PaladinLevel2] = None,
        paladin_level_3: Optional[PaladinLevel3] = None,
        paladin_level_4: Optional[PaladinLevel4] = None,
        paladin_level_5: Optional[PaladinLevel5] = None,
        paladin_level_6: Optional[PaladinLevel6] = None,
        paladin_level_7: Optional[PaladinLevel7] = None,
        paladin_level_8: Optional[PaladinLevel8] = None,
        paladin_level_9: Optional[PaladinLevel9] = None,
        paladin_level_10: Optional[PaladinLevel10] = None,
        paladin_level_11: Optional[PaladinLevel11] = None,
        paladin_level_12: Optional[PaladinLevel12] = None,
        paladin_level_13: Optional[PaladinLevel13] = None,
        paladin_level_14: Optional[PaladinLevel14] = None,
        paladin_level_15: Optional[PaladinLevel15] = None,
        paladin_level_16: Optional[PaladinLevel16] = None,
        paladin_level_17: Optional[PaladinLevel17] = None,
        paladin_level_18: Optional[PaladinLevel18] = None,
        paladin_level_19: Optional[PaladinLevel19] = None,
        paladin_level_20: Optional[PaladinLevel20] = None,
        paladin_subclass_level_3: Optional[PaladinSubclassLevel3] = None,
        paladin_subclass_level_5: Optional[PaladinSubclassLevel5] = None,
        paladin_subclass_level_7: Optional[PaladinSubclassLevel7] = None,
        paladin_subclass_level_9: Optional[PaladinSubclassLevel9] = None,
        paladin_subclass_level_13: Optional[PaladinSubclassLevel13] = None,
        paladin_subclass_level_15: Optional[PaladinSubclassLevel15] = None,
        paladin_subclass_level_17: Optional[PaladinSubclassLevel17] = None,
        paladin_subclass_level_20: Optional[PaladinSubclassLevel20] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.paladin_level = paladin_level
        self.subclass = subclass
        self.abilities = abilities
        self.skills = skills
        self.background_ability_bonuses = background_ability_bonuses
        self.background_skill_proficiencies = background_skill_proficiencies
        self.add_default_equipment = add_default_equipment
        self.origin_feat = origin_feat
        self.armor = armor
        self.weapons = weapons
        self.paladin_level_1 = paladin_level_1
        self.paladin_level_2 = paladin_level_2
        self.paladin_level_3 = paladin_level_3
        self.paladin_level_4 = paladin_level_4
        self.paladin_level_5 = paladin_level_5
        self.paladin_level_6 = paladin_level_6
        self.paladin_level_7 = paladin_level_7
        self.paladin_level_8 = paladin_level_8
        self.paladin_level_9 = paladin_level_9
        self.paladin_level_10 = paladin_level_10
        self.paladin_level_11 = paladin_level_11
        self.paladin_level_12 = paladin_level_12
        self.paladin_level_13 = paladin_level_13
        self.paladin_level_14 = paladin_level_14
        self.paladin_level_15 = paladin_level_15
        self.paladin_level_16 = paladin_level_16
        self.paladin_level_17 = paladin_level_17
        self.paladin_level_18 = paladin_level_18
        self.paladin_level_19 = paladin_level_19
        self.paladin_level_20 = paladin_level_20
        self.paladin_subclass_level_3 = paladin_subclass_level_3
        self.paladin_subclass_level_5 = paladin_subclass_level_5
        self.paladin_subclass_level_7 = paladin_subclass_level_7
        self.paladin_subclass_level_9 = paladin_subclass_level_9
        self.paladin_subclass_level_13 = paladin_subclass_level_13
        self.paladin_subclass_level_15 = paladin_subclass_level_15
        self.paladin_subclass_level_17 = paladin_subclass_level_17
        self.paladin_subclass_level_20 = paladin_subclass_level_20
        self.replace_spells = replace_spells

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_class=CharacterClass.PALADIN,
            character_subclass=self.subclass,
            level=self.paladin_level,
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=PaladinSavingThrowsStatBlock(),
            hit_die=PaladinFeatures.PALADIN_HIT_DIE,
            spell_casting_ability=Ability.CHARISMA,
        )

        # ================ LEVEL 0 ============= #
        data.add_feature(SpellSlots.SpellSlots(SpellSlots.CasterType.HALF_CASTER))
        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)

        ### Equipment ###

        if self.add_default_equipment:
            # Starting armor
            data.add_armor(Armor.ChainMailArmor())
            data.add_armor(Armor.ShieldArmor())

            # Starting weapons
            data.add_weapon(Weapons.Longsword(player_is_proficient=True))
            data.add_weapon(Weapons.Javelin(player_is_proficient=True))

        if self.armor is not None:
            for a in self.armor:
                data.add_armor(a)

        if self.weapons is not None:
            for w in self.weapons:
                data.add_weapon(w)

        # Origin feat
        data.add_feature(self.origin_feat)

        return data

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.add_features(data, self.paladin_level_1, 1)
        data = self.add_features(data, self.paladin_level_2, 2)
        data = self.add_features(data, self.paladin_level_3, 3)
        data = self.add_features(data, self.paladin_level_4, 4)
        data = self.add_features(data, self.paladin_level_5, 5)
        data = self.add_features(data, self.paladin_level_6, 6)
        data = self.add_features(data, self.paladin_level_7, 7)
        data = self.add_features(data, self.paladin_level_8, 8)
        data = self.add_features(data, self.paladin_level_9, 9)
        data = self.add_features(data, self.paladin_level_10, 10)
        data = self.add_features(data, self.paladin_level_11, 11)
        data = self.add_features(data, self.paladin_level_12, 12)
        data = self.add_features(data, self.paladin_level_13, 13)
        data = self.add_features(data, self.paladin_level_14, 14)
        data = self.add_features(data, self.paladin_level_15, 15)
        data = self.add_features(data, self.paladin_level_16, 16)
        data = self.add_features(data, self.paladin_level_17, 17)
        data = self.add_features(data, self.paladin_level_18, 18)
        data = self.add_features(data, self.paladin_level_19, 19)
        data = self.add_features(data, self.paladin_level_20, 20)

        data = self.add_features(data, self.paladin_subclass_level_3, 3)
        data = self.add_features(data, self.paladin_subclass_level_5, 5)
        data = self.add_features(data, self.paladin_subclass_level_7, 7)
        data = self.add_features(data, self.paladin_subclass_level_9, 9)
        data = self.add_features(data, self.paladin_subclass_level_13, 13)
        data = self.add_features(data, self.paladin_subclass_level_15, 15)
        data = self.add_features(data, self.paladin_subclass_level_17, 17)
        data = self.add_features(data, self.paladin_subclass_level_20, 20)

        data.replace_spells(self.replace_spells or {})
        return data

    def add_features(
        self,
        data: CharacterSheetData,
        class_level_base: Optional[ClassLevelBase],
        expected_level: int,
    ) -> CharacterSheetData:
        if class_level_base is None:
            if self.paladin_level < expected_level:
                return data
            else:
                raise ValueError(
                    f"paladin level {expected_level} features must be provided for level {expected_level}."
                )

        if class_level_base.level > self.paladin_level:
            return data

        data = class_level_base.add_features(data=data)
        return data
