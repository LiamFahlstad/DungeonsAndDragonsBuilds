import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Literal, Sequence

from Core.Definitions import CharacterClass
from Core.Rules import MAX_LEVEL, MIN_LEVEL
from Model.Content.Effect import Effect
from Model.Content.FeatureText import Block
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.Spells import FeatureSpell
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
    # The level each box is gained at, one entry per box, printed under it the
    # way spell slots show theirs - e.g. PROFICIENCY_BONUS_GAINED_AT, or
    # Core.Rules.levels_gained(...) for a class-level table. Leave unset for a
    # count that doesn't grow with level (a fixed count, an ability modifier).
    gained_at: list[int] | None = None

    def __post_init__(self):
        if self.gained_at is not None and len(self.gained_at) != self.max_uses:
            raise ValueError(
                f"gained_at has {len(self.gained_at)} entries but max_uses is "
                f"{self.max_uses} - it needs one level per box"
            )


@dataclass
class FeatureDice:
    """A die (or dice pool) that grows with level, rendered on the feature's
    card as a track of every step - "1d6 Lv 1-4 › 1d8 Lv 5-10 › ..." - the
    way FeatureUses renders use boxes.

    Like FeatureUses, the card never calls out the "current" step: level
    pages are generated once and not reprinted as the player levels up, so
    the whole progression is shown with equal weight. A description that
    wants today's value reads it with at(character), so the card text and
    the track come from the same table.

    progression lists (level gained at, dice) in ascending level order, one
    entry per change - e.g. ((1, "1d6"), (5, "1d8"), (11, "1d10"),
    (17, "1d12")). Each step lasts until the next one (the last to level
    20). For a step every level or two, build it with from_function().
    """

    # What the dice are, e.g. "Martial Arts Die" or "Extra Damage".
    label: str
    progression: tuple[tuple[int, str], ...]
    # Whose level the steps are keyed on; None for character level (e.g. a
    # species trait such as Breath Weapon).
    scales_with: CharacterClass | None = None
    # A short rider printed under the track, e.g. "+ Wisdom modifier".
    note: str | None = None

    def __post_init__(self):
        self.progression = tuple(
            (int(level), str(dice)) for level, dice in self.progression
        )
        if not self.progression:
            raise ValueError(f"{self.label}: progression needs at least one step")
        levels = [level for level, _ in self.progression]
        if levels != sorted(set(levels)):
            raise ValueError(
                f"{self.label}: progression levels must be strictly ascending, got {levels}"
            )
        if levels[0] < MIN_LEVEL or levels[-1] > MAX_LEVEL:
            raise ValueError(
                f"{self.label}: progression levels must be within {MIN_LEVEL}-{MAX_LEVEL}, got {levels}"
            )

    @classmethod
    def from_function(
        cls,
        label: str,
        dice_at_level: Callable[[int], str],
        from_level: int = MIN_LEVEL,
        scales_with: CharacterClass | None = None,
        note: str | None = None,
    ) -> "FeatureDice":
        """Build the progression from a level -> dice function (e.g. Sneak
        Attack's (level + 1) // 2 d6), keeping only the levels where the
        dice change."""
        progression: list[tuple[int, str]] = []
        for level in range(from_level, MAX_LEVEL + 1):
            dice = dice_at_level(level)
            if not progression or progression[-1][1] != dice:
                progression.append((level, dice))
        return cls(label, tuple(progression), scales_with, note)

    @property
    def level_basis(self) -> str:
        """Whose level the steps follow, for the card: "Monk level"."""
        if self.scales_with is None:
            return "character level"
        return f"{self.scales_with.value} level"

    def steps(self) -> list[tuple[str, str]]:
        """(level range, dice) per step, e.g. [("1-4", "1d6"), ("5-10", "1d8")]."""
        result = []
        for index, (level, dice) in enumerate(self.progression):
            if index + 1 < len(self.progression):
                last = self.progression[index + 1][0] - 1
            else:
                last = MAX_LEVEL
            result.append((str(level) if level == last else f"{level}-{last}", dice))
        return result

    def at_level(self, level: int) -> str:
        """The dice at `level` (the first step's dice below its level)."""
        dice = self.progression[0][1]
        for step_level, step_dice in self.progression:
            if level >= step_level:
                dice = step_dice
        return dice

    def at(self, character: CharacterView) -> str:
        """The dice at the character's current level (class or character
        level, per scales_with)."""
        if self.scales_with is None:
            return self.at_level(character.character_level)
        return self.at_level(character.get_class_level(self.scales_with))


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


def regained_on_from_uses(uses: FeatureUses | None) -> RegainedOn | None:
    """Derive RegainedOn from a FeatureUses.regain_all_on label, for features
    (like feats) that state their cadence once in FeatureUses rather than
    overriding Feature.regained_on themselves. Rest cadences win over an
    initiative roll, since rests are what restore uses between fights."""
    if uses is None or uses.regain_all_on is None:
        return None
    cadence = uses.regain_all_on.lower()
    has_short, has_long = "short" in cadence, "long" in cadence
    if has_short and has_long:
        return RegainedOn.SHORT_OR_LONG_REST
    if has_short:
        return RegainedOn.SHORT_REST
    if has_long:
        return RegainedOn.LONG_REST
    if "initiative" in cadence:
        return RegainedOn.INITIATIVE_ROLL
    return RegainedOn.OTHER


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

    def __init__(
        self,
        name: str | None = None,
        origin: str | None = None,
        passive: bool = False,
        usage_tags: (
            list[Literal["heal", "buff", "control", "damage", "utility", "summon"]]
            | None
        ) = None,
        activation: "FeatureActivation | None" = None,
        uses: "FeatureUses | None" = None,
        dice: "FeatureDice | Sequence[FeatureDice] | None" = None,
    ):
        self.name = name if name is not None else type(self).__name__
        self.origin = origin
        # Set True for features that only modify the stat block (e.g. a flat
        # bonus or a proficiency): the card gets a Passive tag and is dimmed
        # and sorted after the features used in play.
        self.passive = passive
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
        # Set for features whose dice grow with level (e.g. a Martial Arts
        # die, Sneak Attack, a breath weapon's damage). Each FeatureDice is
        # shown on the card as its full level progression.
        if dice is None:
            self.dice: list[FeatureDice] = []
        elif isinstance(dice, FeatureDice):
            self.dice = [dice]
        else:
            self.dice = list(dice)

    def apply(self, ledger_writer: LedgerWriter):
        """Record this feature's effects on the stat block. Features, armor
        and items apply in no particular order, so only record facts - never
        read a stat here. Anything that depends on other stats or on worn
        armor is a formula evaluated on read (see Core.Improvements)."""
        pass

    def granted_spells(self) -> list[FeatureSpell]:
        """Override to list the spells and cantrips this feature grants (a
        feat's always-prepared spells, a boon's chosen spell, a subclass
        feature's ritual). The character grants them with the feature,
        stamped like it - so whoever grants the feature never adds its
        spells separately (see Character.spell_grants). Return [] (default)
        for features with no spells."""
        return []

    def get_description(self, character: CharacterView) -> str | None:
        return None

    def get_improved_description(
        self, character: CharacterView
    ) -> "list[Block] | None":
        """Override to give the card a clearer layout of the same rules as
        get_description(): paragraphs, facts, tables and named options
        (Model/Content/FeatureText.py, whose docstring has the guidelines).
        When set, the sheet shows it instead of get_description(), which
        stays as the source text (RunCharacterCreator.py --source-text
        prints it instead). Return None (default) to show
        get_description()."""
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
        constantly in play - e.g. Rage Damage or a count of options known.
        Dice that grow with level belong in FeatureDice (Feature(dice=...))
        instead. Returns a list of (group_label, steps) tuples, where
        steps is a list of (step_label, value) pairs - typically one tile
        per level or level-range, e.g. [("Rage Damage",
        [("Lv 1-8", "+2"), ("Lv 9-15", "+3"), ...])], commonly built from
        StringUtils.compress_level_progression(). Every step is shown with
        equal weight and no "current level" is called out: the generated
        page isn't reprinted on every level-up, so a step highlighted as
        "current" at generation time would silently go stale. Return None
        (default) for features with no resource tile at all."""
        return None
