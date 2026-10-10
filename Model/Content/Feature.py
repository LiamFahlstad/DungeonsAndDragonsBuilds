import re
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from Model.Content.Effect import Effect
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView


@dataclass
class FeatureUses:
    """Limited-use tracking for a feature, rendered as checkbox slots on its card.

    max_uses is always the formula's maximum value - the boxes never show a
    build's "current" count directly, since level shard pages are generated
    once and never regenerated as the player levels up in play. A feature
    whose count varies by level or by another stat (e.g. equal to proficiency
    bonus) should explain how to derive the current count via
    current_formula instead.
    """

    max_uses: int
    # Reset cadence label for full recovery, e.g. "long rest", "short rest", "dawn".
    regain_all_on: str | None = None
    # (count, cadence) for partial recovery on a shorter rest, e.g. (1, "short rest").
    # If both this and regain_all_on are set, renders as "Regain <n> on a <cadence>,
    # all on a <regain_all_on>."
    regain_x_on: tuple[int, str] | None = None
    # Short plain-English fragment describing how to derive the build's real current
    # count from the max shown by the boxes (e.g. "equal to your proficiency bonus.").
    current_formula: str | None = None


class ActionType(str, Enum):
    """Action economy cost to activate a feature."""

    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"


class RegainedOn(str, Enum):
    """Cadence on which a feature's expended resource (uses, hit points, etc.)
    comes back, as stated in the feature's own description."""

    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    SHORT_OR_LONG_REST = "short_or_long_rest"
    # "When you roll Initiative [and have no uses left], you regain ..." - a
    # recurring 5e pattern distinct from rest cadences (Rage, Bardic
    # Inspiration, Focus Points, Superiority Dice, Psionic Energy Dice, etc.
    # all have a high-level feature that refunds one use on an initiative roll).
    INITIATIVE_ROLL = "initiative_roll"
    # A regain condition tied to something other than a rest/time cadence or
    # an initiative roll (e.g. "on a kill", "when you cast a spell").
    OTHER = "other"


class FeatureTarget(str, Enum):
    """Who or what a feature's effect can be aimed at, as stated in the
    feature's own description."""

    SELF = "self"
    ALLY = "ally"
    CREATURE = "creature"
    ENEMY = "enemy"
    OBJECT = "object"
    AREA = "area"


_RANGE_SHAPE_RE = re.compile(
    r"(\d+)-Foot[- ](Cone|Cube|Sphere|Line|Emanation|Cylinder|Radius(?: Sphere)?)",
    re.IGNORECASE,
)

_DURATION_RE = re.compile(r"(?:up to\s+)?(\d+)\s+(\w+)", re.IGNORECASE)

_DURATION_UNIT_SECONDS = {
    "second": 1,
    "seconds": 1,
    "round": 6,
    "rounds": 6,
    "turn": 6,
    "turns": 6,
    "minute": 60,
    "minutes": 60,
    "hour": 3600,
    "hours": 3600,
    "day": 86400,
    "days": 86400,
}


@dataclass
class FeatureActivation:
    """Action economy, duration, and range/shape for how a feature is activated,
    rendered as tag chips on its card (mirrors FeatureUses' role for limited-use tracking).

    range_shape captures an area-of-effect shape (e.g. "Cone", "Sphere", "Radius")
    when the range text states one - split out automatically from a combined
    range string like "30-Foot Cone" unless range_shape is passed explicitly.
    Left None when no shape is stated (e.g. "30 Feet", "Self", "Touch").
    """

    action_type: "ActionType | Literal['action', 'bonus_action', 'reaction'] | None" = (
        None
    )
    duration: str | None = None
    range: str | None = None
    range_shape: str | None = None

    def __post_init__(self):
        if self.action_type is not None and not isinstance(
            self.action_type, ActionType
        ):
            self.action_type = ActionType(self.action_type)
        if self.range is not None and self.range_shape is None:
            match = _RANGE_SHAPE_RE.fullmatch(self.range.strip())
            if match:
                self.range = f"{match.group(1)} Feet"
                self.range_shape = match.group(2).title()

    def duration_to_seconds(self) -> int | str | None:
        """Convert duration to a whole number of seconds (a turn/round is 6 seconds).
        Returns the original duration string unchanged when it isn't a plain
        "<number> <unit>" time span (e.g. "Until Incapacitated", "1d6 Long Rests")."""
        if self.duration is None:
            return None
        match = _DURATION_RE.fullmatch(self.duration.strip())
        if match:
            count, unit = match.groups()
            seconds_per_unit = _DURATION_UNIT_SECONDS.get(unit.lower())
            if seconds_per_unit is not None:
                return int(count) * seconds_per_unit
        return self.duration


class Feature(Effect):
    """A single feature type. Override apply() to modify the stat block, get_description() to render a card, or both."""

    # Whether a character may be granted this feature more than once. Class
    # features repeat freely (two Expertise grants, one Spell Slots per
    # class); feats set this False unless they're Repeatable.
    repeatable = True

    # True for a feat or boon taken at an Ability Score Improvement level: its
    # card is labeled with that level ("Fighter Level 8"), since its own
    # origin only says when it's available (see Presentation/FeatureCards.py).
    labeled_by_class_level = False

    # Optional alternate renderings: get_table_description() and get_concise_description()
    # both fall back to get_description() when they return None.

    def __init__(
        self,
        name: str | None = None,
        origin: str | None = None,
        skippable_in_concise: bool = False,
        usage_tags: (
            list[Literal["heal", "buff", "control", "damage", "utility", "summon"]]
            | None
        ) = None,
        activation: "FeatureActivation | None" = None,
        uses: "FeatureUses | None" = None,
    ):
        self.name = name if name is not None else type(self).__name__
        self.origin = origin
        # Set True for features that only modify the stat block (e.g. a flat bonus
        # or a resource pool) where the prose description adds nothing on a
        # concise/table character sheet. Full-mode sheets always show it.
        self.skippable_in_concise = skippable_in_concise
        # Action economy, duration, and range/shape for activating this feature.
        # Leave unset (or pass an empty FeatureActivation()) for passive features
        # and instantaneous effects with no meaningful range.
        self.activation = activation if activation is not None else FeatureActivation()
        # Set for features whose effect falls into one or more of these functional
        # roles - healing, buffing, imposing a condition/controlling a target,
        # dealing damage, or non-combat utility - so the card can be scanned for
        # role at a glance. A feature can carry more than one (e.g. deals damage
        # and also restrains).
        # Leave None/empty for features with no combat/utility role of this kind
        # (e.g. skill proficiencies, passive stat bonuses).
        self.usage_tags = usage_tags
        # Set for features that have a limited number of uses per rest period
        # (e.g. action surge, channel divinity). The FeatureUses dataclass tracks
        # max uses, what resets them, and optionally a formula explaining the
        # current uses based on character stats.
        self.uses = uses

    def apply(self, ledger_writer: LedgerWriter):
        """Record this feature's effects on the stat block. Features, armor
        and items apply in no particular order, so only record facts - never
        read a stat here. Anything that depends on other stats or on worn
        armor is a formula evaluated on read (see Core.Improvements)."""
        pass

    def get_description(self, character: CharacterView) -> str | None:
        return None

    def get_table_description(
        self, character: CharacterView
    ) -> list[tuple[str, str]] | None:
        """Override to provide a concise label/value table version of the description
        (e.g. [("What", "..."), ("Casting Time", "...")]), used when table descriptions
        are requested. Return None to fall back to get_description()."""
        return None

    def get_concise_description(self, character: CharacterView) -> str | None:
        """Override to provide a short prose summary of the description (a sentence
        or two, same formatting rules as get_description), used when concise
        descriptions are requested. Return None to fall back to get_description()."""
        return None

    def calculate_dc(self, character: CharacterView) -> int | None:
        """Override to return this feature's saving throw DC (e.g. 8 plus an
        ability modifier plus proficiency bonus), so the value can be reused
        anywhere it's needed instead of being recomputed inline. Return None
        (default) for features with no DC."""
        return None

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        """Override to return when this feature's expended resource (uses, hit
        points, etc.) is regained (e.g. a short rest, long rest, or an
        initiative roll), so the value can be reused anywhere it's needed
        instead of being re-parsed from prose. Return None (default) for
        features with nothing to regain."""
        return None

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        """Override to return what this feature's effect can be aimed at
        (e.g. self, an ally, a creature, an object), so the value can be
        reused anywhere it's needed instead of being re-parsed from prose.
        Return None (default) for features with no meaningful target (e.g.
        passive features or ones that affect the caster only implicitly)."""
        return None

    def number_of_uses(self, character: CharacterView) -> int:
        """Override to return this feature's actual current number of uses,
        computed from the character's stats (e.g. equal to your proficiency
        bonus or level), for features whose real count is described only in
        FeatureUses.current_formula prose rather than being the flat
        FeatureUses.max_uses. Defaults to max_uses (or 0 if uses is unset)
        for features with a fixed use count."""
        return self.uses.max_uses if self.uses is not None else 0

    def get_resource_tiles(
        self, character: CharacterView
    ) -> list[tuple[str, list[tuple[str, str]]]] | None:
        """Override to surface this feature's core numbers as small stat
        tiles at the top of its own feature card (visually the same idea as
        the Max HP tile, sized down to fit a card) for resources checked
        constantly in play - e.g. a martial arts die size or a resource
        point total. Returns a list of (group_label, steps) tuples, where
        steps is a list of (step_label, value) pairs - typically one tile
        per level or level-range, e.g. [("Martial Arts Die",
        [("Lv 1-4", "1d6"), ("Lv 5-10", "1d8"), ...])], commonly built from
        StringUtils.compress_level_progression(). Every step is shown with
        equal weight and no "current level" is called out: the generated
        page isn't reprinted on every level-up, so a step highlighted as
        "current" at generation time would silently go stale. Return None
        (default) for features with no resource tile at all."""
        return None
