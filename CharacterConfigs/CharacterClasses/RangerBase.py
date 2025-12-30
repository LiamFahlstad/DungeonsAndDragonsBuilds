from abc import ABC, abstractmethod
from typing import Optional

import attr

from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass, RangerSubclass, Skill
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
class ClassLevelFeatures(ABC):
    level: int = attr.field(init=False)

    @abstractmethod
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        pass


@attr.dataclass
class RangerSubclassLevel3(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerSubclassLevel5(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerSubclassLevel7(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerSubclassLevel9(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerSubclassLevel13(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerSubclassLevel15(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerSubclassLevel17(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerSubclassLevel20(ClassLevelFeatures):
    pass


@attr.dataclass
class RangerLevel1(ClassLevelFeatures):
    level: int = attr.field(init=False, default=1)
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
class RangerLevel2(ClassLevelFeatures):
    level: int = attr.field(init=False, default=2)
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
class RangerLevel3(ClassLevelFeatures):
    level: int = attr.field(init=False, default=3)
    spell: RangerLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel4(ClassLevelFeatures):
    level: int = attr.field(init=False, default=4)
    general_feat: GeneralFeats.GeneralFeat
    spell: RangerLevel1Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel5(ClassLevelFeatures):
    level: int = attr.field(init=False, default=5)
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
class RangerLevel6(ClassLevelFeatures):
    level: int = attr.field(init=False, default=6)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RangerFeatures.AuraOfProtection())
        return data


@attr.dataclass
class RangerLevel7(ClassLevelFeatures):
    level: int = attr.field(init=False, default=7)
    spell: RangerLevel1Spells | RangerLevel2Spells

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel8(ClassLevelFeatures):
    level: int = attr.field(init=False, default=8)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RangerLevel9(ClassLevelFeatures):
    level: int = attr.field(init=False, default=9)
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
class RangerLevel10(ClassLevelFeatures):
    level: int = attr.field(init=False, default=10)

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
class RangerLevel11(ClassLevelFeatures):
    level: int = attr.field(init=False, default=11)
    spell: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.RadiantStrikes())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RangerLevel12(ClassLevelFeatures):
    level: int = attr.field(init=False, default=12)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RangerLevel13(ClassLevelFeatures):
    level: int = attr.field(init=False, default=13)
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
class RangerLevel14(ClassLevelFeatures):
    level: int = attr.field(init=False, default=14)

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
class RangerLevel15(ClassLevelFeatures):
    level: int = attr.field(init=False, default=15)
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
class RangerLevel16(ClassLevelFeatures):
    level: int = attr.field(init=False, default=16)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RangerLevel17(ClassLevelFeatures):
    level: int = attr.field(init=False, default=17)
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
class RangerLevel18(ClassLevelFeatures):
    level: int = attr.field(init=False, default=18)

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
class RangerLevel19(ClassLevelFeatures):
    level: int = attr.field(init=False, default=19)
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
class RangerLevel20(ClassLevelFeatures):
    level: int = attr.field(init=False, default=20)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RangerFeaturePerLevel:
    ranger_level_1: Optional[RangerLevel1] = None
    ranger_level_2: Optional[RangerLevel2] = None
    ranger_level_3: Optional[RangerLevel3] = None
    ranger_level_4: Optional[RangerLevel4] = None
    ranger_level_5: Optional[RangerLevel5] = None
    ranger_level_6: Optional[RangerLevel6] = None
    ranger_level_7: Optional[RangerLevel7] = None
    ranger_level_8: Optional[RangerLevel8] = None
    ranger_level_9: Optional[RangerLevel9] = None
    ranger_level_10: Optional[RangerLevel10] = None
    ranger_level_11: Optional[RangerLevel11] = None
    ranger_level_12: Optional[RangerLevel12] = None
    ranger_level_13: Optional[RangerLevel13] = None
    ranger_level_14: Optional[RangerLevel14] = None
    ranger_level_15: Optional[RangerLevel15] = None
    ranger_level_16: Optional[RangerLevel16] = None
    ranger_level_17: Optional[RangerLevel17] = None
    ranger_level_18: Optional[RangerLevel18] = None
    ranger_level_19: Optional[RangerLevel19] = None
    ranger_level_20: Optional[RangerLevel20] = None
    ranger_subclass_level_3: Optional[RangerSubclassLevel3] = None
    ranger_subclass_level_5: Optional[RangerSubclassLevel5] = None
    ranger_subclass_level_7: Optional[RangerSubclassLevel7] = None
    ranger_subclass_level_9: Optional[RangerSubclassLevel9] = None
    ranger_subclass_level_13: Optional[RangerSubclassLevel13] = None
    ranger_subclass_level_15: Optional[RangerSubclassLevel15] = None
    ranger_subclass_level_17: Optional[RangerSubclassLevel17] = None
    ranger_subclass_level_20: Optional[RangerSubclassLevel20] = None

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        ranger_level = data.get_level_for_class(CharacterClass.RANGER)
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
                if ranger_level < expected_level:
                    continue

                # Must provide features for this level
                raise ValueError(
                    f"ranger level {expected_level} features must be provided for level {expected_level}."
                )

            # Skip if the character level is lower than the class level features
            if class_level_features.level > ranger_level:
                return data

            # Add features for this level
            data = class_level_features.add_features(data=data)
        return data


class RangerBase:

    def __init__(
        self,
        ranger_level: int,
        ranger_feature_per_level: RangerFeaturePerLevel,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.ranger_level = ranger_level
        self.ranger_feature_per_level = ranger_feature_per_level
        self.replace_spells = replace_spells

    @abstractmethod
    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        pass

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.ranger_feature_per_level.add_features(data)
        data.replace_spells(self.replace_spells or {})
        return data


class RangerStarter(RangerBase):

    def __init__(
        self,
        ranger_level: int,
        ranger_feature_per_level: RangerFeaturePerLevel,
        subclass: RangerSubclass,
        abilities: AbilitiesStatBlock,
        skills: RangerSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.ranger_level = ranger_level
        self.ranger_feature_per_level = ranger_feature_per_level
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
            ranger_level=ranger_level,
            ranger_feature_per_level=ranger_feature_per_level,
            replace_spells=replace_spells,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.RANGER: self.ranger_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=RangerSavingThrowsStatBlock(),
            starter_class=CharacterClass.RANGER,
            spell_casting_ability=Ability.WISDOM,
        )

        # ================ LEVEL 0 ============= #
        data.add_feature(SpellSlots.SpellSlots(SpellSlots.CasterType.HALF_CASTER))
        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)

        ### Equipment ###

        if self.add_default_equipment:
            # Starting armor
            data.add_armor(Armor.StuddedLeatherArmor())

            # Starting weapons
            data.add_weapon(Weapons.Scimitar(player_is_proficient=True))
            data.add_weapon(Weapons.Shortsword(player_is_proficient=True))
            data.add_weapon(Weapons.Longbow(player_is_proficient=True))

        if self.armor is not None:
            for a in self.armor:
                data.add_armor(a)

        if self.weapons is not None:
            for w in self.weapons:
                data.add_weapon(w)

        # Origin feat
        data.add_feature(self.origin_feat)

        return data


class RangerMulticlass(RangerBase):

    def __init__(
        self,
        ranger_level: int,
        ranger_feature_per_level: RangerFeaturePerLevel,
        subclass: RangerSubclass,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        self.ranger_level = ranger_level
        super().__init__(
            ranger_level=ranger_level,
            ranger_feature_per_level=ranger_feature_per_level,
            replace_spells=replace_spells,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.RANGER: self.ranger_level},
            spell_casting_ability=Ability.WISDOM,
        )

        # ================ LEVEL 0 ============= #
        data.add_feature(SpellSlots.SpellSlots(SpellSlots.CasterType.HALF_CASTER))

        return data
