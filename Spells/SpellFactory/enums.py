from enum import Enum


class School(Enum):
    """The eight schools of magic."""

    ABJURATION = "Abjuration"
    CONJURATION = "Conjuration"
    DIVINATION = "Divination"
    ENCHANTMENT = "Enchantment"
    EVOCATION = "Evocation"
    ILLUSION = "Illusion"
    NECROMANCY = "Necromancy"
    TRANSMUTATION = "Transmutation"


class CastingTimeType(Enum):
    """The broad category of a spell's casting time, ignoring reaction triggers, ritual
    alternatives, and other qualifying detail (e.g. "Reaction, which you take in response
    to taking damage" is just REACTION)."""

    ACTION = "Action"
    BONUS_ACTION = "Bonus Action"
    REACTION = "Reaction"
    MINUTE = "Minute"
    HOUR = "Hour"
