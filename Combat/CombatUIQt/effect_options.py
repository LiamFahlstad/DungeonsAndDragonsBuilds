"""What the Custom Effect dialog's picker offers: everything a combatant can use
(stat-block actions, weapons, spells, features), each as an EffectOption saying
what it fills in on the form. Nothing here is rolled or spent, and nothing
imports Qt, so it can be tested on plain dicts.

Spells, features and monster abilities that say what they do in a fight
(their combat_effects, Model/Content/CombatEffect.py) fill the form from that,
all through _described_option. The rest have their rules text read, as
strictly as it can be: a form the GM can correct beats a wrong number they
don't notice, so what's unclear is left out and said in the option's note."""

import re
from collections.abc import Iterable
from dataclasses import dataclass, fields, replace
from functools import lru_cache

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Effects.triggers import TriggerRow
from Core.Definitions import Condition
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent

from .monster_actions import (
    DAMAGE,
    DAMAGE_TYPE_NAMES,
    DIE,
    JOINED,
    DamageRoll,
    MonsterAction,
    ability_effects,
    is_spent,
    legendary_actions_left,
    monster_actions,
    parse_action,
    tidy_dice,
)
from .saves import (
    ABILITIES,
    ATTACK_ROLL,
    CONDITION_JOINER,
    DAMAGE_AMOUNT,
    FEATURE,
    HEALING,
    MONSTER_ACTION,
    SAVING_THROW,
    SPELL,
    TEMP_HP,
    WEAPON,
    EffectOption,
    condition_names,
    damage_text,
    known_save_dc,
    known_spell_attack_bonus,
    with_dice,
)

# EffectOption, what this module makes, is in saves.py beside CustomEffect,
# which holds the one picked.

ATTACKS = "Attacks"
FEATURES = "Features"
TRAITS = "Traits"  # a monster's, only those with combat effects written on them
ALL_SPELLS = "All spells"
# The long category, which starts folded away. Features start open: passive
# ones aren't listed, nor those with nothing to apply (Feature.combat_effects).
COLLAPSED_CATEGORIES = (ALL_SPELLS,)

_ABILITY_SHORT_NAMES = dict(ABILITIES)
_ABILITY_NAMES = "|".join(_ABILITY_SHORT_NAMES)
_CONDITION_NAMES = "|".join(condition.value for condition in Condition)
# The action types a feature's activation names, as the UI calls them.
FEATURE_ACTION_COSTS = {
    "action": "Action",
    "bonus_action": "Bonus Action",
    "reaction": "Reaction",
}
# The action economy the UI counts (CombatAppQt.ACTION_ECONOMY_TYPES).
ACTION_COSTS = tuple(FEATURE_ACTION_COSTS.values())

# "Using a Higher-Level Spell Slot." and "Cantrip Upgrade.": not what the spell
# does at its own level, so they're read for that alone.
_UPGRADE_PARAGRAPH = re.compile(
    r"\s*(?:Using a Higher-Level Spell Slot|At Higher Levels|Cantrip Upgrade)[.:]"
)
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n+")
# Someone rolling a save. Merely mentioning one isn't: "Advantage on Wisdom
# saving throws" has no such verb, and neither has "with a successful ... save".
_SAVE = re.compile(
    r"\b(?P<verb>makes?|making|succeeds? on|succeeding on|fails?|failing|repeats?)"
    r"\s+(?:a|an|another|the)\s+(?:DC\s+\d+\s+)?"
    rf"(?P<ability>{_ABILITY_NAMES})(?:\s+or\s+(?P<other>{_ABILITY_NAMES}))?"
    r"\s+(?:saving throw|save)\b"
)
# Saves in the text that aren't the target's. "You must succeed on a DC 15
# Constitution saving throw" and "make a DC 15 Intelligence saving throw" are the
# caster's; Sanctuary's is whoever attacks the target; "must first" is for what a
# target tries later; "allows it to make" is any effect, not this one.
_NOT_THE_TARGETS_SAVE = re.compile(
    r"(?:(?:^|[.,;:]\s*|\n|\band\s+|\bthen\s+|\b[Ww]hen\s+|\b[Ii]f\s+)"
    r"[Yy]ou\s+(?:must\s+|can\s+|then\s+)?"
    r"|\bwho targets\b[^.]*|\bmust first\s+|\ballows? \w+ to\s+)$"
)
_FOR_CONCENTRATION = re.compile(r"\s+to maintain Concentration", re.IGNORECASE)
_SAID_TO_THE_CASTER = re.compile(r"(?:^|[.,:\n])\s*$")
_ATTACK = re.compile(r"\bmakes?\s+(?:[\w-]+\s+){0,4}?spell attacks?\b", re.IGNORECASE)
_HALF = re.compile(r"half (?:as much|the initial) damage")
# What ties a sentence after the roll to its outcome.
_ON_A_FAILED_SAVE = re.compile(r"\bfail(?:s|ed|ure)?\b|\bor take\b", re.IGNORECASE)
_ON_A_HIT = re.compile(r"\bhits?\b", re.IGNORECASE)
# Damage joined onto the first that waits on something isn't part of the roll's.
# "on a failed save" isn't that here, as the monster text's _CONDITIONAL has it.
_WAITS_ON_SOMETHING = re.compile(r"\s+(?:if|while|when|unless|until|at the)\b")
_ANOTHER_AMOUNT = re.compile(r"\binstead\b[^.]*\d+d\d+|\bor \d+d\d+")
_MODIFIER = r"(?P<modifier>\s+(?:plus|\+)\s+your spellcasting ability modifier)?"
# As well as what a monster's text has: "Force damage equal to 1d8 plus your
# spellcasting ability modifier", and "3d6 Acid, Cold, or Fire damage".
_DAMAGE_ROLL = re.compile(
    f"{DAMAGE.pattern}"
    r"|(?P<named_type>[A-Za-z]+)(?P<named_or>\s+or\s+[A-Za-z]+)?\s+damage"
    rf"(?:\s+\(your choice\))?\s+equal to\s+(?P<equal_dice>\d+d\d+){_MODIFIER}"
    r"|(?P<list_dice>\d+d\d+)\s+(?:[A-Za-z]+,\s+)+(?:or\s+)?[A-Za-z]+\s+damage"
)
_ANY_DAMAGE = re.compile(r"\d+d\d+[^.\n]*?\bdamage\b|\bdamage\b[^.\n]*?\d+d\d+")
_REPEATS_THE_SAVE = re.compile(
    r"end of each of (?:its|their|the [\w ]+['’]s) turns", re.IGNORECASE
)
_HAS_CONDITION = re.compile(
    rf"\b(?:has|have|having) the ({_CONDITION_NAMES})"
    rf"(?: or ({_CONDITION_NAMES}))? condition\b"
)
# "If it has the Charmed condition" and "ends early if you ... have the
# Incapacitated condition": what it asks about, not what it inflicts. "If it
# has 150 Hit Points or fewer, it has the Stunned condition" and "when you cast
# the spell must succeed on a ... saving throw or have" do inflict it.
_NOT_INFLICTED = re.compile(
    r"(?:\b(?:if|while|whenever|when|unless|until)\b"
    r"(?![^,]*\b(?:sav(?:e|ing throw)|fails?)\b)[^,]*"
    # "a creature that is possessed by or has the Charmed condition"
    r"|\b(?:that|who|which)\s+(?:is\b[^,]*\bor\s+)?"
    r"|\b(?:you|not|no longer)\s+|n['’]t\s+)$",
    re.IGNORECASE,
)
_UPCAST = re.compile(
    r"(?P<subject>[^.]*?)\s+increases?\s+by\s+(?P<dice>\d+d\d+)\b[^.]*?"
    r"for (?:each|every) (?:spell )?slot(?: level)? above"
)
_ONE_DAMAGE = re.compile(
    r"(?:all |the |this spell['’]s |the spell['’]s )*"
    r"(?:initial |base |extra )?damage(?: \(both initial and later\))?",
    re.IGNORECASE,
)
_ANY_UPCAST = re.compile(r"\bdamage\b[^.]*\bslot\b")
_CANTRIP_STEP = re.compile(r"\b(5|11|17)(?:th level)?\s*\((\d+d\d+)")
# One option of several, on a line of its own: "Grovel. The target has the
# Prone condition". What it does isn't what the spell always does.
_OPTION_LINE = re.compile(
    r"([A-Z][\w'’-]*(?:\s+(?:[A-Z][\w'’-]*|of|the|and|or|a|to|in|on))*)\.\s"
)
# How long a condition lasts, when that's a turn: "until the end of its next
# turn", "until the start of the lich's next turn".
_UNTIL_A_TURN = re.compile(
    r"until the (start|end) of (your|its|their|the [\w -]+?['’]s) next turn",
    re.IGNORECASE,
)
_THE_TARGETS = re.compile(r"(?:its|their|the (?:target|creature)['’]s)", re.IGNORECASE)
_HEALS = re.compile(r"\bregains?\b[^.]*\bHit Points?\b")
# Hit Points a spell gives each target now: "regains Hit Points equal to 2d4
# plus your spellcasting ability modifier", "regain 2d8 Hit Points", "gain
# 2d4 + 4 Temporary Hit Points". A number other than dice ("regains 1 Hit
# Point", "equal to half the damage") is a rider, not what it does.
_AMOUNT = r"\d+d\d+(?: \+ \d+)?"
# A stat block writes the average first: "regains 13 (2d8 + 4) Hit Points".
_HEAL_AMOUNT = re.compile(
    rf"\bregains?\s+(?:a number of\s+)?Hit Points equal to ({_AMOUNT})"
    r"(\s+plus your spellcasting ability modifier)?"
    rf"|\bregains?\s+({_AMOUNT}) Hit Points\b"
    rf"|\bregains?\s+\d+ \(({_AMOUNT})\) Hit Points\b"
)
_TEMP_HP_AMOUNT = re.compile(
    rf"\bgains?\s+(?:a number of\s+)?Temporary Hit Points equal to ({_AMOUNT})"
    r"(\s+plus your spellcasting ability modifier)?"
    rf"|\bgains?\s+({_AMOUNT}|\d+) Temporary Hit Points\b"
    rf"|\bgains?\s+\d+ \(({_AMOUNT})\) Temporary Hit Points\b"
)
_HEAL_UPCAST = re.compile(r"healing increases by (\d+d\d+)")
# "5 additional Temporary Hit Points", "The Temporary Hit Points and the Cold
# damage both increase by 5", "the number of Temporary Hit Points you gain
# from this spell increases by 5".
_TEMP_HP_UPCAST = re.compile(
    r"(\d+d\d+|\d+) additional Temporary Hit Points"
    r"|Temporary Hit Points[^.,]*?\bincreases? by (\d+d\d+|\d+)"
)
# "You gain 2d4 + 4 Temporary Hit Points": the caster's, not a target's. It's
# what comes before the amount in its sentence.
_JUST_YOU = re.compile(r"\s*You\s*")
# Where a monster's hit stops and a save it forces begins.
_HIT_ENDS = re.compile(r"\b\w+ Saving Throw:|\bFailure:")
_FLAT_ONE = "1d1"  # how a weapon writes an Unarmed Strike's damage
# What an ExtraDamage's note says when the weapon doesn't always deal it.
_NOT_ALWAYS = re.compile(r"\b(?:activate|chosen|when|while|if|only)\b", re.IGNORECASE)


@dataclass(frozen=True)
class HitPointGain:
    """Hit Points an effect gives each target: regained, or temporary."""

    dice: str
    temporary: bool = False
    add_modifier: bool = False
    upcast: str = ""  # per slot level above the spell's: dice, or a number
    # "You gain ...": they're the caster's.
    is_the_casters: bool = False


@dataclass(frozen=True)
class EffectText:
    """What a spell's or feature's rules text says its effect is."""

    ability: str | None = None  # short, as the dialog has it ("DEX")
    is_attack: bool = False
    half_on_save: bool = False
    repeat_save: bool = False
    damage: tuple[DamageRoll, ...] = ()
    condition: str = ""
    notes: tuple[str, ...] = ()
    # Whether the damage adds the caster's spellcasting ability modifier.
    adds_modifier: bool = False
    # Whether it states damage anywhere (filled in or not), and heals anyone.
    states_damage: bool = False
    heals: bool = False
    # The condition's duration, when that's a turn (see EffectOption.until).
    until: tuple[str, str] | None = None
    # Hit Points it gives each target now, if any.
    gain: HitPointGain | None = None
    # The upcasting and cantrip paragraphs, for working out higher levels.
    upgrades: tuple[str, ...] = ()


def _at_cantrip_level(dice: str, steps: tuple[tuple[int, str], ...], level: int) -> str:
    """A cantrip's described dice at a character's level: its first die
    swapped for the last step reached."""
    reached = [step for at, step in steps if at <= level]
    return DIE.sub(reached[-1], dice, count=1) if reached else dice


def _gain_note(gain: HitPointGain, level: int, modifier: int | None) -> str:
    """The Hit Points a spell that also deals damage gives, which the form's
    one amount box can't hold beside the damage."""
    dice = gain.dice
    if gain.add_modifier and modifier is not None:
        dice = _with_modifier(DamageRoll(dice, None), modifier).dice
    what = "Temporary Hit Points" if gain.temporary else "Hit Points"
    amount = f"{dice} {what}"
    if gain.add_modifier and modifier is None:
        amount += " plus the spellcasting ability modifier"
    more = f" ({gain.upcast} more per slot level above {level})" if gain.upcast else ""
    verb = "gives" if gain.temporary else "heals"
    return f"It also {verb} {amount}{more}: apply that by hand."


def _with_modifier(roll: DamageRoll, modifier: int) -> DamageRoll:
    if roll.dice == "0":
        # The modifier alone (Green-Flame Blade's fire before level 5).
        return DamageRoll(str(max(modifier, 0)), roll.damage_type)
    if not modifier:
        return roll
    sign = "+" if modifier > 0 else "-"
    return DamageRoll(f"{roll.dice} {sign} {abs(modifier)}", roll.damage_type)


def _last_sentence(text: str) -> str:
    return _SENTENCE_END.split(text)[-1]


def _until_a_turn(text: str) -> tuple[str, str] | None:
    """("start" or "end", "source" or "target") for "until the end of its next
    turn" and the like at the start of `text`'s first sentence's rest. "Its" is
    the target's; "your" or "the lich's" the source's."""
    sentence = _SENTENCE_END.split(text)[0]
    match = _UNTIL_A_TURN.search(sentence)
    if match is None:
        return None
    whose = "target" if _THE_TARGETS.fullmatch(match[2]) else "source"
    return match[1].lower(), whose


def _inflicted_condition(
    text: str,
) -> tuple[str, str, tuple[str, str] | None, str]:
    """The first rules condition `text` puts on someone, the one it offers
    instead, how long it lasts if that's a turn, and a note. Only "has the
    Stunned condition" counts: a bare "Stunned" could be anything, like what a
    spell cures. One only in an option ("Grovel. ...") isn't what it always
    does, so it's the note that says it."""
    in_options: dict[str, list[str]] = {}
    for match in _HAS_CONDITION.finditer(text):
        if _NOT_INFLICTED.search(_last_sentence(text[: match.start()])):
            continue
        line = text[text.rfind("\n", 0, match.start()) + 1 :]
        option = _OPTION_LINE.match(line)
        if option is not None:
            in_options.setdefault(match[1], []).append(option[1])
            continue
        return match[1], match[2] or "", _until_a_turn(text[match.end() :]), ""
    if not in_options:
        return "", "", None, ""
    condition, options = next(iter(in_options.items()))
    names = ", ".join(dict.fromkeys(options))
    return "", "", None, f"{condition} only with one of its options ({names})."


def _targets_save(body: str, save: re.Match[str]) -> bool:
    """Whether this is a save the target rolls."""
    before = body[: save.start()]
    if _NOT_THE_TARGETS_SAVE.search(before):
        return False
    if _FOR_CONCENTRATION.match(body, save.end()):
        return False
    return not (save["verb"] == "make" and _SAID_TO_THE_CASTER.search(before))


def _joined_rolls(text: str) -> tuple[tuple[DamageRoll, ...], str, bool]:
    """The first damage in `text` with any joined straight onto it, what comes
    after, and whether it adds a spellcasting modifier. As
    monster_actions._damage_rolls has it, for a sentence that's already the
    roll's outcome."""
    rolls: list[DamageRoll] = []
    position = 0
    adds_modifier = False
    for match in _DAMAGE_ROLL.finditer(text):
        between = text[position : match.start()]
        if rolls and (
            not JOINED.fullmatch(between)
            or _WAITS_ON_SOMETHING.match(text, match.end())
        ):
            break
        word = match["type"] or match["named_type"]
        chosen = match["or"] or match["named_or"] or match["list_dice"]
        damage_type = DAMAGE_TYPE_NAMES.get(word.lower()) if word else None
        if word and damage_type is None and not chosen:
            break  # "3d6 extra damage": which of its parts isn't said
        groups = ("dice", "bare", "flat", "equal_dice", "list_dice")
        dice = next(filter(None, map(match.group, groups)))
        rolls.append(DamageRoll(tidy_dice(dice), None if chosen else damage_type))
        adds_modifier = adds_modifier or bool(match["modifier"])
        position = match.end()
    return tuple(rolls), text[position:], adds_modifier


def _damage_of_the_roll(
    body: str, roll: re.Match[str], is_attack: bool
) -> tuple[tuple[DamageRoll, ...], str, bool]:
    """_joined_rolls for the damage a hit or failed save deals, from the roll's
    own sentence or a later one tied to how it went, with the next sentence
    added to what comes after. Damage anywhere else is for something else:
    Web's for the webs burning, Enervation's 2d8 on later turns."""
    tied = _ON_A_HIT if is_attack else _ON_A_FAILED_SAVE
    sentences = [s for s in _SENTENCE_END.split(body[roll.start() :]) if s.strip()]
    for index, sentence in enumerate(sentences):
        if index and not tied.search(sentence):
            continue
        rolls, rest, adds_modifier = _joined_rolls(sentence)
        if rolls:
            after = " ".join([rest, *sentences[index + 1 : index + 2]])
            return rolls, after, adds_modifier
    return (), "", False


def _roll_notes(
    saves: list[re.Match[str]],
    attack: re.Match[str] | None,
    rolls: tuple[DamageRoll, ...],
    after: str,
) -> list[str]:
    """What the GM should check about how the roll was read."""
    notes = []
    if saves and attack is not None:
        first, second = "a saving throw", "an attack roll"
        if attack.start() < saves[0].start():
            first, second = second, first
        notes.append(f"It has {second} too: {first} comes first, so it's set.")
    abilities = list(dict.fromkeys(save["ability"] for save in saves))
    if saves and saves[0]["other"]:
        notes.append(f"The target rolls {saves[0]['ability']} or {saves[0]['other']}.")
    elif len(abilities) > 1 and attack is None:
        others = " and ".join(abilities[1:])
        notes.append(f"Also {others} saves in the text: {abilities[0]} is set.")
    if rolls and _ANOTHER_AMOUNT.search(after):
        notes.append("The text gives another amount or type: the first is filled in.")
    if any(roll.damage_type is None for roll in rolls):
        notes.append("Its damage is of a type to choose: give one.")
    return notes


@lru_cache(maxsize=None)
def read_effect_text(text: str) -> EffectText:
    """What an effect's rules text rolls and does. The picker reads every spell
    in the game each time it opens, so this is kept once read."""
    lines = text.splitlines()
    body = "\n".join(line for line in lines if not _UPGRADE_PARAGRAPH.match(line))
    upgrades = tuple(line for line in lines if _UPGRADE_PARAGRAPH.match(line))
    saves = [save for save in _SAVE.finditer(body) if _targets_save(body, save)]
    attack = _ATTACK.search(body)
    is_attack = attack is not None and (not saves or attack.start() < saves[0].start())
    is_save = bool(saves) and not is_attack
    roll = attack if is_attack else saves[0] if saves else None
    rolls: tuple[DamageRoll, ...] = ()
    after = ""
    adds_modifier = False
    if roll is not None:
        rolls, after, adds_modifier = _damage_of_the_roll(body, roll, is_attack)
    condition, other_condition, until, option_note = _inflicted_condition(body)
    notes = _roll_notes(saves, attack, rolls, after)
    states_damage = bool(_ANY_DAMAGE.search(body))
    if not rolls and states_damage:
        notes.append("Its text states damage that isn't filled in: check it.")
    if other_condition:
        notes.append(f"The condition can be {other_condition} instead.")
    if option_note:
        notes.append(option_note)
    if is_save:
        sentence = _last_sentence(body[: saves[0].end()])
        if "unwilling" in sentence.lower():
            notes.append("Only an unwilling target rolls this save.")
    return EffectText(
        ability=_ABILITY_SHORT_NAMES[saves[0]["ability"]] if is_save else None,
        is_attack=is_attack,
        half_on_save=is_save and bool(_HALF.search(body)),
        repeat_save=is_save
        and any(
            _REPEATS_THE_SAVE.search(sentence)
            and re.search(r"\bsav(?:e|ing throw)\b", sentence)
            for sentence in _SENTENCE_END.split(body)
        ),
        damage=rolls,
        condition=condition,
        notes=tuple(notes),
        adds_modifier=adds_modifier,
        states_damage=states_damage,
        heals=bool(_HEALS.search(body)),
        until=until,
        upgrades=upgrades,
        gain=_read_gain(body, upgrades),
    )


def _read_gain(body: str, upgrades: tuple[str, ...]) -> HitPointGain | None:
    """The Hit Points the text gives each target, and what more a higher slot
    gives."""
    for pattern, upcast, temporary in (
        (_HEAL_AMOUNT, _HEAL_UPCAST, False),
        (_TEMP_HP_AMOUNT, _TEMP_HP_UPCAST, True),
    ):
        match = pattern.search(body)
        if match is None:
            continue
        more = next((m for m in map(upcast.search, upgrades) if m is not None), None)
        sentence = _SENTENCE_END.split(body[: match.start()])[-1]
        return HitPointGain(
            match[1] or match[3] or match[4],
            temporary=temporary,
            add_modifier=bool(match[2]),
            upcast=next((g for g in more.groups() if g), "") if more else "",
            is_the_casters=bool(_JUST_YOU.fullmatch(sentence)),
        )
    return None


def _upcast_dice(
    rolls: tuple[DamageRoll, ...], upgrades: Iterable[str]
) -> tuple[str, ...]:
    """What each of rolls gains per slot level above the spell's: () when the
    text doesn't say clearly which of them grows, and by how much."""
    for upgrade in upgrades:
        match = _UPCAST.search(_UPGRADE_PARAGRAPH.sub("", upgrade))
        if match is None:
            continue
        subject = match["subject"].split(",")[-1].strip()
        dice = match["dice"]
        named = [
            type_name
            for type_name in DAMAGE_TYPE_NAMES.values()
            if re.search(rf"\b{type_name}\b", subject, re.IGNORECASE)
        ]
        if named:
            if set(named) - {roll.damage_type for roll in rolls}:
                return ()  # it's for damage that wasn't filled in
            return tuple(dice if roll.damage_type in named else "" for roll in rolls)
        if re.match(r"(?:all|both)\b", subject, re.IGNORECASE):
            return tuple(dice for _ in rolls)
        if len(rolls) == 1 and _ONE_DAMAGE.fullmatch(subject):
            return (dice,)
    return ()


def _with_cantrip_level(
    rolls: tuple[DamageRoll, ...], upgrades: Iterable[str], level: int
) -> tuple[DamageRoll, ...]:
    """A cantrip's damage at a character's level: "increases by 1d10 when you
    reach levels 5 (2d10), 11 (3d10), and 17 (4d10)". Only for one part of
    damage rolling the same die, as the others don't say which it means."""
    if len(rolls) != 1:
        return rolls
    first = DIE.search(rolls[0].dice)
    for upgrade in upgrades:
        steps = [
            dice
            for reached, dice in _CANTRIP_STEP.findall(upgrade)
            if int(reached) <= level
        ]
        if steps and first is not None and steps[-1].endswith(f"d{first[2]}"):
            dice = rolls[0].dice[: first.start()] + steps[-1]
            dice += rolls[0].dice[first.end() :]
            return (DamageRoll(dice, rolls[0].damage_type),)
    return rolls


class PactSlot(int):
    """A slot level paid with a Pact Magic slot (char["pact_slots"]) instead
    of a spell slot: a Warlock's own pool, which a Short Rest restores. As an
    int it is the slot's level, so upcasting reads it like any other slot."""

    def __repr__(self) -> str:
        return f"PactSlot({int(self)})"


def has_slots(char: dict) -> bool:
    """Whether char's spell slots or Pact Magic slots are tracked."""
    return bool(char.get("spell_slots") or char.get("pact_slots"))


def spell_slot_choices(char: dict, spell_level: int) -> list[tuple[str, int | None]]:
    """What char can pay for a spell of spell_level with, as (label, slot
    level), cheapest first: its spell slots and Pact Magic slots (a PactSlot)
    of that level or higher that have any left, a spell slot before a Pact
    Magic slot of the same level, then casting without one (a ritual, an
    item, a feature). A cantrip needs no slot, and neither does a caster
    whose slots aren't tracked."""
    if spell_level == 0:
        return [("Cantrip: no slot", None)]
    if not has_slots(char):
        return [("No slots tracked", None)]
    paid: list[tuple[str, int | None]] = [
        (f"Level {level} slot ({count} left)", level)
        for level, count in (char.get("spell_slots") or {}).items()
        if level >= spell_level and count > 0
    ]
    paid += [
        (f"Level {level} Pact Magic slot ({count} left)", PactSlot(level))
        for level, count in (char.get("pact_slots") or {}).items()
        if level >= spell_level and count > 0
    ]
    paid.sort(key=lambda choice: (choice[1], isinstance(choice[1], PactSlot)))
    return paid + [("No slot (ritual, item or feature)", None)]


def casting_time_cost(spell) -> str | None:
    """The action a spell takes, if it's one the UI counts."""
    try:
        cost = spell.casting_time_type.value
    except ValueError:
        return None  # a casting time the spell's data doesn't say plainly
    return cost if cost in ACTION_COSTS else None


def feature_action_cost(feature) -> str | None:
    """The action a feature takes, if it's one the UI counts."""
    action_type = feature.activation.action_type if feature.activation else None
    return None if action_type is None else FEATURE_ACTION_COSTS.get(action_type.value)


def _spell_save_dc(spell, char: dict) -> int | None:
    sheet = char.get("_stat_block")
    if sheet is not None and spell.spell_casting_ability is not None:
        return sheet.calculate_difficulty_class_for_ability(spell.spell_casting_ability)
    return known_save_dc(char)


def _spell_attack_bonus(spell, char: dict) -> int | None:
    sheet = char.get("_stat_block")
    if sheet is not None and spell.spell_casting_ability is not None:
        return sheet.calculate_attack_bonus_for_ability(spell.spell_casting_ability)
    return known_spell_attack_bonus(char)


def _spell_modifier(spell, char: dict) -> int | None:
    """The modifier of the ability char casts `spell` with, if that's known."""
    sheet = char.get("_stat_block")
    if sheet is None:
        return None
    ability = spell.spell_casting_ability or sheet.spell_casting_ability
    return None if ability is None else sheet.get_ability_modifier(ability)


def _casting_modifier(char: dict) -> int | None:
    """The modifier of char's spellcasting ability, if that's known."""
    sheet = char.get("_stat_block")
    if sheet is None or sheet.spell_casting_ability is None:
        return None
    return sheet.get_ability_modifier(sheet.spell_casting_ability)


def _character_level(char: dict) -> int:
    return sum((char.get("class_levels") or {}).values())


def _roll_summary(
    text: EffectText,
    dc: int | None,
    bonus: int | None,
    rolls: Iterable[DamageRoll],
    amount_kind: str = DAMAGE_AMOUNT,
) -> list[str]:
    """The numbers a row shows for what `text` says."""
    parts = []
    if text.is_attack:
        parts.append("attack" if bonus is None else f"{bonus:+d}")
    elif text.ability is not None:
        parts.append(f"DC {dc or '?'} {text.ability}")
    amount = damage_text(rolls)
    if amount:
        parts.append(amount_text(amount, amount_kind))
    if text.half_on_save:
        parts.append("half on save")
    if text.condition:
        parts.append(text.condition)
    return parts


def amount_text(amount: str, amount_kind: str) -> str:
    """ "8d6 Fire", "heals 2d4 + 3", "2d4 + 4 temp HP"."""
    if amount_kind == HEALING:
        return f"heals {amount}"
    if amount_kind == TEMP_HP:
        return f"{amount} temp HP"
    return amount


def _unknown_number_notes(
    text: EffectText, dc: int | None, bonus: int | None
) -> list[str]:
    if text.is_attack and bonus is None:
        return ["The attack bonus isn't known: set it."]
    if text.ability is not None and dc is None:
        return ["The DC isn't known: set it."]
    return []


def is_applicable(spell) -> bool:
    """Whether the spell has anything for the Custom Effect form to apply.
    Only a described spell says it hasn't (Alarm's []); unchecked spells are
    offered."""
    return spell.combat_effects() != []


def spell_options(spell, char: dict | None) -> list[EffectOption]:
    """The picker's rows for casting `spell`, for char (or nobody yet): one
    per way to cast it its combat effects describe (Command's five), one
    that only spends the cast for a spell with nothing to apply (Alarm), or
    for a spell not described, what its text says. A monster's cantrip stays
    at its own level: it has no character level."""
    who = char if char is not None else {}
    effects = spell.combat_effects()
    if effects is None:
        return [_text_spell_option(spell, who)]
    # Nothing to apply (Alarm): casting it still spends the slot and the
    # action, and holds Concentration.
    return [
        _described_spell_option(spell, who, effect)
        for effect in effects or [CombatEffect()]
    ]


def spell_option(spell, char: dict | None) -> EffectOption:
    """The first of spell_options: what casting `spell` fills in."""
    return spell_options(spell, char)[0]


def _described_spell_option(spell, who: dict, effect: CombatEffect) -> EffectOption:
    """What one way to cast a spell its combat effects describe fills in: the
    effect itself, with the caster's DC, attack bonus and modifier, the
    spell's casting time, duration and Concentration, and the cheapest slot
    left. A way that's part of a cast already counted (spends_use=False:
    Ice Knife's explosion) spends nothing."""
    effect = _adjusted(who, spell.name, effect)
    casts = effect.spends_use
    slot = spell_slot_choices(who, spell.level)[0][1] if casts else None
    no_slot = []
    if casts and spell.level and has_slots(who) and slot is None:
        no_slot.append(f"No slot of level {spell.level} or higher left.")
    return _described_option(
        who,
        effect,
        name=spell.name,
        kind=SPELL,
        tooltip=spell.description,
        default_dc=_spell_save_dc(spell, who) if effect.roll == "save" else None,
        default_bonus=(
            _spell_attack_bonus(spell, who) if effect.roll == "attack" else None
        ),
        modifier=_spell_modifier(spell, who),
        level=spell.level,
        duration_seconds=spell.duration_seconds,
        action_cost=casting_time_cost(spell) if casts else None,
        concentration=spell.is_concentration and casts,
        spell_name=spell.name,
        lead_notes=no_slot,
        slot_level=slot,
        spell_level=spell.level,
        counts_uses=casts,
    )


def _text_spell_option(spell, who: dict) -> EffectOption:
    """What casting a spell without combat effects fills in, read from its
    text: the GM checks it."""
    text = read_effect_text(spell.description)
    dc = _spell_save_dc(spell, who) if text.ability is not None else None
    bonus = _spell_attack_bonus(spell, who) if text.is_attack else None
    gain = text.gain
    gains_modifier = gain is not None and gain.add_modifier
    modifier = (
        _spell_modifier(spell, who) if text.adds_modifier or gains_modifier else 0
    )
    upcast: tuple[str, ...] = ()
    rolls = text.damage
    if spell.level == 0:
        rolls = _with_cantrip_level(rolls, text.upgrades, _character_level(who))
    rolls = tuple(_with_modifier(roll, modifier or 0) for roll in rolls)
    if spell.level > 0 and rolls:
        upcast = _upcast_dice(rolls, text.upgrades)
    slot = spell_slot_choices(who, spell.level)[0][1]
    notes = list(text.notes) + _unknown_number_notes(text, dc, bonus)
    if text.adds_modifier and modifier is None:
        notes.append("Add the spellcasting ability modifier to the damage.")
    amount_kind = DAMAGE_AMOUNT
    if gain is not None and rolls:
        # One amount box: the damage goes in it, the Hit Points by hand.
        notes.append(_gain_note(gain, spell.level, modifier))
    elif gain is not None:
        amount_kind = TEMP_HP if gain.temporary else HEALING
        roll = DamageRoll(gain.dice, None)
        rolls = (_with_modifier(roll, modifier or 0) if gain.add_modifier else roll,)
        upcast = (gain.upcast,) if spell.level > 0 and gain.upcast else ()
        if gain.add_modifier and modifier is None:
            notes.append(
                f"Add the spellcasting ability modifier to the {amount_kind.lower()}."
            )
        if gain.is_the_casters:
            notes.append("They're the caster's: pick the caster as the target.")
    elif rolls and not upcast and any(map(_ANY_UPCAST.search, text.upgrades)):
        notes.append("Upcasting won't change the damage: work it out if you do.")
    if spell.level and has_slots(who) and slot is None:
        notes.append(f"No slot of level {spell.level} or higher left.")
    # Like Cast Spell's badge, when there's nothing else to show it happened:
    # not for damage (typed in by hand, it would leave the badge behind), nor
    # healing, nor a spell that's over as soon as it's cast. A described
    # spell says whether it has a badge instead.
    badge = not (
        rolls or text.states_damage or text.heals or spell.duration_seconds == 0
    )
    condition = text.condition or (spell.name if badge else "")
    return EffectOption(
        name=spell.name,
        kind=SPELL,
        summary="  ".join(_roll_summary(text, dc, bonus, rolls, amount_kind)),
        tooltip=spell.description,
        note=" ".join(notes),
        roll=ATTACK_ROLL if text.is_attack else SAVING_THROW,
        ability=text.ability,
        dc=dc,
        bonus=bonus,
        half_on_save=text.half_on_save,
        repeat_save=text.repeat_save,
        rolls=rolls,
        condition=condition,
        duration_seconds=spell.duration_seconds,
        until=text.until if text.condition else None,
        slot_level=slot,
        action_cost=casting_time_cost(spell),
        concentration=spell.is_concentration,
        upcast=upcast,
        amount_kind=amount_kind,
        spell_level=spell.level,
        spell_name=spell.name,
        counts_uses=True,
    )


def _monster_action_condition(
    action: MonsterAction,
) -> tuple[str, tuple[str, str] | None]:
    """The condition its Hit: or Failure: text gives, and how long for if
    that's a turn. A hit's text stops where a save it forces begins: that
    save's condition is only for who fails it, so the GM applies it apart.
    Neither is what "Failure or Success:" gives, whatever the roll: that's in
    the rider."""
    label = "Hit:" if action.to_hit is not None else "Failure:"
    start = action.description.find(label)
    if start < 0:
        return "", None
    text = action.description[start + len(label) :]
    text = re.split(r"\b(?:Success|Failure or Success|Hit or Miss):", text)[0]
    if action.to_hit is not None:
        text = _HIT_ENDS.split(text)[0]
    for rider in action.riders:
        # Its own row gives it, as the attack hits (_rider_options).
        text = text.replace(rider.text, "")
    condition, _, until, _ = _inflicted_condition(text)
    return condition, until


def _monster_action_notes(action: MonsterAction) -> list[str]:
    notes = []
    if action.to_hit is not None and action.save_ability is not None:
        notes.append(f"It has a {action.save_ability} save too: apply it apart.")
    elif action.save_ability is not None and action.save_dc is None:
        notes.append("The DC isn't known: set it.")
    if any(roll.damage_type is None for roll in action.damage):
        notes.append("It chooses a damage type: give one.")
    if action.rider:
        notes.append(f"Also: {action.rider}")
    return notes


def _availability(char: dict, action: MonsterAction, name: str) -> tuple[str, bool]:
    """(the row's name, whether it's greyed out): spent, or a legendary
    action costing more than are left."""
    spent = action.is_limited and is_spent(char, action)
    left = legendary_actions_left(char)
    if spent:
        return f"{name} (spent)", True
    if action.legendary_cost > left:
        return f"{name} ({left} left)", True
    return name, False


def monster_action_options(
    char: dict, action: MonsterAction, by_name: dict[str, MonsterAction]
) -> list[EffectOption]:
    """The picker's rows for one of char's stat-block abilities: one per
    combat effect written on it; else the spells it casts ("The lich casts
    Fear", "uses Spellcasting to cast Mind Spike (level 3 version)"); else
    the action it's another way to use ("makes one Rend attack", "uses
    Dreadful Glare"), from `by_name` (char's actions by name, recharge and
    cost left off); else what its own text says. Each spends this ability:
    its recharge, its uses per day or its legendary actions."""
    if action.effects:
        return [_described_monster_option(char, action, e) for e in action.effects]
    spells = _spells_it_casts(action)
    if spells:
        return [
            option
            for cast in spells
            for option in _monster_spell_options(char, action, *cast)
        ]
    other = _action_it_uses(action, by_name)
    if other is not None:
        return [_as_other_action(char, action, other)]
    return [_monster_action_option(char, action), *_rider_options(char, action)]


def _rider_options(char: dict, action: MonsterAction) -> list[EffectOption]:
    """A row for each condition an attack's hit gives in a sentence of its
    own (monster_actions.hit_riders): "Tree Club: Prone", which the
    simulator applies as Tree Club hits (Notes/combat-effects-plan.md, 6.4),
    and asks first about what it can't check: a size it doesn't know, a
    `when`, which attack hit. It spends nothing: the attack did."""
    base = _NAME_ALONE.sub("", action.name)
    options = []
    for rider in action.riders:
        first, *others = rider.conditions
        until = None
        if rider.until is not None:
            until = (TurnEdge(rider.until[0]), TurnOf(rider.until[1]))
        effect = CombatEffect(
            name=f"{base}: {CONDITION_JOINER.join(rider.conditions)}",
            conditions=(
                CombatCondition(first, until=until),
                *(CombatCondition(c) for c in others),
            ),
            spends_use=False,
            notes=(rider.note,) if rider.note else (),
            trigger=CombatTrigger(
                TriggerEvent.HIT,
                optional=False,
                after=action.name,
                largest_target=rider.largest_target,
                once_per_turn=rider.once_per_turn,
                when=rider.when,
            ),
        )
        option = _described_option(
            char,
            effect,
            name=action.name,
            kind=MONSTER_ACTION,
            tooltip=action.description,
        )
        # Its row says when, not again what: "Tree Club: Prone  on a hit,
        # Large or smaller".
        when = ["on a hit"]
        if rider.largest_target is not None:
            when.append(f"{rider.largest_target.value} or smaller")
        if rider.once_per_turn:
            when.append("once per turn")
        if rider.when:
            when.append(f"if {rider.when}")
        options.append(
            replace(
                option,
                summary=", ".join(when),
                until=rider.until,
                is_described=False,
            )
        )
    return options


def _described_monster_option(
    char: dict, action: MonsterAction, effect: CombatEffect
) -> EffectOption:
    """What one use written on a monster's ability fills in. Its action is the
    stat block's section, which the turn column spends, so none is filled in
    unless the effect says so."""
    row_name, unavailable = _availability(char, action, effect.name or action.name)
    return _described_option(
        char,
        effect,
        name=action.name,
        kind=MONSTER_ACTION,
        tooltip=action.description,
        row_name=row_name,
        monster_action=action,
        is_unavailable=unavailable,
    )


# "The lich casts Fear, using ...", "uses Spellcasting to cast Mind Spike
# (level 3 version).", "casts Cure Wounds (level 2 version), Lesser
# Restoration, or Remove Curse, using ...", "casts Counterspell or Shield in
# response to ...". The names are checked against the spells there are.
_CASTS = re.compile(
    r"\bcasts? (?P<spells>[A-Z].*?)"
    r"(?=, using|\.(?:\s|$)| in response| on that| on the| on a| at will)"
)
_LIST_ITEM = re.compile(r",? or |, ")
_AT_LEVEL = re.compile(r"(?P<name>.+?)(?: \(level (?P<level>\d+) version\))?")


def _spells_it_casts(
    action: MonsterAction,
) -> list[tuple[object, int | None, str]]:
    """(spell, the level it's cast at if the text says, how often: "2/Day
    each" or "") for each spell the ability's text casts: named ("casts
    Fear"), or in a Spellcasting list ("At will: Thaumaturgy. 2/Day each: Hold
    Person, Silence.")."""
    found = []
    for match in _CASTS.finditer(action.description):
        for spell, level in _named_spells(match["spells"]):
            found.append((spell, level, ""))
    following = _FOLLOWING.search(action.description)
    if following is not None:
        for match in _SPELL_LIST.finditer(action.description, following.end()):
            for spell, level in _named_spells(match["spells"]):
                found.append((spell, level, match["often"]))
    return found


def _named_spells(text: str) -> list[tuple[object, int | None]]:
    """The spells "A (level 2 version), B, or C" names that there are."""
    named = []
    for item in _LIST_ITEM.split(text):
        match = _AT_LEVEL.fullmatch(item.strip())
        if match is None:
            continue
        spell = _spell_named(match["name"])
        if spell is not None:
            named.append((spell, int(match["level"]) if match["level"] else None))
    return named


# "casts one of the following spells, ... (spell save DC 12):" and its lists.
_FOLLOWING = re.compile(r"following spells[^:]*:")
_SPELL_LIST = re.compile(r"(?P<often>At will|\d+/Day(?: each)?): (?P<spells>[^.]+)")


def _spell_named(name: str):
    return _spells_by_name().get(name.lower())


@lru_cache(maxsize=1)
def _spells_by_name() -> dict:
    return {spell.name.lower(): spell for spell in SpellFactory.all_spells()}


def _monster_spell_options(
    char: dict, action: MonsterAction, spell, level: int | None, often: str = ""
) -> list[EffectOption]:
    """Casting `spell` as `action`, a row per way to cast it, at `level` if
    it's a higher one, with char's spell save DC and attack bonus. It spends
    the action, not a slot or the spell's casting time: the turn column counts
    the stat block's section. Its condition is the spell's badge. `often` is
    how often its Spellcasting allows it ("2/Day each"), for the GM to keep
    count of."""
    options = spell_options(spell, char)
    several = len(_spells_it_casts(action)) > 1 or len(options) > 1
    return [
        _monster_spell_option(char, action, spell, option, level, often, several)
        for option in options
    ]


def _monster_spell_option(
    char: dict,
    action: MonsterAction,
    spell,
    option: EffectOption,
    level: int | None,
    often: str,
    several: bool,
) -> EffectOption:
    """One row of _monster_spell_options."""
    rolls, upcast = option.rolls, option.upcast
    if level is not None and level > spell.level and upcast:
        rolls = tuple(
            with_dice(roll, dice, level - spell.level) if dice else roll
            for roll, dice in zip(rolls, upcast)
        )
    name = f"{action.name}: {option.name}" if several else action.name
    row_name, unavailable = _availability(char, action, name)
    at_level = f" at level {level}" if level and level > spell.level else ""
    how_often = f" ({often})" if often and often.lower() != "at will" else ""
    note = f"It casts {spell.name}{at_level}{how_often}." + (
        f" {option.note}" if option.note else ""
    )
    summary = option.summary
    if rolls != option.rolls:
        summary = summary.replace(damage_text(option.rolls), damage_text(rolls))
    levels_up = max((level or spell.level) - spell.level, 0)
    return replace(
        option,
        name=name,
        summary=summary,
        kind=MONSTER_ACTION,
        row_name=row_name,
        note=_without_slot_note(note),
        rolls=rolls,
        upcast=(),
        instances=option.instances_at(spell.level + levels_up),
        instances_upcast=0,
        slot_level=None,
        action_cost=None,
        spell_name=spell.name,
        monster_action=action,
        is_unavailable=unavailable,
    )


def _without_slot_note(note: str) -> str:
    """A monster's spell spends no slot of the caster's."""
    return re.sub(r"\s*No slot of level \d+ or higher left\.", "", note).strip()


# "The dragon makes one Rend attack.", "The mummy uses Dreadful Glare."
_MAKES_ONE = re.compile(r"\bmakes one (?P<name>[A-Z][\w'’ -]*?) attack\b")
_USES = re.compile(r"\buses (?P<name>[A-Z][\w'’ -]*?)(?=[.,]| to | on )")
_NAME_ALONE = re.compile(r"\s*\(.*")


def _action_it_uses(
    action: MonsterAction, by_name: dict[str, MonsterAction]
) -> MonsterAction | None:
    """The other action this one makes or uses, when its whole point is that
    (Pounce, Tail Swipe, a lich's Glare), and char has it."""
    if action.is_rollable or action.save_ability is not None:
        return None
    for pattern in (_MAKES_ONE, _USES):
        match = pattern.search(action.description)
        if match is None:
            continue
        other = by_name.get(match["name"].lower())
        if other is not None and other.name != action.name:
            return other
    return None


def _as_other_action(
    char: dict, action: MonsterAction, other: MonsterAction
) -> EffectOption:
    """What `other` fills in, used as `action`, which is what's spent."""
    used = _monster_action_option(char, other)
    row_name, unavailable = _availability(char, action, action.name)
    base = _NAME_ALONE.sub("", other.name)
    verb = "makes one" if _MAKES_ONE.search(action.description) else "uses"
    rest = f"{base} attack" if verb == "makes one" else base
    note = f"It {verb} {rest}." + (f" {used.note}" if used.note else "")
    if _MOVES.search(action.description):
        note += " It moves first: move it by hand."
    return replace(
        used,
        name=action.name,
        row_name=row_name,
        note=note,
        tooltip=action.description,
        monster_action=action,
        is_unavailable=unavailable,
    )


_MOVES = re.compile(r"\bmoves up to\b")


def _monster_action_option(char: dict, action: MonsterAction) -> EffectOption:
    """What an ability's own text fills in: its attack or save and damage, the
    condition its hit or failed save gives, or the Hit Points it gives."""
    row_name, unavailable = _availability(char, action, action.name)
    is_save = action.to_hit is None and action.save_ability is not None
    ability = _ABILITY_SHORT_NAMES.get(action.save_ability or "")
    condition, until = _monster_action_condition(action)
    notes = _monster_action_notes(action)
    rolls, amount_kind = action.damage, DAMAGE_AMOUNT
    gain = None if action.is_rollable or is_save else _read_gain(action.description, ())
    if gain is not None:
        amount_kind = TEMP_HP if gain.temporary else HEALING
        rolls = (DamageRoll(gain.dice, None),)
    if action.name.startswith("Multiattack"):
        notes.insert(0, "Pick each of its attacks in turn.")
    summary = action.summary
    if gain is not None:
        summary = amount_text(gain.dice, amount_kind)
    return EffectOption(
        name=action.name,
        kind=MONSTER_ACTION,
        row_name=row_name,
        summary=summary,
        tooltip=action.description,
        note=" ".join(notes),
        roll=ATTACK_ROLL if action.to_hit is not None else SAVING_THROW,
        ability=ability if is_save else None,
        dc=action.save_dc if is_save else None,
        bonus=action.to_hit,
        half_on_save=is_save and action.half_on_save,
        repeat_save=is_save and bool(_REPEATS_THE_SAVE.search(action.description)),
        rolls=rolls,
        amount_kind=amount_kind,
        condition=condition,
        until=until,
        monster_action=action,
        is_unavailable=unavailable,
    )


def _weapon_rolls(weapon, sheet) -> tuple[tuple[DamageRoll, ...], list[str]]:
    """What a hit deals, as the sheet's weapon card has it, and a note for extra
    damage it doesn't always deal. A die of 1 is an Unarmed Strike's flat 1,
    which a critical hit doesn't double."""
    die = weapon.get_damage_roll(sheet).value
    bonus = weapon.calculate_damage_bonus_int(sheet)
    if die == _FLAT_ONE:
        dice = str(max(1 + bonus, 0))
    elif bonus:
        dice = f"{die} {'+' if bonus > 0 else '-'} {abs(bonus)}"
    else:
        dice = die
    rolls = [DamageRoll(dice, weapon.damage_type.value)]
    notes = []
    for extra in weapon.extra_damage:
        if _NOT_ALWAYS.search(extra.note or ""):
            notes.append(f"Not counted: {extra.format_damage()} ({extra.note}).")
        else:
            rolls.append(DamageRoll(extra.damage_roll.value, extra.damage_type.value))
    return tuple(rolls), notes


def _weapon_option(char: dict, weapon, sheet) -> EffectOption:
    """An attack with the weapon. It costs the Action only if char hasn't used
    one this turn: Extra Attack makes more attacks with the same Action, and an
    Opportunity Attack is a Reaction, for the GM to choose."""
    bonus = weapon.calculate_total_attack_roll_bonus_int(sheet)
    rolls, notes = _weapon_rolls(weapon, sheet)
    acted = char.get("action_uses", {}).get("Action", 0) > 0
    return EffectOption(
        name=weapon.name,
        kind=WEAPON,
        summary=f"{bonus:+d}  {damage_text(rolls)}",
        tooltip=weapon.description_text,
        note=" ".join(notes),
        roll=ATTACK_ROLL,
        bonus=bonus,
        rolls=rolls,
        action_cost=None if acted else "Action",
        # "A weapon attack is an attack roll made with a weapon" (Rules
        # Glossary); an Unarmed Strike isn't one.
        weapon_attack=not getattr(weapon, "is_unarmed_strike", False),
    )


def feature_uses(char: dict, feature, sheet) -> tuple[int, int] | None:
    """(uses left, uses at most) of a limited feature, counted as
    FeaturesMixin._feature_uses_text counts them."""
    if feature.uses is None:
        return None
    most = feature.number_of_uses(sheet) if sheet is not None else feature.uses.max_uses
    used = char.get("feature_uses_used", {}).get(feature.name, 0)
    return max(most - used, 0), most


def _feature_duration(feature) -> int | None:
    seconds = feature.activation.duration_to_seconds() if feature.activation else None
    return seconds if isinstance(seconds, int) else None


def _feature_option(char: dict, feature) -> EffectOption:
    """What using a feature fills in. Most have no numbers to find, so it's
    their name and what they cost."""
    sheet = char.get("_stat_block")
    description = (feature.get_description(sheet) if sheet is not None else None) or ""
    text = read_effect_text(description)
    dc = feature.calculate_dc(sheet) if sheet is not None else None
    if dc is None and (text.ability is not None or "spell save DC" in description):
        dc = known_save_dc(char)
    bonus = known_spell_attack_bonus(char) if text.is_attack else None
    uses = feature_uses(char, feature, sheet)
    notes = list(text.notes) + _unknown_number_notes(text, dc, bonus)
    parts = _roll_summary(text, dc, bonus, text.damage)
    if uses is not None:
        parts.insert(0, f"{uses[0]}/{uses[1]}")
        if uses[0] == 0:
            notes.append("No uses left.")
    return EffectOption(
        name=feature.name,
        kind=FEATURE,
        summary="  ".join(parts),
        tooltip=description,
        note=" ".join(notes),
        roll=ATTACK_ROLL if text.is_attack else SAVING_THROW,
        ability=text.ability,
        dc=dc,
        bonus=bonus,
        half_on_save=text.half_on_save,
        repeat_save=text.repeat_save,
        rolls=text.damage,
        condition=text.condition,
        duration_seconds=_feature_duration(feature),
        until=text.until if text.condition else None,
        action_cost=feature_action_cost(feature),
        counts_uses=feature.uses is not None,
    )


def feature_options(char: dict, feature) -> list[EffectOption]:
    """The picker's rows for a feature: one per use its combat_effects()
    describes, or, for one it doesn't describe, what its text says. A passive
    feature it doesn't describe only changes the stat block, so it has none."""
    sheet = char.get("_stat_block")
    effects = feature.combat_effects(sheet) if sheet is not None else None
    if effects is None:
        rows = [] if feature.passive else [_feature_option(char, feature)]
    else:
        rows = [_described_feature_option(char, feature, e) for e in effects]
    return rows + _extension_options(char, feature)


def _extension_options(char: dict, parent) -> list[EffectOption]:
    """The rows of the features granted as extensions of `parent`: more ways
    to use it (Radiance of the Dawn, a use of Channel Divinity). One that
    only changes the parent's own effect (Combat Inspiration) says so with
    adjust_combat_effect and has none. An extension not described has none
    either: they never had rows of their own."""
    sheet = char.get("_stat_block")
    if sheet is None:
        return []
    rows = []
    for extension in sheet.extensions_of(parent):
        for effect in extension.combat_effects(sheet) or []:
            rows.append(_described_feature_option(char, extension, effect, parent))
        rows += _extension_options(char, extension)
    return rows


def _described_feature_option(
    char: dict, feature, effect: CombatEffect, parent=None
) -> EffectOption:
    """What one use a feature describes fills in. What it leaves unset is the
    feature's own: its DC, action, duration and uses, or for an extension
    without them, its parent's (Radiance of the Dawn spends a use of Channel
    Divinity). A use that casts a spell takes that spell's effect under its
    own, and where the feature doesn't say them, the spell's casting time
    and duration; and its Concentration (Wild Companion's Magic action casts
    Find Familiar, whose casting time is an hour)."""
    sheet = char.get("_stat_block")
    description = (feature.get_description(sheet) if sheet is not None else None) or ""
    owner = parent if parent is not None and feature.uses is None else feature
    duration = _feature_duration(feature)
    action_cost = feature_action_cost(feature)
    dc = feature.calculate_dc(sheet) if sheet is not None else None
    if parent is not None:
        duration = duration if duration is not None else _feature_duration(parent)
        action_cost = action_cost or feature_action_cost(parent)
        if dc is None and sheet is not None:
            dc = parent.calculate_dc(sheet)
    concentration = False
    spell = _spell_named(effect.spell) if effect.spell else None
    if spell is not None:
        effect = _casting(spell, effect)
        if duration is None:
            duration = spell.duration_seconds
        if action_cost is None:
            action_cost = casting_time_cost(spell)
        concentration = spell.is_concentration
    effect = _adjusted(char, feature.name, effect)
    counts_uses = owner.uses is not None and effect.spends_use
    uses = feature_uses(char, owner, sheet) if counts_uses else None
    lead, lead_notes = [], []
    if uses is not None:
        lead.append(f"{uses[0]}/{uses[1]}")
        if uses[0] == 0:
            lead_notes.append("No uses left.")
    return _described_option(
        char,
        effect,
        name=feature.name,
        kind=FEATURE,
        tooltip=description,
        default_dc=dc,
        modifier=_casting_modifier(char),
        duration_seconds=duration,
        action_cost=action_cost,
        concentration=concentration,
        lead=lead,
        lead_notes=lead_notes,
        counts_uses=counts_uses,
        feature_name=owner.name,
    )


def _casting(spell, effect: CombatEffect) -> CombatEffect:
    """A use that casts `spell`: the spell's own (first) combat effect, with
    whatever `effect` sets instead, and both their notes, its own first.
    Without the spell described, just `effect`."""
    described = spell.combat_effects()
    if not described:
        return effect
    base = described[0]
    changes = {
        field.name: getattr(effect, field.name)
        for field in fields(CombatEffect)
        if getattr(effect, field.name) != field.default
    }
    changes["notes"] = effect.notes + base.notes
    return replace(base, **changes)


def _adjusted(char: dict, source: str, effect: CombatEffect) -> CombatEffect:
    """`effect` of char's feature or spell named `source`, as char's
    features change it (Feature.adjust_combat_effect)."""
    sheet = char.get("_stat_block")
    if sheet is None:
        return effect
    for feature in sheet.iter_features_with_extensions():
        effect = feature.adjust_combat_effect(sheet, source, effect)
    return effect


def _described_option(
    char: dict,
    effect: CombatEffect,
    *,
    name: str,
    kind: str,
    tooltip: str,
    default_dc: int | None = None,
    default_bonus: int | None = None,
    modifier: int | None = None,
    level: int = 0,
    duration_seconds: int | None = None,
    action_cost: str | None = None,
    concentration: bool = False,
    spell_name: str = "",
    lead: Iterable[str] = (),
    lead_notes: Iterable[str] = (),
    **fields,
) -> EffectOption:
    """What a CombatEffect fills in, for a spell, a feature's use or a
    monster's ability: exactly what it says, and for what it leaves unset, its
    source's defaults (`default_dc`, `default_bonus`, `duration_seconds`,
    `action_cost`, `concentration`), then char's own known DC and spell
    attack bonus. `modifier` is the spellcasting ability modifier an amount
    adds (None: not known), `level` the spell's (0: nothing upcasts). `lead`
    goes before its numbers in the row (a feature's uses), `lead_notes` after
    its own notes, and `fields` straight onto the EffectOption."""
    is_save = effect.roll == "save"
    is_attack = effect.roll == "attack"
    ability = effect.save_ability.short_name if effect.save_ability else None
    dc = None
    if is_save:
        dc = effect.dc if effect.dc is not None else default_dc
        dc = dc if dc is not None else known_save_dc(char)
    bonus = None
    if is_attack:
        bonus = (
            effect.attack_bonus if effect.attack_bonus is not None else default_bonus
        )
        bonus = bonus if bonus is not None else known_spell_attack_bonus(char)
    char_level = _character_level(char)
    rolls, upcast, amount_kind, amount_notes = _effect_amounts(
        effect, level, char_level, modifier
    )
    conditions = effect.conditions
    first = conditions[0] if conditions else None
    shown_name = effect.name or name
    text = EffectText(
        ability=ability,
        is_attack=is_attack,
        half_on_save=effect.half_on_success,
        # A badge of its own name says nothing more in its row.
        condition=CONDITION_JOINER.join(
            c.name for c in conditions if c.name not in (shown_name, name)
        ),
    )
    notes = list(effect.notes)
    for damage in effect.damage:
        if damage.damage_type is None:
            choices = ", ".join(choice.value for choice in damage.choices)
            notes.append(f"Its damage is of a type to choose ({choices}): give one.")
    notes += _unknown_number_notes(text, dc, bonus)
    notes += amount_notes
    notes += _condition_notes(conditions)
    notes += lead_notes
    parts = [*lead, *_roll_summary(text, dc, bonus, rolls, amount_kind)]
    instances = effect.instances
    count = instances.at(char_level, 0) if instances is not None else 1
    if count > 1:
        noun = instances.noun if instances is not None else ""
        parts.insert(len(list(lead)), f"{count} {noun}s" if noun else f"{count}×")
    if first is not None and first.duration_seconds is not None:
        duration_seconds = first.duration_seconds
    if effect.action_type is not None:
        action_cost = FEATURE_ACTION_COSTS[effect.action_type.value]
    return EffectOption(
        name=shown_name,
        kind=kind,
        summary="  ".join(parts),
        tooltip=tooltip,
        note=" ".join(notes),
        roll=ATTACK_ROLL if is_attack else SAVING_THROW,
        ability=ability,
        dc=dc,
        bonus=bonus,
        half_on_save=effect.half_on_success,
        repeat_save=effect.repeat_save,
        rolls=rolls,
        condition=CONDITION_JOINER.join(c.name for c in conditions),
        duration_seconds=duration_seconds,
        until=first.until if first is not None else None,
        action_cost=action_cost,
        concentration=effect.concentration or concentration,
        spell_name=spell_name or effect.spell or "",
        upcast=upcast,
        amount_kind=amount_kind,
        is_described=True,
        instances=count,
        instances_upcast=(
            instances.upcast if instances is not None and level > 0 else 0
        ),
        badge_modifiers=tuple((c.name, c.modifiers) for c in conditions if c.modifiers),
        trigger=effect.trigger,
        **fields,
    )


def _condition_notes(conditions: tuple[CombatCondition, ...]) -> list[str]:
    """What the form can't hold about several conditions: it gives them one
    duration, the first's."""
    first, *others = conditions or (None,)
    if first is None:
        return []
    differ = [
        c.name
        for c in others
        if (c.until, c.duration_seconds) != (first.until, first.duration_seconds)
    ]
    if not differ:
        return []
    return [
        f"{', '.join(differ)} lasts another time than {first.name}: set it by hand."
    ]


def _effect_amounts(
    effect: CombatEffect, level: int, char_level: int, modifier: int | None
) -> tuple[tuple[DamageRoll, ...], tuple[str, ...], str, list[str]]:
    """What goes in the form's amount box for a described effect: its damage,
    or else its healing or Temporary Hit Points (an amount of "" is the
    user's to type, as Lay on Hands' pool), at the user's character level
    (cantrip dice) and with `modifier` added where it says so. Also what
    each part gains per slot level above `level` (() when nothing does, or
    nothing upcasts), the amount's kind, and a note if the modifier it adds
    isn't known."""
    notes = []
    always = [damage for damage in effect.damage if not damage.when]
    for damage in effect.damage:
        if damage.when:
            notes.append(_conditional_damage_note(damage, level, char_level, modifier))
    if always:
        rolls = []
        for damage in always:
            rolls.append(_damage_roll(damage, char_level, modifier))
        if any(damage.add_modifier for damage in always) and modifier is None:
            notes.append("Add the spellcasting ability modifier to the damage.")
        upcast = tuple(damage.upcast for damage in always)
        return (
            tuple(rolls),
            upcast if level > 0 and any(upcast) else (),
            DAMAGE_AMOUNT,
            notes,
        )
    for points, kind in ((effect.healing, HEALING), (effect.temp_hp, TEMP_HP)):
        if points is None:
            continue
        if not points.dice and not (points.add_modifier and modifier is not None):
            if points.add_modifier:
                notes.append(
                    f"Type in the spellcasting ability modifier: it's the whole"
                    f" {kind.lower()}."
                )
            return (), (), kind, notes
        if not points.dice:
            # The modifier alone (Heroism).
            upcast = (points.upcast,) if level > 0 and points.upcast else ()
            return (DamageRoll(str(max(modifier or 0, 0)), None),), upcast, kind, notes
        roll = DamageRoll(points.dice, None)
        if points.add_modifier:
            roll = _with_modifier(roll, modifier or 0)
            if modifier is None:
                notes.append(
                    f"Add the spellcasting ability modifier to the {kind.lower()}."
                )
        upcast = (points.upcast,) if level > 0 and points.upcast else ()
        return (roll,), upcast, kind, notes
    return (), (), DAMAGE_AMOUNT, notes


def _damage_roll(
    damage: CombatDamage, char_level: int, modifier: int | None
) -> DamageRoll:
    """A part of described damage, at the user's character level, with the
    modifier added if it says so."""
    dice = _at_cantrip_level(damage.dice, damage.cantrip, char_level)
    damage_type = damage.damage_type.value if damage.damage_type else None
    roll = DamageRoll(dice, damage_type)
    return _with_modifier(roll, modifier or 0) if damage.add_modifier else roll


def _conditional_damage_note(
    damage: CombatDamage, level: int, char_level: int, modifier: int | None
) -> str:
    """Damage only some targets take, which the GM adds for those: "If the
    target is a Fiend or an Undead: 1d8 Radiant more (1d8 more per slot
    level above 1)." """
    roll = _damage_roll(damage, char_level, modifier)
    what = damage_text([roll]) or roll.dice
    if roll.damage_type is None:
        what += f" ({', '.join(choice.value for choice in damage.choices)})"
    more = ""
    if level > 0 and damage.upcast:
        more = f" ({damage.upcast} more per slot level above {level})"
    return f"If {damage.when}: {what} more{more}. Add it for those targets."


def effect_options(
    char: dict | None, all_spells: Iterable | None = None
) -> list[tuple[str, list[EffectOption]]]:
    """Everything char can use, as (category, options), in the order the
    picker shows them, empty categories left out. `all_spells` is every spell
    in the game, sorted, if the caller has them already."""
    who = char if char is not None else {}
    sheet = who.get("_stat_block")
    if all_spells is None:
        all_spells = sorted(SpellFactory.all_spells(), key=lambda s: (s.level, s.name))
    own_spells = sorted(
        (who.get("_spell_objects") or {}).values(), key=lambda s: (s.level, s.name)
    )
    own_names = {spell.name for spell in own_spells}
    sections = monster_actions(who)
    # A trait is listed only when combat effects say what to apply: most just
    # are (Pack Tactics), but one like Divine Smite is used.
    described_traits = [
        parse_action(trait)
        for trait in who.get("traits") or []
        if ability_effects(trait)
    ]
    if described_traits:
        sections.append((TRAITS, described_traits))
    by_name = {
        _NAME_ALONE.sub("", action.name).lower(): action
        for _, actions in sections
        for action in actions
    }
    categories = [
        (
            title,
            [
                o
                for action in actions
                for o in monster_action_options(who, action, by_name)
            ],
        )
        for title, actions in sections
    ]
    weapons = who.get("_weapons_objects") or []
    features = who.get("_feature_objects") or []
    categories += [
        (ATTACKS, [_weapon_option(who, weapon, sheet) for weapon in weapons]),
        (
            f"{who.get('name')}'s Spells",
            [o for s in own_spells for o in spell_options(s, who)],
        ),
        (FEATURES, [o for feature in features for o in feature_options(who, feature)]),
        # A caster's own spell is listed even with nothing to apply: picking
        # it still spends the slot and the action, and holds Concentration.
        (
            ALL_SPELLS,
            [
                o
                for s in all_spells
                if s.name not in own_names and is_applicable(s)
                for o in spell_options(s, who)
            ],
        ),
    ]
    return [(title, options) for title, options in categories if options]


def trigger_option(
    char: dict | None, source: str | None, name: str
) -> EffectOption | None:
    """The picker row called `name` for char, among the rows of `source` (a
    spell, or one of char's features): the effect a badge's trigger uses
    (Heroism's "Heroism: Temporary Hit Points"). With no source known, or
    none of that name, every row char has is looked through."""
    who = char if char is not None else {}
    options: list[EffectOption] = []
    if source:
        own = {s.name: s for s in (who.get("_spell_objects") or {}).values()}
        spell = own.get(source) or _spell_named(source)
        if spell is not None:
            options = spell_options(spell, who)
        else:
            options = [
                option
                for feature in who.get("_feature_objects") or []
                if feature.name == source
                for option in feature_options(who, feature)
            ]
    found = next((o for o in options if o.name == name), None)
    if found is not None:
        return found
    return next(
        (o for _, rows in effect_options(who) for o in rows if o.name == name), None
    )


def triggered_rows(char: dict) -> list[TriggerRow]:
    """char's own picker rows that have a trigger (Hill's Tumble), for
    Combat/Effects/triggers.py: from its stat-block actions and traits, its
    weapons, its own spells and its features with their extensions, never
    "All spells". Each is built as the picker builds it, for char as it is now
    (a Wild Shape form's actions, uses spent), so nothing is cached."""
    rows = []
    for _, options in effect_options(char, all_spells=()):
        for option in options:
            if option.trigger is None:
                continue
            uses = _trigger_row_uses(char, option)
            rows.append(
                TriggerRow(
                    name=option.name,
                    trigger=option.trigger,
                    conditions=tuple(condition_names(option.condition)),
                    what=_trigger_row_what(option),
                    uses=uses,
                    costs=option.counts_uses or uses is not None,
                    option=option,
                )
            )
    return rows


def _trigger_row_what(option: EffectOption) -> str:
    """What a triggered row does, for its line in the pop-up: "Prone",
    "1d10 Fire", "1d6 Cold, Frost's Chill"."""
    parts = [option.damage] if option.damage else []
    parts += condition_names(option.condition)
    return ", ".join(parts)


def _trigger_row_uses(char: dict, option: EffectOption) -> tuple[int, int] | None:
    """(uses left, uses at most) of what a triggered row spends: a feature's
    uses, or a monster's limited action (none left once it's spent). None
    when it spends nothing counted."""
    if option.kind == FEATURE and option.counts_uses:
        sheet = char.get("_stat_block")
        name = option.feature_name or option.name
        features = list(char.get("_feature_objects") or [])
        if sheet is not None:
            features += list(sheet.iter_features_with_extensions())
        feature = next((f for f in features if f.name == name), None)
        return feature_uses(char, feature, sheet) if feature is not None else None
    action = option.monster_action
    if action is not None and action.is_limited:
        return (0, 1) if is_spent(char, action) else (1, 1)
    return None
