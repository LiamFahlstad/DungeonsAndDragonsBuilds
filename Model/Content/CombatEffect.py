"""What one use of a feature does in a fight, said by the feature itself
(Feature.combat_effects), so the combat simulator doesn't have to read it from
the rules text. The combat UI's Custom Effect picker fills its form from these
(Combat/CombatUIQt/effect_options.py), the way it fills a spell from its
checked mechanics (CharacterContent/Spells/SpellFactory/Mechanics.py).

Unlike a spell's mechanics, a feature knows whose it is, so its numbers are
worked out already: the DC, the dice at the character's level. Whatever is
left unset falls back to what the feature already says - its DC from
calculate_dc(), its action and duration from its FeatureActivation, a use
spent if it has FeatureUses - so most effects only say what they roll and do:

    CombatEffect(
        name="Jolt to Life",
        roll="save",
        save_ability=Ability.DEXTERITY,
        half_on_success=True,
        damage=(CombatDamage("2d4", DamageType.LIGHTNING),),
        notes=("...",),
    )

A condition is what lands on a target: on a failed save, on a hit, or on
every target when there's no roll. It's a rules condition (Prone) or a badge
naming what the target has (Bardic Inspiration), which the target's card can
be clicked on to read.
"""

import re
from dataclasses import dataclass
from typing import Literal

from Core.Definitions import Ability, DamageType
from Model.Content.ActionType import ActionType

# "2d4", "1d8 + 3", or a flat "5".
DICE = re.compile(r"\d+d\d+(?: [+-] \d+)?|\d+")
ROLLS = ("save", "attack", "none")
# ("start" or "end", "source" or "target"): "until the end of its next turn"
# is ("end", "target"), as the spell mechanics and the combat UI have it.
_UNTIL_EDGES = ("start", "end")
_UNTIL_WHOSE = ("source", "target")


@dataclass(frozen=True)
class CombatDamage:
    """Damage one use deals: dice at the character's level and a type, or
    None with the types the user chooses from."""

    dice: str
    damage_type: DamageType | None
    choices: tuple[DamageType, ...] = ()

    def __post_init__(self):
        if not DICE.fullmatch(self.dice):
            raise ValueError(f"{self.dice!r} is not dice like '2d4' or '1d8 + 3'")
        if self.damage_type is None and len(self.choices) < 2:
            raise ValueError("A damage type to choose needs two or more choices")
        if self.damage_type is not None and self.choices:
            raise ValueError("Choices are only for a damage type of None")


@dataclass(frozen=True)
class CombatCondition:
    """What lands on a target, and for how long: `until` a turn's start or
    end, or `duration_seconds` (None: the feature's own duration)."""

    name: str
    until: tuple[str, str] | None = None
    duration_seconds: int | None = None

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("A condition needs a name")
        if self.until is not None:
            edge, whose = self.until
            if edge not in _UNTIL_EDGES or whose not in _UNTIL_WHOSE:
                raise ValueError(
                    f"until must be ({'|'.join(_UNTIL_EDGES)},"
                    f" {'|'.join(_UNTIL_WHOSE)}), got {self.until!r}"
                )


@dataclass(frozen=True)
class CombatEffect:
    """One use of a feature in a fight: what it rolls, what it does to its
    targets and what it costs. See the module docstring."""

    # The picker's row and the log's name for it; "" is the feature's name.
    # A feature with several uses (Reanimator's Skill Set's Jolt to Life)
    # names each.
    name: str = ""
    # "save": each target saves; "attack": the user rolls against each
    # target's AC; "none": it just happens, to every target.
    roll: Literal["save", "attack", "none"] = "none"
    save_ability: Ability | None = None
    dc: int | None = None  # None: the feature's calculate_dc()
    half_on_success: bool = False
    # A target repeats the save at the end of each of its turns, ending the
    # condition on itself.
    repeat_save: bool = False
    attack_bonus: int | None = None  # None: the user's spell attack bonus
    damage: tuple[CombatDamage, ...] = ()
    # Hit Points each target regains, or Temporary Hit Points it gains, at
    # the character's level ("1d10 + 3"). Every target gets them, whatever
    # the roll. The form has one amount box, so only one of damage, healing
    # and temp_hp can be set: the rest go in the notes.
    healing: str | None = None
    temp_hp: str | None = None
    condition: CombatCondition | None = None
    # None: the feature's FeatureActivation action_type (and none if it has
    # none). Set it when using it takes an action the feature doesn't say,
    # like the casting of the spell it rides on.
    action_type: ActionType | None = None
    concentration: bool = False
    # Whether it spends one of the feature's FeatureUses (if it has any).
    spends_use: bool = True
    # The spell it casts, if any: a condition it gives is that spell's badge,
    # and shows the spell when clicked.
    spell: str | None = None
    # For the user, about what the form can't do (healing, moving, a choice).
    notes: tuple[str, ...] = ()

    def __post_init__(self):
        if self.roll not in ROLLS:
            raise ValueError(f"roll {self.roll!r} is not one of {list(ROLLS)}")
        if (self.roll == "save") != (self.save_ability is not None):
            raise ValueError("A save_ability goes with a roll of 'save', and only then")
        if self.roll != "save" and (self.half_on_success or self.repeat_save):
            raise ValueError("half_on_success and repeat_save are for a 'save' only")
        if self.roll != "save" and self.dc is not None:
            raise ValueError("A dc is for a 'save' only")
        if self.roll != "attack" and self.attack_bonus is not None:
            raise ValueError("An attack_bonus is for an 'attack' only")
        if any(not note.strip() for note in self.notes):
            raise ValueError("A note can't be empty")
        for field, dice in (("healing", self.healing), ("temp_hp", self.temp_hp)):
            if dice is not None and not DICE.fullmatch(dice):
                raise ValueError(f"{field} {dice!r} is not dice like '2d4 + 3'")
        amounts = [
            bool(self.damage),
            self.healing is not None,
            self.temp_hp is not None,
        ]
        if sum(amounts) > 1:
            raise ValueError(
                "Only one of damage, healing and temp_hp: the rest go in notes"
            )
