"""What the players know of the fight, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.4): who they can perceive, which log lines they may read, and what the
log and the Limited view have shown them of a monster (its maximum Hit
Points, its resistances and immunities), kept in its public keys so Undo and
a saved fight keep it too. The players' screen and the player link show it
(Combat/CombatUIQt/player_view.py, player_server.py)."""

from Combat.Definitions import CombatStatus
from Combat.Effects.modifiers import (
    hit_point_maximum,
    immune_to_condition,
    immune_to_damage,
    resists,
)
from Combat.Summons import owner_name
from Core.Definitions import Condition

from .fight import initiative_units

# A monster with one of these (a condition, a Visibility, or the spell's badge)
# isn't shown to the players.
HIDDEN_STATES = {
    "Darkness",
    "Greater Invisibility",
    "Heavily Obscured",
    "Hidden",
    "Invisibility",
    "Invisible",
    "Total Cover",
}
# All the players see of a monster's conditions: the rules' own, which show on
# the table. Spell badges and a GM's custom conditions are private notes.
SHOWN_MONSTER_CONDITIONS = {c.value for c in Condition} - HIDDEN_STATES
# The log can say Bloodied as well, since they can see the HP it comes from.
LOGGED_MONSTER_CONDITIONS = SHOWN_MONSTER_CONDITIONS | {CombatStatus.BLOODIED.value}
# The Limited view's words: the highest percentage of Hit Points each one covers,
# lowest first. Bloodied is the rules' own, half or fewer.
_HEALTH_WORDS = ((25, "Dying"), (50, "Bloodied"), (75, "Injured"), (100, "Healthy"))
# The public key that keeps each kind of defense the log has shown, and its word.
_KNOWN_DEFENSES = (("known_resistances", "Resists"), ("known_immunities", "Immune to"))


def _can_be_seen(char: dict) -> bool:
    """A monster the GM has hidden from the players (one that joins the fight
    later) is as unseen as an invisible one."""
    if char.get("_is_player"):
        return True
    states = set(char.get("conditions", [])) | set(char.get("visibility_states", []))
    return not char.get("hidden_from_players") and not states & HIDDEN_STATES


def _player_names(chars: list[dict]) -> set[str]:
    return {c["name"] for c in chars if c.get("_is_player")}


def _is_players_summon(char: dict, players: set[str]) -> bool:
    """Whether char is the summon of one of `players` (their names)."""
    return not char.get("_is_player") and owner_name(char) in players


def _is_known(char: dict, players: set[str]) -> bool:
    """Whether the players know all of char: theirs, or a summon of theirs."""
    return bool(char.get("_is_player")) or _is_players_summon(char, players)


def _seen(char: dict, players: set[str]) -> bool:
    """_can_be_seen, where a player's summon is seen as its owner is: wherever
    it is, once the GM no longer hides it from them."""
    if _is_players_summon(char, players):
        return not char.get("hidden_from_players")
    return _can_be_seen(char)


def _highest_max_hp(lost: int, percent: int) -> int:
    """The highest maximum HP that's down to `percent` or less after losing
    `lost`. What's left is max HP - lost, so max HP * (100 - percent) <= 100 * lost."""
    return 100 * lost // (100 - percent)


def note_health(char: dict):
    """Keep what char's word on the Limited view shows about its maximum HP,
    going by the damage taken beside it, less the healing in the log. Having lost
    12, Bloodied is 17 to 24: 16 would be Dying and 25 Injured. Each word narrows
    it down, so it's called once a change of HP is over, and it's kept in char's
    public keys, so undo and a saved fight keep it too. It's what the players can
    work out, so a monster they can't see shows nothing, and neither does a sum
    that doesn't add up to the HP really lost, as when hidden temp HP soaked some
    of it: the note would be false. At 0 HP the sum runs over by the overkill."""
    if char.get("_is_player") or not _can_be_seen(char):
        return
    stats = char.get("stats", {})
    lost = stats.get("damage_taken", 0) - stats.get("healing_received", 0)
    hp, max_hp = char["hp"], hit_point_maximum(char)
    # A summon whose HP isn't set yet (max HP 0) has no maximum to show.
    if lost <= 0 or max_hp <= 0:
        return
    if lost < max_hp if hp <= 0 else lost != max_hp - hp:
        return
    if hp <= 0:
        char["max_hp_at_most"] = min(lost, char.get("max_hp_at_most", lost))
        return
    percents = [0] + [percent for percent, _ in _HEALTH_WORDS]
    top = next(p for p in percents if 100 * hp <= p * max_hp)
    least = _highest_max_hp(lost, percents[percents.index(top) - 1]) + 1
    char["max_hp_at_least"] = max(least, char.get("max_hp_at_least", least))
    if top < 100:
        most = _highest_max_hp(lost, top)
        char["max_hp_at_most"] = min(most, char.get("max_hp_at_most", most))


def known_max_hp_text(char: dict) -> str:
    """What the words have shown of char's maximum HP: "Max HP ≥ 49",
    "Max HP ≤ 24", "Max HP 17–24" or, once they meet, "Max HP = 20". "" if
    they've shown nothing."""
    least, most = char.get("max_hp_at_least"), char.get("max_hp_at_most")
    if least is None and most is None:
        return ""
    if most is None:
        return f"Max HP ≥ {least}"
    if least is None:
        return f"Max HP ≤ {most}"
    if least == most:
        return f"Max HP = {most}"
    return f"Max HP {least}–{most}"


def _unbroken(text: str) -> str:
    return text.replace(" ", "\N{NO-BREAK SPACE}")


def _note_defense(char: dict, key: str, name: str):
    """Keep a defense the log has shown in char's public keys, so undo and a
    saved fight keep it too. Players know their own characters' already."""
    if not char.get("_is_player") and name not in char.get(key, []):
        char.setdefault(key, []).append(name)


def note_damage_defense(char: dict, damage_type: str, outcome: str | None):
    """Keep what a damage line players read showed of char's defenses, `outcome`
    being what _damage_type_modifier said. A condition or a badge can give
    Resistance or Immunity (Petrified, to all damage; Stoneskin), and then
    the outcome says nothing about char's own defenses."""
    if outcome == "immune" and not immune_to_damage(char, damage_type):
        _note_defense(char, "known_immunities", damage_type)
    elif outcome and "resisted" in outcome and not resists(char, damage_type):
        _note_defense(char, "known_resistances", damage_type)


def note_condition_immunity(char: dict, condition: str):
    """Keep what a line players read showed of char's immunity to `condition`.
    A condition can give the immunity (Petrified, to Poisoned), and then it
    says nothing about char."""
    if not immune_to_condition(char, condition):
        _note_defense(char, "known_immunities", condition)


def known_defense_texts(char: dict) -> list[str]:
    """What the log has shown of char's defenses: "Resists Fire, Cold" and
    "Immune to Poison, Charmed". A long list can only break after a comma."""
    return [
        _unbroken(f"{word} ") + ", ".join(char[key])
        for key, word in _KNOWN_DEFENSES
        if char.get(key)
    ]


def may_read_log_line(
    text: str, character: str | None, value: object, chars: list[dict]
) -> bool:
    """Whether players may read an encounter log line. It's asked when the line
    is logged, because it depends on who they can perceive at that moment: a
    hidden monster's attack stays private after it's revealed.

    A line about a monster says which condition or effect it's about in
    `value`, since the text can't be trusted to name it: it may already be gone,
    and "keeps concentration" doesn't say Concentrating. The whole text is also
    checked, not just `character`: a hidden monster can be named as the source
    of a line about someone else, or in its turn's prefix.

    A line about a player's summon is as readable as one about a player, once
    the GM no longer hides it from them."""
    players = _player_names(chars)
    private = {c["name"] for c in chars if not _seen(c, players)}
    for unit in initiative_units(chars):
        group = unit[0].get("initiative_group")
        if group and not any(_seen(c, players) for c in unit):
            private.add(group)
    if character in private:
        return False
    condition = value.get("condition", "") if isinstance(value, dict) else ""
    # Every one by that name: nothing stops two monsters sharing one.
    for subject in chars:
        if subject["name"] != character or _is_known(subject, players):
            continue
        if condition and condition not in LOGGED_MONSTER_CONDITIONS:
            return False
        private |= set(subject.get("conditions", [])) - LOGGED_MONSTER_CONDITIONS
    return not any(name in text for name in private)
