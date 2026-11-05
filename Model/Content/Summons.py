"""What a feature (or, later, a spell) summons: SummonSpec, one description of
the creatures a source creates or calls up to fight beside its owner, read by
the combat simulator (Combat/Summons.py).

Pure data plus a stat-block builder, like the rest of Model/Content. It
doesn't import Feature.py (Feature.py imports it), so a spec has no action
cost of its own: a feature's comes from its activation, a spell's from its
casting time.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from Model.Creatures.Combatants import ExtendedCombatantData
from Model.View import CharacterView


class SummonLifetime(Enum):
    """How long a summon lasts once it's out."""

    UNTIL_LONG_REST = "until long rest"  # Reanimated Companion, Steel Defender
    UNTIL_DISMISSED = "until dismissed"  # Drake, Find Familiar (gone at 0 HP / recast)
    CONCENTRATION = "concentration"  # Summon X spells (also has a duration)
    DURATION = "duration"  # Wildfire Spirit 1 hour, Animate Dead 24 hours


class SummonTurn(Enum):
    """When a summon takes its turn in combat."""

    AFTER_OWNER = "after owner"  # shares the owner's initiative
    OWN_INITIATIVE = "own initiative"  # 2024 Find Familiar


class OnZeroHp(Enum):
    """What happens to a summon that drops to 0 Hit Points."""

    VANISHES = "vanishes"  # removed from the fight (most summons)
    DIES = "dies"  # stays as a corpse (Reanimated Companion, Animate Dead's undead)


class WhenFull(Enum):
    """What summoning again does when max_out are already out."""

    REPLACES = "replaces"  # the oldest goes (drake, Find Familiar, Find Steed)
    # Can't (Reanimated Companion: "can't create one while your companion is present").
    REFUSED = "refused"


@dataclass(frozen=True)
class SummonCost:
    """One way to pay for a feature's summon; a spec lists them in the order
    to try. Spells don't use it: casting already spends the slot."""

    # The name of the feature whose use is spent ("Wild Shape"); None: the
    # summoning feature's own use. Ignored when spell_slot is set.
    feature_use: str | None = None
    # The lowest spell slot level that pays for it; None: no slot.
    spell_slot: int | None = None

    def __post_init__(self):
        if self.spell_slot is not None and self.spell_slot < 1:
            raise ValueError(
                f"spell_slot is {self.spell_slot}; a slot that pays for a"
                " summon is level 1 or higher"
            )


@dataclass(frozen=True)
class SummonContext:
    """What a summon was made with, passed to SummonSpec.build."""

    # One of SummonSpec.choices (a drake's Draconic Essence); None: the
    # build's own.
    choice: str | None = None
    # The slot level that was spent; drives a spell's upcast scaling.
    slot_level: int | None = None


def _no_choices(character: CharacterView) -> list[str]:
    return []


def _one_creature(character: CharacterView, ctx: SummonContext) -> int:
    return 1


@dataclass(frozen=True)
class SummonSpec:
    """The creatures one source (a feature's Drake Companion, later a spell's
    Bestial Spirit) summons, and the rules they follow while they're out.
    Feature.summons returns these; Feature.adjust_summon returns a changed
    copy (dataclasses.replace) rather than editing one."""

    name: str  # "Drake Companion", "Bestial Spirit"
    # The stat block of one creature, made with what was chosen and spent.
    build: Callable[[CharacterView, SummonContext], ExtendedCombatantData]
    # What's chosen each time it's summoned, each a SummonContext.choice;
    # [] when there's nothing to choose.
    choices: Callable[[CharacterView], list[str]] = _no_choices
    choice_label: str = ""  # "Draconic Essence", "Environment", "Form"
    # How many creatures one summon makes (Animate Dead: more when upcast).
    count: Callable[[CharacterView, SummonContext], int] = _one_creature
    max_out: int | None = 1  # None: no limit (Animate Dead)
    when_full: WhenFull = WhenFull.REPLACES
    lifetime: SummonLifetime = SummonLifetime.UNTIL_LONG_REST
    # How long a DURATION (or CONCENTRATION) summon lasts at most.
    duration_seconds: int | None = None
    turn: SummonTurn = SummonTurn.AFTER_OWNER
    # The ways to pay for it, tried in order; () is free. A tuple, so a
    # copy made with dataclasses.replace can't change the original's.
    costs: tuple[SummonCost, ...] = ()
    on_zero_hp: OnZeroHp = OnZeroHp.VANISHES
    # It drops to 0 Hit Points when its owner dies (Reanimated Companion's
    # "if you die"; the drake's "or until you die").
    drops_with_owner: bool = False

    def __post_init__(self):
        if self.max_out is not None and self.max_out < 1:
            raise ValueError(
                f"{self.name}: max_out is {self.max_out}; use None for no limit"
            )
        if self.duration_seconds is not None and self.duration_seconds <= 0:
            raise ValueError(
                f"{self.name}: duration_seconds is {self.duration_seconds}"
            )
        if self.lifetime is SummonLifetime.DURATION and self.duration_seconds is None:
            raise ValueError(f"{self.name}: a DURATION summon needs duration_seconds")
