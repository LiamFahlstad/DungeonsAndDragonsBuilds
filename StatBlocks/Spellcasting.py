from typing import Optional

from Core.Definitions import Ability, CharacterClass
from Core.SpellcastingRules import CasterType, calculate_spell_slots
from StatBlocks.ClassLevels import ClassLevels


class Spellcasting:
    """The character's spellcasting ability (None for a non-caster), spell
    save DC bonus, and every registered caster class (used to work out spell
    slots and Pact Magic slots together - see spell_slots). A character with
    no Spell Slots feature (e.g. a companion) can still be given a fixed
    table of slots directly."""

    def __init__(
        self,
        ability: Optional[Ability] = None,
        fixed_slots: Optional[dict[int, int]] = None,
    ):
        self.ability = ability
        # Slots for a character with no Spell Slots feature (e.g. companions);
        # otherwise worked out from the registered casters - see spell_slots.
        self._fixed_spell_slots = fixed_slots
        self._casters: dict[CharacterClass, CasterType] = {}
        self.spell_save_dc_bonus = 0

    def register_caster(
        self, character_class: CharacterClass, caster_type: CasterType
    ) -> None:
        self._casters[character_class] = caster_type

    def add_spell_save_dc_bonus(self, bonus: int) -> None:
        self.spell_save_dc_bonus += bonus

    def spell_slots(self, class_levels: ClassLevels) -> Optional[dict[int, int]]:
        if not self._casters:
            return self._fixed_spell_slots
        return calculate_spell_slots(self._casters, class_levels.level_per_class)[0]

    def pact_magic_slots(self, class_levels: ClassLevels) -> dict[int, int]:
        return calculate_spell_slots(self._casters, class_levels.level_per_class)[1]

    def require_ability(self) -> Ability:
        if self.ability is None:
            raise ValueError("Character does not have a spell casting ability.")
        return self.ability

    def difficulty_class(self, proficiency_bonus: int, ability_modifier: int) -> int:
        return 8 + proficiency_bonus + ability_modifier + self.spell_save_dc_bonus

    def attack_bonus(self, proficiency_bonus: int, ability_modifier: int) -> int:
        return proficiency_bonus + ability_modifier
