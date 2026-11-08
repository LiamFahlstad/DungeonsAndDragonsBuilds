"""Summons mixin for CombatAppQt: a player's summons (the dict side is
Combat/Summons.py) being summoned, dismissed, dying with their owner, coming
back in the next encounter as they were, and joining a fight already summoned.

A summon is made when its owner summons it: from Enable Feature (Drake
Companion, Reanimated Companion) or from the owner's or the summon's card
menu, which also offers the choices made when it's summoned (a drake's
Draconic Essence). It's paid for with the first of its SummonSpec's costs the
owner can pay (cost_options: the feature's use, else their lowest spell slot);
the card menu's "using..." entry pays another way. It spends the feature's
Action too, and the summon comes out at full Hit Points right after its owner
in the turn order, or, rolling its own initiative (SummonTurn.OWN_INITIATIVE),
where its roll puts it (a row of its own on the initiative screen, rolled with
the monsters). With as many out as its feature allows, summoning another
replaces the oldest (a drake) or isn't possible (a Reanimated Companion:
greyed out). The summon's card menu also dismisses it. Its menu entries
are labelled by its SummonSpec ("Summon Dancing Item"), one for each spec of a
source that has several. One that vanishes at 0 Hit Points (a drake) leaves
the fight then (_vanish_at_zero_hp); one that dies (a Reanimated Companion)
stays, dead.

The feature's use and the slot are logged with their own actions, so the
player log's replay spends them for the rest of the day too; the summon
itself is logged as Action.SUMMON, and dismissing or replacing one as
Action.DISMISS (with "reason": "0 hp" for one that vanished), which the next
encounter's carry-over reads: one dismissed or vanished isn't brought back. A summon carried over keeps the card it was built with
(only summoning it again rebuilds it from the owner's sheet).

Add Combatant's "Already summoned..." adds one made before the fight (any of
the party's, with its choice) at full Hit Points, spending nothing.
"""

from pathlib import Path

from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QMenu

import Combat.PlayerLog as PlayerLog
from Combat.Definitions import Action
from Combat.LogFiles import read_json
from Combat.Summons import (
    CHOICE_KEY,
    VANISHED_REASON,
    SummonOption,
    SummonPayment,
    carried_state,
    choice_of,
    cost_options,
    create,
    feature_summons,
    follows_owner,
    is_out,
    keep_card,
    last_seen,
    make_room,
    mark,
    numbered,
    old_name,
    owner_name,
    place_after_owners,
    source_for,
    summon_event,
    summon_name,
    vanishes_at_zero_hp,
)
from Model.Character import Character
from Model.Content.Feature import Feature
from Model.Content.Summons import OnZeroHp, SummonContext, SummonLifetime, SummonSpec

from .effect_options import PactSlot, feature_action_cost
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

    @staticmethod
    def _payments(
        owner: dict, feature: Feature, spec: SummonSpec
    ) -> list[SummonPayment]:
        """How owner can pay for spec now, cheapest (the default) first."""
        return cost_options(owner, owner["_stat_block"], feature, spec)

    def _pay_for_summon(self, owner: dict, payment: SummonPayment):
        """Spend `payment` (logged with its own action, so the replay spends
        it too). A slot isn't a use of the feature: the replay would count it
        as one."""
        if payment.feature_use is not None:
            self._count_feature_use(owner, payment.feature_use, counts_uses=True)
        elif payment.slot_level is not None:
            level = payment.slot_level
            self._spend_slot(owner, PactSlot(level) if payment.pact else level)

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
        """menu's entry that summons spec, paid the cheapest way (a submenu
        of its choices, `current` checked), and, when owner can pay another
        way too, a "using..." submenu of those; greyed out while one is out
        that it can't make another beside. When owner can't pay for it, the
        entry says so, and _summon asks whether to summon it anyway."""
        payments = self._payments(owner, feature, spec)
        if self._room_for(owner, feature, spec, SummonContext()) is None:
            action = menu.addAction(f"{_summon_label(spec)} (one is already out)")
            assert action is not None  # addAction with a text always makes one
            action.setEnabled(False)
            return
        if not payments:
            label = f"{_summon_label(spec)} ({_unpaid_text(feature, spec)})"
            self._add_summon_entry(
                menu, label, owner, sheet, feature, spec, current, None
            )
            return
        label = f"{_summon_label(spec)} ({payments[0].text})"
        self._add_summon_entry(menu, label, owner, sheet, feature, spec, current, None)
        if len(payments) > 1:
            other = menu.addMenu(f"{_summon_label(spec)} using…")
            assert other is not None  # addMenu with a title always makes one
            other.setStyleSheet(QSS)
            for payment in payments[1:]:
                self._add_summon_entry(
                    other, payment.text, owner, sheet, feature, spec, current, payment
                )

    def _add_summon_entry(
        self,
        menu: QMenu,
        label: str,
        owner: dict,
        sheet: Character,
        feature: Feature,
        spec: SummonSpec,
        current: str | None,
        payment: SummonPayment | None,
    ):
        """menu's entry `label` that summons spec paid with `payment` (None:
        the cheapest way): a submenu of its choices, `current` checked, when
        it has any."""
        choices = spec.choices(sheet)
        if not choices:
            menu.addAction(
                label,
                lambda _=False, o=owner, f=feature, s=spec, p=payment: self._summon(
                    o, f, s, None, p
                ),
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
                lambda _=False, o=owner, f=feature, s=spec, ch=choice, p=payment: (
                    self._summon(o, f, s, ch, p)
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
        self,
        owner: dict,
        feature: Feature,
        spec: SummonSpec,
        choice: str | None,
        payment: SummonPayment | None = None,
    ):
        """owner summons spec of feature (with `choice`), paid with `payment`
        (None: the cheapest way they can, cost_options) and the feature's
        Action; the summon comes out at full Hit Points in the turn order
        (right after owner, or where its own initiative roll puts it),
        replacing the oldest one when there's no room for it."""
        if self._nothing_logged_here():
            self._show_status("No summon: open an encounter first.")
            return
        if self._char_death_state(owner) != "alive":
            self._show_status(f"No summon: {owner['name']} is down.")
            return
        payments = self._payments(owner, feature, spec)
        if payment is None and payments:
            payment = payments[0]
        # A slot that pays for it is the slot it's made with.
        slot = payment.slot_level if payment is not None else None
        ctx = SummonContext(choice=choice, slot_level=slot)
        gone = self._room_for(owner, feature, spec, ctx)
        if gone is None:
            out = [c for c in self._same_summons(owner, feature, spec) if is_out(c)]
            self._show_status(
                f"No summon: {out[-1]['name']} is still out, and"
                f" {feature.name} can't make another while it is."
            )
            return
        # Out of what it costs, the GM can summon it anyway, unpaid.
        unpaid = None
        if payment is None:
            unpaid = f"{feature.name}: {_unpaid_text(feature, spec)}"
        elif payment not in payments:
            unpaid = f"{feature.name}: can't pay with {payment.text} now"
        action_cost = feature_action_cost(feature)
        lacks = [unpaid, self._action_lack(owner, action_cost)]
        if not self._go_ahead_anyway(owner, f"Summon {spec.name}", lacks):
            return
        if payment is not None and unpaid is None:
            self._pay_for_summon(owner, payment)
        if action_cost is not None:
            self._add_action_use(action_cost, owner, ask=False)
        new, rolls = self._bring_in(owner, feature, spec, ctx, gone)
        chosen = f" ({choice})" if choice else ""
        self._log_event(
            f"{owner['name']} summons {_names(new)}{chosen}{_rolled(rolls)}",
            character=owner["name"],
            action=Action.SUMMON,
            value=summon_event(new, initiative=rolls),
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
    ) -> tuple[list[dict], dict[str, int]]:
        """Make spec's creatures and put them in the fight (_join_fight), once
        `gone` (the ones they replace, logged) and the ones of spec that
        aren't out and won't be back (an older log's hidden one, a drake at
        0 Hit Points) are out of it. Returns the new ones, and the initiative
        each one that rolls its own rolled."""
        for char in gone:
            self._log_event(
                f"{char['name']} vanishes: {owner['name']} summons another",
                character=owner["name"],
                action=Action.DISMISS,
                value=summon_event([char], replaced=True),
            )
            self._remove_from_fight(char)
        for char in self._same_summons(owner, feature, spec):
            if not is_out(char) and (
                char.get("hidden_from_players") or spec.on_zero_hp is OnZeroHp.VANISHES
            ):
                self._remove_from_fight(char)
        taken = {c["name"] for c in self.characters}
        new = create(owner["_stat_block"], feature, spec, ctx, taken)
        return new, self._join_fight(new)

    def _join_fight(self, new: list[dict]) -> dict[str, int]:
        """Put the summons `new` in the window and, when the fight is on, in
        the turn order, keeping whoever's turn it is: right after their
        owners, or, one that rolls its own initiative, where its roll puts it
        (before the fight, a row of its own on the initiative screen; between
        encounters, right after their owners, with no turns to take).
        Returns each roll, by name."""
        for char in new:
            char["stats"] = _default_stats()
        own = [c for c in new if not follows_owner(c)]
        follow = [c for c in new if follows_owner(c)]
        rolls: dict[str, int] = {}
        if self.phase == "COMBAT" and self.initiative_order:
            # Whoever's turn it is keeps it.
            current = self.initiative_order[self.current_turn_idx]
            self.initiative_order = place_after_owners(self.initiative_order, follow)
            at = next(i for i, c in enumerate(self.initiative_order) if c is current)
            self.current_turn_idx = self._turn_span(at)[0]
            for char in own:
                rolls[char["name"]] = self._roll_into_turn_order(char)
                self._place_as_in_turn_order(char)
            self.characters[:] = place_after_owners(self.characters, follow)
            return rolls
        self.characters[:] = place_after_owners(self.characters, new)
        if self.phase == "INITIATIVE":
            for char in own:
                self._add_initiative_row([char])
            if own:
                self._check_start_button()
        return rolls

    def _place_as_in_turn_order(self, char: dict):
        """Put char (in the turn order, not yet in the window) in the window
        where it is in the turn order: before the next one after it there."""
        order = self.initiative_order
        at = next(i for i, c in enumerate(order) if c is char)
        later = next(
            (
                i
                for c in order[at + 1 :]
                for i, w in enumerate(self.characters)
                if w is c
            ),
            len(self.characters),
        )
        self.characters.insert(later, char)

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
        if self.phase == "INITIATIVE":
            self._remove_initiative_row(char)
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
        owner = owner_name(summon)
        # Logged while it's still there, so players read it if they saw it.
        self._log_event(
            f"{owner or 'Its owner'} dismisses {summon['name']}",
            character=owner or summon["name"],
            action=Action.DISMISS,
            value=summon_event([summon]),
        )
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
            if not self._vanish_at_zero_hp(summon):
                self._rebuild_card(summon)

    def _vanish_at_zero_hp(self, summon: dict) -> bool:
        """summon has just dropped to 0 Hit Points: one that vanishes then
        (its spec's OnZeroHp, as its dict holds it) leaves the fight, logged
        as Action.DISMISS on its owner with "reason": "0 hp" (so the next
        encounter doesn't bring it back from an earlier one). One that dies
        stays, dead. Returns whether it vanished. Its caller is @undoable."""
        if summon.get("hp", 0) > 0 or not vanishes_at_zero_hp(summon):
            return False
        if not any(c is summon for c in self.characters):
            return False
        owner = owner_name(summon)
        # Logged while it's still there, so players read it if they saw it.
        self._log_event(
            f"{summon['name']} drops to 0 HP and vanishes",
            character=owner or summon["name"],
            action=Action.DISMISS,
            value=summon_event([summon], reason=VANISHED_REASON),
        )
        self._remove_from_fight(summon)
        self._save_fight_state()
        self._rebuild_cards()
        if self.phase == "COMBAT":
            self._refresh_turn()
        self._refresh_views()
        return True

    def _carry_summons_over(self, log_path: Path):
        """Start the encounter log at `log_path` (one not started yet) with
        the party's summons the last encounter left out, as it left them:
        their card (as it was built), Hit Points, conditions and choice. One
        dismissed or replaced since (Action.DISMISS) stays gone (last_seen).
        A long rest since ends a Reanimated Companion and rests a drake (its
        SummonSpec's lifetime)."""
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
                played.append((read_json(path), False))
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
                    keep_card(here, seen[0])
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
        if self._nothing_logged_here():
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
        new, rolls = self._bring_in(owner, feature, spec, ctx, gone)
        self._log_event(
            f"{_names(new)} joins the fight, already summoned{_rolled(rolls)}",
            note_turn=False,
            character=owner["name"],
            action=Action.SUMMON,
            value=summon_event(new, before_combat=True, initiative=rolls),
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


def _rolled(rolls: dict[str, int]) -> str:
    """What a summon line says of the initiative its summons rolled."""
    if not rolls:
        return ""
    if len(rolls) == 1:
        return f" (initiative {next(iter(rolls.values()))})"
    return " (initiative " + ", ".join(f"{n} {v}" for n, v in rolls.items()) + ")"


def _summon_label(spec: SummonSpec) -> str:
    """The menu's verb and name for summoning spec, by what it summons, not
    the feature: "Summon Drake Companion", "Summon Wildfire Spirit" (from
    Summon Wildfire Spirit), "Summon Dancing Item" (from Animating
    Performance). A source with several specs gets one entry for each."""
    return f"Summon {spec.name}"


def _unpaid_text(feature: Feature, spec: SummonSpec) -> str:
    """What owner lacks when they can't pay for spec: "no use of Drake
    Companion and no spell slot left"."""
    lacks = []
    for cost in spec.costs:
        if cost.spell_slot is None:
            lacks.append(f"no use of {cost.feature_use or feature.name}")
        elif cost.spell_slot == 1:
            lacks.append("no spell slot")
        else:
            lacks.append(f"no spell slot of level {cost.spell_slot} or higher")
    return " and ".join(lacks) + " left"


def _ability_name(ability) -> str | None:
    """A stat-block ability's name, as a MonsterAbility or as a log stores it."""
    if isinstance(ability, dict):
        return ability.get("name")
    return getattr(ability, "name", None)
