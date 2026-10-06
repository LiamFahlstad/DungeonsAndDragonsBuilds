from typing import Optional, Sequence

from Core.Definitions import Ability, CharacterClass
from Core.Rules import SPELL_SAVE_DC_BASE
from Core.SpellcastingRules import (
    CasterType,
    SlotProgression,
    calculate_slot_progression,
    calculate_spell_slots,
)
from Model.Contracts import StatView
from Model.Recorder import Recorder, records


class Spellcasting(Recorder):
    """The spell save DC bonus and every registered caster class (used to
    work out spell slots and Pact Magic slots together - see spell_slots).
    The spellcasting ability and a fixed table of slots (for a character with
    no Spell Slots feature, e.g. a companion) are sources on the Character,
    read through the view.

    Merge rule: one CasterType per class; registering a class again with a
    different CasterType raises. Spell save DC bonuses sum."""

    def __init__(self):
        self._casters: dict[CharacterClass, CasterType] = {}
        self.spell_save_dc_bonus = 0

    @records
    def register_caster(
        self, character_class: CharacterClass, caster_type: CasterType
    ) -> None:
        registered = self._casters.get(character_class)
        if registered is not None and registered != caster_type:
            raise ValueError(
                f"{character_class.value} is registered as both {registered.name} "
                f"and {caster_type.name} caster."
            )
        self._casters[character_class] = caster_type

    @records
    def add_spell_save_dc_bonus(self, bonus: int) -> None:
        self.spell_save_dc_bonus += bonus

    def spell_slots(self, view: StatView) -> Optional[dict[int, int]]:
        """Worked out from the registered casters - or, with none, the
        character's fixed table of slots (e.g. a companion's)."""
        if not self._casters:
            return view.fixed_spell_slots
        levels = view.class_levels.level_per_class
        return calculate_spell_slots(self._casters, levels).spell_slots

    def pact_magic_slots(self, view: StatView) -> dict[int, int]:
        levels = view.class_levels.level_per_class
        return calculate_spell_slots(self._casters, levels).pact_magic_slots

    def slot_progression(
        self, class_by_character_level: Sequence[CharacterClass]
    ) -> SlotProgression:
        """When each slot is gained, as character levels, for a character
        taking these classes level by level (see
        Core.SpellcastingRules.calculate_slot_progression)."""
        return calculate_slot_progression(self._casters, list(class_by_character_level))

    def difficulty_class(self, ability: Ability, view: StatView) -> int:
        """Spell save DC when casting with `ability`."""
        return (
            SPELL_SAVE_DC_BASE
            + view.get_proficiency_bonus()
            + view.get_ability_modifier(ability)
            + self.spell_save_dc_bonus
        )

    def attack_bonus(self, ability: Ability, view: StatView) -> int:
        """Spell attack bonus when casting with `ability`."""
        return view.get_proficiency_bonus() + view.get_ability_modifier(ability)
