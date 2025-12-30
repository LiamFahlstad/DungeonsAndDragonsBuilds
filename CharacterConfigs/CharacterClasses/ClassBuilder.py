from abc import ABC, abstractmethod
from typing import Optional
import attr
from Definitions import CharacterClass
import Definitions
from Features import GeneralFeats, OriginFeats
from CharacterSheetCreator import CharacterSheetData
from Features import Armor
from Features import Backgrounds
from Features.ClassFeatures import SpellSlots
from Features import Weapons
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.AbilitiesStatBlock import (
    AbilitiesStatBlock,
)
from StatBlocks.SkillsStatBlock import ClassSkillsStatBlock


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


@attr.dataclass
class BaseClassLevel2(LevelFeatures):
    level: int = attr.field(init=False, default=2)


@attr.dataclass
class BaseClassLevel3(LevelFeatures):
    level: int = attr.field(init=False, default=3)


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


class BaseClassLevelFeatures:
    def __init__(
        self,
        base_class_features_by_level: dict[int, LevelFeatures],
        subclass_features_by_level: dict[int, LevelFeatures],
    ):
        self.base_class_features_by_level = base_class_features_by_level
        self.subclass_features_by_level = subclass_features_by_level

    def add_features(
        self,
        data: CharacterSheetData,
        base_class: CharacterClass,
    ) -> CharacterSheetData:
        class_level = data.get_level_for_class(base_class)

        for features_by_level in [
            self.base_class_features_by_level,
            self.subclass_features_by_level,
        ]:
            for level, features in features_by_level.items():
                if class_level < level:
                    continue

                assert features is not None, "Features for level cannot be None."
                assert level == features.level, "Level mismatch in base class features."

                # Add features for this level
                data = features.add_features(data=data)
        return data


class ClassBuilder(ABC):

    def __init__(
        self,
        base_class: CharacterClass,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
        replace_spells: Optional[dict[str, str]] = None,
        spell_casting_ability: Optional[Definitions.Ability] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):
        self.base_class = base_class
        self.base_class_level_features = base_class_level_features
        self.base_class_level = base_class_level
        self.replace_spells = replace_spells
        self.spell_casting_ability = spell_casting_ability
        self.caster_type = caster_type

    @abstractmethod
    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        pass

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.base_class_level_features.add_features(data, self.base_class)
        data.replace_spells(self.replace_spells or {})
        return data


class StarterClassBuilder(ClassBuilder):

    def __init__(
        self,
        base_class: CharacterClass,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        skills: ClassSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        saving_throws: SavingThrowsStatBlock,
        add_default_equipment: bool,
        default_equipment: list[Weapons.AbstractWeapon | Armor.AbstractArmor],
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
        spell_casting_ability: Optional[Definitions.Ability] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
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
            replace_spells=replace_spells,
            spell_casting_ability=spell_casting_ability,
            caster_type=caster_type,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={self.base_class: self.base_class_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=self.saving_throws,
            starter_class=self.base_class,
            spell_casting_ability=self.spell_casting_ability,
        )

        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)
        if self.caster_type is not None:
            data.add_feature(SpellSlots.SpellSlots(self.caster_type))

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
        replace_spells: Optional[dict[str, str]] = None,
        spell_casting_ability: Optional[Definitions.Ability] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=base_class,
            base_class_level_features=base_class_level_features,
            base_class_level=base_class_level,
            replace_spells=replace_spells,
            spell_casting_ability=spell_casting_ability,
            caster_type=caster_type,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={self.base_class: self.base_class_level},
            spell_casting_ability=self.spell_casting_ability,
        )
        return data
