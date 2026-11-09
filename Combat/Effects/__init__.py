"""Lasting effects in a fight, without Qt, so the UI and the tests share them
(Notes/combat-effects-plan.md, Phase 3).

- active_effects: the record. Each combatant's lasting effects are one list,
  char["active_effects"]; the combat window (Combat/CombatUIQt/) calls in here
  to add, end and tick them.
- modifiers: what those effects do to rolls, AC and damage, read from their
  CombatModifiers."""
