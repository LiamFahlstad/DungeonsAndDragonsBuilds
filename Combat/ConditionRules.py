from enum import Enum


class ConditionRule(Enum):
    """Each member stores (heading, description) taken from the rules glossary."""

    BLINDED = (
        "Blinded [Condition]",
        "While you have the Blinded condition, you experience the following effects.\n\n"
        "Can't See. You can't see and automatically fail any ability check that requires sight.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage, and your attack rolls have Disadvantage.",
    )
    CHARMED = (
        "Charmed [Condition]",
        "While you have the Charmed condition, you experience the following effects.\n\n"
        "Can't Harm the Charmer. You can't attack the charmer or target the charmer with damaging abilities or magical effects.\n\n"
        "Social Advantage. The charmer has Advantage on any ability check to interact with you socially.",
    )
    CONCENTRATING = (
        "Concentration",
        "Some spells and other effects require Concentration to remain active. "
        "If the effect's creator loses Concentration, the effect ends. "
        "The creator can end Concentration at any time (no action required). "
        "The following factors break Concentration.\n\n"
        "Another Concentration Effect. You lose Concentration on an effect the moment you start casting a spell "
        "that requires Concentration or activate another effect that requires Concentration.\n\n"
        "Damage. If you take damage, you must succeed on a Constitution saving throw to maintain Concentration. "
        "The DC equals 10 or half the damage taken (round down), whichever is higher, up to a maximum DC of 30.\n\n"
        "Incapacitated or Dead. Your Concentration ends if you have the Incapacitated condition or you die.",
    )
    FRIGHTENED = (
        "Frightened [Condition]",
        "While you have the Frightened condition, you experience the following effects.\n\n"
        "Ability Checks and Attacks Affected. You have Disadvantage on ability checks and attack rolls "
        "while the source of fear is within line of sight.\n\n"
        "Can't Approach. You can't willingly move closer to the source of fear.",
    )
    GRAPPLED = (
        "Grappled [Condition]",
        "While you have the Grappled condition, you experience the following effects.\n\n"
        "Speed 0. Your Speed is 0 and can't increase.\n\n"
        "Attacks Affected. You have Disadvantage on attack rolls against any target other than the grappler.\n\n"
        "Movable. The grappler can drag or carry you when it moves, but every foot of movement costs it "
        "1 extra foot unless you are Tiny or two or more sizes smaller than it.",
    )
    PARALYZED = (
        "Paralyzed [Condition]",
        "While you have the Paralyzed condition, you experience the following effects.\n\n"
        "Incapacitated. You have the Incapacitated condition.\n\n"
        "Speed 0. Your Speed is 0 and can't increase.\n\n"
        "Saving Throws Affected. You automatically fail Strength and Dexterity saving throws.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage.\n\n"
        "Automatic Critical Hits. Any attack roll that hits you is a Critical Hit if the attacker is within 5 feet of you.",
    )
    POISONED = (
        "Poisoned [Condition]",
        "While you have the Poisoned condition, you experience the following effect.\n\n"
        "Ability Checks and Attacks Affected. You have Disadvantage on attack rolls and ability checks.",
    )
    PRONE = (
        "Prone [Condition]",
        "While you have the Prone condition, you experience the following effects.\n\n"
        "Restricted Movement. Your only movement options are to crawl or to spend an amount of movement "
        "equal to half your Speed (round down) to right yourself and thereby end the condition. "
        "If your Speed is 0, you can't right yourself.\n\n"
        "Attacks Affected. You have Disadvantage on attack rolls. An attack roll against you has Advantage "
        "if the attacker is within 5 feet of you. Otherwise, that attack roll has Disadvantage.",
    )
    STUNNED = (
        "Stunned [Condition]",
        "While you have the Stunned condition, you experience the following effects.\n\n"
        "Incapacitated. You have the Incapacitated condition.\n\n"
        "Saving Throws Affected. You automatically fail Strength and Dexterity saving throws.\n\n"
        "Attacks Affected. Attack rolls against you have Advantage.",
    )

    @property
    def heading(self) -> str:
        return self.value[0]

    @property
    def description(self) -> str:
        return self.value[1]

    @classmethod
    def from_name(cls, name: str) -> "ConditionRule | None":
        try:
            return cls[name.upper().replace(" ", "_")]
        except KeyError:
            pass
        name_lower = name.lower()
        for member in cls:
            if member.heading.lower().startswith(name_lower):
                return member
        return None
