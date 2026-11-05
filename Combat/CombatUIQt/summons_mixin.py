"""Summons mixin for CombatAppQt: a player's summons (the dict side is
Combat/Summons.py) being summoned, dismissed, dying with their owner, coming
back in the next encounter as they were, and joining a fight already summoned.

A summon is made when its owner summons it: from Enable Feature (Drake
Companion, Reanimated Companion) or from the owner's or the summon's card
menu, which also offers the choices made when it's summoned (a drake's
Draconic Essence). It spends the feature's use and its Action, or a spell slot
once the use is spent, as the features allow, and the summon comes out at
full Hit Points right after its owner in the turn order. With as many out as
its feature allows, summoning another replaces the oldest (a drake) or isn't
possible (a Reanimated Companion: greyed out). The summon's card menu also
dismisses it. The feature's use and the slot are logged with actions, so the
player log's replay spends them for the rest of the day too.

Add Combatant's "Already summoned..." adds one made before the fight (any of
the party's, with its choice) at full Hit Points, spending nothing.
"""

import json
from pathlib import Path

from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QMenu

import Combat.PlayerLog as PlayerLog
from Combat.Summons import (
    CHOICE_KEY,
    SummonOption,
    carried_state,
    choice_of,
    create,
    feature_summons,
    is_out,
    last_seen,
    make_room,
    mark,
    numbered,
    old_name,
    owner_name,
    place_after_owners,
    set_stat_block,
    source_for,
    summon_name,
)
from Model.Character import Character
from Model.Content.Feature import Feature
from Model.Content.Summons import OnZeroHp, SummonContext, SummonLifetime, SummonSpec

from .effect_options import feature_action_cost
from .state import CombatWindowState
from .stats import _default_stats
from .styles import QSS
from .undo import undoable


class SummonsMixin(CombatWindowState):
    """Mixin for players' summons."""

    def _summon_owner(self, char: dict) -> dict | None:
        """The player in the window whose summon char is, if any."""
        name = owner_name(char)
        if name is None:
            return None
        return next(
            (c for c in self.characters if c.get("_is_player") and c["name"] == name),
            None,
        )

    def _owner_summons(self, owner: dict) -> list[dict]:
        return [c for c in self.characters if owner_name(c) == owner["name"]]

    def _summon_source(
        self, summon: dict
    ) -> tuple[dict, Character, Feature, SummonSpec] | None:
        """(owner, the owner's character, the feature that summons it, its
        SummonSpec)."""
        owner = self._summon_owner(summon)
        sheet = owner.get("_stat_block") if owner is not None else None
        if owner is None or not isinstance(sheet, Character):
            return None
        found = source_for(sheet, summon)
        return None if found is None else (owner, sheet, *found)

    def _same_summons(
        self, owner: dict, feature: Feature, spec: SummonSpec
    ) -> list[dict]:
        """owner's summons in the window made by feature's spec, in the
        window's order (oldest first)."""
        sheet = owner["_stat_block"]
        same = []
        for char in self._owner_summons(owner):
            found = source_for(sheet, char)
            if found is not None and (found[0].name, found[1].name) == (
                feature.name,
                spec.name,
            ):
                same.append(char)
        return same

    def _summon_uses_left(self, owner: dict, feature: Feature) -> int:
        used = owner.get("feature_uses_used", {}).get(feature.name, 0)
        return max(feature.number_of_uses(owner["_stat_block"]) - used, 0)

    @staticmethod
    def _lowest_slot(owner: dict) -> int | None:
        """The lowest level owner has a spell slot (or Pact Magic slot) of."""
        levels = [
            int(level)
            for pool in ("spell_slots", "pact_slots")
            for level, left in owner.get(pool, {}).items()
            if left > 0 and int(level) >= 1
        ]
        return min(levels, default=None)

    def _summon_cost_text(self, owner: dict, feature: Feature) -> str:
        if self._summon_uses_left(owner, feature) > 0:
            return "1 use left"
        level = self._lowest_slot(owner)
        return f"a level {level} slot" if level is not None else "no uses or slots"

    def _room_for(
        self, owner: dict, feature: Feature, spec: SummonSpec, ctx: SummonContext
    ) -> list[dict] | None:
        """Who summoning spec again now replaces ([]: nobody), or None when
        it can't be summoned while the ones out are (make_room)."""
        out = [c for c in self._same_summons(owner, feature, spec) if is_out(c)]
        return make_room(out, spec, spec.count(owner["_stat_block"], ctx))

    def _add_summon_actions(self, menu: QMenu, char: dict):
        """On a summon's card, or its owner's: summon it (again), with a
        choice (Draconic Essence) when the feature has them, the current one
        checked; and on a summon's card, dismiss it."""
        if owner_name(char) is not None:
            found = self._summon_source(char)
            entries = [] if found is None else [(*found, choice_of(char))]
        elif char.get("_is_player") and isinstance(char.get("_stat_block"), Character):
            sheet = char["_stat_block"]
            entries = []
            for feature, spec in feature_summons(sheet):
                out = [c for c in self._same_summons(char, feature, spec) if is_out(c)]
                current = choice_of(out[-1]) if out else None
                entries.append((char, sheet, feature, spec, current))
        else:
            return
        for owner, sheet, feature, spec, current in entries:
            menu.addSeparator()
            self._add_spec_summon_actions(menu, owner, sheet, feature, spec, current)
        if owner_name(char) is not None:
            if not entries:
                menu.addSeparator()
            menu.addAction("Dismiss", lambda _=False, c=char: self._dismiss_summon(c))

    def _add_spec_summon_actions(
        self,
        menu: QMenu,
        owner: dict,
        sheet: Character,
        feature: Feature,
        spec: SummonSpec,
        current: str | None,
    ):
        """menu's entry that summons spec (a submenu of its choices, `current`
        checked), greyed out when it can't be summoned now."""
        if self._room_for(owner, feature, spec, SummonContext()) is None:
            action = menu.addAction(f"Summon {feature.name} (one is already out)")
            assert action is not None  # addAction with a text always makes one
            action.setEnabled(False)
            return
        label = f"Summon {feature.name} ({self._summon_cost_text(owner, feature)})"
        choices = spec.choices(sheet)
        if not choices:
            menu.addAction(
                label,
                lambda _=False, o=owner, f=feature, s=spec: self._summon(o, f, s, None),
            )
            return
        submenu = menu.addMenu(label)
        assert submenu is not None  # addMenu with a title always makes one
        submenu.setStyleSheet(QSS)
        for choice in choices:
            action = submenu.addAction(choice)
            assert action is not None  # addAction with a text always makes one
            action.setCheckable(True)
            action.setChecked(current == choice)
            action.triggered.connect(
                lambda _=False, o=owner, f=feature, s=spec, ch=choice: self._summon(
                    o, f, s, ch
                )
            )

    def _pick_summon(self, owner: dict, feature: Feature):
        """Enable Feature's summon: ask the choice at the mouse when there is
        one, else summon right away."""
        sheet = owner["_stat_block"]
        specs = feature.summons(sheet)
        if len(specs) == 1 and not specs[0].choices(sheet):
            self._summon(owner, feature, specs[0], None)
            return
        menu = QMenu(self._window)
        menu.setStyleSheet(QSS)
        for spec in specs:
            out = [c for c in self._same_summons(owner, feature, spec) if is_out(c)]
            current = choice_of(out[-1]) if out else None
            self._add_spec_summon_actions(menu, owner, sheet, feature, spec, current)
        menu.exec(QCursor.pos())

    @undoable
    def _summon(
        self, owner: dict, feature: Feature, spec: SummonSpec, choice: str | None
    ):
        """owner summons spec of feature (with `choice`): the feature's use
        or, with none left, their lowest spell slot, and its Action; the
        summon comes out at full Hit Points right after owner in the turn
        order, replacing the oldest one when there's no room for it."""
        if self.phase == "PARTY":
            self._show_status("No summon: open an encounter first.")
            return
        if self._char_death_state(owner) != "alive":
            self._show_status(f"No summon: {owner['name']} is down.")
            return
        ctx = SummonContext(choice=choice)
        gone = self._room_for(owner, feature, spec, ctx)
        if gone is None:
            out = [c for c in self._same_summons(owner, feature, spec) if is_out(c)]
            self._show_status(
                f"No summon: {out[-1]['name']} is still out, and"
                f" {feature.name} can't make another while it is."
            )
            return
        if self._summon_uses_left(owner, feature) > 0:
            self._count_feature_use(owner, feature.name, counts_uses=True)
        else:
            level = self._lowest_slot(owner)
            if level is None:
                self._show_status(
                    f"No summon: {owner['name']} has no use of {feature.name}"
                    " and no spell slot left."
                )
                return
            # Not a use of the feature: the replay would count it as one.
            self._spend_slot(owner, level)
        action_cost = feature_action_cost(feature)
        if action_cost is not None:
            self._add_action_use(action_cost, owner)
        new = self._bring_in(owner, feature, spec, ctx, gone)
        chosen = f" ({choice})" if choice else ""
        self._log_event(
            f"{owner['name']} summons {_names(new)}{chosen}",
            character=new[0]["name"] if new else None,
        )
        self._rebuild_cards()
        if self.phase == "COMBAT":
            self._refresh_turn()
        self._refresh_views()

    def _bring_in(
        self,
        owner: dict,
        feature: Feature,
        spec: SummonSpec,
        ctx: SummonContext,
        gone: list[dict],
    ) -> list[dict]:
        """Make spec's creatures and put them in the fight after owner, once
        `gone` (the ones they replace, logged) and the ones of spec that
        aren't out and won't be back (an older log's hidden one, a drake at
        0 Hit Points) are out of it. Returns the new ones."""
        for char in gone:
            self._log_event(
                f"{char['name']} vanishes: {owner['name']} summons another",
                character=char["name"],
            )
            self._remove_from_fight(char)
        for char in self._same_summons(owner, feature, spec):
            if not is_out(char) and (
                char.get("hidden_from_players") or spec.on_zero_hp is OnZeroHp.VANISHES
            ):
                self._remove_from_fight(char)
        taken = {c["name"] for c in self.characters}
        new = create(owner["_stat_block"], feature, spec, ctx, taken)
        self._join_fight(new)
        return new

    def _join_fight(self, new: list[dict]):
        """Put the summons `new` in the window right after their owners, and
        in the turn order when the fight is on, keeping whoever's turn it is."""
        for char in new:
            char["stats"] = _default_stats()
        if self.phase == "COMBAT" and self.initiative_order:
            # Whoever's turn it is keeps it.
            current = self.initiative_order[self.current_turn_idx]
            self.initiative_order = place_after_owners(self.initiative_order, new)
            at = next(i for i, c in enumerate(self.initiative_order) if c is current)
            self.current_turn_idx = self._turn_span(at)[0]
        self.characters[:] = place_after_owners(self.characters, new)

    def _remove_from_fight(self, char: dict):
        """Take char out of the window and the turn order, keeping whoever's
        turn it is (the next one's, when it was char's)."""
        order = self.initiative_order
        if self.phase == "COMBAT" and any(c is char for c in order):
            current = order[self.current_turn_idx]
            at = next(i for i, c in enumerate(order) if c is char)
            self.initiative_order = [c for c in order if c is not char]
            if not self.initiative_order:
                self.current_turn_idx = 0
            elif current is char:
                at %= len(self.initiative_order)
                self.current_turn_idx = self._turn_span(at)[0]
            else:
                at = next(
                    i for i, c in enumerate(self.initiative_order) if c is current
                )
                self.current_turn_idx = self._turn_span(at)[0]
        self.characters[:] = [c for c in self.characters if c is not char]
        if self.selected_character is char:
            self.selected_character = None
            self.selected_label.setText("Source: None")
        if any(t is char for t in self.target_characters):
            self.target_characters = [
                t for t in self.target_characters if t is not char
            ]
            self._update_target_label()

    @undoable
    def _dismiss_summon(self, summon: dict):
        """Its owner dismisses summon: it leaves the fight."""
        owner = owner_name(summon) or "Its owner"
        # Logged while it's still there, so players read it if they saw it.
        self._log_event(f"{owner} dismisses {summon['name']}", character=summon["name"])
        self._remove_from_fight(summon)
        self._save_fight_state()
        self._rebuild_cards()
        if self.phase == "COMBAT":
            self._refresh_turn()
        self._refresh_views()

    def _summons_die_with(self, owner: dict):
        """owner died: each summon of theirs that's out and drops with them
        drops to 0 Hit Points (a Reanimated Companion's Death Burst goes off;
        a drake is gone)."""
        for summon in self._owner_summons(owner):
            if not is_out(summon):
                continue
            found = self._summon_source(summon)
            if found is not None and not found[3].drops_with_owner:
                continue
            summon["hp"] = 0
            summon["temp_hp"] = 0
            self._apply_bloodied_condition(summon)
            traits = summon.get("traits") or []
            burst = any(_ability_name(t) == "Death Burst" for t in traits)
            self._log_event(
                f"{summon['name']} drops to 0 HP: {owner['name']} died"
                + (" (its Death Burst goes off)" if burst else ""),
                character=summon["name"],
            )
            self._rebuild_card(summon)

    def _carry_summons_over(self, log_path: Path):
        """Start the encounter log at `log_path` (one not started yet) with
        the party's summons the last encounter left out, as it left them:
        their Hit Points, conditions and choice. A long rest since ends a
        Reanimated Companion and rests a drake (its SummonSpec's lifetime)."""
        if not self.player_log_file:
            return
        ref = PlayerLog.log_ref(self.player_log_file, log_path)
        # Each encounter log played, with whether a long rest came after it.
        played: list[tuple[dict, bool]] = []
        for session in self.player_log_data["sessions"]:
            if session.get("type") == PlayerLog.LONG_REST:
                played = [(data, True) for data, _ in played]
                continue
            if not session.get("log") or session["log"] == ref:
                continue
            path = PlayerLog.resolve_log(self.player_log_file, session["log"])
            if path.exists():
                played.append((json.loads(path.read_text(encoding="utf-8")), False))
        taken = {c["name"] for c in self.characters}
        new: list[dict] = []
        for owner in [c for c in self.characters if c.get("_is_player")]:
            sheet = owner.get("_stat_block")
            if not isinstance(sheet, Character):
                continue
            for feature, spec in feature_summons(sheet):
                # Only one that lasts until dismissed outlasts a long rest.
                ends_on_long_rest = spec.lifetime is not SummonLifetime.UNTIL_DISMISSED
                logs = [(d, r) for d, r in played if not (r and ends_on_long_rest)]
                for name, aliases in _earlier_names(owner, sheet, feature, spec, logs):
                    seen = last_seen(name, logs, aliases)
                    if seen is None:
                        continue
                    state = carried_state(*seen)
                    if state["hidden_from_players"]:
                        continue  # not out: summoned again when it's wanted
                    names = {name, *aliases}
                    # An older log's hidden one, prepared with the encounter.
                    here = next(
                        (c for c in self.characters if c["name"] in names), None
                    )
                    if here is None:
                        ctx = SummonContext(choice=state.get(CHOICE_KEY))
                        here = create(sheet, feature, spec, ctx, taken)[0]
                        here["name"] = numbered(name, taken)
                        new.append(here)
                    else:
                        mark(here, sheet, feature, spec)
                        set_stat_block(here, sheet, spec, state.get(CHOICE_KEY))
                    taken.add(here["name"])
                    here.update(state)
                    del here["hidden_from_players"]
        # Before the fight: there's no turn order yet.
        for char in new:
            char["stats"] = _default_stats()
        self.characters[:] = place_after_owners(self.characters, new)

    def _already_summoned_options(self) -> list[SummonOption]:
        """Add Combatant's "Already summoned...": each summon (with each of
        its choices) of each player in the window."""
        options = []
        for player in self.characters:
            sheet = player.get("_stat_block")
            if not player.get("_is_player") or not isinstance(sheet, Character):
                continue
            for feature, spec in feature_summons(sheet):
                for choice in spec.choices(sheet) or [None]:
                    label = summon_name(player["name"], spec)
                    if choice is not None:
                        label += f" ({choice})"
                    options.append(SummonOption(label, player, feature, spec, choice))
        return options

    @undoable
    def _add_already_summoned(self, option: SummonOption):
        """Add a summon made before the fight (Add Combatant): out at full
        Hit Points after its owner, spending nothing."""
        if self.phase == "PARTY":
            return
        owner, feature, spec = option.owner, option.feature, option.spec
        ctx = SummonContext(choice=option.choice)
        gone = self._room_for(owner, feature, spec, ctx)
        if gone is None:
            self._show_status(
                f"Not added: {feature.name} can't make another while"
                f" {owner['name']}'s is out."
            )
            return
        new = self._bring_in(owner, feature, spec, ctx, gone)
        self._log_event(
            f"{_names(new)} joins the fight, already summoned",
            note_turn=False,
            character=new[0]["name"] if new else None,
        )
        self._rebuild_cards()
        if self.phase == "COMBAT":
            self._refresh_turn()
        self._refresh_views()


def _earlier_names(
    owner: dict,
    sheet: Character,
    feature: Feature,
    spec: SummonSpec,
    logs: list[tuple[dict, bool]],
) -> list[tuple[str, tuple[str, ...]]]:
    """The names owner's summons of spec had in the encounter logs `logs`,
    as today's names, each with the names older logs gave it (the first's
    "<owner>'s Companion (<type>)")."""
    base = summon_name(owner["name"], spec)
    combatant_type = spec.build(sheet, SummonContext()).combatant_type
    legacy = old_name(owner["name"], combatant_type)
    names: list[str] = []
    for data, _ in logs:
        for char in data.get("combatants", []):
            if owner_name(char) != owner["name"]:
                continue
            found = source_for(sheet, char)
            if found is None or (found[0].name, found[1].name) != (
                feature.name,
                spec.name,
            ):
                continue
            name = base if char["name"] == legacy else char["name"]
            if name not in names:
                names.append(name)
    return [(name, (legacy,) if name == base else ()) for name in names]


def _names(chars: list[dict]) -> str:
    return " and ".join(c["name"] for c in chars)


def _ability_name(ability) -> str | None:
    """A stat-block ability's name, as a MonsterAbility or as a log stores it."""
    if isinstance(ability, dict):
        return ability.get("name")
    return getattr(ability, "name", None)
