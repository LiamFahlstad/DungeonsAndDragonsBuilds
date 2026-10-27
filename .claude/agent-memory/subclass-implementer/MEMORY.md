# subclass-implementer lessons

- 2026-10-27: Example builds are named `Builds/Examples/Y2024_<Class>_<Subclass>_<Name>.py` (class `Y2024<Class><Subclass><Name>CharacterBuilder`), not `Example<Class><Subclass>.py` as the prompt says. They are auto-discovered by `RunCharacterCreator.py --example`.
- 2026-10-27: Registering a new 2024 subclass = two entries in `Scrapers/GenerateClassHandouts.py` (description dict near `# --- <Class> ---`, and `_SUBCLASS_RAW` with `_s2024("<text stem>")`). Verify with `python Scrapers/GenerateClassHandouts.py`.
- 2026-10-27: Fighter's Tactical Shift and Tactical Mind are extensions of `SecondWind`; a Tactical Shift rider must use `extends=FighterFeatures.SecondWind` (a type parent only matches top-level grants).
- 2026-10-27: Working-tree files are CRLF (core.autocrlf=true). A Python read/write script with `newline=''` silently converts a whole file to LF; prefer Edit, or write bytes back with `\r\n`.
- 2026-10-27: During `UPDATE_SNAPSHOTS=1 ... -k <new build>`, `test_creator_roundtrip` fails with KeyError and order-invariance may fail (goldens loaded before the rewrite); both pass on the plain rerun.
