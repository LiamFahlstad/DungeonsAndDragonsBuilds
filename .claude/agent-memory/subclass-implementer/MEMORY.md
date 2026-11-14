# subclass-implementer lessons

- 2026-10-27: Fighter's Tactical Shift and Tactical Mind are extensions of `SecondWind`; a Tactical Shift rider must use `extends=FighterFeatures.SecondWind` (a type parent only matches top-level grants).
- 2026-10-27: Working-tree files are CRLF (core.autocrlf=true). A Python read/write script with `newline=''` silently converts a whole file to LF; prefer Edit, or write bytes back with `\r\n`.
- 2026-10-27: During `UPDATE_SNAPSHOTS=1 ... -k <new build>`, `test_creator_roundtrip` fails with KeyError and order-invariance may fail (goldens loaded before the rewrite); both pass on the plain rerun.
- 2026-11-14: A Channel Divinity option (Holy Bolt), a Cunning Strike option (Panache) or a Patient Defense rider is itself an extension, so it can't be extended by type: Cunning Strike options extend `RogueFeatures.SneakAttack`, Patient Defense riders extend `MonkFeatures.MonksFocus`, and a later upgrade of a Channel Divinity option is granted on its own.
- 2026-11-14: A subclass can't remove or replace a base-class feature (DI-089). Grant the replacement plainly and say in its text what it replaces.
- 2026-11-14: A spell can be granted only once per class (`resolve_spells` keys on name + granted_by class); a feature can't re-grant via `granted_spells()` a spell the subclass spell table already grants. Put that free-cast rule in the feature text instead.
