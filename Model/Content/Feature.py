from dataclasses import dataclass
from enum import Enum
from typing import Callable, Literal, Sequence

from Core.Definitions import CharacterClass
from Core.Rules import MAX_LEVEL, MIN_LEVEL, SECONDS_PER_ROUND
from Model.Content.ActionType import ActionType
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatModifiers import Aura, Modifier, Movement
from Model.Content.Effect import Effect
from Model.Content.FeatureText import Block
from Model.Creatures.Combatants import ExtendedCombatantData
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.Content.Summons import SummonContext, SummonSpec
from Model.Spells import FeatureSpell
from Model.View import CharacterView

# ActionType (imported above) lives in its own module so CombatEffect can use
# it too; everything else imports it from here.

# A feature's or spell's functional role, shown as a chip on its card (the
# usage-tags skill has the rubric).
UsageTag = Literal["heal", "buff", "control", "damage", "utility", "summon"]


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


class TimeUnit(Enum):
    """The unit of a FeatureDuration, as its card names it."""

    ROUND = "Round"
    MINUTE = "Minute"
    HOUR = "Hour"
    DAY = "Day"


_SECONDS_PER_UNIT = {
    TimeUnit.ROUND: SECONDS_PER_ROUND,
    TimeUnit.MINUTE: 60,
    TimeUnit.HOUR: 3600,
    TimeUnit.DAY: 86400,
}


@dataclass(frozen=True)
class FeatureDuration:
    """How long a feature's effect lasts, when that's a length of time:
    "1 Minute", "Up to 10 Minutes", "1 Minute or Until Incapacitated".
    `text` is its card's Duration tag and `seconds` its badge's timer in the
    combat UI, which runs the whole length (what `or_until` says can end it
    sooner is the GM's to see). A duration that isn't a length of time
    ("Until Start of Next Turn", "Proficiency Bonus Hours") stays a plain
    string, with no timer (Notes/explicit-attributes-plan.md, 6.2)."""

    amount: int
    unit: TimeUnit
    up_to: bool = False
    or_until: str = ""

    def __post_init__(self):
        if self.amount < 1:
            raise ValueError(f"A FeatureDuration lasts at least 1 {self.unit.value}")

    @property
    def seconds(self) -> int:
        return self.amount * _SECONDS_PER_UNIT[self.unit]

    @property
    def text(self) -> str:
        unit = self.unit.value if self.amount == 1 else f"{self.unit.value}s"
        text = f"{self.amount} {unit}"
        if self.up_to:
            text = f"Up to {text}"
        if self.or_until:
            text = f"{text} or {self.or_until}"
        return text

    def __str__(self) -> str:
        return self.text


@dataclass
class FeatureActivation:
    """Action economy, duration, and range/shape for how a feature is activated,
    rendered as tag chips on its card (mirrors FeatureUses' role for limited-use tracking).

    `duration` is a FeatureDuration when it's a length of time (its badge
    gets a timer), else plain card text. `range_shape` is an area-of-effect
    shape (e.g. "Cone", "Emanation", "Radius") shown with the range ("30
    Feet"); None when no shape is stated (e.g. "30 Feet", "Self", "Touch").
    """

    action_type: "ActionType | Literal['action', 'bonus_action', 'reaction'] | None" = (
        None
    )
    duration: "FeatureDuration | str | None" = None
    range: str | None = None
    range_shape: str | None = None

    def __post_init__(self):
        if self.action_type is not None and not isinstance(
            self.action_type, ActionType
        ):
            self.action_type = ActionType(self.action_type)

    @property
    def duration_text(self) -> str | None:
        """The card's Duration tag."""
        return None if self.duration is None else str(self.duration)

    def duration_to_seconds(self) -> int | None:
        """How long its effect lasts in seconds, for its badge's timer: a
        FeatureDuration's; None for a plain-text duration or none."""
        if isinstance(self.duration, FeatureDuration):
            return self.duration.seconds
        return None


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

    # Why a feature whose rules text has a Trigger ("Trigger": "You fall")
    # has no row with a CombatTrigger, when it's something the combat
    # simulator can't see or check: "falling isn't simulated". Empty for a
    # feature without a Trigger fact, or with a triggered row
    # (combat_effects.py triggers lists the rest; plan step 6.8).
    untriggered = ""

    # The turn's actions using this feature gives back to its owner, which
    # the combat simulator then lets it spend again (Action Surge's "one
    # additional action": ("Action",); Combat/Fight/attack_action.py, plan
    # step 9.3). Empty for a feature that gives none.
    gives_actions: tuple[str, ...] = ()

    def __init__(
        self,
        name: str | None = None,
        origin: str | None = None,
        passive: bool = False,
        usage_tags: list[UsageTag] | None = None,
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

    def combat_effects(self, character: CharacterView) -> list[CombatEffect] | None:
        """Override to say what using this feature does in a fight, for the
        combat simulator's Custom Effect picker (Model/Content/CombatEffect.py
        has the fields): one CombatEffect per way to use it, with the roll,
        damage, condition and cost worked out for `character`. Return [] for
        a feature with nothing to apply to a target in a fight (one that only
        grants spells, proficiencies or a language, or one used from its own
        control, like Wild Shape or a summon), which leaves it out of the
        picker. Return None (default) for a feature not described yet: the
        picker reads its rules text instead, and leaves out a passive one.

        A use that casts a spell (`spell="Hunter's Mark"`) takes that spell's
        own combat effect, if it has one, with what this effect sets on top:
        say only how this feature's casting differs (no slot, another action).
        """
        return None

    def adjust_combat_effect(
        self, character: CharacterView, source: str, effect: CombatEffect
    ) -> CombatEffect:
        """Override when this feature changes what using another of the
        character's features or spells does in a fight (Combat Inspiration:
        two more ways to spend a Bardic Inspiration die). It sees every
        effect of the character's features and spells, so check `source` (the
        feature's or spell's name) first, and return
        dataclasses.replace(effect, ...). Applied in no particular order, like
        apply(): only add (a note, a damage part, add_modifier), never undo or
        read what another feature added. Returns `effect` unchanged (default)
        for features that change no other effect."""
        return effect

    def movement(self, character: CharacterView) -> Movement | None:
        """Override when this feature, always on, changes how `character`
        moves among other creatures or over the ground, which the combat
        UI's battle map counts (Halfling Nimbleness:
        Movement(past_larger=True); Model/Content/CombatModifiers.py's
        Movement has the rules it can say). A feature that does it only
        while it's used (a form, a Bonus Action) gives the Movement on its
        badge in combat_effects() instead. Return None (default) for
        features that don't."""
        return None

    def combat_modifiers(self, character: CharacterView) -> tuple[Modifier, ...]:
        """Override when this feature, always on, changes a roll the combat
        simulator makes for `character` (Model/Content/CombatModifiers.py),
        as a badge's modifiers do while it's on: Brave's Advantage on saves
        to avoid or end Frightened, War Caster's on Concentration saves
        (Notes/combat-effects-plan.md, step 9.2). The fight reads them
        beside the badges' (Combat/Effects/modifiers.py, modifiers_on). Only
        what the fight doesn't already take from the sheet: not a save's
        bonus, AC or a Resistance apply() gives, which the combatant already
        has; a sheet's Advantage (SavingThrowAdvantage) isn't read there, so
        it's said here too. A feature that does it only while it's used
        gives the modifiers on its badge in combat_effects() instead.
        Returns () (default) for features that change no roll."""
        return ()

    def attacks_per_attack_action(self, character: CharacterView) -> int | None:
        """Override when this feature changes how many attacks `character`
        makes when it takes the Attack action (Extra Attack: 2; Two Extra
        Attacks: 3), which the combat simulator opens a weapon row's Times
        at (Combat/Fight/attack_action.py, plan step 9.3); the most any of
        the character's features gives counts. Returns None (default) for
        features that don't."""
        return None

    def aura(self, character: CharacterView) -> Aura | None:
        """Override when this feature, always on, is an aura around
        `character` that gives its allies within it modifiers, as their
        distance from it on the battle map says (Aura of Protection:
        Model/Content/CombatModifiers.py's Aura; Combat/Fight/auras.py, plan
        step 9.4). Returns None (default) for features that aren't."""
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

    def summons(self, character: CharacterView) -> list[SummonSpec]:
        """Override to describe the creatures this feature creates or
        summons to fight beside the character (e.g. a Reanimated Companion,
        a Drake Companion): their stat block, choices, lifetime and cost
        (Model/Content/Summons.py), so the combat simulator can summon them
        in the character's encounters (Combat/Summons.py). Return [] (default)
        for features that summon nothing."""
        return []

    def adjust_summon(self, character: CharacterView, spec: SummonSpec) -> SummonSpec:
        """Override when this feature changes what another source summons
        (e.g. Undead Thralls: Animate Dead makes one more creature): return
        `spec` with more creatures or more choices (dataclasses.replace). It
        sees every summon of the character, so check spec.name first.
        Applied in no particular order. Return `spec` unchanged (default)
        for features that change no summon."""
        return spec

    def modify_summon(
        self,
        character: CharacterView,
        spec: SummonSpec,
        stat_block: ExtendedCombatantData,
        ctx: SummonContext,
    ) -> None:
        """Override when this feature changes the stat block of a summoned
        creature (e.g. Mighty Summoner: more Hit Points per Hit Die): edit
        `stat_block`, one creature `spec` built with `ctx`, in place. It sees
        every summon of the character, so check spec.name first. Applied in
        no particular order. Does nothing (default) for features that change
        no summon."""
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
