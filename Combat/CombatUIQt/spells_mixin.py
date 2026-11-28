"""Spells mixin for CombatAppQt."""

from Combat.Fight.badge_text import spell_badge_color, spell_badge_description
from Combat.Fight.spells import (
    active_spell_record,
    log_spell_cast,
    spell_called,
    spell_recipients,
    tick,
    ticks_now,
    use_slot,
)
from Combat.Definitions import Action
from Combat.Effects.active_effects import (
    SPELL,
    badge_modifiers,
    describe,
    link_concentration,
    note_origin,
)
from Combat.PlayerCombatant import max_pact_slots
from Combat.Fight.effect_options import PactSlot, casting_time_cost
from Model.Content.CombatAdjustments import EffectSource, adjusted_effects
from Combat.Fight.resources import spell_slot_lack
from Combat.Fight.cascade import (
    clear_concentration_if_unused,
    end_concentration_spells,
    end_linked_effects,
    end_when,
    end_spell_effects,
    holder_of,
    start_concentration,
)
from Model.Content.CombatModifiers import EndEvent
from .state import CombatWindowState
from .steps import run_step
from .undo import undoable


class SpellsMixin(CombatWindowState):
    """Mixin for spell-related methods."""

    @undoable
    def _cast_spell_slot_level(self, level: int):
        """Spend one of the source's slots of `level`: a Pact Magic slot for a
        PactSlot, else a spell slot, or a Pact Magic slot when no spell slot
        of that level is left (so the 1-9 keys work for a Warlock too)."""
        char = self.selected_character
        if not char:
            self._show_status("Nothing spent: left-click a card to pick a source.")
            return
        if self._spend_slot(char, level):
            self._refresh_selected_card()

    def _spend_slot(self, char: dict, level: int) -> bool:
        """Spend one of char's slots of `level`, as _cast_spell_slot_level
        does; False, saying why, when there's none left."""
        asked_for_pact = isinstance(level, PactSlot)
        level = int(level)
        if use_slot(self.logger, char, level, asked_for_pact) is None:
            kind = "Pact Magic slots" if asked_for_pact else "slots"
            self._show_status(
                f"Nothing spent: {char['name']} has no level {level} {kind} left."
            )
            return False
        return True

    @undoable
    def _regain_spell_slot(self):
        """Give the source back a slot of the level picked: a Pact Magic slot
        while it has fewer of that level than when rested, else a spell slot."""
        char = self.selected_character
        if not char:
            self._show_status("Nothing regained: left-click a card to pick a source.")
            return
        level = self.spell_combo.currentIndex() + 1
        pact_left = char.get("pact_slots", {}).get(level, 0)
        pact = pact_left < max_pact_slots(char).get(level, 0)
        slots = char.setdefault("pact_slots" if pact else "spell_slots", {})
        slots[level] = slots.get(level, 0) + 1
        kind = "Pact Magic slot" if pact else "spell slot"
        self._log_event(
            f"{char['name']} regains a Level {level} {kind}",
            character=char["name"],
            action=Action.ADD_PACT_SLOT if pact else Action.ADD_SPELL_SLOT,
            value=level,
        )
        self._refresh_selected_card()

    def _clear_concentration_if_unused(self, char: dict):
        """Remove Concentrating if no remaining active spell on char still
        needs it: Combat/Fight/cascade.py's clear_concentration_if_unused."""
        clear_concentration_if_unused(char)

    def _end_concentration_spells(self, char: dict, reason: str = "concentration lost"):
        """End char's concentration spells and every effect still linked to
        its concentration, whenever Concentrating goes by any path other
        than the spell's own duration expiring: cascade.py's
        end_concentration_spells."""
        run_step(self, end_concentration_spells, char, reason)

    def _end_linked_effects(self, char: dict):
        """Every effect lasting while char concentrates ends:
        cascade.py's end_linked_effects."""
        run_step(self, end_linked_effects, char)

    def _end_spell_effects(self, entry: dict):
        """What an ended concentration spell put on its targets comes off
        them: cascade.py's end_spell_effects."""
        run_step(self, end_spell_effects, entry)

    def _held_by_effect(self, applied: dict, excluding: dict | None = None) -> bool:
        """Whether a running spell, other than `excluding`, put this condition
        on this target."""
        return self._holder_of(applied, excluding) is not None

    def _holder_of(
        self, applied: dict, excluding: dict | None = None
    ) -> tuple[dict, dict] | None:
        """The caster and active spell, other than `excluding`, that put this
        condition on this target and still run: cascade.py's holder_of."""
        return holder_of(self.characters, applied, excluding)

    def _start_concentration(self, source: dict, name: str):
        """Source starts concentrating on `name`: Combat/Fight/cascade.py's
        start_concentration."""
        run_step(self, start_concentration, source, name)

    def _tick_active_spells(self, started: list[dict], new_round: bool):
        """Deduct 6 seconds (one round) from the active spell timers due as the
        turn passes to `started` (`new_round` when that begins a round),
        expiring and logging any that reach zero, and dropping Concentrating if
        its spell expired. A timer counts on the turn the spell was cast, like
        a timed condition, so a late caster's spell lasts as long as anyone's;
        at the round's start if that combatant has no turn (any more), or for
        a timer that doesn't say."""
        started_names = {c["name"] for c in started}
        in_order = {c["name"] for c in self.initiative_order}
        ticked = False
        for char in self.characters:
            active_spells = char.get("active_spells")
            if not active_spells:
                continue
            remaining = []
            expired_concentration = False
            for entry in active_spells:
                if not ticks_now(entry, started_names, in_order, new_round):
                    remaining.append(entry)
                    continue
                ticked = True
                if not tick(entry):
                    remaining.append(entry)
                else:
                    self._log_event(
                        f"{char['name']}'s {entry['name']} expires",
                        note_turn=False,
                        character=char["name"],
                        value={"condition": entry["name"]},
                    )
                    if entry.get("concentration"):
                        expired_concentration = True
                    self._end_spell_effects(entry)
            char["active_spells"] = remaining
            if expired_concentration:
                self._clear_concentration_if_unused(char)
        if ticked:
            self._rebuild_cards()

    @undoable
    def _remove_active_spell(self, char: dict, entry: dict):
        """Manually dismiss an active spell before its duration timer runs out."""
        active_spells = char.get("active_spells") or []
        if entry not in active_spells:
            return
        active_spells.remove(entry)
        self._log_event(
            f"{char['name']}'s {entry['name']} ends early",
            character=char["name"],
            value={"condition": entry["name"]},
        )
        self._end_spell_effects(entry)
        if entry.get("concentration"):
            self._clear_concentration_if_unused(char)
        self._rebuild_card(char)

    def _all_spells(self) -> list:
        """Every spell in the game, by level then name, read once (Cast Spell
        and the Custom Effect dialog's picker both list them)."""
        if not hasattr(self, "_spells_cache"):
            from CharacterContent.Spells.SpellFactory import SpellFactory

            self._spells_cache = sorted(
                SpellFactory.all_spells(), key=lambda s: (s.level, s.name)
            )
        return self._spells_cache

    def _spell_named(self, name: str):
        """The spell called `name` (as a Cast Spell badge is), or None:
        Combat/Fight/spells.py's spell_called."""
        return spell_called(name)

    def _count_spell_cast(
        self, caster: dict, name: str, level: int, slot_level: int | None
    ):
        """Count and log a cast: Combat/Fight/spells.py's log_spell_cast;
        and end what ends as caster casts a spell (Invisibility)."""
        log_spell_cast(self.logger, caster, name, level, slot_level)
        run_step(self, end_when, caster, EndEvent.CASTS_SPELL)

    @undoable
    def _apply_cast_spell(self, spell, slot_level: int | None = None):
        """Cast a spell. The spell's own declared metadata decides what happens:
        spell.target decides who is affected (SELF/None always means the
        caster; AREA means whichever targets are selected, possibly none, since
        the caster alone tracks its duration and concentration; any other target
        type requires a target to be selected first),
        spell.casting_time_type logs the action-economy cost on the caster,
        spell.is_concentration breaks any prior concentration and marks the
        caster Concentrating (concentration always belongs to the caster, even
        when the spell's effect lands on a target), and spell.duration_seconds
        (if set) adds a ticking duration bar on every recipient. Every cast also
        adds a condition badge (with the description as a hover tooltip) on its
        recipient(s) and increments the caster's spells_cast stat. slot_level
        is the spell slot it uses, higher than the spell's level to upcast it;
        None uses no slot.

        No window path calls it (the Use / Cast dialog casts through
        _apply_effect_to_targets): tests cast a spell through it. Kept until
        step 5.4's Use / Cast slice (plan R43)."""
        source = self.selected_character
        if source is None:
            self._show_status("No spell cast: left-click a card to pick a source.")
            return
        if not self._can_cast_or_say(source, spell.name):
            return

        recipients = spell_recipients(spell, source, self.target_characters)
        if recipients is None:
            target = spell.target.value if spell.target is not None else ""
            self._show_status(
                f"No spell cast: {spell.name} needs a target"
                f" ({target}). Right-click a card."
            )
            return

        # Action economy: the caster spends the action, regardless of who it affects
        action_cost = casting_time_cost(spell)
        lacks = [
            spell_slot_lack(source, spell.level, slot_level),
            self._action_lack(source, action_cost),
        ]
        if not self._go_ahead_anyway(source, f"Cast {spell.name}", lacks):
            return

        self._count_spell_cast(source, spell.name, spell.level, slot_level)
        if slot_level is not None:
            self._cast_spell_slot_level(slot_level)

        if spell.is_concentration:
            self._start_concentration(source, spell.name)

        if action_cost is not None:
            self._add_action_use(action_cost, ask=False)

        tooltip_html = spell_badge_description(spell)
        badge_color = spell_badge_color(spell)

        # Duration -> a ticking bar, always tracked on the caster (source) regardless
        # of who the badge lands on — _tick_active_spells/_clear_concentration_if_unused
        # clear Concentrating off whichever character owns the expiring entry, and
        # Concentrating itself is only ever added to the caster.
        duration = spell.duration_seconds
        has_duration = bool(duration)

        # Store the tooltip description and badge color, and add the condition,
        # on every recipient (the caster for a self-cast, each target otherwise).
        applied = []
        if spell.is_concentration:
            for char in recipients:
                row = {"target": char["name"], "condition": spell.name}
                if spell.name not in char["conditions"] or self._held_by_effect(row):
                    applied.append(row)
        # What the badge does while it's on (Bless's 1d4), as the spell says.
        # And what the caster's features change about it.
        effects = adjusted_effects(
            source.get("_stat_block"),
            EffectSource(spell.name, spell=spell, with_slot=slot_level is not None),
            spell.combat_effects(),
        )
        modifiers = badge_modifiers(effects, spell.name)
        for char in list(recipients):
            describe(char, spell.name, tooltip_html, badge_color, SPELL)
            self._add_condition_to(char, spell.name, source=source)
            note_origin(char, spell.name, source=spell.name, caster=source["name"])
            self._give_badge_modifiers(
                char,
                spell.name,
                modifiers,
                levels_up=max((slot_level or spell.level) - spell.level, 0),
                source=source,
            )
            # The active spell below holds what it put on whom.
            if has_duration and any(r["target"] == char["name"] for r in applied):
                link_concentration(char, spell.name, source["name"])

        if has_duration:
            turn = self._current_turn_group()
            source.setdefault("active_spells", []).append(
                active_spell_record(
                    spell.name,
                    duration,
                    spell.is_concentration,
                    applied,
                    turn[0]["name"] if turn else None,
                )
            )

        self._save_fight_state()
        self._refresh_selected_card()
