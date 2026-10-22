"""The combat UI's More Info dialog (DialogsMixin._show_more_info)."""

from PyQt6.QtWidgets import QLabel, QPushButton

from Combat.Monsters.CR_0.monsters import DraconicSpirit
from tests._combat_ui import make_ui, open_dialog


def _texts(dialog) -> list[str]:
    return [w.text() for w in dialog.findChildren((QLabel, QPushButton))]


def test_a_save_with_a_prose_dc_opens_without_a_probability_table(
    tmp_path, monkeypatch
):
    # Draconic Spirit's Breath Weapon DC "equals your spell save DC": there's
    # no number to tabulate, so it's listed as a plain ability.
    ui = make_ui(tmp_path, [DraconicSpirit()])
    ui.selected_character = ui.characters[0]
    texts = _texts(open_dialog(monkeypatch, ui._show_more_info))
    breath = [t for t in texts if t.startswith("<b><i>Breath Weapon.")]
    assert breath == [
        "<b><i>Breath Weapon.</i></b> Dexterity Saving Throw: DC equals your"
        " spell save DC, each creature in a 30-foot Cone. Failure: 2d6 damage of"
        " a type this spirit has Resistance to (your choice when you cast the"
        " spell). Success: Half damage."
    ]
