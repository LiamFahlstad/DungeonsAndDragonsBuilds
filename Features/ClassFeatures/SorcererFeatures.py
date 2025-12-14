from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill
from Features import Weapons, Maneuvers
from Features.BaseFeatures import CharacterFeature, TextFeature


RANGER_HIT_DIE = 6


class InnateSorcery(TextFeature):
    def __init__(self):
        super().__init__(name="Innate Sorcery", origin="Sorcerer Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "An event in your past left an indelible mark on you, infusing you with simmering magic. As a Bonus Action, you can unleash that magic for 1 minute, during which you gain the following benefits:\n"
            "The spell save DC of your Sorcerer spells increases by 1.\n"
            "You have Advantage on the attack rolls of Sorcerer spells you cast.\n"
            "You can use this feature twice, and you regain all expended uses of it when you finish a Long Rest."
        )
        return description


class FontofMagic(TextFeature):
    def __init__(self):
        super().__init__(name="Font of Magic", origin="Sorcerer Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can tap into the wellspring of magic within yourself. This wellspring is represented by Sorcery Points, which allow you to create a variety of magical effects.\n"
            "You have 2 Sorcery Points, and you gain more as you reach higher levels, as shown in the Sorcery Points column of the Sorcerer Features table. You can’t have more Sorcery Points than the number shown in the table for your level. You regain all expended Sorcery Points when you finish a Long Rest.\n"
            "You can use your Sorcery Points to fuel the options below, along with other features, such as Metamagic, that use those points.\n"
            "Converting Spell Slots to Sorcery Points. You can expend a spell slot to gain a number of Sorcery Points equal to the slot’s level (no action required).\n"
            "Creating Spell Slots. As a Bonus Action, you can transform unexpended Sorcery Points into one spell slot. The Creating Spell Slots table shows the cost of creating a spell slot of a given level, and it lists the minimum Sorcerer level you must be to create a slot. You can create a spell slot no higher than level 5.\n"
            "Any spell slot you create with this feature vanishes when you finish a Long Rest."
        )
        return description


class Metamagic(TextFeature):
    def __init__(self):
        super().__init__(name="Metamagic", origin="Sorcerer Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Because your magic flows from within, you can alter your spells to suit your needs; you gain two Metamagic options of your choice from “Metamagic Options” later in this class’s description. You use the chosen options to temporarily modify spells you cast. To use an option, you must spend the number of Sorcery Points that it costs.\n"
            "You can use only one Metamagic option on a spell when you cast it unless otherwise noted in one of those options.\n"
            "Whenever you gain a Sorcerer level, you can replace one of your Metamagic options with one you don’t know. You gain two more options at Sorcerer level 10 and two more at Sorcerer level 17."
        )
        return description


class SorcerousRestoration(TextFeature):
    def __init__(self):
        super().__init__(name="Sorcerous Restoration", origin="Sorcerer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you finish a Short Rest, you can regain expended Sorcery Points, but no more than a number equal to half your Sorcerer level (round down). Once you use this feature, you can’t do so again until you finish a Long Rest."
        return description


class SorceryIncarnate(TextFeature):
    def __init__(self):
        super().__init__(name="Sorcery Incarnate", origin="Sorcerer Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "If you have no uses of Innate Sorcery left, you can use it if you spend 2 Sorcery Points when you take the Bonus Action to activate it.\n"
            "In addition, while your Innate Sorcery feature is active, you can use up to two of your Metamagic options on each spell you cast."
        )
        return description


class ArcaneApotheosis(TextFeature):
    def __init__(self):
        super().__init__(name="Arcane Apotheosis", origin="Sorcerer Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While your Innate Sorcery feature is active, you can use one Metamagic option on each of your turns without spending Sorcery Points on it."
        return description
