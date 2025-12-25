from abc import ABC, abstractmethod
import attr
from Definitions import Ability, CharacterClass, Skill, WizardSubclass
from Features import GeneralFeats, OriginFeats
from CharacterSheetCreator import CharacterSheetData
from Features import Armor
from Features import Backgrounds
from Features import Weapons
from Features.ClassFeatures import WizardFeatures, WizardFeatures
from Features.ClassFeatures import SpellSlots
from StatBlocks.AbilitiesStatBlock import (
    AbilitiesStatBlock,
)
from StatBlocks.SavingThrowsStatBlock import WizardSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock
from Spells.Definitions import (
    WizardLevel0Spells,
    WizardLevel1Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
    WizardLevel6Spells,
    WizardLevel7Spells,
    WizardLevel8Spells,
    WizardLevel9Spells,
)

from typing import Optional, TypeAlias

WizardSpellsUpTo2: TypeAlias = WizardLevel1Spells | WizardLevel2Spells

WizardSpellsUpTo3: TypeAlias = WizardSpellsUpTo2 | WizardLevel3Spells

WizardSpellsUpTo4: TypeAlias = WizardSpellsUpTo3 | WizardLevel4Spells

WizardSpellsUpTo5: TypeAlias = WizardSpellsUpTo4 | WizardLevel5Spells

WizardSpellsUpTo6: TypeAlias = WizardSpellsUpTo5 | WizardLevel6Spells

WizardSpellsUpTo7: TypeAlias = WizardSpellsUpTo6 | WizardLevel7Spells

WizardSpellsUpTo8: TypeAlias = WizardSpellsUpTo7 | WizardLevel8Spells

WizardSpellsUpTo9: TypeAlias = WizardSpellsUpTo8 | WizardLevel9Spells


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
class WizardSubclassLevel3(ClassLevelFeatures):
    pass


@attr.dataclass
class WizardSubclassLevel5(ClassLevelFeatures):
    pass

@attr.dataclass
class WizardSubclassLevel6(ClassLevelFeatures):
    pass


@attr.dataclass
class WizardSubclassLevel7(ClassLevelFeatures):
    pass


@attr.dataclass
class WizardSubclassLevel9(ClassLevelFeatures):
    pass

@attr.dataclass
class WizardSubclassLevel10(ClassLevelFeatures):
    pass

@attr.dataclass
class WizardSubclassLevel11(ClassLevelFeatures):
    pass

@attr.dataclass
class WizardSubclassLevel13(ClassLevelFeatures):
    pass

@attr.dataclass
class WizardSubclassLevel14(ClassLevelFeatures):
    pass


@attr.dataclass
class WizardSubclassLevel15(ClassLevelFeatures):
    pass


@attr.dataclass
class WizardSubclassLevel17(ClassLevelFeatures):
    pass


@attr.dataclass
class WizardLevel1(ClassLevelFeatures):
    cantrip_1: WizardLevel0Spells
    cantrip_2: WizardLevel0Spells
    cantrip_3: WizardLevel0Spells
    spell_1: WizardLevel1Spells
    spell_2: WizardLevel1Spells
    spell_3: WizardLevel1Spells
    spell_4: WizardLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.RitualAdept())
        data.add_feature(WizardFeatures.ArcaneRecovery())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_cantrip(self.cantrip_3)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        data.add_spell(self.spell_4)
        return data


@attr.dataclass
class WizardLevel2(ClassLevelFeatures):
    skill_to_expertise_in: Skill
    spell: WizardLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.Scholar(self.skill_to_expertise_in))
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel3(ClassLevelFeatures):
    spell: WizardSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel4(ClassLevelFeatures):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: WizardLevel0Spells
    spell: WizardSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel5(ClassLevelFeatures):
    spell_1: WizardSpellsUpTo3
    spell_2: WizardSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.MemorizeSpell())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WizardLevel6(ClassLevelFeatures):
    spell: WizardSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel7(ClassLevelFeatures):
    spell: WizardSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel8(ClassLevelFeatures):
    general_feat: GeneralFeats.GeneralFeat
    spell: WizardSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel9(ClassLevelFeatures):
    spell_1: WizardSpellsUpTo5
    spell_2: WizardSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WizardLevel10(ClassLevelFeatures):
    spell: WizardSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel11(ClassLevelFeatures):
    spell: WizardSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel12(ClassLevelFeatures):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class WizardLevel13(ClassLevelFeatures):
    spell: WizardSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel14(ClassLevelFeatures):
    spell: WizardSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel15(ClassLevelFeatures):
    spell: WizardSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel16(ClassLevelFeatures):
    general_feat: GeneralFeats.GeneralFeat
    spell_1: WizardSpellsUpTo8
    spell_2: WizardSpellsUpTo8

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WizardLevel17(ClassLevelFeatures):
    spell: WizardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel18(ClassLevelFeatures):
    spell: WizardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SpellMastery())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel19(ClassLevelFeatures):
    spell: WizardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel20(ClassLevelFeatures):
    spell: WizardSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SignatureSpells())
        data.add_spell(self.spell)
        return data


attr.dataclass


class WizardFeaturePerLevel:
    wizard_level_1: Optional[WizardLevel1] = None
    wizard_level_2: Optional[WizardLevel2] = None
    wizard_level_3: Optional[WizardLevel3] = None
    wizard_level_4: Optional[WizardLevel4] = None
    wizard_level_5: Optional[WizardLevel5] = None
    wizard_level_6: Optional[WizardLevel6] = None
    wizard_level_7: Optional[WizardLevel7] = None
    wizard_level_8: Optional[WizardLevel8] = None
    wizard_level_9: Optional[WizardLevel9] = None
    wizard_level_10: Optional[WizardLevel10] = None
    wizard_level_11: Optional[WizardLevel11] = None
    wizard_level_12: Optional[WizardLevel12] = None
    wizard_level_13: Optional[WizardLevel13] = None
    wizard_level_14: Optional[WizardLevel14] = None
    wizard_level_15: Optional[WizardLevel15] = None
    wizard_level_16: Optional[WizardLevel16] = None
    wizard_level_17: Optional[WizardLevel17] = None
    wizard_level_18: Optional[WizardLevel18] = None
    wizard_level_19: Optional[WizardLevel19] = None
    wizard_level_20: Optional[WizardLevel20] = None    
    wizard_subclass_level_3: Optional[WizardSubclassLevel3] = None
    wizard_subclass_level_5: Optional[WizardSubclassLevel5] = None
    wizard_subclass_level_6: Optional[WizardSubclassLevel6] = None
    wizard_subclass_level_7: Optional[WizardSubclassLevel7] = None
    wizard_subclass_level_9: Optional[WizardSubclassLevel9] = None
    wizard_subclass_level_10: Optional[WizardSubclassLevel10] = None
    wizard_subclass_level_11: Optional[WizardSubclassLevel11] = None
    wizard_subclass_level_13: Optional[WizardSubclassLevel13] = None
    wizard_subclass_level_14: Optional[WizardSubclassLevel14] = None
    wizard_subclass_level_15: Optional[WizardSubclassLevel15] = None
    wizard_subclass_level_17: Optional[WizardSubclassLevel17] = None

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        wizard_level = data.get_level_for_class(CharacterClass.WIZARD)
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
                if wizard_level < expected_level:
                    continue

                # Must provide features for this level
                raise ValueError(
                    f"wizard level {expected_level} features must be provided for level {expected_level}."
                )

            # Skip if the character level is lower than the class level features
            if class_level_features.level > wizard_level:
                return data

            # Add features for this level
            data = class_level_features.add_features(data=data)
        return data


class WizardBase:

    def __init__(
        self,
        wizard_level: int,
        wizard_feature_per_level: WizardFeaturePerLevel,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.wizard_level = wizard_level
        self.wizard_feature_per_level = wizard_feature_per_level
        self.replace_spells = replace_spells

    @abstractmethod
    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        pass

    def create(
        self,
    ) -> CharacterSheetData:
        data = self._get_character_sheet_creator_base()
        data = self.wizard_feature_per_level.add_features(data)
        data.replace_spells(self.replace_spells or {})
        return data


class WizardStarter(WizardBase):

    def __init__(
        self,
        wizard_level: int,
        wizard_feature_per_level: WizardFeaturePerLevel,
        subclass: WizardSubclass,
        abilities: AbilitiesStatBlock,
        skills: WizardSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.wizard_level = wizard_level
        self.wizard_feature_per_level = wizard_feature_per_level
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
            wizard_level=wizard_level,
            wizard_feature_per_level=wizard_feature_per_level,
            replace_spells=replace_spells,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.WIZARD: self.wizard_level},
            abilities=self.abilities,
            skills=self.skills,
            saving_throws=WizardSavingThrowsStatBlock(),
            starter_class=CharacterClass.WIZARD,
            spell_casting_ability=Ability.INTELLIGENCE,
        )

        # ================ LEVEL 0 ============= #
        data.add_feature(SpellSlots.SpellSlots(SpellSlots.CasterType.FULL_CASTER))
        data.add_feature(self.background_ability_bonuses)
        data.add_feature(self.background_skill_proficiencies)

        ### Equipment ###

        if self.add_default_equipment:
            # Starting armor
            # No starting armor for Wizards

            # data.add_armor(Armor.StuddedLeatherArmor())

            # Starting weapons
        data.add_weapon(Weapons.Dagger(player_is_proficient=True))
        data.add_weapon(Weapons.Quarterstaff(player_is_proficient=True))

        if self.armor is not None:
            for a in self.armor:
                data.add_armor(a)

        if self.weapons is not None:
            for w in self.weapons:
                data.add_weapon(w)

        # Origin feat
        data.add_feature(self.origin_feat)

        return data


class WizardMulticlass(WizardBase):

    def __init__(
        self,
        wizard_level: int,
        wizard_feature_per_level: WizardFeaturePerLevel,
        subclass: WizardSubclass,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        self.wizard_level = wizard_level
        super().__init__(
            wizard_level=wizard_level,
            wizard_feature_per_level=wizard_feature_per_level,
            replace_spells=replace_spells,
        )

    def _get_character_sheet_creator_base(self) -> CharacterSheetData:
        data = CharacterSheetData(
            character_subclass=self.subclass,
            level_per_class={CharacterClass.WIZARD: self.wizard_level},
            spell_casting_ability=Ability.INTELLIGENCE,
        )

        # ================ LEVEL 0 ============= #
        data.add_feature(SpellSlots.SpellSlots(SpellSlots.CasterType.FULL_CASTER))

        return data
