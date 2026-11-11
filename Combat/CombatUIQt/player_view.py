"""The players' screen (a second monitor or a TV): the turn order, whose turn
it is and who's next, so players plan during other turns. player_view_rows
decides what they may see. The Informative view has everyone's Hit Points, as on
the GM's cards, size, Challenge Rating, AC and speed. The Limited view is the same for players,
who can tell each other all of it anyway, but a monster's row has only
its speed, the damage it's taken, a word for how hurt it is, what those two and
attack rolls have shown of its maximum HP and AC, and what the log has shown of
its resistances and immunities. In both, a monster they can't perceive, or
the GM has hidden from them until it joins the fight, isn't listed, and
nothing else of its stat block is shown.

A player's own summon (its owner, owner_name, is a player in the fight) is
theirs to know: it's listed as a player is, with its numbers and conditions in
both views. While it's out (is_out), its whole stat block goes on its row on its
turn and the one before (its owner's, usually), to plan with: on every row, the
cards would push the turn order off a TV. One the GM still hides from them
isn't listed. A monster's summon is a monster."""

import math
import re
from dataclasses import asdict, dataclass, replace
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QGuiApplication, QKeyEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import CombatStatus
from Combat.Effects.modifiers import (
    immune_to_condition,
    immune_to_damage,
    resists,
)
from Combat.Summons import is_out, owner_name
from Core.Definitions import Condition
from Core.Rules import ability_modifier
from .attack_rolls import known_ac_text
from .cards_mixin import _hp_chunk_color
from .dialogs_mixin import (
    _MONSTER_ABILITY_SECTIONS,
    _ability_entry,
    _damage_entry_text,
    _display,
    _speed_text,
)
from .monster_actions import first_number
from .turns_mixin import initiative_units, unit_label

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

_STYLE = """
QWidget#playerView { background-color: #1a1a2e; }
QLabel { color: #eaeaea; font-size: 26px; background: transparent; }
QLabel#playerViewRound { color: #c9a84c; font-size: 34px; font-weight: bold; }
QFrame#playerViewRow { border-radius: 6px; }
QFrame#playerViewRow[turn="now"] { background-color: #3a2e00; }
QFrame#playerViewRow[turn="next"] { background-color: #0f3460; }
QLabel#playerViewMark { color: #c9a84c; font-weight: bold; }
QLabel#playerViewConditions { color: #a0c4ff; font-size: 22px; }
QLabel#playerViewDetails { color: #a0a0b0; font-size: 20px; }
QLabel#playerViewMember { font-size: 22px; }
QLabel#playerViewCard { color: #c8c8d8; font-size: 18px; }
QProgressBar {
    background-color: #8a8a9a;
    font-size: 22px;
    min-height: 34px;
    max-height: 34px;
}
"""
_BAR_WIDTH = 320
# How far the window shrinks its text and bars to fit every row on the screen
# (a big fight on a 1080p TV), at most: below this a TV is unreadable anyway.
_MIN_SCALE = 0.5
_SCALE_STEP = 0.05


def _scaled_style(scale: float) -> str:
    """_STYLE with every size in it (fonts, bar heights, corners) `scale`
    times as big."""
    return re.sub(
        r"(\d+)px",
        lambda size: f"{max(1, round(int(size.group(1)) * scale))}px",
        _STYLE,
    )


@dataclass(frozen=True)
class PlayerViewHealth:
    name: str  # whose it is, to tell an initiative group's members apart
    text: str  # "12 / 30", or how they stand at 0 HP
    percent: int  # how full the bar is
    color: str  # the bar's color, the same as on the GM's card


@dataclass(frozen=True)
class PlayerViewRow:
    name: str
    details: str  # "Large · AC 13 · Speed 40 ft.", or "" if nothing's known
    health: tuple[PlayerViewHealth, ...]  # one bar for each combatant on this turn
    conditions: tuple[str, ...]
    turn: str  # "now", "next" or ""
    # A player's summon's stat block, a line each ("Dreadful Swipe (Action).
    # Melee Attack Roll: +5, ..."), on its turn and the one before; () for
    # everyone else.
    card: tuple[str, ...] = ()

    def as_json(self) -> dict:
        """The row as the player link sends it. Only a row with a stat block
        has a "card", so nobody else's row tells anything new."""
        data = asdict(self)
        if not self.card:
            del data["card"]
        return data


def _health_text(char: dict, death_state: str) -> str:
    if death_state == "dead":
        return "Dead" if char.get("_is_player") else "Defeated"
    if death_state == "stabilized":
        return "Stable"
    if death_state == "dying":
        fails, saves = char.get("death_saves_fail", 0), char.get(
            "death_saves_success", 0
        )
        return f"Dying ({fails} failed, {saves} saved)"
    temp = char.get("temp_hp", 0)
    return f"{char['hp']} / {char['max_hp']}" + (f" (+{temp} temp)" if temp else "")


def _health(char: dict, death_state: str) -> PlayerViewHealth:
    hp, max_hp = max(char["hp"], 0), max(char["max_hp"], 1)
    return PlayerViewHealth(
        char["name"],
        _health_text(char, death_state),
        # Rounded up, so a bar is only empty at 0 HP.
        min(math.ceil(100 * hp / max_hp), 100),
        _hp_chunk_color(hp, max_hp),
    )


def _limited_health(char: dict, death_state: str) -> PlayerViewHealth:
    """_health without the numbers: a word, and a bar that only moves when the
    word does, since an exact bar would give the HP away just the same."""
    if death_state != "alive":
        text = "Dying" if death_state == "dying" else _health_text(char, death_state)
        return PlayerViewHealth(char["name"], text, 0, _hp_chunk_color(0, 1))
    # A summon whose HP isn't set yet (max HP 0) has nothing to be hurt from.
    left = min(100 * char["hp"] / char["max_hp"], 100) if char["max_hp"] > 0 else 100
    percent, word = next(band for band in _HEALTH_WORDS if left <= band[0])
    return PlayerViewHealth(char["name"], word, percent, _hp_chunk_color(percent, 100))


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
    hp, max_hp = char["hp"], char["max_hp"]
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


def _unit_speeds(unit: list[dict]) -> list[str]:
    return list(
        dict.fromkeys(f"Speed {speed}" for speed in map(_speed_text, unit) if speed)
    )


def _unit_details(unit: list[dict]) -> str:
    """Everyone's size, Challenge Rating (monsters and summons have one), AC
    and speed. A player's AC is a sentence once they have a Shield, so only
    the number they have now is shown."""
    sizes = [_display(c["size"]) for c in unit if c.get("size")]
    ratings = [f"CR {c['cr']}" for c in unit if c.get("cr")]
    armor = [
        f"AC {first_number(c.get('ac'))}"
        for c in unit
        if first_number(c.get("ac")) is not None
    ]
    return " · ".join(dict.fromkeys(sizes + ratings + armor + _unit_speeds(unit)))


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


def _limited_view(
    unit: list[dict], death_state: Callable[[dict], str]
) -> tuple[str, tuple[PlayerViewHealth, ...]]:
    """A monster's details and bars on the Limited view. Damage taken and what's
    known of the maximum HP, AC and defenses go under a lone monster's name, and
    by each member's name in a group, where each bar already has one. A phone's
    narrow column shouldn't break inside any of them, so damage taken goes first
    on a row of its own, or can't break by a member's name, and what's known
    can't break, but for a list of defenses, which is too long not to."""
    notes = [
        [f"{c.get('stats', {}).get('damage_taken', 0)} damage taken"]
        + [_unbroken(t) for t in (known_max_hp_text(c), known_ac_text(c)) if t]
        + known_defense_texts(c)
        for c in unit
    ]
    health = tuple(_limited_health(c, death_state(c)) for c in unit)
    if len(unit) == 1:
        return " · ".join(notes[0] + _unit_speeds(unit)), health
    return (
        " · ".join(_unit_speeds(unit)),
        tuple(
            replace(h, name=" · ".join([h.name, _unbroken(n[0])] + n[1:]))
            for h, n in zip(health, notes)
        ),
    )


def _unit_conditions(unit: list[dict], players: set[str]) -> tuple[str, ...]:
    names: dict[str, None] = {}
    for char in unit:
        for cond in char.get("conditions", []):
            if _is_known(char, players) or cond in SHOWN_MONSTER_CONDITIONS:
                names[cond] = None
    return tuple(names)


def _ability_scores_text(char: dict) -> str:
    """char's scores, "STR 11 (+0) · DEX 10 (+0) · ...", and "Saving Throws
    CON +5" for the saves that aren't just the modifier."""
    scores = {
        name: score
        for name, score in (char.get("Ability Scores") or {}).items()
        if isinstance(score, int)
    }
    modifiers = {name: ability_modifier(score) for name, score in scores.items()}
    parts = [
        _unbroken(f"{name} {score} ({modifiers[name]:+})")
        for name, score in scores.items()
    ]
    saves = [
        f"{name} {bonus:+}"
        for name, bonus in (char.get("Saving Throws") or {}).items()
        if bonus != modifiers.get(name)
    ]
    if saves:
        parts.append(_unbroken("Saving Throws ") + ", ".join(saves))
    return " · ".join(parts)


def summon_card(char: dict) -> tuple[str, ...]:
    """A player's summon's stat block as lines of plain text, as the GM's card
    has it: its scores, skills, defenses, senses and languages, then each
    trait and action. Its HP, AC, size and speed are on its row already."""
    lines = [_ability_scores_text(char)]
    if char.get("skills"):
        lines.append(
            "Skills "
            + ", ".join(f"{_display(k)} {v:+}" for k, v in char["skills"].items())
        )
    for key, label in (
        ("damage_vulnerabilities", "Vulnerabilities"),
        ("damage_resistances", "Resistances"),
        ("damage_immunities", "Damage Immunities"),
    ):
        if char.get(key):
            lines.append(f"{label} " + "; ".join(map(_damage_entry_text, char[key])))
    if char.get("condition_immunities"):
        immune = ", ".join(_display(c) for c in char["condition_immunities"])
        lines.append(f"Condition Immunities {immune}")
    for key, label in (("senses", "Senses"), ("languages", "Languages")):
        if char.get(key):
            lines.append(f"{label} {char[key]}")
    for key, section in _MONSTER_ABILITY_SECTIONS:
        # "Bonus Actions" -> "(Bonus Action)"; a trait needs no word.
        kind = "" if key == "traits" else f" ({section.removesuffix('s')})"
        for ability in char.get(key) or []:
            name, description = _ability_entry(ability)
            lines.append(f"{name}{kind}. {description}".strip())
    return tuple(line for line in lines if line)


def _unit_card(unit: list[dict], players: set[str]) -> tuple[str, ...]:
    """The stat block of each of the players' summons in unit that's out, a
    line once if they share it."""
    lines = [
        line
        for c in unit
        if _is_players_summon(c, players) and is_out(c)
        for line in summon_card(c)
    ]
    return tuple(dict.fromkeys(lines))


def player_view_rows(
    order: list[dict],
    now: list[dict],
    upcoming: list[list[dict]],
    death_state: Callable[[dict], str],
    limited: bool = False,
) -> list[PlayerViewRow]:
    """A row for each turn in `order` that the players can see. `now` is the
    current turn and `upcoming` the turns after it; "next" goes on the first
    of those they can see, so a hidden monster's place doesn't give it away.
    On that monster's own turn, "now" stays where it was, for the same reason.
    `limited` is the Limited view, for monsters' rows: a player is never in an
    initiative group, so a row is all monsters or one player. A player's
    summon's row is as its owner's, with its stat block while it's out and
    its turn is now or next."""
    players = _player_names(order)
    next_unit = next(
        (unit for unit in upcoming if any(_seen(c, players) for c in unit)), []
    )
    units = initiative_units(order)
    now_index = next(
        (i for i, unit in enumerate(units) if any(c is n for c in unit for n in now)),
        0,
    )
    shown_now = next(
        (
            units[(now_index - back) % len(units)]
            for back in range(len(units))
            if any(_seen(c, players) for c in units[(now_index - back) % len(units)])
        ),
        [],
    )
    rows = []
    for unit in units:
        shown = [c for c in unit if _seen(c, players)]
        if not shown:
            continue
        turn = ""
        if unit is shown_now:
            turn = "now"
        elif any(c is n for c in unit for n in next_unit):
            turn = "next"
        if limited and not all(_is_known(c, players) for c in shown):
            details, health = _limited_view(shown, death_state)
        else:
            details = _unit_details(shown)
            health = tuple(_health(c, death_state(c)) for c in shown)
        rows.append(
            PlayerViewRow(
                unit_label(shown),
                details,
                health,
                _unit_conditions(shown, players),
                turn,
                _unit_card(shown, players) if turn else (),
            )
        )
    return rows


def _health_line(health: PlayerViewHealth, in_group: bool) -> QHBoxLayout:
    """A combatant's HP bar, with its name when it shares a row with others."""
    line = QHBoxLayout()
    if in_group:
        member = QLabel(health.name)
        member.setObjectName("playerViewMember")
        member.setWordWrap(True)
        line.addWidget(member, stretch=1)
    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(health.percent)
    bar.setFormat(health.text)
    bar.setTextVisible(True)
    bar.setFixedWidth(_BAR_WIDTH)
    bar.setStyleSheet(
        f"QProgressBar::chunk {{ background-color: {health.color};"
        " border-radius: 3px; }"
    )
    line.addWidget(bar)
    return line


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


class PlayerViewWindow(QWidget):
    """Shows the rows it's given. It reads nothing itself, so all it can ever
    show the players is what player_view_rows let through.

    Every row has to fit on the screen: nobody scrolls a TV. When they don't
    fit the window's height, the text and bars shrink until they do (down to
    _MIN_SCALE), rather than the window growing past the screen or squashing
    wrapped lines away."""

    def __init__(self, on_close: Callable[[], None]):
        super().__init__()
        self._on_close = on_close
        self._scale = 1.0
        self._fitting = False
        self.setObjectName("playerView")
        # It goes when the main window does, instead of keeping the app open.
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowTitle("Players")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(_STYLE)
        self.resize(900, 700)
        layout = QVBoxLayout(self)
        # The rows don't set the window's minimum size, which would grow it
        # past the screen: _fit shrinks them into it instead.
        layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self._title = QLabel("")
        self._title.setObjectName("playerViewRound")
        layout.addWidget(self._title)
        self._rows_box = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_box)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(6)
        layout.addWidget(self._rows_box)
        layout.addStretch()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self._on_close()
        super().closeEvent(a0)

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:
        # Full screen on a TV, it has no X to click.
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(a0)

    def show_rows(self, title: str, rows: list[PlayerViewRow]):
        self._title.setText(title)
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        for row in rows:
            frame = self._row_widget(row)
            self._rows_layout.addWidget(frame)
            # New rows take the style sheet's fonts now, so _fit measures them.
            frame.ensurePolished()
        self._fit()

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        self._fit()

    @property
    def scale(self) -> float:
        """How big the text and bars are now, 1.0 being their full size."""
        return self._scale

    def needed_height(self) -> int:
        """The height every row needs at the window's width and its scale."""
        layout = self.layout()
        assert layout is not None
        layout.invalidate()
        if layout.hasHeightForWidth():
            return layout.heightForWidth(self.width())
        return layout.sizeHint().height()

    def _set_scale(self, scale: float):
        if scale != self._scale:
            self._scale = scale
            self.setStyleSheet(_scaled_style(scale))

    def _fit(self):
        """The biggest scale, in _SCALE_STEPs from full size, at which every row
        fits the window's height."""
        if self._fitting:
            return
        self._fitting = True
        try:
            self._set_scale(1.0)
            needed, height = self.needed_height(), self.height()
            if needed <= height:
                return
            # Sizes don't all scale (margins, the bars' width), so start
            # from the guess and step down until it fits.
            scale = max(_MIN_SCALE, min(1.0, height / needed))
            scale = math.floor(scale / _SCALE_STEP) * _SCALE_STEP
            while True:
                self._set_scale(max(_MIN_SCALE, round(scale, 2)))
                if self._scale <= _MIN_SCALE or self.needed_height() <= height:
                    return
                scale -= _SCALE_STEP
        finally:
            self._fitting = False

    @staticmethod
    def _row_widget(row: PlayerViewRow) -> QFrame:
        frame = QFrame()
        frame.setObjectName("playerViewRow")
        frame.setProperty("turn", row.turn)
        grid = QGridLayout(frame)
        grid.setContentsMargins(12, 6, 12, 6)
        grid.setColumnStretch(1, 1)
        mark = QLabel({"now": "NOW", "next": "NEXT"}.get(row.turn, ""))
        mark.setObjectName("playerViewMark")
        mark.setFixedWidth(100)
        grid.addWidget(mark, 0, 0)
        grid.addWidget(QLabel(row.name), 0, 1)
        if row.details:
            details = QLabel(row.details)
            details.setObjectName("playerViewDetails")
            details.setWordWrap(True)
            grid.addWidget(details, 1, 1)
        in_group = len(row.health) > 1
        bars = QVBoxLayout()
        bars.setSpacing(4)
        for health in row.health:
            bars.addLayout(_health_line(health, in_group))
        if in_group:
            grid.addLayout(bars, 2, 1, 1, 2)
        else:
            grid.addLayout(bars, 0, 2, 2, 1)
        if row.conditions:
            conditions = QLabel(", ".join(row.conditions))
            conditions.setObjectName("playerViewConditions")
            conditions.setWordWrap(True)
            grid.addWidget(conditions, 3, 1, 1, 2)
        if row.card:
            card = QLabel("\n".join(row.card))
            card.setObjectName("playerViewCard")
            card.setTextFormat(Qt.TextFormat.PlainText)
            card.setWordWrap(True)
            grid.addWidget(card, 4, 1, 1, 2)
        return frame

    def show_on_spare_screen(self, main_window: QWidget):
        """Fill a screen the main window isn't on, or else open as a window."""
        main_screen = main_window.screen()
        spare = [s for s in QGuiApplication.screens() if s is not main_screen]
        if not spare:
            self.show()
            return
        self.setGeometry(spare[0].geometry())
        self.showFullScreen()
