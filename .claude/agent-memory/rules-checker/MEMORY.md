# rules-checker lessons

- 2026-10-27: Combat/ conditions (Grappled etc.) are only labels + reference text (Combat/Definitions.py); no escape DC, Speed 0 or auto-ending is simulated. Don't hunt for grapple mechanics there.
- 2026-10-27: Feats have no file under SourceTexts/; the feat class's get_description() holds the source wording. Monk text is SourceTexts/ClassTexts/monk.txt.
- 2026-10-27: Martial Arts reaches the Unarmed Strike only through MonkBase default_equipment (starting class). A multiclass that doesn't start as Monk shows a 1d1 Str strike; check such builds when judging unarmed numbers.
- 2026-10-27: Temp HP stacking, death-save details (nat 1/20, damage at 0 HP), massive damage and Unconscious-at-0-HP live only in "Playing the Game" (not local). Locally only Hit-Points.md ("can't have less than 0") and Death-Saving-Throw.md ("A player character") apply, so the rest goes under Needs a ruling.
- 2026-10-27: Combat/CombatUIQt mixins can be probed without a Qt app: subclass the mixin, set phase="SETUP" and _open_undo_point=None (so @undoable just runs), and stub _log_event/_rebuild_card plus the input widgets (.text()/.currentData()).
