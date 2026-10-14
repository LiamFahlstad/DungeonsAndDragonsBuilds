from Core.Definitions import Sense
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import GrantSense
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph

SPEED = 30  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Hexblood Trait")
        self._sense = GrantSense(Sense.DARKVISION, 60)

    def apply(self, ledger_writer: LedgerWriter):
        self._sense.apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        return "You have Darkvision with a range of 60 feet."


class EerieToken(Feature):
    def __init__(self):
        super().__init__(
            name="Eerie Token",
            origin="Hexblood Trait",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Long Rest",
                range="10 Miles",
            ),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Make a magical token from a lock of hair, a nail or similar."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Lasts", "Until you finish a Long Rest, unless destroyed early"),
                    ("Limit", "Once per Long Rest"),
                    (
                        "Distant Message",
                        "Magic action: send a telepathic message of up to 25 words to whoever holds or carries the token, within 10 miles",
                    ),
                    (
                        "Remote Viewing",
                        "Magic action, within 10 miles: see and hear as if you were at the token for 1 minute, until you're Incapacitated or you end it (no action required). The token is then destroyed.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
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

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class HexMagic(Feature):
    def __init__(self):
        super().__init__(name="Hex Magic", origin="Hexblood Trait")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spells", "Disguise Self and Hex, always prepared"),
                    (
                        "Casting",
                        "Each once per Long Rest without a spell slot, or with your spell slots",
                    ),
                    (
                        "Ability",
                        "Intelligence, Wisdom or Charisma (chosen with the species)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You always have the Disguise Self and Hex spells prepared. "
            "You can cast each spell once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. "
            "You can also cast the spell using any spell slots you have of the appropriate level. "
            "Intelligence, Wisdom, or Charisma is your spellcasting ability for the spells you cast with this trait (choose the ability when you select this species)."
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
