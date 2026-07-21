"""Global stylesheet — dark fantasy theme"""

QSS = """
QMainWindow, QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}

/* Combatant cards */
QFrame#combatantCard {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 6px;
}
QFrame#combatantCard[dead="true"] {
    background-color: #0e0e18;
    border: 2px solid #2a2a2a;
}
QFrame#combatantCard[dying="true"] {
    background-color: #1a0e2e;
    border: 2px solid #7a2fa0;
}
QFrame#combatantCard[stabilized="true"] {
    background-color: #0e1a18;
    border: 2px solid #2a6a5a;
}
QFrame#combatantCard[selected="true"] {
    background-color: #1e2d5a;
    border: 2px solid #ffffff;
}
QFrame#combatantCard[active="true"] {
    background-color: #2a2010;
    border: 2px solid #c9a84c;
}
QFrame#combatantCard[selected-active="true"] {
    background-color: #1a3a1a;
    border: 3px solid #ffffff;
    border-left: 3px solid #c9a84c;
    border-bottom: 3px solid #c9a84c;
}
QFrame#combatantCard[target="true"] {
    background-color: #3a1010;
    border: 2px solid #e74c3c;
}
QFrame#combatantCard[selected-target="true"] {
    background-color: #2a1020;
    border: 3px solid #ffffff;
    border-left: 3px solid #e74c3c;
    border-bottom: 3px solid #e74c3c;
}
QFrame#combatantCard[active-target="true"] {
    background-color: #3a1c10;
    border: 3px solid #c9a84c;
    border-left: 3px solid #e74c3c;
    border-bottom: 3px solid #e74c3c;
}
QFrame#combatantCard[selected-active-target="true"] {
    background-color: #2a2a1a;
    border: 3px solid #ffffff;
    border-left: 3px solid #c9a84c;
    border-bottom: 3px solid #e74c3c;
}

/* Control panel */
QFrame#controlPanel {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
}

/* Dividers */
QFrame#divider {
    background-color: #0f3460;
    max-height: 1px;
    min-height: 1px;
}

/* Section headers inside control panel */
QLabel#sectionHeader {
    color: #c9a84c;
    font-weight: bold;
    font-size: 11px;
}

/* Card name label */
QLabel#cardName {
    color: #c9a84c;
    font-weight: bold;
    font-size: 13px;
}

/* Secondary text */
QLabel#secondary {
    color: #a0a0b0;
    font-size: 11px;
}

/* Condition badge */
QLabel#conditionBadge {
    background-color: #7a5c00;
    color: #ffffff;
    border-radius: 3px;
    padding: 1px 4px;
    font-size: 10px;
}

/* Selected combatant label */
QLabel#selectedLabel {
    color: #e94560;
    font-weight: bold;
    font-size: 12px;
}

QLabel#targetLabel {
    color: #e74c3c;
    font-weight: bold;
    font-size: 12px;
}

/* HP bar */
QProgressBar {
    border: 1px solid #0f3460;
    border-radius: 3px;
    background-color: #555;
    text-align: center;
    color: #1a1a2e;
    font-size: 10px;
    font-weight: bold;
    min-height: 14px;
    max-height: 14px;
}
QProgressBar::chunk#hp_green  { background-color: #2ecc71; border-radius: 3px; }
QProgressBar::chunk#hp_orange { background-color: #e67e22; border-radius: 3px; }
QProgressBar::chunk#hp_red    { background-color: #e74c3c; border-radius: 3px; }
QProgressBar::chunk#hp_dead   { background-color: #555;    border-radius: 3px; }

/* Inputs */
QLineEdit {
    background-color: #0f3460;
    border: 1px solid #e94560;
    border-radius: 3px;
    color: #eaeaea;
    padding: 3px 5px;
}
QLineEdit:focus {
    border: 1px solid #c9a84c;
}

QComboBox {
    background-color: #0f3460;
    border: 1px solid #0f3460;
    border-radius: 3px;
    color: #eaeaea;
    padding: 2px 5px;
}
QComboBox::drop-down {
    border: none;
    width: 16px;
}
QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #eaeaea;
    selection-background-color: #0f3460;
}

/* Buttons — base */
QPushButton {
    background-color: #0f3460;
    color: #eaeaea;
    border: 1px solid #1a4a80;
    border-radius: 4px;
    padding: 4px 8px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #1a4a80;
}
QPushButton:pressed {
    background-color: #0a2540;
}
QPushButton:disabled {
    background-color: #0a1a30;
    color: #555;
    border-color: #0a2540;
}

/* Primary buttons (damage) */
QPushButton#primaryBtn {
    background-color: #3d1a2e;
    border: 1px solid #e94560;
    color: #e94560;
    font-weight: bold;
}
QPushButton#primaryBtn:hover {
    background-color: #5a2040;
}
QPushButton#primaryBtn:pressed {
    background-color: #2a0f1e;
}

/* Heal button */
QPushButton#healBtn {
    background-color: #1a3d2e;
    border: 1px solid #4caf82;
    color: #4caf82;
    font-weight: bold;
}
QPushButton#healBtn:hover {
    background-color: #204d38;
}
QPushButton#healBtn:pressed {
    background-color: #102a1e;
}

/* Temp HP button */
QPushButton#tempHpBtn {
    background-color: #1a2e3d;
    border: 1px solid #4a9fc4;
    color: #4a9fc4;
    font-weight: bold;
}
QPushButton#tempHpBtn:hover {
    background-color: #20384d;
}
QPushButton#tempHpBtn:pressed {
    background-color: #10202e;
}

/* Death save — fail */
QPushButton#deathFailBtn {
    background-color: #3d1a1a;
    border: 1px solid #c04040;
    color: #c04040;
    font-weight: bold;
}
QPushButton#deathFailBtn:hover { background-color: #4d2020; }
QPushButton#deathFailBtn:pressed { background-color: #2a1010; }
QPushButton#deathFailBtn:disabled { color: #555; border-color: #333; background: #1a1a1a; }

/* Death save — success */
QPushButton#deathSuccessBtn {
    background-color: #1a3d1a;
    border: 1px solid #40c040;
    color: #40c040;
    font-weight: bold;
}
QPushButton#deathSuccessBtn:hover { background-color: #204d20; }
QPushButton#deathSuccessBtn:pressed { background-color: #102a10; }
QPushButton#deathSuccessBtn:disabled { color: #555; border-color: #333; background: #1a1a1a; }

/* Scrollbar styling */
QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 0; }
"""
