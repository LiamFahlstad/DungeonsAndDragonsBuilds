"""Summons mixin for CombatAppQt: a player's summons (the dict side is
Combat/Summons.py, the questions a fight asks of them and the carry-over
Combat/Fight/summons.py) being summoned, dismissed, dying with their owner, coming
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

from Combat.Arena.arena import place_summons
from Combat.Definitions import Action, CombatStatus, Phase
from Combat.Effects.active_effects import held_by_concentration
from Combat.Summons import (
    VANISHED_REASON,
    SummonOption,
    SummonPayment,
    choice_of,
    cost_options,
    create,
    feature_summons,
    follows_owner,
    is_out,
    owner_name,
    place_after_owners,
    summon_event,
    vanishes_at_zero_hp,
)
from Model.Character import Character
from Model.Content.Feature import Feature
from Model.Content.Summons import OnZeroHp, SummonContext, SummonSpec

from Combat.Fight.effect_options import PactSlot, feature_action_cost
from Combat.Fight.summons import (
    already_summoned_options,
    carry_summons_over,
    owner_summons,
    room_for,
    same_summons,
    summon_owner,
    summon_source,
)
from .state import CombatWindowState
from Combat.Fight.stats import _default_stats
from .styles import QSS
from .undo import undoable


class SummonsMixin(CombatWindowState):
    """Mixin for players' summons."""

    def _summon_owner(self, char: dict) -> dict | None:
        return summon_owner(self.fight, char)

    def _owner_summons(self, owner: dict) -> list[dict]:
        return owner_summons(self.fight, owner)

    def _summon_source(
        self, summon: dict
    ) -> tuple[dict, Character, Feature, SummonSpec] | None:
        return summon_source(self.fight, summon)

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
                out = [
                    c
                    for c in same_summons(self.fight, char, feature, spec)
                    if is_out(c)
                ]
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
        if room_for(self.fight, owner, feature, spec, SummonContext()) is None:
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
            out = [
                c for c in same_summons(self.fight, owner, feature, spec) if is_out(c)
            ]
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
        gone = room_for(self.fight, owner, feature, spec, ctx)
        if gone is None:
            out = [
                c for c in same_summons(self.fight, owner, feature, spec) if is_out(c)
            ]
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
        if self.phase == Phase.COMBAT:
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
        for char in same_summons(self.fight, owner, feature, spec):
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
        # On the battle map, beside their owners (when they're on it).
        place_summons(new, self.characters, self._map_settings())
        own = [c for c in new if not follows_owner(c)]
        follow = [c for c in new if follows_owner(c)]
        rolls: dict[str, int] = {}
        if self.phase == Phase.COMBAT and self.initiative_order:
            # Whoever's turn it is keeps it.
            self.fight.follow_owners_in_turn_order(follow)
            for char in own:
                rolls[char["name"]] = self._roll_into_turn_order(char)
                self.fight.place_as_in_turn_order(char)
            self.characters[:] = place_after_owners(self.characters, follow)
            return rolls
        self.characters[:] = place_after_owners(self.characters, new)
        if self.phase == Phase.INITIATIVE:
            for char in own:
                self._add_initiative_row([char])
            if own:
                self._check_start_button()
        return rolls

    def _remove_from_fight(self, char: dict):
        """Take char out of the window and the turn order, keeping whoever's
        turn it is (the next one's, when it was char's). What it concentrates
        on ends first: nobody holds it once char is gone."""
        if CombatStatus.CONCENTRATING.value in char.get("conditions", []) or (
            held_by_concentration(self.characters, char["name"])
        ):
            self._end_concentration_spells(
                char, reason=f"{char['name']} leaves the fight"
            )
        self.fight.remove(char)
        if self.phase == Phase.INITIATIVE:
            self._remove_initiative_row(char)
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
        if self.phase == Phase.COMBAT:
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
        if self.phase == Phase.COMBAT:
            self._refresh_turn()
        self._refresh_views()
        return True

    def _carry_summons_over(self, log_path: Path):
        """Start the encounter log at `log_path` (one not started yet) with
        the party's summons the last encounter left out (carry_summons_over)."""
        if not self.player_log_file:
            return
        carry_summons_over(
            self.fight, self.player_log_file, self.player_log_data, log_path
        )

    def _already_summoned_options(self) -> list[SummonOption]:
        return already_summoned_options(self.fight)

    @undoable
    def _add_already_summoned(self, option: SummonOption):
        """Add a summon made before the fight (Add Combatant): out at full
        Hit Points after its owner, spending nothing."""
        if self._nothing_logged_here():
            return
        owner, feature, spec = option.owner, option.feature, option.spec
        ctx = SummonContext(choice=option.choice)
        gone = room_for(self.fight, owner, feature, spec, ctx)
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
        if self.phase == Phase.COMBAT:
            self._refresh_turn()
        self._refresh_views()


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
