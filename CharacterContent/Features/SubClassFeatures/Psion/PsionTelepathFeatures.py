from Core.Definitions import PSION_HIT_DIE, Ability
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.View import CharacterView


class MindInfiltrator(Feature):
    def __init__(self):
        super().__init__(name="Mind Infiltrator", origin="Telepath Psion Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you cast Detect Thoughts, you can expend one "
            "Psionic Energy Die to modify the spell so that the "
            "spell doesn't require spell components or "
            "Concentration. In addition, when you use the Read "
            "Thoughts effect of the spell, the target doesn't know "
            "you're probing its mind if it fails the Wisdom saving "
            "throw."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("Spell", "Detect Thoughts"),
            ("Cost", "1 Psionic Energy Die"),
            ("No Components", "Spell components waived"),
            ("No Concentration", "Spell doesn't require Concentration"),
            (
                "Stealth on Read Thoughts",
                "Target doesn't know you're probing (if fails save)",
            ),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class TelepathicDistraction(Feature):
    def __init__(self):
        super().__init__(
            name="Telepathic Distraction",
            origin="Telepath Psion Level 3",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When a creature you can see within range of your "
            "telepathy hits with an attack roll, you can take a "
            "Reaction to roll one Psionic Energy Die and subtract "
            "the number rolled from attack roll, potentially "
            "causing the attack to miss. The die is expended only "
            "if the target misses the attack."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class BulwarkMind(Feature):
    def __init__(self):
        super().__init__(
            name="Bulwark Mind",
            origin="Telepath Psion Level 6",
            activation=FeatureActivation(duration="10 Minutes"),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At the start of your turn, you can expend one Psionic "
            "Energy Die to strengthen your mind and enter a "
            "fortified state. For the next 10 minutes, you have "
            "Resistance to Psychic damage; and whenever you "
            "make an Intelligence, Wisdom, or Charisma saving "
            "throw, you add a roll of your Psionic Energy Die to "
            "the save. Rolling the Psionic Energy Die doesn't "
            "expend it. You can't use this benefit if you have the "
            "Incapacitated condition."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("Activation", "Start of turn"),
            ("Cost", "1 Psionic Energy Die"),
            ("Duration", "10 minutes"),
            ("Damage Resistance", "Psychic damage"),
            (
                "Saving Throw Bonus",
                "Add die roll to INT/WIS/CHA saves (die doesn't expend)",
            ),
            ("Restriction", "Not while Incapacitated"),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class PotentThoughts(Feature):
    def __init__(self):
        super().__init__(
            name="Potent Thoughts",
            origin="Telepath Psion Level 6",
            usage_tags=["damage", "utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have telepathy with a range of 60 feet. In "
            "addition, you add your Intelligence modifier to the "
            "damage you deal with any Psion cantrip."
        )
        return description


class TelepathicBolstering(Feature):
    def __init__(self):
        super().__init__(
            name="Telepathic Bolstering",
            origin="Telepath Psion Level 10",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you or a creature you can see within range of "
            "your telepathy fails an ability check or misses with "
            "an attack roll, you can take a Reaction to expend one "
            "Psionic Energy Die. Roll the die and add the number "
            "rolled to the d20, potentially turning a failed check "
            "into a success or a miss into a hit. The Psionic "
            "Energy Die is expended only if the check succeeds or "
            "the attack hits."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            (
                "Trigger",
                "You or ally within telepathy range fails check or misses attack",
            ),
            ("Action", "Reaction"),
            ("Effect", "Roll Psionic Energy Die and add to d20 roll"),
            ("Cost", "1 Psionic Energy Die (expended only if success)"),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ScrambleMinds(Feature):
    def __init__(self):
        super().__init__(
            name="Scramble Minds",
            origin="Telepath Psion Level 14",
            activation=FeatureActivation(range="30-Foot Radius"),
            usage_tags=["control"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can cast Confusion without expending a spell "
            "slot by instead expending four Psionic Energy Dice. "
            "When you cast Confusion without a spell slot using "
            "this feature, you can modify the spell so that the "
            "radius of the spell's Sphere becomes 30 feet and you "
            "can choose one creature you can see in the spell's "
            "area to automatically succeed on their saving throw "
            "against the spell.\n"
            "In addition, when a creature under the effect of "
            "the spell starts its turn, you choose their behavior "
            "from the table for the turn instead of the creature "
            "rolling to determine its behavior."
        )
        return description

    def get_concise_description(self, character: CharacterView) -> str:
        return (
            "Cast Confusion without slot by expending 4 Psionic Energy Dice. Spell's radius becomes 30 feet, "
            "choose one creature to auto-succeed on save, and you pick each creature's confused behavior each turn "
            "(instead of rolling)."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA
