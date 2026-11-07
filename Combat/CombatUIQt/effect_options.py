"""What the Custom Effect dialog's picker offers: everything a combatant can use
(stat-block actions, weapons, spells, features), each as an EffectOption saying
what it fills in on the form. Nothing here is rolled or spent, and nothing
imports Qt, so it can be tested on plain dicts.

A spell with an entry in its source's mechanics file
(CharacterContent/Spells/spells_<source>_mechanics.json) fills the form from
that checked data. Other spells and features have no structured data for this,
so their rules text is read, as strictly as it can be: a form the GM can
correct beats a wrong number they don't notice, so what's unclear is left out
and said in the option's note."""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache

from CharacterContent.Spells.SpellFactory import SpellFactory
from CharacterContent.Spells.SpellFactory.Mechanics import SpellMechanics
from Core.Definitions import Condition
from Model.Content.CombatEffect import CombatEffect

from .monster_actions import (
    DAMAGE,
    DAMAGE_TYPE_NAMES,
    DIE,
    JOINED,
    DamageRoll,
    MonsterAction,
    is_spent,
    legendary_actions_left,
    monster_actions,
    tidy_dice,
)
from .saves import (
    ABILITIES,
    ATTACK_ROLL,
    FEATURE,
    MONSTER_ACTION,
    SAVING_THROW,
    SPELL,
    WEAPON,
    EffectOption,
    damage_text,
    known_save_dc,
    known_spell_attack_bonus,
)

# EffectOption, what this module makes, is in saves.py beside CustomEffect,
# which holds the one picked.

ATTACKS = "Attacks"
FEATURES = "Features"
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
# Where a monster's hit stops and a save it forces begins.
_HIT_ENDS = re.compile(r"\b\w+ Saving Throw:|\bFailure:")
_FLAT_ONE = "1d1"  # how a weapon writes an Unarmed Strike's damage
# What an ExtraDamage's note says when the weapon doesn't always deal it.
_NOT_ALWAYS = re.compile(r"\b(?:activate|chosen|when|while|if|only)\b", re.IGNORECASE)


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
    # The upcasting and cantrip paragraphs, for working out higher levels.
    upgrades: tuple[str, ...] = ()


def _curated_text(mechanics: SpellMechanics) -> EffectText:
    """A spell's checked mechanics as what its text would say, for what
    spell_option works out the same way either way. Its notes are the
    entry's own, and what the form can't hold."""
    save = mechanics.save
    notes = list(mechanics.notes)
    for damage in mechanics.damage:
        if damage.damage_type is None:
            choices = ", ".join(damage.choices)
            notes.append(f"Its damage is of a type to choose ({choices}): give one.")
    condition = mechanics.condition
    if condition is not None and condition.alternatives:
        others = " or ".join(condition.alternatives)
        notes.append(f"The condition can be {others} instead.")
    return EffectText(
        ability=save.ability if save is not None else None,
        is_attack=mechanics.roll == "attack",
        half_on_save=save is not None and save.half_on_success,
        repeat_save=save is not None and save.repeat,
        condition=condition.name if condition is not None else "",
        notes=tuple(notes),
        adds_modifier=any(damage.add_modifier for damage in mechanics.damage),
        states_damage=bool(mechanics.damage),
        heals=mechanics.heal is not None,
        until=condition.until if condition is not None else None,
    )


def _at_cantrip_level(dice: str, steps: tuple[tuple[int, str], ...], level: int) -> str:
    """Curated cantrip dice at a character's level: its first die swapped for
    the last step reached."""
    reached = [step for at, step in steps if at <= level]
    return DIE.sub(reached[-1], dice, count=1) if reached else dice


def _curated_rolls(
    mechanics: SpellMechanics, level: int, char_level: int, modifier: int | None
) -> tuple[tuple[DamageRoll, ...], tuple[str, ...]]:
    """The damage a curated spell deals for a caster of char_level, with the
    modifier added to the parts that add it, and what each part gains per
    slot level above the spell's (() when nothing does)."""
    rolls = []
    for damage in mechanics.damage:
        dice = damage.dice
        if level == 0:
            dice = _at_cantrip_level(dice, damage.cantrip, char_level)
        roll = DamageRoll(dice, damage.damage_type)
        rolls.append(
            _with_modifier(roll, modifier or 0) if damage.add_modifier else roll
        )
    upcast = tuple(damage.upcast for damage in mechanics.damage)
    return tuple(rolls), upcast if level > 0 and any(upcast) else ()


def _heal_note(mechanics: SpellMechanics, level: int, modifier: int | None) -> str:
    """What a curated spell heals, which the form has no box for."""
    heal = mechanics.heal
    if heal is None:
        return ""
    dice = heal.dice
    if heal.add_modifier and modifier is not None:
        dice = _with_modifier(DamageRoll(dice, None), modifier).dice
    amount = f"{dice} Hit Points"
    if heal.add_modifier and modifier is None:
        amount += " plus the spellcasting ability modifier"
    more = f" ({heal.upcast} more per slot level above {level})" if heal.upcast else ""
    return f"It heals {amount}{more}: apply that by hand."


def _with_modifier(roll: DamageRoll, modifier: int) -> DamageRoll:
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
    )


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


def _character_level(char: dict) -> int:
    return sum((char.get("class_levels") or {}).values())


def _roll_summary(
    text: EffectText, dc: int | None, bonus: int | None, rolls: Iterable[DamageRoll]
) -> list[str]:
    """The numbers a row shows for what `text` says."""
    parts = []
    if text.is_attack:
        parts.append("attack" if bonus is None else f"{bonus:+d}")
    elif text.ability is not None:
        parts.append(f"DC {dc or '?'} {text.ability}")
    damage = damage_text(rolls)
    if damage:
        parts.append(damage)
    if text.half_on_save:
        parts.append("half on save")
    if text.condition:
        parts.append(text.condition)
    return parts


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
    Only a curated entry says it hasn't (Alarm); unchecked spells are offered."""
    mechanics = spell.mechanics
    return mechanics is None or mechanics.applicable


def spell_option(spell, char: dict | None) -> EffectOption:
    """What casting `spell` fills in, for char (or nobody yet): from its
    checked mechanics if it has them, otherwise from its text. A monster's
    cantrip stays at its own level: it has no character level."""
    who = char if char is not None else {}
    mechanics: SpellMechanics | None = spell.mechanics
    if mechanics is not None:
        text = _curated_text(mechanics)
    else:
        text = read_effect_text(spell.description)
    dc = _spell_save_dc(spell, who) if text.ability is not None else None
    bonus = _spell_attack_bonus(spell, who) if text.is_attack else None
    heals_with_modifier = mechanics is not None and bool(
        mechanics.heal and mechanics.heal.add_modifier
    )
    modifier = (
        _spell_modifier(spell, who) if text.adds_modifier or heals_with_modifier else 0
    )
    upcast: tuple[str, ...] = ()
    if mechanics is not None:
        rolls, upcast = _curated_rolls(
            mechanics, spell.level, _character_level(who), modifier
        )
    else:
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
    if mechanics is not None:
        heal_note = _heal_note(mechanics, spell.level, modifier)
        if heal_note:
            notes.append(heal_note)
    elif rolls and not upcast and any(map(_ANY_UPCAST.search, text.upgrades)):
        notes.append("Upcasting won't change the damage: work it out if you do.")
    if spell.level and has_slots(who) and slot is None:
        notes.append(f"No slot of level {spell.level} or higher left.")
    # Like Cast Spell's badge, when there's nothing else to show it happened:
    # not for damage (typed in by hand, it would leave the badge behind), nor
    # healing, nor a spell that's over as soon as it's cast.
    badge = not (
        rolls or text.states_damage or text.heals or spell.duration_seconds == 0
    )
    if mechanics is not None and mechanics.badge is not None:
        badge = mechanics.badge
    condition = text.condition or (spell.name if badge else "")
    return EffectOption(
        name=spell.name,
        kind=SPELL,
        summary="  ".join(_roll_summary(text, dc, bonus, rolls)),
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
        spell_level=spell.level,
        is_curated=mechanics is not None,
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


def _monster_action_option(char: dict, action: MonsterAction) -> EffectOption:
    spent = action.is_limited and is_spent(char, action)
    left = legendary_actions_left(char)
    too_dear = action.legendary_cost > left
    row_name = action.name
    if spent:
        row_name = f"{action.name} (spent)"
    elif too_dear:
        row_name = f"{action.name} ({left} left)"
    is_save = action.to_hit is None and action.save_ability is not None
    ability = _ABILITY_SHORT_NAMES.get(action.save_ability or "")
    condition, until = _monster_action_condition(action)
    return EffectOption(
        name=action.name,
        kind=MONSTER_ACTION,
        row_name=row_name,
        summary=action.summary,
        tooltip=action.description,
        note=" ".join(_monster_action_notes(action)),
        roll=ATTACK_ROLL if action.to_hit is not None else SAVING_THROW,
        ability=ability if is_save else None,
        dc=action.save_dc if is_save else None,
        bonus=action.to_hit,
        half_on_save=is_save and action.half_on_save,
        repeat_save=is_save and bool(_REPEATS_THE_SAVE.search(action.description)),
        rolls=action.damage,
        condition=condition,
        until=until,
        monster_action=action,
        is_unavailable=spent or too_dear,
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
        return [] if feature.passive else [_feature_option(char, feature)]
    return [_described_feature_option(char, feature, effect) for effect in effects]


def _described_feature_option(
    char: dict, feature, effect: CombatEffect
) -> EffectOption:
    """What one use a feature describes fills in. What it leaves unset is the
    feature's own: its DC, action, duration and uses."""
    sheet = char.get("_stat_block")
    description = (feature.get_description(sheet) if sheet is not None else None) or ""
    is_save = effect.roll == "save"
    is_attack = effect.roll == "attack"
    ability = effect.save_ability.short_name if effect.save_ability else None
    dc = None
    if is_save:
        dc = effect.dc if effect.dc is not None else feature.calculate_dc(sheet)
        dc = dc if dc is not None else known_save_dc(char)
    bonus = None
    if is_attack:
        bonus = effect.attack_bonus
        bonus = bonus if bonus is not None else known_spell_attack_bonus(char)
    rolls = tuple(
        DamageRoll(
            damage.dice, damage.damage_type.value if damage.damage_type else None
        )
        for damage in effect.damage
    )
    condition = effect.condition
    text = EffectText(
        ability=ability,
        is_attack=is_attack,
        half_on_save=effect.half_on_success,
        condition=condition.name if condition is not None else "",
    )
    notes = list(effect.notes)
    for damage in effect.damage:
        if damage.damage_type is None:
            choices = ", ".join(choice.value for choice in damage.choices)
            notes.append(f"Its damage is of a type to choose ({choices}): give one.")
    notes += _unknown_number_notes(text, dc, bonus)
    counts_uses = feature.uses is not None and effect.spends_use
    uses = feature_uses(char, feature, sheet) if counts_uses else None
    parts = _roll_summary(text, dc, bonus, rolls)
    if uses is not None:
        parts.insert(0, f"{uses[0]}/{uses[1]}")
        if uses[0] == 0:
            notes.append("No uses left.")
    duration = _feature_duration(feature)
    if condition is not None and condition.duration_seconds is not None:
        duration = condition.duration_seconds
    action_cost = feature_action_cost(feature)
    if effect.action_type is not None:
        action_cost = FEATURE_ACTION_COSTS[effect.action_type.value]
    return EffectOption(
        name=effect.name or feature.name,
        kind=FEATURE,
        summary="  ".join(parts),
        tooltip=description,
        note=" ".join(notes),
        roll=ATTACK_ROLL if is_attack else SAVING_THROW,
        ability=ability,
        dc=dc,
        bonus=bonus,
        half_on_save=effect.half_on_success,
        repeat_save=effect.repeat_save,
        rolls=rolls,
        condition=condition.name if condition is not None else "",
        duration_seconds=duration,
        until=condition.until if condition is not None else None,
        action_cost=action_cost,
        concentration=effect.concentration,
        counts_uses=counts_uses,
        feature_name=feature.name,
        spell_name=effect.spell or "",
        is_curated=True,
    )


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
    categories = [
        (title, [_monster_action_option(who, action) for action in actions])
        for title, actions in monster_actions(who)
    ]
    weapons = who.get("_weapons_objects") or []
    features = who.get("_feature_objects") or []
    categories += [
        (ATTACKS, [_weapon_option(who, weapon, sheet) for weapon in weapons]),
        (f"{who.get('name')}'s Spells", [spell_option(s, who) for s in own_spells]),
        (FEATURES, [o for feature in features for o in feature_options(who, feature)]),
        # A caster's own spell is listed even with nothing to apply: picking
        # it still spends the slot and the action, and holds Concentration.
        (
            ALL_SPELLS,
            [
                spell_option(s, who)
                for s in all_spells
                if s.name not in own_names and is_applicable(s)
            ],
        ),
    ]
    return [(title, options) for title, options in categories if options]
