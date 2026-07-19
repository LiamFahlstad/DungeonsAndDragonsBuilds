from abc import ABC, abstractmethod
from typing import Optional

import attr

import Definitions
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.Equipment import Armor, Weapons
from Features.ClassFeatures import SpellSlots
from Features.Items import Items
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import ClassSkillsStatBlock
from ToolProficiencies.ToolProficiencies import ToolProficiency


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
class AppliedLevelFeatures:
    """Tracks which (class, level) feature sets have already been applied
    across a character's starter class and multiclass builders, so that a
    level appearing in more than one builder (e.g. a class picked up again
    after a multiclass dip) only has its features added once, from whichever
    builder is processed first (the starter class, by convention)."""

    base_class_levels: set[tuple[CharacterClass, int]] = attr.Factory(set)
    subclass_levels: set[tuple[CharacterClass, int]] = attr.Factory(set)


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
        applied_level_features: "AppliedLevelFeatures",
    ) -> CharacterSheetData:
        """Apply this builder's per-level features to `data`, in ascending
        level order (all base-class levels first, then all subclass levels),
        skipping levels above the class's declared level and levels another
        builder already applied for the same class."""
        class_level = data.get_level_for_class(base_class)

        for features_by_level, applied_levels in [
            (self.base_class_features_by_level, applied_level_features.base_class_levels),
            (self.subclass_features_by_level, applied_level_features.subclass_levels),
        ]:
            for level in sorted(features_by_level):
                features = features_by_level[level]
                if features is None:
                    raise ValueError(
                        f"{base_class.value} level {level}: features cannot be None."
                    )
                if features.level != level:
                    raise ValueError(
                        f"{base_class.value} level {level} is mapped to features "
                        f"declared for level {features.level} "
                        f"({type(features).__name__})."
                    )

                if class_level < level:
                    continue

                key = (base_class, level)
                if key in applied_levels:
                    continue
                applied_levels.add(key)

                data = features.add_features(data=data)
        return data


class ClassBuilder(ABC):

    def __init__(
        self,
        base_class: CharacterClass,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        if not 1 <= base_class_level <= 20:
            raise ValueError(
                f"{base_class.value}: class level must be between 1 and 20, "
                f"got {base_class_level}."
            )
        self.base_class = base_class
        self.base_class_level_features = base_class_level_features
        self.base_class_level = base_class_level
        self.replace_spells = replace_spells

    @abstractmethod
    def _create_base_sheet_data(self) -> CharacterSheetData:
        """Build a fresh CharacterSheetData holding only this builder's
        class-level contribution (class registration, stat blocks, equipment,
        spell slots, ...) - everything except per-level features, which
        create() applies afterwards onto the merged sheet."""
        pass

    def create(
        self,
        character_sheet_data: Optional[CharacterSheetData] = None,
        applied_level_features: Optional["AppliedLevelFeatures"] = None,
    ) -> CharacterSheetData:
        """Merge this class builder's contribution into `character_sheet_data`
        (a fresh one is created if not provided) and return it. Feature
        application happens directly on that (possibly shared/cumulative)
        object so that a base class split across multiple builders - e.g. a
        starter class resumed later via a multiclass builder after a dip
        into another class - sees features from earlier levels (added by an
        earlier builder) already present, and never has a given class level's
        features applied more than once. A builder resuming a class declares
        the class's final total level. `replace_spells` operates on the
        cumulative sheet, so it may also replace a spell added by an earlier
        builder."""
        if character_sheet_data is None:
            character_sheet_data = CharacterSheetData()
        if applied_level_features is None:
            applied_level_features = AppliedLevelFeatures()

        base_sheet_data = self._create_base_sheet_data()

        previously_declared_level = character_sheet_data.get_level_for_class(
            self.base_class
        )
        if previously_declared_level > 0:
            if self.base_class_level < previously_declared_level:
                raise ValueError(
                    f"{self.base_class.value} is declared with level "
                    f"{self.base_class_level}, but an earlier builder already "
                    f"declared level {previously_declared_level}. A builder "
                    f"resuming a class must declare the class's final total "
                    f"level."
                )
            # The builder that introduced the class already registered its
            # SpellSlots feature; don't add a duplicate for the same class.
            base_sheet_data.remove_features(
                lambda f: isinstance(f, SpellSlots.SpellSlots)
                and f.character_class == self.base_class
            )

        character_sheet_data.merge_with(base_sheet_data)
        character_sheet_data = self.base_class_level_features.add_features(
            character_sheet_data, self.base_class, applied_level_features
        )
        character_sheet_data.replace_spells(self.replace_spells or {})
        return character_sheet_data


class CustomStarterClassArgs:
    def __init__(
        self,
        base_class: CharacterClass,
        default_equipment: list[Weapons.AbstractWeapon | Armor.AbstractArmor],
        saving_throws: SavingThrowsStatBlock,
        skills: ClassSkillsStatBlock,
        subclass: str,
        spell_casting_ability: Optional[Ability] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
        armor_proficiencies: Optional[list[Definitions.ArmorType]] = None,
    ):
        self.base_class = base_class
        self.default_equipment = default_equipment
        self.saving_throws = saving_throws
        self.skills = skills
        self.subclass = subclass
        self.spell_casting_ability = spell_casting_ability
        self.caster_type = caster_type
        self.armor_proficiencies = armor_proficiencies


class StarterClassBuilder(ClassBuilder):

    def __init__(
        self,
        non_generic_arguments: CustomStarterClassArgs,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
        abilities: AbilitiesStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
        items: Optional[list[tuple[Items.Item, int]]] = None,
        tool_proficiencies: Optional[ToolProficiency] = None,
    ):
        self.non_generic_arguments = non_generic_arguments
        self.abilities = abilities
        self.background_ability_bonuses = background_ability_bonuses
        self.background_skill_proficiencies = background_skill_proficiencies
        self.add_default_equipment = add_default_equipment
        self.origin_feat = origin_feat
        self.armor = armor
        self.weapons = weapons
        self.items = items
        self.tool_proficiencies = tool_proficiencies

        super().__init__(
            base_class=non_generic_arguments.base_class,
            base_class_level_features=base_class_level_features,
            base_class_level=base_class_level,
            replace_spells=replace_spells,
        )

    @property
    def saving_throws(self) -> SavingThrowsStatBlock:
        return self.non_generic_arguments.saving_throws

    @property
    def subclass(self) -> str:
        return self.non_generic_arguments.subclass

    @property
    def skills(self) -> ClassSkillsStatBlock:
        return self.non_generic_arguments.skills

    @property
    def default_equipment(self) -> list[Weapons.AbstractWeapon | Armor.AbstractArmor]:
        return self.non_generic_arguments.default_equipment

    @property
    def spell_casting_ability(self) -> Optional[Ability]:
        return self.non_generic_arguments.spell_casting_ability

    @property
    def caster_type(self) -> Optional[SpellSlots.CasterType]:
        return self.non_generic_arguments.caster_type

    @property
    def armor_proficiencies(self) -> Optional[list[Definitions.ArmorType]]:
        return self.non_generic_arguments.armor_proficiencies

    def _create_base_sheet_data(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={self.base_class: self.base_class_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=self.saving_throws,
            base_class=self.base_class,
            spell_casting_ability=self.spell_casting_ability,
        )

        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)
        data.add_origin_feat(self.origin_feat)
        if self.caster_type is not None:
            data.add_feature(SpellSlots.SpellSlots(self.caster_type, self.base_class))

        for armor_type in self.armor_proficiencies or []:
            data.add_armor_proficiency(armor_type)

        if not any(isinstance(item, Weapons.UnarmedStrike) for item in self.default_equipment):
            data.add_weapon(Weapons.UnarmedStrike(player_is_proficient=True))

        # Explicit body armor replaces the default one (a character can only
        # wear one armor at a time); default shields still apply.
        has_explicit_body_armor = any(not a.is_shield for a in (self.armor or []))
        if self.add_default_equipment:
            for item in self.default_equipment:
                if isinstance(item, Weapons.AbstractWeapon):
                    data.add_weapon(item)
                elif isinstance(item, Armor.AbstractArmor):
                    if item.is_shield or not has_explicit_body_armor:
                        data.add_armor(item)

        if self.armor is not None:
            for a in self.armor:
                data.add_armor(a)

        if self.weapons is not None:
            for w in self.weapons:
                data.add_weapon(w)

        if self.items is not None:
            for item, quantity in self.items:
                data.add_item(item, quantity)

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
        )
        self.spell_casting_ability = spell_casting_ability
        self.caster_type = caster_type

    def _create_base_sheet_data(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={self.base_class: self.base_class_level},
            spell_casting_ability=self.spell_casting_ability,
        )
        if self.caster_type is not None:
            data.add_feature(SpellSlots.SpellSlots(self.caster_type, self.base_class))
        return data
