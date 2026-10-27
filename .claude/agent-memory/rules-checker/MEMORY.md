# rules-checker lessons

- 2026-10-27: Combat/ conditions (Grappled etc.) are only labels + reference text (Combat/Definitions.py); no escape DC, Speed 0 or auto-ending is simulated. Don't hunt for grapple mechanics there.
- 2026-10-27: Feats have no file under SourceTexts/; the feat class's get_description() holds the source wording. Monk text is SourceTexts/ClassTexts/monk.txt.
- 2026-10-27: Martial Arts reaches the Unarmed Strike only through MonkBase default_equipment (starting class). A multiclass that doesn't start as Monk shows a 1d1 Str strike; check such builds when judging unarmed numbers.
