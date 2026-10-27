---
name: run-apps
description: How to launch and look at this repo's apps - the PyQt6 combat simulator (RunCombatSimulator.py), the Character Creator GUI (RunCharacterCreatorUI.py) and a build's HTML character sheet - including a script that screenshots either window offscreen (no display, no event loop, no log written) and renders one build's sheet to a throwaway folder, so a change can be seen working, not just tested. Use whenever asked to run, start, open, show or screenshot an app or sheet, after any change under Builds/CharacterCreator/, Combat/CombatUIQt/ or Presentation/ to look at the result, and when the generic run skill looks for the project's launch recipe.
---

# Run and look at the apps

Tests prove behaviour. They don't show a squashed layout, an unreadable colour or a missing button. After a UI or sheet change, **look at it**.

## Screenshot (no display needed)

```bash
python .claude/skills/run-apps/screenshot.py combat [--scenario ashelm_church] [--size 1600x1000]
python .claude/skills/run-apps/screenshot.py creator [--load-build Builds/Characters/<File>.py] [--tab Equipment]
python .claude/skills/run-apps/screenshot.py sheet <part of build name> [--feature-tags]
```

- Each command prints the files it wrote, in a screenshots folder under the system temp directory (or `--out <dir>`). **Read the PNGs** to see them. For `sheet`, read the HTML, or diff it with the `snapshot-diffs` skill.
- The windows are built the same way the apps build them (`CombatAppQt(...)._build_window()`, `CreatorApp()` + `load_build`), on Qt's `offscreen` platform. No event loop, no session timer. The combat log goes to a temp folder, never a campaign's `CombatLogs/`.
- A modal dialog or message box that would block is skipped and printed. A load warning (the creator can't load multiclass builds, for example) shows up there.
- `creator` writes one PNG per tab (Basics, Level features, Equipment, Advanced) unless you pass `--tab`.
- Combat cards squash below the default size. Change `--size` only on purpose.

Gotchas the script already handles, which matter if you write your own Qt probe:

- On Windows the offscreen platform has no fonts, so every glyph is a box. Set `QT_QPA_FONTDIR` to `%WINDIR%\Fonts`.
- `Builds.CharacterCreator.Ui` creates Qt objects at import time. Create the `QApplication` **before** importing it, or the process dies silently (exit code 127, no traceback).
- Keep a reference to the `QApplication`. If it's garbage-collected, Qt aborts at the next widget (`tests/_combat_ui.py` holds it in a global for this reason).

## Launch for real (the user's display)

These open windows and block until closed, so run them only when the user wants the app open, never in an agent or a test:

| App | Command |
|---|---|
| Combat simulator | `python RunCombatSimulator.py --scenario <name>`. **Don't** pass `--player-log` or `--rest` unless asked: they write to the campaign's persistent party log. |
| Character Creator | `python RunCharacterCreatorUI.py [--load-build <path>]`. Its **Generate** button writes into `Builds/GeneratedBuilds/`. |
| Every sheet | `python RunCharacterCreator.py [--example] [--feature-tags]` writes `Output/<class>_<subclass>_<name>/`. Open `character.html` in a browser. |

The full flag lists are in [HOWTO.md](../../../HOWTO.md) sections 1-4. Encounter difficulty without a window: `python RunCombatSimulator.py --scenario <name> --difficulty`.
