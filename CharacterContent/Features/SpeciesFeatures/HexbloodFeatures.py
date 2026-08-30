from Core.Definitions import Sense
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn, FeatureTarget
from CharacterContent.Features.Core.Improvements import GrantSense
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Hexblood Trait")
        self._sense = GrantSense(Sense.DARKVISION, 60, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._sense.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class EerieToken(Feature):
    def __init__(self):
        super().__init__(name="Eerie Token", origin="Hexblood Trait", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="Until Long Rest", range="10 Miles"), usage_tags=["utility"], uses=FeatureUses(max_uses=1))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can create a magical token by harmlessly removing a lock of hair, detaching a nail, or using some other method. "
            "While the token exists, you gain the following benefits:\n"
            "Distant Message. As a Magic action, you can send a telepathic message of 25 words or fewer to a creature holding or carrying the token, as long as you are within 10 miles of it.\n"
            "Remote Viewing. If you are within 10 miles of the token, you can take a Magic action to extend your senses through the token for 1 minute, until you have the Incapacitated condition, or until you end this state (no action required). "
            "During this state, you can see and hear from the token as if you were located where it is. When this state ends, the token is harmlessly destroyed.\n"
            "Unless the token is destroyed early, it lasts until you finish a Long Rest. "
            "Once you create a token using this feature, you can't do so again until you finish a Long Rest."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class HexMagic(Feature):
    def __init__(self):
        super().__init__(name="Hex Magic", origin="Hexblood Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You always have the Disguise Self and Hex spells prepared. "
            "You can cast each spell once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. "
            "You can also cast the spell using any spell slots you have of the appropriate level. "
            "Intelligence, Wisdom, or Charisma is your spellcasting ability for the spells you cast with this trait (choose the ability when you select this species)."
        )

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
