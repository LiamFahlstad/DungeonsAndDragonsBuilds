from abc import ABC, abstractmethod
from typing import Optional

import attr

from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass, WarlockSubclass
from Features import (
    Armor,
    Backgrounds,
    FightingStyles,
    GeneralFeats,
    OriginFeats,
    Weapons,
)
from Features.ClassFeatures import SpellSlots, WarlockFeatures
from Spells.Definitions import (
    WarlockLevel1Spells,
    WarlockLevel2Spells,
    WarlockLevel3Spells,
    WarlockLevel4Spells,
    WarlockLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import WarlockSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class ClassLevelFeatures(ABC):
    level: int = attr.field(init=False)

    @abstractmethod
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        pass


@attr.dataclass
class WarlockSubclassLevel3(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockSubclassLevel5(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockSubclassLevel7(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockSubclassLevel9(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockSubclassLevel13(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockSubclassLevel15(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockSubclassLevel17(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockSubclassLevel20(ClassLevelFeatures):
    pass


@attr.dataclass
class WarlockLevel1(ClassLevelFeatures):
    level: int = attr.field(init=False, default=1)
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    spell_1: WarlockLevel1Spells
    spell_2: WarlockLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_feature(WarlockFeatures.ReplacingEldritchInvocations())
        data.add_feature(WarlockFeatures.ReplacingCantripsAndSpells())
        data.add_feature(WarlockFeatures.RegainingSpellSlots())

        # Add/Change prepared spells:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WarlockLevel2(ClassLevelFeatures):
    level: int = attr.field(init=False, default=2)
    fighting_style: FightingStyles.FightingStyle
    spell: WarlockLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        # Choose one Fighting Style
        data.add_fighting_style(self.fighting_style)

        # Automatic feature
        data.add_feature(WarlockFeatures.WarlocksSmite())
        data.add_spell(WarlockLevel1Spells.DIVINE_SMITE)

        # Add prepared spells:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel3(ClassLevelFeatures):
    level: int = attr.field(init=False, default=3)
    spell: WarlockLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        channel_divinity_feature = WarlockFeatures.ChannelDivinity()
        channel_divinity_feature.add_spell("Divine Sense")
        data.add_feature(channel_divinity_feature)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel4(ClassLevelFeatures):
    level: int = attr.field(init=False, default=4)
    general_feat: GeneralFeats.GeneralFeat
    spell: WarlockLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel5(ClassLevelFeatures):
    level: int = attr.field(init=False, default=5)
    spell: WarlockLevel1Spells | WarlockLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        # Automatic feature
        data.add_feature(WarlockFeatures.ExtraAttack())
        data.add_feature(WarlockFeatures.FaithfulSteed())
        data.add_spell(WarlockLevel2Spells.FIND_STEED)

        # Oath of vengeance features
        data.add_spell(WarlockLevel2Spells.HOLD_PERSON)
        data.add_spell(WarlockLevel2Spells.MISTY_STEP)

        # Add/Change prepared spells:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel6(ClassLevelFeatures):
    level: int = attr.field(init=False, default=6)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.AuraOfProtection())
        return data


@attr.dataclass
class WarlockLevel7(ClassLevelFeatures):
    level: int = attr.field(init=False, default=7)
    spell: WarlockLevel1Spells | WarlockLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel8(ClassLevelFeatures):
    level: int = attr.field(init=False, default=8)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class WarlockLevel9(ClassLevelFeatures):
    level: int = attr.field(init=False, default=9)
    spell: WarlockLevel1Spells | WarlockLevel2Spells | WarlockLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: WarlockFeatures.ChannelDivinity = (
            data.get_features_by_type(WarlockFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.add_spell("Abjure Foes")
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel10(ClassLevelFeatures):
    level: int = attr.field(init=False, default=10)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: WarlockFeatures.AuraOfProtection = (
            data.get_features_by_type(WarlockFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(WarlockFeatures.AuraOfCourage())
        return data


@attr.dataclass
class WarlockLevel11(ClassLevelFeatures):
    level: int = attr.field(init=False, default=11)
    spell: WarlockLevel1Spells | WarlockLevel2Spells | WarlockLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.RadiantStrikes())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel12(ClassLevelFeatures):
    level: int = attr.field(init=False, default=12)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class WarlockLevel13(ClassLevelFeatures):
    level: int = attr.field(init=False, default=13)
    spell: (
        WarlockLevel1Spells
        | WarlockLevel2Spells
        | WarlockLevel3Spells
        | WarlockLevel4Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel14(ClassLevelFeatures):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        lay_on_hands: WarlockFeatures.LayOnHands = data.get_features_by_type(
            WarlockFeatures.LayOnHands
        )[0]
        lay_on_hands.add_feature(WarlockFeatures.RestoringTouch())
        return data


@attr.dataclass
class WarlockLevel15(ClassLevelFeatures):
    level: int = attr.field(init=False, default=15)
    spell: (
        WarlockLevel1Spells
        | WarlockLevel2Spells
        | WarlockLevel3Spells
        | WarlockLevel4Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel16(ClassLevelFeatures):
    level: int = attr.field(init=False, default=16)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class WarlockLevel17(ClassLevelFeatures):
    level: int = attr.field(init=False, default=17)
    spell_1: (
        WarlockLevel1Spells
        | WarlockLevel2Spells
        | WarlockLevel3Spells
        | WarlockLevel4Spells
        | WarlockLevel5Spells
    )
    spell_2: (
        WarlockLevel1Spells
        | WarlockLevel2Spells
        | WarlockLevel3Spells
        | WarlockLevel4Spells
        | WarlockLevel5Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WarlockLevel18(ClassLevelFeatures):
    level: int = attr.field(init=False, default=18)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: WarlockFeatures.AuraOfProtection = (
            data.get_features_by_type(WarlockFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(WarlockFeatures.AuraExpansion())
        return data


@attr.dataclass
class WarlockLevel19(ClassLevelFeatures):
    level: int = attr.field(init=False, default=19)
    spell: (
        WarlockLevel1Spells
        | WarlockLevel2Spells
        | WarlockLevel3Spells
        | WarlockLevel4Spells
        | WarlockLevel5Spells
    )

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel20(ClassLevelFeatures):
    level: int = attr.field(init=False, default=20)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class WarlockFeaturePerLevel:
    warlock_level_1: Optional[WarlockLevel1] = None
    warlock_level_2: Optional[WarlockLevel2] = None
    warlock_level_3: Optional[WarlockLevel3] = None
    warlock_level_4: Optional[WarlockLevel4] = None
    warlock_level_5: Optional[WarlockLevel5] = None
    warlock_level_6: Optional[WarlockLevel6] = None
    warlock_level_7: Optional[WarlockLevel7] = None
    warlock_level_8: Optional[WarlockLevel8] = None
    warlock_level_9: Optional[WarlockLevel9] = None
    warlock_level_10: Optional[WarlockLevel10] = None
    warlock_level_11: Optional[WarlockLevel11] = None
    warlock_level_12: Optional[WarlockLevel12] = None
    warlock_level_13: Optional[WarlockLevel13] = None
    warlock_level_14: Optional[WarlockLevel14] = None
    warlock_level_15: Optional[WarlockLevel15] = None
    warlock_level_16: Optional[WarlockLevel16] = None
    warlock_level_17: Optional[WarlockLevel17] = None
    warlock_level_18: Optional[WarlockLevel18] = None
    warlock_level_19: Optional[WarlockLevel19] = None
    warlock_level_20: Optional[WarlockLevel20] = None
    warlock_subclass_level_3: Optional[WarlockSubclassLevel3] = None
    warlock_subclass_level_5: Optional[WarlockSubclassLevel5] = None
    warlock_subclass_level_7: Optional[WarlockSubclassLevel7] = None
    warlock_subclass_level_9: Optional[WarlockSubclassLevel9] = None
    warlock_subclass_level_13: Optional[WarlockSubclassLevel13] = None
    warlock_subclass_level_15: Optional[WarlockSubclassLevel15] = None
    warlock_subclass_level_17: Optional[WarlockSubclassLevel17] = None
    warlock_subclass_level_20: Optional[WarlockSubclassLevel20] = None

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        warlock_level = data.get_level_for_class(CharacterClass.WARLOCK)
        for level_features in attr.fields(self.__class__):
            class_level_features: Optional[ClassLevelFeatures] = getattr(
                self, level_features.name
            )
            expected_level: int = (
                class_level_features.level
                if class_level_features is not None
                else int(level_features.name.split("_")[-1])
            )

            if class_level_features is None:
                # Skip if the character level is lower than the expected level
                if warlock_level < expected_level:
                    continue

                # Must provide features for this level
                raise ValueError(
                    f"warlock level {expected_level} features must be provided for level {expected_level}."
                )

            # Skip if the character level is lower than the class level features
            if class_level_features.level > warlock_level:
                return data

            # Add features for this level
            data = class_level_features.add_features(data=data)
        return data


class WarlockBase:

    def __init__(
        self,
        warlock_level: int,
        warlock_feature_per_level: WarlockFeaturePerLevel,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.warlock_level = warlock_level
        self.warlock_feature_per_level = warlock_feature_per_level
        self.replace_spells = replace_spells

    @abstractmethod
    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        pass

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.warlock_feature_per_level.add_features(data)
        data.replace_spells(self.replace_spells or {})
        return data


class WarlockStarter(WarlockBase):

    def __init__(
        self,
        warlock_level: int,
        warlock_feature_per_level: WarlockFeaturePerLevel,
        subclass: WarlockSubclass,
        abilities: AbilitiesStatBlock,
        skills: WarlockSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.warlock_level = warlock_level
        self.warlock_feature_per_level = warlock_feature_per_level
        self.subclass = subclass
        self.abilities = abilities
        self.skills = skills
        self.background_ability_bonuses = background_ability_bonuses
        self.background_skill_proficiencies = background_skill_proficiencies
        self.add_default_equipment = add_default_equipment
        self.origin_feat = origin_feat
        self.armor = armor
        self.weapons = weapons
        super().__init__(
            warlock_level=warlock_level,
            warlock_feature_per_level=warlock_feature_per_level,
            replace_spells=replace_spells,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.WARLOCK: self.warlock_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=WarlockSavingThrowsStatBlock(),
            starter_class=CharacterClass.WARLOCK,
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


class WarlockMulticlass(WarlockBase):

    def __init__(
        self,
        warlock_level: int,
        warlock_feature_per_level: WarlockFeaturePerLevel,
        subclass: WarlockSubclass,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        self.warlock_level = warlock_level
        super().__init__(
            warlock_level=warlock_level,
            warlock_feature_per_level=warlock_feature_per_level,
            replace_spells=replace_spells,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.WARLOCK: self.warlock_level},
            spell_casting_ability=Ability.CHARISMA,
        )

        # ================ LEVEL 0 ============= #
        data.add_feature(SpellSlots.SpellSlots(SpellSlots.CasterType.HALF_CASTER))

        return data
