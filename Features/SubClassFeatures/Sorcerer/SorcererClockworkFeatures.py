from Core.Definitions import Ability, SORCERER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ClockworkSpells(Feature):
    def __init__(self):
        super().__init__(name="Clockwork Spells", origin="Clockwork Sorcery Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Clockwork Spells table, you thereafter always have the listed spells prepared.\n"
            "Clockwork Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Aid, Alarm, Lesser Restoration, Protection from Evil and Good\n"
            "5	Dispel Magic, Protection from Energy\n"
            "7	Freedom of Movement, Summon Construct\n"
            "9	Greater Restoration, Wall of Force\n"
            "In addition, consult the Manifestations of Order table and choose or randomly determine a way your connection to order manifests while you are casting any of your Sorcerer spells.\n"
            "Manifestations of Order\n"
            "1d6	Manifestation\n"
            "1	Spectral cogwheels hover behind you.\n"
            "2	The hands of a clock spin in your eyes.\n"
            "3	Your skin glows with a brassy sheen.\n"
            "4	Floating equations and geometric objects overlay your body.\n"
            "5	Your Spellcasting Focus temporarily takes the form of a Tiny clockwork mechanism.\n"
            "6	The ticking of gears or ringing of a clock can be heard by you and those affected by your magic."
        )
        return description


class RestoreBalance(Feature):
    def __init__(self):
        super().__init__(name="Restore Balance", origin="Clockwork Sorcery Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        uses = max(1, charisma_modifier)
        description = (
            "Your connection to the plane of absolute order allows you to equalize chaotic moments. When a creature you can see within 60 feet of yourself is about to roll a d20 with Advantage or Disadvantage, you can take a Reaction to prevent the roll from being affected by Advantage and Disadvantage.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class BastionOfLaw(Feature):
    def __init__(self):
        super().__init__(name="Bastion of Law", origin="Clockwork Sorcery Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can tap into the grand equation of existence to imbue a creature with a shimmering shield of order. As a Magic action, you can expend 1 to 5 Sorcery Points to create a magical ward around yourself or another creature you can see within 30 feet of yourself. The ward is represented by a number of d8s equal to the number of Sorcery Points spent to create it. When the warded creature takes damage, it can expend a number of those dice, roll them, and reduce the damage taken by the total rolled on those dice.\n"
            "The ward lasts until you finish a Long Rest or until you use this feature again."
        )
        return description


class TranceOfOrder(Feature):
    def __init__(self):
        super().__init__(name="Trance of Order", origin="Clockwork Sorcery Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to align your consciousness with the endless calculations of Mechanus. As a Bonus Action, you can enter this state for 1 minute. For the duration, attack rolls against you can’t benefit from Advantage, and whenever you make a D20 Test, you can treat a roll of 9 or lower on the d20 as a 10.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it."
        )
        return description


class ClockworkCavalcade(Feature):
    def __init__(self):
        super().__init__(
            name="Clockwork Cavalcade", origin="Clockwork Sorcery Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You momentarily summon spirits of order to expunge disorder around you. As a Magic action, you summon the spirits in a 30-foot Cube originating from you. The spirits look like modrons or other Constructs of your choice. The spirits are intangible and invulnerable, and they create the effects below within the Cube before vanishing. Once you use this action, you can’t use it again until you finish a Long Rest unless you spend 7 Sorcery Points (no action required) to restore your use of it.\n"
            "Heal. The spirits restore up to 100 Hit Points, divided as you choose among any number of creatures of your choice in the Cube.\n"
            "Repair. Any damaged objects entirely in the Cube are repaired instantly.\n"
            "Dispel. Every spell of level 6 and lower ends on creatures and objects of your choice in the Cube."
        )
        return description
