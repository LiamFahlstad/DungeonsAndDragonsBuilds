from abc import ABC, abstractmethod
from typing import Optional
import attr
from Definitions import Ability, CharacterClass, BarbarianSubclass, Skill
import Definitions
from Features import GeneralFeats, OriginFeats
from CharacterSheetCreator import CharacterSheetData
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import BarbarianFeatures
from StatBlocks.AbilitiesStatBlock import (
    AbilitiesStatBlock,
)
from StatBlocks.SavingThrowsStatBlock import BarbarianSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


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
class BarbarianSubclassLevel3(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianSubclassLevel5(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianSubclassLevel7(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianSubclassLevel9(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianSubclassLevel13(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianSubclassLevel15(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianSubclassLevel17(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianSubclassLevel20(ClassLevelFeatures):
    pass


@attr.dataclass
class BarbarianLevel1(ClassLevelFeatures):
    level: int = attr.field(init=False, default=1)
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(BarbarianFeatures.Rage())
        data.add_feature(BarbarianFeatures.UnarmoredDefense())
        data.add_feature(BarbarianFeatures.UnarmoredDefenseText())
        data.add_feature(BarbarianFeatures.WeaponMastery())
        return data


@attr.dataclass
class BarbarianLevel2(ClassLevelFeatures):
    level: int = attr.field(init=False, default=2)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.DangerSenseText())
        data.add_feature(BarbarianFeatures.DangerSense())
        data.add_feature(BarbarianFeatures.RecklessAttack())
        return data


@attr.dataclass
class BarbarianLevel3(ClassLevelFeatures):
    level: int = attr.field(init=False, default=3)
    skill: Definitions.Skill

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.PrimalKnowledgeSkillProficiency(self.skill))
        data.add_feature(BarbarianFeatures.PrimalKnowledge())
        return data


@attr.dataclass
class BarbarianLevel4(ClassLevelFeatures):
    level: int = attr.field(init=False, default=4)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        data.add_feature(self.general_feat)

        return data


@attr.dataclass
class BarbarianLevel5(ClassLevelFeatures):
    level: int = attr.field(init=False, default=5)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        # Automatic feature
        data.add_feature(BarbarianFeatures.ExtraAttack())
        data.add_feature(BarbarianFeatures.FaithfulSteed())

        # Oath of vengeance features

        return data


@attr.dataclass
class BarbarianLevel6(ClassLevelFeatures):
    level: int = attr.field(init=False, default=6)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.AuraOfProtection())
        return data


@attr.dataclass
class BarbarianLevel7(ClassLevelFeatures):
    level: int = attr.field(init=False, default=7)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        return data


@attr.dataclass
class BarbarianLevel8(ClassLevelFeatures):
    level: int = attr.field(init=False, default=8)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BarbarianLevel9(ClassLevelFeatures):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: BarbarianFeatures.ChannelDivinity = (
            data.get_features_by_type(BarbarianFeatures.ChannelDivinity)[0]
        )

        return data


@attr.dataclass
class BarbarianLevel10(ClassLevelFeatures):
    level: int = attr.field(init=False, default=10)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: BarbarianFeatures.AuraOfProtection = (
            data.get_features_by_type(BarbarianFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(BarbarianFeatures.AuraOfCourage())
        return data


@attr.dataclass
class BarbarianLevel11(ClassLevelFeatures):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.RadiantStrikes())

        return data


@attr.dataclass
class BarbarianLevel12(ClassLevelFeatures):
    level: int = attr.field(init=False, default=12)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BarbarianLevel13(ClassLevelFeatures):
    level: int = attr.field(init=False, default=13)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel14(ClassLevelFeatures):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        lay_on_hands: BarbarianFeatures.LayOnHands = data.get_features_by_type(
            BarbarianFeatures.LayOnHands
        )[0]
        lay_on_hands.add_feature(BarbarianFeatures.RestoringTouch())
        return data


@attr.dataclass
class BarbarianLevel15(ClassLevelFeatures):
    level: int = attr.field(init=False, default=15)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel16(ClassLevelFeatures):
    level: int = attr.field(init=False, default=16)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BarbarianLevel17(ClassLevelFeatures):
    level: int = attr.field(init=False, default=17)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel18(ClassLevelFeatures):
    level: int = attr.field(init=False, default=18)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: BarbarianFeatures.AuraOfProtection = (
            data.get_features_by_type(BarbarianFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(BarbarianFeatures.AuraExpansion())
        return data


@attr.dataclass
class BarbarianLevel19(ClassLevelFeatures):
    level: int = attr.field(init=False, default=19)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        return data


@attr.dataclass
class BarbarianLevel20(ClassLevelFeatures):
    level: int = attr.field(init=False, default=20)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianFeaturePerLevel:
    barbarian_level_1: Optional[BarbarianLevel1] = None
    barbarian_level_2: Optional[BarbarianLevel2] = None
    barbarian_level_3: Optional[BarbarianLevel3] = None
    barbarian_level_4: Optional[BarbarianLevel4] = None
    barbarian_level_5: Optional[BarbarianLevel5] = None
    barbarian_level_6: Optional[BarbarianLevel6] = None
    barbarian_level_7: Optional[BarbarianLevel7] = None
    barbarian_level_8: Optional[BarbarianLevel8] = None
    barbarian_level_9: Optional[BarbarianLevel9] = None
    barbarian_level_10: Optional[BarbarianLevel10] = None
    barbarian_level_11: Optional[BarbarianLevel11] = None
    barbarian_level_12: Optional[BarbarianLevel12] = None
    barbarian_level_13: Optional[BarbarianLevel13] = None
    barbarian_level_14: Optional[BarbarianLevel14] = None
    barbarian_level_15: Optional[BarbarianLevel15] = None
    barbarian_level_16: Optional[BarbarianLevel16] = None
    barbarian_level_17: Optional[BarbarianLevel17] = None
    barbarian_level_18: Optional[BarbarianLevel18] = None
    barbarian_level_19: Optional[BarbarianLevel19] = None
    barbarian_level_20: Optional[BarbarianLevel20] = None
    barbarian_subclass_level_3: Optional[BarbarianSubclassLevel3] = None
    barbarian_subclass_level_5: Optional[BarbarianSubclassLevel5] = None
    barbarian_subclass_level_7: Optional[BarbarianSubclassLevel7] = None
    barbarian_subclass_level_9: Optional[BarbarianSubclassLevel9] = None
    barbarian_subclass_level_13: Optional[BarbarianSubclassLevel13] = None
    barbarian_subclass_level_15: Optional[BarbarianSubclassLevel15] = None
    barbarian_subclass_level_17: Optional[BarbarianSubclassLevel17] = None
    barbarian_subclass_level_20: Optional[BarbarianSubclassLevel20] = None

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        barbarian_level = data.get_level_for_class(CharacterClass.BARBARIAN)
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
                if barbarian_level < expected_level:
                    continue

                # Must provide features for this level
                raise ValueError(
                    f"barbarian level {expected_level} features must be provided for level {expected_level}."
                )

            # Skip if the character level is lower than the class level features
            if class_level_features.level > barbarian_level:
                return data

            # Add features for this level
            data = class_level_features.add_features(data=data)
        return data


class BarbarianBase:

    def __init__(
        self,
        barbarian_level: int,
        barbarian_feature_per_level: BarbarianFeaturePerLevel,
    ):
        self.barbarian_level = barbarian_level
        self.barbarian_feature_per_level = barbarian_feature_per_level

    @abstractmethod
    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        pass

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.barbarian_feature_per_level.add_features(data)
        return data


class BarbarianStarter(BarbarianBase):

    def __init__(
        self,
        barbarian_level: int,
        barbarian_feature_per_level: BarbarianFeaturePerLevel,
        subclass: BarbarianSubclass,
        abilities: AbilitiesStatBlock,
        skills: BarbarianSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
    ):
        self.barbarian_level = barbarian_level
        self.barbarian_feature_per_level = barbarian_feature_per_level
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
            barbarian_level=barbarian_level,
            barbarian_feature_per_level=barbarian_feature_per_level,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.BARBARIAN: self.barbarian_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=BarbarianSavingThrowsStatBlock(),
            starter_class=CharacterClass.BARBARIAN,
        )

        # ================ LEVEL 0 ============= #

        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)

        ### Equipment ###

        if self.add_default_equipment:
            # Starting armor
            # data.add_armor(Armor.StuddedLeatherArmor())

            # Starting weapons
            data.add_weapon(Weapons.Greataxe(player_is_proficient=True))
            # data.add_weapon(Weapons.Handaxe(player_is_proficient=True))

        if self.armor is not None:
            for a in self.armor:
                data.add_armor(a)

        if self.weapons is not None:
            for w in self.weapons:
                data.add_weapon(w)

        # Origin feat
        data.add_feature(self.origin_feat)

        return data


class BarbarianMulticlass(BarbarianBase):

    def __init__(
        self,
        barbarian_level: int,
        barbarian_feature_per_level: BarbarianFeaturePerLevel,
        subclass: BarbarianSubclass,
    ):
        self.subclass = subclass
        self.barbarian_level = barbarian_level
        super().__init__(
            barbarian_level=barbarian_level,
            barbarian_feature_per_level=barbarian_feature_per_level,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.BARBARIAN: self.barbarian_level},
        )

        # ================ LEVEL 0 ============= #

        return data
