from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ArcaneInitiate(Feature):
    def __init__(self):
        super().__init__(name="Arcane Initiate", origin="Arcana Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency in the Arcana skill, and you gain two cantrips of your choice from the wizard spell list. For you, these cantrips count as cleric cantrips."
        return description


class ArcanaDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Arcana Domain Spells", origin="Arcana Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Arcana Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Arcana Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tDetect Magic, Magic Missile\n"
            "3rd\tMagic Weapon, Nystul's Magic Aura\n"
            "5th\tDispel Magic, Magic Circle\n"
            "7th\tArcane Eye, Leomund's Secret Chest\n"
            "9th\tPlanar Binding, Teleportation Circle"
        )
        return description


class ArcaneAbjurationChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Arcane Abjuration",
            origin="Arcana Domain Cleric Level 3",
            action_type="action",
            range="30 Feet",
            duration="1 Minute or Until Takes Any Damage",
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to abjure otherworldly creatures.\n"
            "As an action, you present your holy symbol, and one celestial, elemental, fey, or fiend of your choice that is within 30 feet of you must make a Wisdom saving throw, provided that the creature can see or hear you. If the creature fails its saving throw, it is turned for 1 minute or until it takes any damage.\n"
            "A turned creature must spend its turns trying to move as far away from you as it can, and it can't willingly end its move in a space within 30 feet of you. It also can't take reactions. For its action, it can only use the Dash action or try to escape from an effect that prevents it from moving. If there's nowhere to move, the creature can use the Dodge action.\n"
            "After you reach 5th level, when a creature fails its saving throw against your Arcane Abjuration feature, the creature is banished for 1 minute (as in the Banishment spell, no concentration required) if it isn't on its plane of origin and its challenge rating is at or below a certain threshold, as shown on the Arcane Banishment table.\n"
            "Arcane Banishment\n"
            "Cleric Level\tBanishes Creatures of CR...\n"
            "5th\t1/2 or lower\n"
            "8th\t1 or lower\n"
            "11th\t2 or lower\n"
            "14th\t3 or lower\n"
            "17th\t4 or lower"
        )
        return description


class SpellBreaker(Feature):
    def __init__(self):
        super().__init__(name="Spell Breaker", origin="Arcana Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you restore hit points to an ally with a spell of 1st level or higher, you can also end one spell of your choice on that creature. The level of the spell you end must be equal to or lower than the level of the spell slot you use to cast the healing spell."
        return description


class PotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(name="Potent Spellcasting", origin="Arcana Domain Cleric Level 8", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You add your Wisdom modifier to the damage you deal with any cleric cantrip."
        return description


class ArcaneMastery(Feature):
    def __init__(self):
        super().__init__(name="Arcane Mastery", origin="Arcana Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You choose four spells from the wizard spell list, one from each of the following levels: 6th, 7th, 8th, and 9th. You add them to your list of domain spells. Like your other domain spells, they are always prepared and count as cleric spells for you."
        return description
