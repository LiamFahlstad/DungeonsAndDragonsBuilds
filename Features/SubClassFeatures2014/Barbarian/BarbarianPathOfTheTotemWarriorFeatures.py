from Core.Definitions import BARBARIAN_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class SpiritSeeker(Feature):
    def __init__(self):
        super().__init__(
            name="Spirit Seeker",
            origin="Path Of The Totem Warrior Barbarian Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Yours is a path that seeks attunement with the natural world, giving you a kinship with beasts. You gain the ability to cast the Beast Sense and Speak with Animals spells, but only as rituals."
        return description


class TotemSpirit(Feature):
    def __init__(self):
        super().__init__(
            name="Totem Spirit",
            origin="Path Of The Totem Warrior Barbarian Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You choose a totem spirit and gain its feature. You must make or acquire a physical totem object – an amulet or similar adornment – that incorporates fur or feathers, claws, teeth, or bones of the totem animal. At your option, you also gain minor physical attributes that are reminiscent of your totem spirit. For example, if you have a bear totem spirit, you might be unusually hairy and thick-skinned, or if your totem is the eagle, your eyes turn bright yellow.\n"
            "Your totem animal might be an animal related to those listed here but more appropriate to your homeland. For example, you could choose a hawk or vulture in place of an eagle.\n"
            "Bear. While raging, you have resistance to all damage except psychic damage. The spirit of the bear makes you tough enough to stand up to any punishment.\n"
            "Eagle. While you're raging and aren't wearing heavy armor, other creatures have disadvantage on opportunity attack rolls against you, and you can use the Dash action as a bonus action on your turn. The spirit of the eagle makes you into a predator who can weave through the fray with ease.\n"
            "Elk. While you're raging and aren't wearing heavy armor, your walking speed increases by 15 feet. The spirit of the elk makes you extraordinarily swift.\n"
            "Tiger. While raging, you can add 10 feet to your long jump distance and 3 feet to your high jump distance. The spirit of the tiger empowers your leaps.\n"
            "Wolf. While you're raging, your friends have advantage on melee attack rolls against any creature within 5 feet of you that is hostile to you. The spirit of the wolf makes you a leader of hunters."
        )
        return description


class AspectOfTheBeast(Feature):
    def __init__(self):
        super().__init__(
            name="Aspect of the Beast",
            origin="Path Of The Totem Warrior Barbarian Level 6",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain a magical benefit based on the totem animal of your choice. You can choose the same animal you selected at 3rd level or a different one.\n"
            "Bear. You gain the might of a bear. Your carrying capacity (including maximum load and maximum lift) is doubled, and you have advantage on Strength checks made to push, pull, lift, or break objects.\n"
            "Eagle. You gain the eyesight of an eagle. You can see up to 1 mile away with no difficulty, able to discern even fine details as though looking at something no more than 100 feet away from you. Additionally, dim light doesn't impose disadvantage on your Wisdom (Perception) checks.\n"
            "Elk. Whether mounted or on foot, your travel pace is doubled, as is the travel pace of up to ten companions while they're within 60 feet of you and you're not incapacitated. The elk spirit helps you roam far and fast.\n"
            "Tiger. You gain proficiency in two skills from the following list: Athletics, Acrobatics, Stealth, and Survival. The cat spirit hones your survival instincts.\n"
            "Wolf. You gain the hunting sensibilities of a wolf. You can track other creatures while traveling at a fast pace, and you can move stealthily while traveling at a normal pace."
        )
        return description


class SpiritWalker(Feature):
    def __init__(self):
        super().__init__(
            name="Spirit Walker",
            origin="Path Of The Totem Warrior Barbarian Level 10",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can cast the Commune with Nature spell, but only as a ritual. When you do so, a spiritual version of one of the animals you chose for Totem Spirit or Aspect of the Beast appears to you to convey the information you seek."
        return description


class TotemicAttunement(Feature):
    def __init__(self):
        super().__init__(
            name="Totemic Attunement",
            origin="Path Of The Totem Warrior Barbarian Level 14",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain a magical benefit based on a totem animal of your choice. You can choose the same animal you selected previously or a different one.\n"
            "Bear. While you're raging, any creature within 5 feet of you that's hostile to you has disadvantage on attack rolls against targets other than you or another character with this feature. An enemy is immune to this effect if it can't see or hear you or if it can't be frightened.\n"
            "Eagle. While raging, you have a flying speed equal to your current walking speed. This benefit works only in short bursts; you fall if you end your turn in the air and nothing else is holding you aloft.\n"
            "Elk. While raging, you can use a bonus action during your move to pass through the space of a Large or smaller creature. That creature must succeed on a Strength saving throw (DC 8 + your Strength bonus + your proficiency bonus) or be knocked prone and take bludgeoning damage equal to 1d12 + your Strength modifier.\n"
            "Tiger. While you're raging, if you move at least 20 feet in a straight line toward a Large or smaller target right before making a melee weapon attack against it, you can use a bonus action to make an additional melee weapon attack against it.\n"
            "Wolf. While you're raging, you can use a bonus action on your turn to knock a Large or smaller creature prone when you hit it with melee weapon attack."
        )
        return description
