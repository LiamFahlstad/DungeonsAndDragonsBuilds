"""A creature's stat-block abilities (traits, actions, reactions, ...): the
free-form MonsterAbility and the structured subclasses that build the
standard 5e stat-block sentence from fields (MeleeAttack, SavingThrowEffect,
...). Shared by the monster catalog (Combat/Monsters), companions and wild
shapes (CharacterContent) and the combat engine."""

import re
from dataclasses import dataclass as dataclass_decorator
from dataclasses import field
from enum import Enum
from typing import Optional

from Core.Definitions import Ability, DamageType


@dataclass_decorator
class MonsterAbility:
    """A single ability (trait, action, etc.) from a monster's stat block."""

    name: str
    description: str


_DC_PATTERN = re.compile(r"\bDC\s*(\d+)", re.IGNORECASE)


def extract_dc_from_text(text: str) -> Optional[int]:
    """Pull the first "DC <n>" (or "DC<n>") out of free-form ability text,
    e.g. "Wisdom Saving Throw: DC 14, ..." or "... forces a DC15 Constitution
    save." -> 14 / 15. Returns None if no such pattern is found."""
    match = _DC_PATTERN.search(text)
    return int(match.group(1)) if match else None


@dataclass_decorator
class DcMonsterAbility(MonsterAbility):
    """A MonsterAbility whose description is hand-written prose (rather than
    built from structured fields like SavingThrowEffect) but still names a
    save DC inline. extract_dc() pulls that number back out of the free text,
    so the combat UI can still render a save-chance-by-modifier table without
    the ability needing to be rewritten as a fully structured subclass."""

    def extract_dc(self) -> Optional[int]:
        return extract_dc_from_text(self.description)


class DiceType(int, Enum):
    """A single die's size, e.g. the d6 in "2d6 + 5"."""

    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20

    @property
    def notation(self) -> str:
        return f"d{self.value}"

    def average(self, count: int = 1) -> float:
        """True statistical average, e.g. D6.average() == 3.5. Callers that
        need the 5e stat-block display convention (rounded down) floor this
        themselves -- kept fractional here so other consumers (e.g. monster
        scoring) can use the precise value."""
        return count * (self.value + 1) / 2


@dataclass_decorator
class MeleeAttack(MonsterAbility):
    """A MonsterAbility subclass for a standard melee attack action. Builds
    the standard 5e stat-block sentence from structured inputs instead of a
    hand-written description string."""

    attack_bonus: int = 0
    reach_ft: int = 5
    dice_count: int = 1
    dice_type: DiceType = DiceType.D4
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.BLUDGEONING
    secondary_dice_count: int = 0
    secondary_dice_type: DiceType = DiceType.D4
    secondary_damage_bonus: int = 0
    secondary_damage_type: Optional[DamageType] = None
    additional_ruling: str = ""
    description: str = field(init=False, default="")

    def __post_init__(self):
        average = int(self.dice_type.average(self.dice_count)) + self.damage_bonus
        dice_notation = f"{self.dice_count}{self.dice_type.notation}"
        if self.damage_bonus > 0:
            dice_notation += f" + {self.damage_bonus}"
        elif self.damage_bonus < 0:
            dice_notation += f" - {abs(self.damage_bonus)}"
        secondary = ""
        if self.secondary_dice_count > 0 and self.secondary_damage_type is not None:
            sec_notation, sec_average = _format_dice_notation(
                self.secondary_dice_count,
                self.secondary_dice_type,
                self.secondary_damage_bonus,
            )
            secondary = f" plus {sec_average} ({sec_notation}) {self.secondary_damage_type.value} damage"
        ruling = f" {self.additional_ruling}" if self.additional_ruling else ""
        self.description = (
            f"Melee Attack Roll: +{self.attack_bonus}, reach {self.reach_ft} ft. "
            f"Hit: {average} ({dice_notation}) {self.damage_type.value} damage{secondary}.{ruling}"
        )


def _format_dice_notation(
    dice_count: int, dice_type: DiceType, damage_bonus: int
) -> tuple[str, int]:
    """Shared by RangedAttack/SavingThrowEffect: renders a "NdM + B" damage
    entry and its rounded-down average, matching 5e stat-block convention."""
    average = int(dice_type.average(dice_count)) + damage_bonus
    dice_notation = f"{dice_count}{dice_type.notation}"
    if damage_bonus > 0:
        dice_notation += f" + {damage_bonus}"
    elif damage_bonus < 0:
        dice_notation += f" - {abs(damage_bonus)}"
    return dice_notation, average


@dataclass_decorator
class RangedAttack(MonsterAbility):
    """A MonsterAbility subclass for a standard ranged attack action (thrown
    weapons, bows, ranged spell-like attacks). Builds the standard 5e
    stat-block sentence from structured inputs instead of a hand-written
    description string."""

    attack_bonus: int = 0
    range_ft: int = 30
    long_range_ft: Optional[int] = None
    dice_count: int = 1
    dice_type: DiceType = DiceType.D4
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.PIERCING
    secondary_dice_count: int = 0
    secondary_dice_type: DiceType = DiceType.D4
    secondary_damage_bonus: int = 0
    secondary_damage_type: Optional[DamageType] = None
    additional_ruling: str = ""
    description: str = field(init=False, default="")

    def __post_init__(self):
        dice_notation, average = _format_dice_notation(
            self.dice_count, self.dice_type, self.damage_bonus
        )
        range_text = (
            f"{self.range_ft}/{self.long_range_ft} ft."
            if self.long_range_ft
            else f"{self.range_ft} ft."
        )
        secondary = ""
        if self.secondary_dice_count > 0 and self.secondary_damage_type is not None:
            sec_notation, sec_average = _format_dice_notation(
                self.secondary_dice_count,
                self.secondary_dice_type,
                self.secondary_damage_bonus,
            )
            secondary = f" plus {sec_average} ({sec_notation}) {self.secondary_damage_type.value} damage"
        ruling = f" {self.additional_ruling}" if self.additional_ruling else ""
        self.description = (
            f"Ranged Attack Roll: +{self.attack_bonus}, range {range_text} "
            f"Hit: {average} ({dice_notation}) {self.damage_type.value} damage{secondary}.{ruling}"
        )


@dataclass_decorator
class SavingThrowEffect(DcMonsterAbility):
    """A MonsterAbility subclass for a saving-throw-based effect (breath
    weapons, gaze attacks, and other area effects). Builds the standard 5e
    "<Ability> Saving Throw: DC N, <target>. Failure: ... Success: ..."
    stat-block sentence from structured inputs instead of a hand-written
    description string. Leave `damage_type` as None for a saving throw with
    no direct damage (e.g. a condition- or exhaustion-only effect) — in that
    case `failure_effect` is used verbatim as the Failure text. Inherits from
    DcMonsterAbility since it always has a DC, though callers should read the
    `dc` field directly rather than extract_dc() -- it's the exact value,
    not a regex guess."""

    ability: Ability = Ability.DEXTERITY
    dc: int = 10
    target: str = ""
    dice_count: int = 0
    dice_type: DiceType = DiceType.D6
    damage_bonus: int = 0
    damage_type: Optional[DamageType] = None
    failure_effect: str = ""
    success_effect: str = ""
    extra_ruling: str = ""
    description: str = field(init=False, default="")

    def __post_init__(self):
        sentences = [f"{self.ability.value} Saving Throw: DC {self.dc}, {self.target}."]

        if self.dice_count > 0 and self.damage_type is not None:
            dice_notation, average = _format_dice_notation(
                self.dice_count, self.dice_type, self.damage_bonus
            )
            failure_text = (
                f"{average} ({dice_notation}) {self.damage_type.value} damage"
            )
            if self.failure_effect:
                failure_text += f", {self.failure_effect}"
            failure_text += "."
        else:
            failure_text = self.failure_effect
        sentences.append(f"Failure: {failure_text}")

        if self.success_effect:
            sentences.append(f"Success: {self.success_effect}")
        if self.extra_ruling:
            sentences.append(self.extra_ruling)

        self.description = " ".join(sentences)


@dataclass_decorator
class MagicResistance(MonsterAbility):
    """A trait for the standard "Advantage on saving throws against spells
    and other magical effects" text. `creature_name` is the monster's
    lowercase self-reference (e.g. "sphinx"), matching stat-block convention."""

    name: str = field(init=False, default="")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.name = "Magic Resistance"
        self.description = (
            f"The {self.creature_name} has Advantage on saving throws "
            f"against spells and other magical effects."
        )


@dataclass_decorator
class LegendaryResistance(MonsterAbility):
    """A trait for the standard Legendary Resistance text, with the
    "(N/Day, or M/Day in Lair)" name suffix built from `uses`/`lair_uses`."""

    name: str = field(init=False, default="")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    uses: int = 1
    lair_uses: Optional[int] = None
    flavor_note: str = ""

    def __post_init__(self):
        lair_note = f", or {self.lair_uses}/Day in Lair" if self.lair_uses else ""
        self.name = f"Legendary Resistance ({self.uses}/Day{lair_note})"
        tail = f", {self.flavor_note}" if self.flavor_note else ""
        self.description = (
            f"If the {self.creature_name} fails a saving throw, "
            f"it can choose to succeed instead{tail}."
        )


@dataclass_decorator
class Regeneration(MonsterAbility):
    """A trait for the standard "regains N Hit Points at the start of each
    of its turns" text. `exception_note` covers riders like "If the troll
    takes Acid or Fire damage, this trait doesn't function on the troll's
    next turn." `name_suffix` covers qualifiers like "(Slaad Only)"."""

    name: str = field(init=False, default="")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    hp: int = 5
    exception_note: str = ""
    name_suffix: str = ""

    def __post_init__(self):
        self.name = (
            f"Regeneration ({self.name_suffix})" if self.name_suffix else "Regeneration"
        )
        exception = f" {self.exception_note}" if self.exception_note else ""
        self.description = (
            f"The {self.creature_name} regains {self.hp} Hit Points at the "
            f"start of each of its turns if it has at least 1 Hit Point.{exception}"
        )


@dataclass_decorator
class PackTactics(MonsterAbility):
    """A trait for the standard Pack Tactics text (Advantage on an attack
    roll if an ally is adjacent to the target). `name_suffix` covers
    qualifiers like "(Land and Water Only)"."""

    name: str = field(init=False, default="")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    name_suffix: str = ""

    def __post_init__(self):
        self.name = (
            f"Pack Tactics ({self.name_suffix})" if self.name_suffix else "Pack Tactics"
        )
        self.description = (
            f"The {self.creature_name} has Advantage on an attack roll against a "
            f"creature if at least one of the {self.creature_name}'s allies is "
            f"within 5 feet of the creature and the ally doesn't have the "
            f"Incapacitated condition."
        )


@dataclass_decorator
class Amphibious(MonsterAbility):
    """A trait for the standard "can breathe air and water" text."""

    name: str = field(init=False, default="Amphibious")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.description = f"The {self.creature_name} can breathe air and water."


@dataclass_decorator
class SunlightSensitivity(MonsterAbility):
    """A trait for the standard Sunlight Sensitivity text (Disadvantage on
    ability checks and attack rolls while in sunlight)."""

    name: str = field(init=False, default="Sunlight Sensitivity")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.description = (
            f"While in sunlight, the {self.creature_name} has Disadvantage "
            f"on ability checks and attack rolls."
        )


@dataclass_decorator
class Rampage(MonsterAbility):
    """A bonus action for the standard Rampage text (a free move + extra
    attack after bloodying a creature). Set `uses_per_day` for a limited
    variant (e.g. `1` -> "Rampage (1/Day)"); leave None for an at-will one."""

    name: str = field(init=False, default="")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    attack_name: str = "Bite"
    uses_per_day: Optional[int] = None

    def __post_init__(self):
        self.name = (
            f"Rampage ({self.uses_per_day}/Day)" if self.uses_per_day else "Rampage"
        )
        self.description = (
            f"Immediately after dealing damage to a creature that is "
            f"already Bloodied, the {self.creature_name} moves up to half "
            f"its Speed, and it makes one {self.attack_name} attack."
        )


@dataclass_decorator
class NimbleEscape(MonsterAbility):
    """A bonus action for the standard Nimble Escape text (Disengage or
    Hide as a bonus action)."""

    name: str = field(init=False, default="Nimble Escape")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} takes the Disengage or Hide action."
        )


@dataclass_decorator
class Multiattack(MonsterAbility):
    """An action for the standard Multiattack text. `attacks_text` is the
    free-text clause that follows "The <creature> makes " (e.g. "two Rend
    attacks" or "two attacks, using Scimitar and Pistol in any
    combination"); the wide variety of real stat-block phrasing here doesn't
    template further without becoming lossy. `extra_ruling` covers a
    trailing rider sentence like "It can replace one attack with a Bite
    attack." Only fits monsters whose Multiattack sentence actually starts
    with "The <creature> makes ..." -- ones phrased around a different verb
    (e.g. "The zombie uses Eye Rays twice.") should stay a plain
    MonsterAbility instead of being forced into this shape. Set
    `use_article=False` for a proper-name monster whose stat block omits
    "The" (e.g. "Garron makes two Surgeon's Maul attacks." rather than
    "The Garron makes...") -- pass the exact display name as `creature_name`
    in that case."""

    name: str = field(init=False, default="Multiattack")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    attacks_text: str = ""
    extra_ruling: str = ""
    use_article: bool = True

    def __post_init__(self):
        article = "The " if self.use_article else ""
        ruling = f" {self.extra_ruling}" if self.extra_ruling else ""
        self.description = (
            f"{article}{self.creature_name} makes {self.attacks_text}.{ruling}"
        )


@dataclass_decorator
class SpiderClimb(MonsterAbility):
    """A trait for the standard Spider Climb text (climbing difficult
    surfaces, including ceilings, without an ability check)."""

    name: str = field(init=False, default="Spider Climb")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} can climb difficult surfaces, "
            f"including along ceilings, without needing to make an ability check."
        )


@dataclass_decorator
class Illumination(MonsterAbility):
    """A trait for the standard Illumination text (shedding Bright/Dim
    Light in a radius). `dim_radius_ft` is the extra Dim Light distance
    beyond `radius_ft`, matching the "an additional N feet" stat-block
    phrasing."""

    name: str = field(init=False, default="Illumination")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    radius_ft: int = 10
    dim_radius_ft: int = 10

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} sheds Bright Light in a {self.radius_ft}-foot "
            f"radius and Dim Light for an additional {self.dim_radius_ft} feet."
        )


@dataclass_decorator
class SiegeMonster(MonsterAbility):
    """A trait for the standard Siege Monster text (double damage to
    objects and structures)."""

    name: str = field(init=False, default="Siege Monster")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} deals double damage to objects and structures."
        )


@dataclass_decorator
class Pounce(MonsterAbility):
    """A legendary action for the standard Pounce text (a free half-Speed
    move plus one attack, with no Bloodied trigger -- unlike Rampage).
    `attack_name` defaults to "Rend", matching every stat block that uses
    this trait in the current corpus."""

    name: str = field(init=False, default="Pounce")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    attack_name: str = "Rend"

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} moves up to half its Speed, and it "
            f"makes one {self.attack_name} attack."
        )


@dataclass_decorator
class WebWalker(MonsterAbility):
    """A trait for the standard Web Walker text (ignoring web movement
    restrictions). Set `knows_location=False` for the shorter variant that
    omits the "knows the location of any other creature in contact with the
    same web" clause."""

    name: str = field(init=False, default="Web Walker")
    description: str = field(init=False, default="")
    creature_name: str = "creature"
    knows_location: bool = True

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} ignores movement restrictions caused by webs"
        )
        if self.knows_location:
            self.description += (
                f", and the {self.creature_name} knows the location of any "
                f"other creature in contact with the same web."
            )
        else:
            self.description += "."


@dataclass_decorator
class WaterBreathing(MonsterAbility):
    """A trait for the standard "can breathe only underwater" text."""

    name: str = field(init=False, default="Water Breathing")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.description = f"The {self.creature_name} can breathe only underwater."


@dataclass_decorator
class PrimalBond(MonsterAbility):
    """A trait for the standard Primal Bond text (add your Proficiency
    Bonus to the beast's ability checks/saving throws). Always phrased
    around "the beast" regardless of the specific creature, matching the
    5e source text verbatim -- no variable fields."""

    name: str = field(init=False, default="Primal Bond")
    description: str = field(
        init=False,
        default="Add your Proficiency Bonus to any ability check or saving throw the beast makes.",
    )


@dataclass_decorator
class Flyby(MonsterAbility):
    """A trait for the standard Flyby text (no Opportunity Attack when
    flying out of an enemy's reach)."""

    name: str = field(init=False, default="Flyby")
    description: str = field(init=False, default="")
    creature_name: str = "creature"

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} doesn't provoke Opportunity Attacks "
            f"when it flies out of an enemy's reach."
        )


@dataclass_decorator
class TinySwarm(MonsterAbility):
    """A trait for the standard tiny-creature Swarm text (occupying another
    creature's space, moving through Tiny-sized openings, and losing the
    ability to regain Hit Points/gain Temporary Hit Points while at reduced
    strength). `creature_type` is the singular Tiny creature named in the
    "opening large enough for a Tiny X" clause (e.g. "bat", "insect",
    "rat", "raven")."""

    name: str = field(init=False, default="Swarm")
    description: str = field(init=False, default="")
    creature_type: str = "creature"

    def __post_init__(self):
        self.description = (
            f"The swarm can occupy another creature's space and vice versa, "
            f"and the swarm can move through any opening large enough for a "
            f"Tiny {self.creature_type}. The swarm can't regain Hit Points "
            f"or gain Temporary Hit Points."
        )


@dataclass_decorator
class MeleeOrRangedAttack(MonsterAbility):
    """A MonsterAbility subclass for a combined "Melee or Ranged Attack
    Roll" action (a weapon usable either way, e.g. a dagger, or a spirit's
    slam that can also lash out at range). `attack_bonus_note` covers a
    trailing qualifier appended directly after the bonus, e.g. " (with
    Advantage if the target is inside the revenant's space)"."""

    name: str
    attack_bonus: int = 0
    attack_bonus_note: str = ""
    reach_ft: int = 5
    range_ft: int = 30
    long_range_ft: Optional[int] = None
    dice_count: int = 1
    dice_type: DiceType = DiceType.D4
    damage_bonus: int = 0
    damage_type: DamageType = DamageType.PIERCING
    additional_ruling: str = ""
    description: str = field(init=False, default="")

    def __post_init__(self):
        dice_notation, average = _format_dice_notation(
            self.dice_count, self.dice_type, self.damage_bonus
        )
        range_text = (
            f"{self.range_ft}/{self.long_range_ft} ft."
            if self.long_range_ft
            else f"{self.range_ft} ft."
        )
        ruling = f" {self.additional_ruling}" if self.additional_ruling else ""
        self.description = (
            f"Melee or Ranged Attack Roll: +{self.attack_bonus}{self.attack_bonus_note}, "
            f"reach {self.reach_ft} ft. or range {range_text} "
            f"Hit: {average} ({dice_notation}) {self.damage_type.value} damage.{ruling}"
        )


@dataclass_decorator
class CastSpellLegendaryAction(MonsterAbility):
    """A legendary action for the standard "uses Spellcasting to cast X"
    idiom, with the fixed "can't take this action again until the start of
    its next turn" recharge rider."""

    name: str
    creature_name: str = "creature"
    spell: str = ""
    description: str = field(init=False, default="")

    def __post_init__(self):
        self.description = (
            f"The {self.creature_name} uses Spellcasting to cast {self.spell}. "
            f"The {self.creature_name} can't take this action again until "
            f"the start of its next turn."
        )


@dataclass_decorator
class NamedAttackAction(MonsterAbility):
    """An action for the "makes one X attack" idiom under a bespoke action
    name -- unlike Multiattack, whose name is always literally
    "Multiattack", this covers a legendary/bonus action with its own name
    (e.g. "Chain Lash (Costs 1 Action)") whose entire body is "The bell
    saint makes one Chain Lash attack." `use_article` mirrors Multiattack's
    for proper-name monsters that don't take "The" (pass the exact display
    name as `creature_name` in that case)."""

    name: str
    creature_name: str = "creature"
    attack_name: str = ""
    use_article: bool = True
    extra_ruling: str = ""
    description: str = field(init=False, default="")

    def __post_init__(self):
        article = "The " if self.use_article else ""
        ruling = f" {self.extra_ruling}" if self.extra_ruling else ""
        self.description = f"{article}{self.creature_name} makes one {self.attack_name} attack.{ruling}"
