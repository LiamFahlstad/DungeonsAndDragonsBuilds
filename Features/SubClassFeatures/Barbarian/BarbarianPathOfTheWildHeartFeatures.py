from Definitions import BARBARIAN_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AnimalSpeaker(Feature):
    def __init__(self):
        super().__init__(
            name="Animal Speaker", origin="Path Of The Wild Heart Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can cast the Beast Sense and Speak with Animals spells but only as Rituals. Wisdom is your spellcasting ability for them."
        return description


class RageOfTheWilds(Feature):
    def __init__(self):
        super().__init__(
            name="Rage of the Wilds", origin="Path Of The Wild Heart Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Rage taps into the primal power of animals. Whenever you activate your Rage, you gain one of the following options of your choice.\n"
            "Bear. While your Rage is active, you have Resistance to every damage type except Force, Necrotic, Psychic, and Radiant.\n"
            "Eagle. When you activate your Rage, you can take the Disengage and Dash actions as part of that Bonus Action. While your Rage is active, you can take a Bonus Action to take both of those actions.\n"
            "Wolf. While your Rage is active, your allies have Advantage on attack rolls against any enemy of yours within 5 feet of you."
        )
        return description


class AspectOfTheWilds(Feature):
    def __init__(self):
        super().__init__(
            name="Aspect of the Wilds",
            origin="Path Of The Wild Heart Barbarian Level 6",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain one of the following options of your choice. Whenever you finish a Long Rest, you can change your choice.\n"
            "Owl. You have Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 60 feet.\n"
            "Panther. You have a Climb Speed equal to your Speed.\n"
            "Salmon. You have a Swim Speed equal to your Speed."
        )
        return description


class NatureSpeaker(Feature):
    def __init__(self):
        super().__init__(
            name="Nature Speaker", origin="Path Of The Wild Heart Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can cast the Commune with Nature spell but only as a Ritual. Wisdom is your spellcasting ability for it."
        return description


class PowerOfTheWilds(Feature):
    def __init__(self):
        super().__init__(
            name="Power of the Wilds",
            origin="Path Of The Wild Heart Barbarian Level 14",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you activate your Rage, you gain one of the following options of your choice.\n"
            "Falcon. While your Rage is active, you have a Fly Speed equal to your Speed if you aren’t wearing any armor.\n"
            "Lion. While your Rage is active, any of your enemies within 5 feet of you have Disadvantage on attack rolls against targets other than you or another Barbarian who has this option active.\n"
            "Ram. While your Rage is active, you can cause a Large or smaller creature to have the Prone condition when you hit it with a melee attack."
        )
        return description
