from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

PALADIN_HIT_DIE = 10


class ElementalSmite(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Smite", origin="Oath of the Noble Genies Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Immediately after you cast Divine Smite, you can expend one use of your Channel Divinity and invoke one of the following effects.\n"
            "Dao's Crush. Earth rises up around the target of your Divine Smite. The target has the Grappled condition (escape DC equal to your spell save DC). While Grappled, the target has the Restrained condition.\n"
            "Djinni's Escape. You teleport to an unoccupied space you can see within 30 feet of yourself and take on a semi-incorporeal form, which lasts until the end of your next turn. While in this form, you have Resistance to Bludgeoning, Piercing, and Slashing damage, and you have Immunity to the Grappled, Prone, and Restrained conditions.\n"
            "Efreeti's Fury. The target of your Divine Smite takes an extra 2d4 Fire damage, and fire jumps from the target to another creature you can see within 30 feet of yourself. The second creature also takes 2d4 Fire damage.\n"
            "Marid's Surge. The target of your Divine Smite and each creature of your choice in a 10-foot Emanation originating from you make a Strength saving throw against your spell save DC. On a failed save, a creature is pushed 15 feet straight away from you and has the Prone condition."
        )
        return description


class GenieSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Genie Spells", origin="Oath of the Noble Genies Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Paladin level specified in the Genie Spells table, you thereafter always have the listed spells prepared\n"
            "Genie Spells\n"
            "Paladin Level	Spells\n"
            "3	Chromatic Orb, Elementalism, Thunderous Smite\n"
            "5	Mirror Image, Phantasmal Force\n"
            "9	Fly, Gaseous Form\n"
            "13	Conjure Minor Elementals, Summon Elemental\n"
            "17	Banishing Smite, Contact Other Plane"
        )
        return description


class GeniesSplendor(Feature):
    def __init__(self):
        super().__init__(
            name="Genie's Splendor", origin="Oath of the Noble Genies Paladin Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you aren't wearing any armor, your base Armor Class equals 10 plus your Dexterity and Charisma modifiers. You can use a Shield and still gain this benefit.\n"
            "You also gain proficiency in one of the following skills of your choice: Acrobatics, Intimidation, Performance, or Persuasion."
        )
        return description


class AuraOfElementalShielding(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Elemental Shielding",
            origin="Oath of the Noble Genies Paladin Level 7",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. You and your allies have Resistance to that damage type while in your Aura of Protection.\n"
            "At the start of each of your turns, you can change the damage type affected by this feature to one of the other listed options (no action required)."
        )
        return description


class ElementalRebuke(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Rebuke", origin="Oath of the Noble Genies Paladin Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, charisma_modifier)
        description = (
            "When you are hit by an attack roll, you can take a Reaction to halve the attack's damage against yourself (round down) and force the attacker to make a Dexterity saving throw against your spell save DC. On a failed save, the attacker takes damage equal to 2d10 plus your Charisma modifier of one of the following types (your choice): Acid, Cold, Fire, Lightning, or Thunder. On a successful save, the attacker takes half as much damage.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class NobleScion(Feature):
    def __init__(self):
        super().__init__(
            name="Noble Scion", origin="Oath of the Noble Genies Paladin Level 20"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you gain the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Flight. You have a Fly Speed of 60 feet and can hover.\n"
            "Minor Wish. When you or an ally in your Aura of Protection fails a D20 Test, you can take a Reaction to make you or that ally succeed instead."
        )
        return description
