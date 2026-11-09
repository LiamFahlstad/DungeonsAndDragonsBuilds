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


class RangeType(Enum):
    """What a spell's range is measured in, or the word that stands for it.
    FOOT and MILE take an amount (SpellFields.Range)."""

    SELF = "Self"
    TOUCH = "Touch"
    SIGHT = "Sight"
    UNLIMITED = "Unlimited"
    SPECIAL = "Special"
    FOOT = "Foot"
    MILE = "Mile"


class DurationType(Enum):
    """What a spell's duration is measured in, or the word that stands for
    it. ROUND to DAY take an amount (SpellFields.Duration)."""

    INSTANTANEOUS = "Instantaneous"
    ROUND = "Round"
    MINUTE = "Minute"
    HOUR = "Hour"
    DAY = "Day"
    UNTIL_DISPELLED = "Until dispelled"
    UNTIL_DISPELLED_OR_TRIGGERED = "Until dispelled or triggered"
    SPECIAL = "Special"


class AreaShape(Enum):
    """The shape in a 2014 range such as "Self (15-foot cone)"."""

    CONE = "Cone"
    CUBE = "Cube"
    LINE = "Line"
    RADIUS = "Radius"
    SPHERE = "Sphere"
    HEMISPHERE = "Hemisphere"
