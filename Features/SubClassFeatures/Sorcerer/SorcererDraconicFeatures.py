from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SORCERER_HIT_DIE = 6


class DraconicSpells(Feature):
    def __init__(self):
        super().__init__(name="Draconic Spells", origin="Draconic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Draconic Spells table, you thereafter always have the listed spells prepared.\n"
            "Draconic Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Alter Self, Chromatic Orb, Command, Dragon's Breath\n"
            "5	Fear, Fly\n"
            "7	Arcane Eye, Charm Monster\n"
            "9	Legend Lore, Summon Dragon"
        )
        return description


class DraconicResilience(Feature):
    def __init__(self):
        super().__init__(name="Draconic Resilience", origin="Draconic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic in your body manifests physical traits of your draconic gift. Your Hit Point maximum increases by 3, and it increases by 1 whenever you gain another Sorcerer level.\n"
            "Parts of you are also covered by dragon-like scales. While you aren’t wearing armor, your base Armor Class equals 10 plus your Dexterity and Charisma modifiers."
        )
        return description


class ElementalAffinity(Feature):
    def __init__(self):
        super().__init__(name="Elemental Affinity", origin="Draconic Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your draconic magic has an affinity with a damage type associated with dragons. Choose one of those types: Acid, Cold, Fire, Lightning, or Poison.\n"
            "You have Resistance to that damage type, and when you cast a spell that deals damage of that type, you can add your Charisma modifier to one damage roll of that spell."
        )
        return description


class DragonWings(Feature):
    def __init__(self):
        super().__init__(name="Dragon Wings", origin="Draconic Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can cause draconic wings to appear on your back. The wings last for 1 hour or until you dismiss them (no action required). For the duration, you have a Fly Speed of 60 feet.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you spend 3 Sorcery Points (no action required) to restore your use of it."
        )
        return description


class DragonCompanion(Feature):
    def __init__(self):
        super().__init__(name="Dragon Companion", origin="Draconic Sorcerer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Summon Dragon without a Material component. You can also cast it once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest.\n"
            "Whenever you start casting the spell, you can modify it so that it doesn’t require Concentration. If you do so, the spell’s duration becomes 1 minute for that casting."
        )
        return description
