from abc import ABC, abstractmethod
from typing import Optional

import attr

import Core.Definitions as Definitions
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import Ability, CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Features.ClassFeatures import ClassProficiencies, SpellSlots
from CharacterContent.Items import Items, Packs
from Model.AbilityScores import AbilityScores
from CharacterContent.ToolProficiencies.Proficiencies import ToolProficiency


@attr.dataclass
class LevelFeatures(ABC):
    level: int = attr.field(init=False)

    @abstractmethod
    def add_features(
        self,
        data: Grants,
    ) -> None:
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

    def add_features(self, data: Grants) -> None:
        pass


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
        data: Character,
        base_class: CharacterClass,
        applied_level_features: "AppliedLevelFeatures",
    ) -> Character:
        """Apply this builder's per-level features to `data`, in ascending
        level order (all base-class levels first, then all subclass levels),
        skipping levels above the class's declared level and levels another
        builder already applied for the same class."""
        class_level = data.get_level_for_class(base_class)

        for features_by_level, applied_levels, kind in [
            (
                self.base_class_features_by_level,
                applied_level_features.base_class_levels,
                "class",
            ),
            (
                self.subclass_features_by_level,
                applied_level_features.subclass_levels,
                "subclass",
            ),
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

                features.add_features(Grants(data, level, base_class.value, kind))
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
    def _grant_class(self, data: Character, is_resuming: bool) -> None:
        """Grant this builder's class-level contribution (class registration,
        spell slots, proficiencies, ...) straight into `data` - everything
        except per-level features, which create() applies afterwards.
        `is_resuming` means an earlier builder already introduced this class
        (a class resumed after a dip into another), so the grants that come
        once per class (SpellSlots, proficiencies) must not be repeated."""
        pass

    def create(
        self,
        character_sheet_data: Optional[Character] = None,
        applied_level_features: Optional["AppliedLevelFeatures"] = None,
    ) -> Character:
        """Grant this class builder's contribution straight into
        `character_sheet_data` (a fresh one is created if not provided) and
        return it. Every builder writes into the same object, so a base class
        split across multiple builders - e.g. a starter class resumed later
        via a multiclass builder after a dip into another class - sees
        features from earlier levels (added by an earlier builder) already
        present, and never has a given class level's features applied more
        than once. A builder resuming a class declares
        the class's final total level. `replace_spells` operates on the
        cumulative sheet, so it may also replace a spell added by an earlier
        builder."""
        if character_sheet_data is None:
            character_sheet_data = Character()
        if applied_level_features is None:
            applied_level_features = AppliedLevelFeatures()

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

        # Record which total character level each newly-gained class level
        # corresponds to, before this builder's level count is added to
        # character_sheet_data.character_level.
        starting_character_level = character_sheet_data.character_level + 1
        new_class_level_count = self.base_class_level - previously_declared_level
        for offset in range(new_class_level_count):
            character_sheet_data.record_class_level(
                starting_character_level + offset, self.base_class
            )

        # A builder resuming a class states the class's final total level.
        character_sheet_data.set_class_level(self.base_class, self.base_class_level)
        self._grant_class(
            character_sheet_data, is_resuming=previously_declared_level > 0
        )
        self._update_subclass_name(character_sheet_data)
        character_sheet_data = self.base_class_level_features.add_features(
            character_sheet_data, self.base_class, applied_level_features
        )
        character_sheet_data.replace_spells(self.replace_spells or {})
        return character_sheet_data

    def _update_subclass_name(self, data: Character) -> None:
        """Show every class's subclass on a multiclass sheet ("Oath of Glory /
        Bladesinger") instead of only the last builder's. Classes that
        haven't reached their subclass level are left out; if none has, the
        first declared subclass is kept."""
        subclass = getattr(self, "subclass", None)
        class_levels = data.class_levels
        if subclass and _subclass_reached(self):
            class_levels.active_subclasses[self.base_class] = subclass
        if class_levels.active_subclasses:
            class_levels.character_subclass = " / ".join(
                class_levels.active_subclasses.values()
            )
        elif class_levels.character_subclass is None:
            class_levels.character_subclass = subclass or None


def _subclass_reached(builder: "ClassBuilder") -> bool:
    """A class has a subclass once its level reaches the first level that
    grants subclass features (e.g. a Fighter 1 dip has none yet)."""
    subclass_levels = builder.base_class_level_features.subclass_features_by_level
    return any(level <= builder.base_class_level for level in subclass_levels)


class CustomStarterClassArgs:
    def __init__(
        self,
        base_class: CharacterClass,
        default_equipment: list[Weapons.AbstractWeapon | Armor.AbstractArmor],
        skills: list[Skill],
        subclass: str,
        spell_casting_ability: Optional[Ability] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
        armor_proficiencies: Optional[list[Definitions.ArmorType]] = None,
        weapon_proficiencies: Optional[list[Weapons.WeaponProficiency]] = None,
        default_pack: Optional[Packs.Pack] = None,
    ):
        self.base_class = base_class
        self.default_equipment = default_equipment
        # The class's chosen skills (ClassProficiencies.CLASS_SKILL_CHOICES
        # holds the pool/count every class picks from; saving throw
        # proficiencies come from the same table, granted by
        # ClassProficiencies - neither is a caller argument).
        self.skills = skills
        self.subclass = subclass
        self.spell_casting_ability = spell_casting_ability
        self.caster_type = caster_type
        self.armor_proficiencies = armor_proficiencies
        self.weapon_proficiencies = weapon_proficiencies
        # The equipment pack (Dungeoneer's, Explorer's, ...) granted by this
        # class's Starting Equipment option A, per SourceTexts/ClassTexts.
        self.default_pack = default_pack


class StarterClassBuilder(ClassBuilder):

    def __init__(
        self,
        non_generic_arguments: CustomStarterClassArgs,
        base_class_level_features: BaseClassLevelFeatures,
        base_class_level: int,
        abilities: AbilityScores,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
        items: Optional[list[tuple[Items.Item, int]]] = None,
        tool_proficiencies: Optional[list[ToolProficiency]] = None,
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
    def subclass(self) -> str:
        return self.non_generic_arguments.subclass

    @property
    def skills(self) -> list[Skill]:
        return self.non_generic_arguments.skills

    @property
    def default_equipment(self) -> list[Weapons.AbstractWeapon | Armor.AbstractArmor]:
        return self.non_generic_arguments.default_equipment

    @property
    def default_pack(self) -> Optional[Packs.Pack]:
        return self.non_generic_arguments.default_pack

    @property
    def spell_casting_ability(self) -> Optional[Ability]:
        return self.non_generic_arguments.spell_casting_ability

    @property
    def caster_type(self) -> Optional[SpellSlots.CasterType]:
        return self.non_generic_arguments.caster_type

    @property
    def armor_proficiencies(self) -> Optional[list[Definitions.ArmorType]]:
        return self.non_generic_arguments.armor_proficiencies

    @property
    def weapon_proficiencies(self) -> Optional[list[Weapons.WeaponProficiency]]:
        return self.non_generic_arguments.weapon_proficiencies

    def _grant_class(self, data: Character, is_resuming: bool) -> None:
        # The starting class is always the first builder, so never resumed.
        data.base_class = self.base_class
        data.base_abilities = self.abilities
        if self.spell_casting_ability is not None:
            data.spell_casting_ability = self.spell_casting_ability

        background = Grants(data, 1, "Background", "background")
        background.add_feature(self.background_ability_bonuses)
        background.add_feature(self.background_skill_proficiencies)
        self.origin_feat.grant_to(background)

        grants = Grants(data, 1, self.base_class.value, "class")
        if self.caster_type is not None:
            grants.add_feature(SpellSlots.SpellSlots(self.caster_type, self.base_class))
        grants.add_feature(
            ClassProficiencies.ClassProficiencies(
                self.base_class,
                armor=list(self.armor_proficiencies or []),
                weapons=list(self.weapon_proficiencies or []),
                tools=list(self.tool_proficiencies or []),
            )
        )
        pool, count = ClassProficiencies.CLASS_SKILL_CHOICES[self.base_class]
        grants.add_feature(
            ClassProficiencies.ClassSkillChoice(pool, count, self.skills)
        )

        # Equipment (default_equipment/default_pack/add_default_equipment/
        # armor/weapons/items, plus starting_gold) is handled by
        # CharacterBuilder via an Inventory (see Builds/StartingEquipment.py), not
        # here - this builder only stores those values (see properties above
        # and __init__) for CharacterBuilder to read when it constructs the
        # inventory.


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

    def _grant_class(self, data: Character, is_resuming: bool) -> None:
        if self.spell_casting_ability is not None:
            data.spell_casting_ability = self.spell_casting_ability
        if is_resuming:
            # The builder that introduced the class already registered its
            # SpellSlots feature and granted its proficiencies.
            return
        grants = Grants(data, 1, self.base_class.value, "class")
        if self.caster_type is not None:
            grants.add_feature(SpellSlots.SpellSlots(self.caster_type, self.base_class))
        # Only part of the class's proficiencies.
        grants.add_feature(ClassProficiencies.MulticlassProficiencies(self.base_class))
