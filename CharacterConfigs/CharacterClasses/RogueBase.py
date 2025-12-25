from abc import ABC, abstractmethod
from typing import Optional
import attr
from Definitions import Ability, CharacterClass, RogueSubclass, Skill
import Definitions
from Features import GeneralFeats, OriginFeats
from CharacterSheetCreator import CharacterSheetData
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import PaladinFeatures, RogueFeatures
from StatBlocks.AbilitiesStatBlock import (
    AbilitiesStatBlock,
)
from StatBlocks.SavingThrowsStatBlock import RogueSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


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
class RogueSubclassLevel3(ClassLevelFeatures):
    pass


@attr.dataclass
class RogueSubclassLevel9(ClassLevelFeatures):
    pass


@attr.dataclass
class RogueSubclassLevel13(ClassLevelFeatures):
    pass


@attr.dataclass
class RogueSubclassLevel17(ClassLevelFeatures):
    pass


@attr.dataclass
class RogueLevel1(ClassLevelFeatures):
    level: int = attr.field(init=False, default=1)
    skill_1: Definitions.Skill
    skill_2: Definitions.Skill
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(RogueFeatures.Expertise(self.skill_1, self.skill_2))
        data.add_feature(RogueFeatures.SneakAttack())
        data.add_feature(RogueFeatures.ThievesCant())
        data.add_feature(RogueFeatures.WeaponMastery())
        return data


@attr.dataclass
class RogueLevel2(ClassLevelFeatures):
    level: int = attr.field(init=False, default=2)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.CunningAction())
        return data


@attr.dataclass
class RogueLevel3(ClassLevelFeatures):
    level: int = attr.field(init=False, default=3)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.SteadyAim())
        return data


@attr.dataclass
class RogueLevel4(ClassLevelFeatures):
    level: int = attr.field(init=False, default=4)
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel5(ClassLevelFeatures):
    level: int = attr.field(init=False, default=5)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.UncannyDodge())
        return data


@attr.dataclass
class RogueLevel6(ClassLevelFeatures):
    level: int = attr.field(init=False, default=6)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel7(ClassLevelFeatures):
    level: int = attr.field(init=False, default=7)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.ReliableTalent())
        return data


@attr.dataclass
class RogueLevel8(ClassLevelFeatures):
    level: int = attr.field(init=False, default=8)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel9(ClassLevelFeatures):
    level: int = attr.field(init=False, default=9)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel10(ClassLevelFeatures):
    level: int = attr.field(init=False, default=10)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel11(ClassLevelFeatures):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.ImprovedCunningStrike())
        return data


@attr.dataclass
class RogueLevel12(ClassLevelFeatures):
    level: int = attr.field(init=False, default=12)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel13(ClassLevelFeatures):
    level: int = attr.field(init=False, default=13)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel14(ClassLevelFeatures):
    level: int = attr.field(init=False, default=14)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.DeviousStrikes())
        return data


@attr.dataclass
class RogueLevel15(ClassLevelFeatures):
    level: int = attr.field(init=False, default=15)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.SlipperyMind())
        return data


@attr.dataclass
class RogueLevel16(ClassLevelFeatures):
    level: int = attr.field(init=False, default=16)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel17(ClassLevelFeatures):
    level: int = attr.field(init=False, default=17)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel18(ClassLevelFeatures):
    level: int = attr.field(init=False, default=18)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueFeatures.Elusive())
        return data


@attr.dataclass
class RogueLevel19(ClassLevelFeatures):
    level: int = attr.field(init=False, default=19)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        return data


@attr.dataclass
class RogueLevel20(ClassLevelFeatures):
    level: int = attr.field(init=False, default=20)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.StrokeOfLuck())
        return data


@attr.dataclass
class RogueFeaturePerLevel:
    rogue_level_1: Optional[RogueLevel1] = None
    rogue_level_2: Optional[RogueLevel2] = None
    rogue_level_3: Optional[RogueLevel3] = None
    rogue_level_4: Optional[RogueLevel4] = None
    rogue_level_5: Optional[RogueLevel5] = None
    rogue_level_6: Optional[RogueLevel6] = None
    rogue_level_7: Optional[RogueLevel7] = None
    rogue_level_8: Optional[RogueLevel8] = None
    rogue_level_9: Optional[RogueLevel9] = None
    rogue_level_10: Optional[RogueLevel10] = None
    rogue_level_11: Optional[RogueLevel11] = None
    rogue_level_12: Optional[RogueLevel12] = None
    rogue_level_13: Optional[RogueLevel13] = None
    rogue_level_14: Optional[RogueLevel14] = None
    rogue_level_15: Optional[RogueLevel15] = None
    rogue_level_16: Optional[RogueLevel16] = None
    rogue_level_17: Optional[RogueLevel17] = None
    rogue_level_18: Optional[RogueLevel18] = None
    rogue_level_19: Optional[RogueLevel19] = None
    rogue_level_20: Optional[RogueLevel20] = None
    rogue_subclass_level_3: Optional[RogueSubclassLevel3] = None
    rogue_subclass_level_9: Optional[RogueSubclassLevel9] = None
    rogue_subclass_level_13: Optional[RogueSubclassLevel13] = None
    rogue_subclass_level_17: Optional[RogueSubclassLevel17] = None

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rogue_level = data.get_level_for_class(CharacterClass.ROGUE)
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
                if rogue_level < expected_level:
                    continue

                # Must provide features for this level
                raise ValueError(
                    f"rogue level {expected_level} features must be provided for level {expected_level}."
                )

            # Skip if the character level is lower than the class level features
            if class_level_features.level > rogue_level:
                return data

            # Add features for this level
            data = class_level_features.add_features(data=data)
        return data


class RogueBase:

    def __init__(
        self,
        rogue_level: int,
        rogue_feature_per_level: RogueFeaturePerLevel,
    ):
        self.rogue_level = rogue_level
        self.rogue_feature_per_level = rogue_feature_per_level

    @abstractmethod
    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        pass

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.rogue_feature_per_level.add_features(data)
        return data


class RogueStarter(RogueBase):

    def __init__(
        self,
        rogue_level: int,
        rogue_feature_per_level: RogueFeaturePerLevel,
        subclass: RogueSubclass,
        abilities: AbilitiesStatBlock,
        skills: RogueSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
    ):
        self.rogue_level = rogue_level
        self.rogue_feature_per_level = rogue_feature_per_level
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
            rogue_level=rogue_level,
            rogue_feature_per_level=rogue_feature_per_level,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.ROGUE: self.rogue_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=RogueSavingThrowsStatBlock(),
            starter_class=CharacterClass.ROGUE,
        )

        # ================ LEVEL 0 ============= #

        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)

        ### Equipment ###

        if self.add_default_equipment:
            # Starting armor
            data.add_armor(Armor.LeatherArmor())

            # Starting weapons
            data.add_weapon(Weapons.Shortsword(player_is_proficient=True))
            data.add_weapon(Weapons.Dagger(player_is_proficient=True))
            data.add_weapon(Weapons.Scimitar(player_is_proficient=True))

        if self.armor is not None:
            for a in self.armor:
                data.add_armor(a)

        if self.weapons is not None:
            for w in self.weapons:
                data.add_weapon(w)

        # Origin feat
        data.add_feature(self.origin_feat)

        return data


class RogueMulticlass(RogueBase):

    def __init__(
        self,
        rogue_level: int,
        rogue_feature_per_level: RogueFeaturePerLevel,
        subclass: RogueSubclass,
    ):
        self.subclass = subclass
        self.rogue_level = rogue_level
        super().__init__(
            rogue_level=rogue_level,
            rogue_feature_per_level=rogue_feature_per_level,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.ROGUE: self.rogue_level},
        )

        # ================ LEVEL 0 ============= #

        return data
