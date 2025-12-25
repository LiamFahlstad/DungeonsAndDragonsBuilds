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
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.AbilitiesStatBlock import (
    AbilitiesStatBlock,
)
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


@attr.dataclass
class LevelFeatures(ABC):
    level: int = attr.field(init=False)

    @abstractmethod
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        pass


@attr.dataclass
class SubclassLevel3(LevelFeatures):
    level: int = attr.field(init=False, default=3)


@attr.dataclass
class SubclassLevel4(LevelFeatures):
    level: int = attr.field(init=False, default=4)


@attr.dataclass
class SubclassLevel5(LevelFeatures):
    level: int = attr.field(init=False, default=5)


@attr.dataclass
class SubclassLevel6(LevelFeatures):
    level: int = attr.field(init=False, default=6)


@attr.dataclass
class SubclassLevel7(LevelFeatures):
    level: int = attr.field(init=False, default=7)


@attr.dataclass
class SubclassLevel8(LevelFeatures):
    level: int = attr.field(init=False, default=8)


@attr.dataclass
class SubclassLevel9(LevelFeatures):
    level: int = attr.field(init=False, default=9)


@attr.dataclass
class SubclassLevel10(LevelFeatures):
    level: int = attr.field(init=False, default=10)


@attr.dataclass
class SubclassLevel11(LevelFeatures):
    level: int = attr.field(init=False, default=11)


@attr.dataclass
class SubclassLevel12(LevelFeatures):
    level: int = attr.field(init=False, default=12)


@attr.dataclass
class SubclassLevel13(LevelFeatures):
    level: int = attr.field(init=False, default=13)


@attr.dataclass
class SubclassLevel14(LevelFeatures):
    level: int = attr.field(init=False, default=14)


@attr.dataclass
class SubclassLevel15(LevelFeatures):
    level: int = attr.field(init=False, default=15)


@attr.dataclass
class SubclassLevel16(LevelFeatures):
    level: int = attr.field(init=False, default=16)


@attr.dataclass
class SubclassLevel17(LevelFeatures):
    level: int = attr.field(init=False, default=17)


@attr.dataclass
class SubclassLevel18(LevelFeatures):
    level: int = attr.field(init=False, default=18)


@attr.dataclass
class SubclassLevel19(LevelFeatures):
    level: int = attr.field(init=False, default=19)


@attr.dataclass
class SubclassLevel20(LevelFeatures):
    level: int = attr.field(init=False, default=20)


@attr.dataclass
class BaseClassLevel1(LevelFeatures):
    level: int = attr.field(init=False, default=1)
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon


@attr.dataclass
class BaseClassLevel2(LevelFeatures):
    level: int = attr.field(init=False, default=2)


@attr.dataclass
class BaseClassLevel3(LevelFeatures):
    level: int = attr.field(init=False, default=3)
    skill: Definitions.Skill


@attr.dataclass
class BaseClassLevel4(LevelFeatures):
    level: int = attr.field(init=False, default=4)
    general_feat: GeneralFeats.GeneralFeat


@attr.dataclass
class BaseClassLevel5(LevelFeatures):
    level: int = attr.field(init=False, default=5)


@attr.dataclass
class BaseClassLevel6(LevelFeatures):
    level: int = attr.field(init=False, default=6)


@attr.dataclass
class BaseClassLevel7(LevelFeatures):
    level: int = attr.field(init=False, default=7)


@attr.dataclass
class BaseClassLevel8(LevelFeatures):
    level: int = attr.field(init=False, default=8)
    general_feat: GeneralFeats.GeneralFeat


@attr.dataclass
class BaseClassLevel9(LevelFeatures):
    level: int = attr.field(init=False, default=9)


@attr.dataclass
class BaseClassLevel10(LevelFeatures):
    level: int = attr.field(init=False, default=10)


@attr.dataclass
class BaseClassLevel11(LevelFeatures):
    level: int = attr.field(init=False, default=11)


@attr.dataclass
class BaseClassLevel12(LevelFeatures):
    level: int = attr.field(init=False, default=12)
    general_feat: GeneralFeats.GeneralFeat


@attr.dataclass
class BaseClassLevel13(LevelFeatures):
    level: int = attr.field(init=False, default=13)


@attr.dataclass
class BaseClassLevel14(LevelFeatures):
    level: int = attr.field(init=False, default=14)


@attr.dataclass
class BaseClassLevel15(LevelFeatures):
    level: int = attr.field(init=False, default=15)


@attr.dataclass
class BaseClassLevel16(LevelFeatures):
    level: int = attr.field(init=False, default=16)
    general_feat: GeneralFeats.GeneralFeat


@attr.dataclass
class BaseClassLevel17(LevelFeatures):
    level: int = attr.field(init=False, default=17)


@attr.dataclass
class BaseClassLevel18(LevelFeatures):
    level: int = attr.field(init=False, default=18)


@attr.dataclass
class BaseClassLevel19(LevelFeatures):
    level: int = attr.field(init=False, default=19)


@attr.dataclass
class BaseClassLevel20(LevelFeatures):
    level: int = attr.field(init=False, default=20)

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BaseClassLevelFeatures:
    base_class_level_1: Optional[BaseClassLevel1] = None
    base_class_level_2: Optional[BaseClassLevel2] = None
    base_class_level_3: Optional[BaseClassLevel3] = None
    base_class_level_4: Optional[BaseClassLevel4] = None
    base_class_level_5: Optional[BaseClassLevel5] = None
    base_class_level_6: Optional[BaseClassLevel6] = None
    base_class_level_7: Optional[BaseClassLevel7] = None
    base_class_level_8: Optional[BaseClassLevel8] = None
    base_class_level_9: Optional[BaseClassLevel9] = None
    base_class_level_10: Optional[BaseClassLevel10] = None
    base_class_level_11: Optional[BaseClassLevel11] = None
    base_class_level_12: Optional[BaseClassLevel12] = None
    base_class_level_13: Optional[BaseClassLevel13] = None
    base_class_level_14: Optional[BaseClassLevel14] = None
    base_class_level_15: Optional[BaseClassLevel15] = None
    base_class_level_16: Optional[BaseClassLevel16] = None
    base_class_level_17: Optional[BaseClassLevel17] = None
    base_class_level_18: Optional[BaseClassLevel18] = None
    base_class_level_19: Optional[BaseClassLevel19] = None
    base_class_level_20: Optional[BaseClassLevel20] = None
    subclass_level_3: Optional[SubclassLevel3] = None
    subclass_level_4: Optional[SubclassLevel4] = None
    subclass_level_5: Optional[SubclassLevel5] = None
    subclass_level_6: Optional[SubclassLevel6] = None
    subclass_level_7: Optional[SubclassLevel7] = None
    subclass_level_8: Optional[SubclassLevel8] = None
    subclass_level_9: Optional[SubclassLevel9] = None
    subclass_level_10: Optional[SubclassLevel10] = None
    subclass_level_11: Optional[SubclassLevel11] = None
    subclass_level_12: Optional[SubclassLevel12] = None
    subclass_level_13: Optional[SubclassLevel13] = None
    subclass_level_14: Optional[SubclassLevel14] = None
    subclass_level_15: Optional[SubclassLevel15] = None
    subclass_level_16: Optional[SubclassLevel16] = None
    subclass_level_17: Optional[SubclassLevel17] = None
    subclass_level_18: Optional[SubclassLevel18] = None
    subclass_level_19: Optional[SubclassLevel19] = None
    subclass_level_20: Optional[SubclassLevel20] = None

    def add_features(
        self,
        data: CharacterSheetData,
        base_class: CharacterClass,
    ) -> CharacterSheetData:
        class_level = data.get_level_for_class(base_class)
        for level_features in attr.fields(self.__class__):
            class_level_features: Optional[LevelFeatures] = getattr(
                self, level_features.name
            )
            expected_level: int = (
                class_level_features.level
                if class_level_features is not None
                else int(level_features.name.split("_")[-1])
            )

            if class_level_features is None:
                # Skip if the character level is lower than the expected level
                if class_level < expected_level:
                    continue

                # Must provide features for this level
                raise ValueError(
                    f"{base_class.name.lower()} level {expected_level} features must be provided for level {expected_level}."
                )

            # Skip if the character level is lower than the class level features
            if class_level_features.level > class_level:
                return data

            # Add features for this level
            data = class_level_features.add_features(data=data)
        return data


class ClassBuilder(ABC):

    def __init__(
        self,
        base_class: CharacterClass,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
    ):
        self.base_class = base_class
        self.base_class_level_features = base_class_level_features
        self.base_class_level = base_class_level

    @abstractmethod
    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        pass

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.base_class_level_features.add_features(data, self.base_class)
        return data


class StarterClassBuilder(ClassBuilder):

    def __init__(
        self,
        base_class: CharacterClass,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        skills: BarbarianSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        saving_throws: SavingThrowsStatBlock,
        add_default_equipment: bool,
        default_equipment: list[Weapons.AbstractWeapon | Armor.AbstractArmor],
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
    ):
        self.subclass = subclass
        self.abilities = abilities
        self.skills = skills
        self.background_ability_bonuses = background_ability_bonuses
        self.background_skill_proficiencies = background_skill_proficiencies
        self.saving_throws = saving_throws
        self.add_default_equipment = add_default_equipment
        self.default_equipment = default_equipment
        self.origin_feat = origin_feat
        self.armor = armor
        self.weapons = weapons
        super().__init__(
            base_class=base_class,
            base_class_level_features=base_class_level_features,
            base_class_level=base_class_level,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={self.base_class: self.base_class_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=self.saving_throws,
            starter_class=self.base_class,
        )

        # ================ LEVEL 0 ============= #

        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)

        ### Equipment ###

        if self.add_default_equipment:
            for item in self.default_equipment:
                if isinstance(item, Weapons.AbstractWeapon):
                    data.add_weapon(item)
                elif isinstance(item, Armor.AbstractArmor):
                    data.add_armor(item)

        if self.armor is not None:
            for a in self.armor:
                data.add_armor(a)

        if self.weapons is not None:
            for w in self.weapons:
                data.add_weapon(w)

        # Origin feat
        data.add_feature(self.origin_feat)

        return data


class MulticlassBuilder(ClassBuilder):

    def __init__(
        self,
        base_class: CharacterClass,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
        subclass: str,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=base_class,
            base_class_level_features=base_class_level_features,
            base_class_level=base_class_level,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={self.base_class: self.base_class_level},
        )

        # ================ LEVEL 0 ============= #

        return data
