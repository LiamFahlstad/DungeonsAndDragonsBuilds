import Core.Definitions as Definitions
from Model.Content.Feature import Feature
from Core.SpellcastingRules import CasterType
from Model.Effects import Effects
from Model.View import CharacterView


class SpellSlots(Feature):
    def __init__(
        self, caster_type: CasterType, character_class: Definitions.CharacterClass
    ) -> None:
        self.caster_type = caster_type
        self.character_class = character_class
        super().__init__(
            name="Spell Slots",
            origin=f"{character_class.value} Spellcasting",
            skippable_in_concise=True,
        )

    def get_description(self, character: CharacterView) -> str:
        caster_map = {
            CasterType.FULL_CASTER: "You are a full spellcaster and gain spell slots according to the full caster table.",
            CasterType.HALF_CASTER: "You are a half-spellcaster and gain spell slots at half your class level (rounded up).",
            CasterType.WARLOCK_CASTER: "You are a warlock and gain pact magic slots that refresh on short or long rests.",
            CasterType.THIRD_CASTER: "You are a one-third spellcaster and gain spell slots according to one-third of your class level.",
        }
        description = caster_map.get(
            self.caster_type, "You gain spell slots for spellcasting."
        )
        return f"{self.character_class.value} Spellcasting.\n{description}"

    def apply(self, effects: Effects):
        # The slots themselves are worked out on read from every registered
        # caster (Core.SpellcastingRules.calculate_spell_slots), so it doesn't
        # matter which class's Spell Slots feature applies first.
        effects.register_caster(self.character_class, self.caster_type)
