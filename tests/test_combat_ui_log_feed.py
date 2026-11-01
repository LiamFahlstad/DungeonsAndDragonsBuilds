"""The encounter log under the turn column (log_feed.py): always open, up to
date with every line and undo, and scrolling only when the GM wants it to."""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.log_feed import log_feed_html
from tests._combat_ui import make_ui

MANY = 80


def _start(ui):
    pirate, tiger = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()


@pytest.fixture
def fight(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    _start(ui)
    pirate, tiger = ui.characters
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    return ui


@pytest.fixture
def shown(fight):
    """The fight in a shown window, for what depends on the real layout."""
    fight._window.resize(1600, 1000)
    fight._window.show()
    QApplication.processEvents()
    return fight


def _settled(ui) -> str:
    """Let the deferred refresh run; the feed's text."""
    QApplication.processEvents()
    return ui._log_feed.toPlainText()


def _fill(ui, lines: int = MANY):
    for i in range(lines):
        ui._log_event(f"Line {i}")
    _settled(ui)


def _hit(ui, amount: int = 5):
    ui.damage_type_combo.setCurrentIndex(1)  # reset to "none" after every hit
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def _bar(ui):
    return ui._log_feed.verticalScrollBar()


def _at_end(ui) -> bool:
    return _bar(ui).value() == _bar(ui).maximum()


def test_a_logged_line_appears_without_touching_a_card(fight):
    fight._log_event("The door creaks open")
    assert "The door creaks open" in _settled(fight)


def test_the_feed_has_the_lines_the_players_dont_get(fight):
    fight._log_event("The secret door opens", public=False)
    assert "The secret door opens" in _settled(fight)


def test_a_hit_reads_the_same_as_in_the_log(fight):
    _hit(fight)
    assert "Tiger takes 5 Acid damage from Pirate" in _settled(fight)


def test_undo_takes_the_line_back_out(fight):
    _hit(fight)
    assert "takes 5" in _settled(fight)
    fight._undo_last()
    assert "takes 5" not in _settled(fight)


def test_a_new_turn_and_round_get_headings(fight):
    fight._log_event("First")
    fight._advance_turn()
    fight._log_event("Second")
    fight._advance_turn()
    fight._log_event("Third")
    assert _settled(fight).split("\n") == [
        "Round 1",
        "Pirate",
        "First",
        "Tiger",
        "Second",
        "Round 2",
        "Pirate",
        "Third",
    ]


def test_a_groups_turn_has_one_heading():
    log = {
        "round_1": [
            {"text": "[Goblins's turn] One"},
            "[Goblins's turn] Two, from an old log",
        ]
    }
    assert log_feed_html(log).count("Goblins") == 1


def test_a_name_with_an_apostrophe_keeps_its_heading():
    html = log_feed_html({"round_1": ["[D'Arc's turn] D'Arc uses Action"]})
    assert ">D&#x27;Arc</p>" in html
    assert "turn]" not in html


def test_a_line_outside_a_turn_stays_as_it_is():
    html = log_feed_html({"round_1": ["Vine added to the encounter"]})
    assert "Vine added to the encounter" in html


def test_a_line_cant_be_read_as_markup():
    html = log_feed_html({"round_1": ["<b>Bob</b> & co"]})
    assert "<b>" not in html
    assert "&lt;b&gt;Bob&lt;/b&gt; &amp; co" in html


def test_rounds_sort_as_numbers_and_other_keys_are_left_out():
    log = {"round_10": ["Late"], "round_2": ["Early"], "round_number": 10}
    html = log_feed_html(log)
    assert html.index("Early") < html.index("Late")
    assert "Round number" not in html


def test_the_feed_follows_the_newest_line(shown):
    _fill(shown)
    assert _bar(shown).maximum() > 0, "the test needs a log long enough to scroll"
    assert _at_end(shown)
    shown._log_event("Newest")
    _settled(shown)
    assert _at_end(shown)


def test_scrolling_back_stays_put_while_lines_arrive(shown):
    _fill(shown)
    _bar(shown).setValue(10)
    shown._log_event("Newest")
    assert "Newest" in _settled(shown)
    assert _bar(shown).value() == 10


def test_scrolling_back_to_the_end_follows_again(shown):
    _fill(shown)
    _bar(shown).setValue(10)
    _bar(shown).setValue(_bar(shown).maximum())
    shown._log_event("Newest")
    _settled(shown)
    assert _at_end(shown)


def test_a_refresh_without_new_lines_leaves_the_text_alone(shown, monkeypatch):
    _fill(shown)
    _bar(shown).setValue(10)
    monkeypatch.setattr(
        shown._log_feed, "setHtml", lambda html: pytest.fail("replaced the text")
    )
    shown._refresh_views()
    assert _bar(shown).value() == 10


def test_undo_while_scrolled_back_stays_put(shown):
    _fill(shown)
    _hit(shown)
    _settled(shown)
    _bar(shown).setValue(10)
    shown._undo_last()
    assert "takes 5" not in _settled(shown)
    assert _bar(shown).value() == 10


def test_a_continued_fight_opens_at_its_newest_line(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    _start(ui)
    _fill(ui)

    fresh = make_ui(tmp_path, [])
    fresh._window.resize(1600, 1000)
    fresh._window.show()
    fresh._load_log_from_path(str(ui.log_file))
    assert f"Line {MANY - 1}" in _settled(fresh)
    assert _bar(fresh).maximum() > 0
    assert _at_end(fresh)
    fresh._log_event("Newest")
    _settled(fresh)
    assert _at_end(fresh), "it still follows afterwards"


def test_a_new_short_log_follows_after_a_long_one_scrolled_back(shown):
    _fill(shown)
    _bar(shown).setValue(10)
    shown._log_feed.show_log({"round_1": ["Only line"]})
    QApplication.processEvents()
    assert _bar(shown).maximum() == 0
    shown._log_feed.show_log({"round_1": [f"Line {i}" for i in range(MANY)]})
    QApplication.processEvents()
    assert _bar(shown).maximum() > 0
    assert _at_end(shown)


def test_clicking_the_feed_leaves_the_damage_field_focused(shown):
    shown._window.activateWindow()
    shown.damage_input.setFocus()
    QApplication.processEvents()
    assert QApplication.focusWidget() is shown.damage_input
    QTest.mouseClick(shown._log_feed.viewport(), Qt.MouseButton.LeftButton)
    assert QApplication.focusWidget() is shown.damage_input


def test_the_feed_sits_below_the_now_label(shown):
    now = shown._turn_now_label.mapToGlobal(shown._turn_now_label.rect().topLeft())
    feed = shown._log_feed.mapToGlobal(shown._log_feed.rect().topLeft())
    assert feed.y() > now.y()
    assert shown._log_feed.isVisible()
    assert shown._log_feed.height() >= 120
