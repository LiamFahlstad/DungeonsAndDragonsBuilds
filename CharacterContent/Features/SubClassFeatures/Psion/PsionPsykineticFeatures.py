from Core.Definitions import PSION_HIT_DIE
from Model.Content.Feature import Feature, FeatureActivation, FeatureTarget
from Model.View import CharacterView


class StrongerTelekinesis(Feature):
    def __init__(self):
        super().__init__(name="Stronger Telekinesis", origin="Psykinetic Psion Level 3")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you cast Mage Hand, its range increases by 30 "
            "feet when you cast it, and the hand can carry up to "
            "20 pounds."
        )
        return description


class TelekineticTechniques(Feature):
    def __init__(self):
        super().__init__(
            name="Telekinetic Techniques",
            origin="Psykinetic Psion Level 3",
            usage_tags=["buff", "control", "damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use Telekinetic Propel, you can roll 1d4 "
            "and use the number rolled instead of expending a "
            "Psionic Energy Die.\n"
            "In addition, when a target fails the saving throw "
            "against your Telekinetic Propel, you can impose one "
            "of the following effects on that target "
            "Boost. The target's Speed increases by 10 feet "
            "until the start of your next turn.\n"
            "Disorient. The target can't make Opportunity "
            "Attacks until the start of its next turn.\n"
            "Telekinetic Bolt. The target takes Force damage "
            "equal to the number rolled on the Psionic Energy "
            "Die."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class DestructiveTrance(Feature):
    def __init__(self):
        super().__init__(
            name="Destructive Trance",
            origin="Psykinetic Psion Level 6",
            activation=FeatureActivation(duration="10 Minutes"),
            usage_tags=["buff", "damage", "utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At the start of your turn, you can expend one Psionic "
            "Energy Die to enter a destructive state. For the next "
            "10 minutes, you gain a Fly Speed of 20 feet and can "
            "hover, and when you cast a Psion spell that expends "
            "a spell slot, you can roll your Psionic Energy Die and "
            "add the number rolled to one damage roll of that "
            "spell. This roll doesn't expend the Psionic Energy "
            "Die."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("Activation", "Start of turn"),
            ("Cost", "1 Psionic Energy Die"),
            ("Duration", "10 minutes"),
            ("Fly Speed", "20 feet (can hover)"),
            (
                "Damage Bonus",
                "Add die roll to one damage roll of Psion spells (die doesn't expend)",
            ),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ReboundingField(Feature):
    def __init__(self):
        super().__init__(
            name="Rebounding Field",
            origin="Psykinetic Psion Level 6",
            usage_tags=["damage", "buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you cast Shield in response to being hit by an "
            "attack roll and cause the triggering attack to miss, "
            "you can expend one Psionic Energy Die to launch the "
            "force back at the attacker. The attacker makes a "
            "Dexterity saving throw. Roll one Psionic Energy Die. "
            "On a failed save, the attacker takes Force damage "
            "equal to the amount rolled plus your Intelligence "
            "modifier. On a successful save, the attacker takes "
            "half as much damage only. Whether the target fails "
            "or succeeds on the saving throw, you gain "
            "Temporary Hit Points equal to the amount of "
            "damage dealt."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        int_mod = character.get_intelligence_modifier()
        return [
            ("Trigger", "Cast Shield as reaction to attack hit and cause it to miss"),
            ("Cost", "1 Psionic Energy Die"),
            ("Save", "Dexterity saving throw"),
            (
                "On Failed Save",
                f"Attacker takes [die roll + INT mod ({int_mod})] Force damage",
            ),
            ("On Successful Save", "Attacker takes half damage"),
            ("Temp HP", "You gain temp HP equal to damage dealt"),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class EnhancedTelekineticCrush(Feature):
    def __init__(self):
        super().__init__(
            name="Enhanced Telekinetic Crush",
            origin="Psykinetic Psion Level 10",
            usage_tags=["damage", "control"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you cast Telekinetic Crush, you can expend one "
            "Psionic Energy Die to modify the spell so that "
            "whether a creature fails or succeeds on the saving "
            "throw against the spell, its Speed is halved until the "
            "start of your next turn. In addition, you can roll the "
            "expended Psionic Energy Die and add the number "
            "rolled to one damage roll of the spell."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("Spell", "Telekinetic Crush"),
            ("Cost", "1 Psionic Energy Die"),
            (
                "Speed Effect",
                "Speed halved until start of next turn (save doesn't prevent)",
            ),
            ("Damage Bonus", "Roll die and add to one damage roll of spell"),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class HeightenedTelekinesis(Feature):
    def __init__(self):
        super().__init__(
            name="Heightened Telekinesis", origin="Psykinetic Psion Level 14"
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can cast Telekinesis without expending a spell "
            "slot by instead expending four Psionic Energy Dice. "
            "When you cast Telekinesis without expending a spell "
            "slot using this feature, you can modify the spell so "
            "that it doesn't require Concentration. If you do so, "
            "the spell's duration becomes 1 minute for that "
            "casting, and you can concentrate on another spell as normal."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("Spell", "Telekinesis"),
            ("Resource Cost", "4 Psionic Energy Dice (instead of spell slot)"),
            (
                "Optional: Remove Concentration",
                "Spell no longer requires Concentration",
            ),
            (
                "If No Concentration",
                "Duration becomes 1 minute; you can concentrate on another spell",
            ),
        ]
