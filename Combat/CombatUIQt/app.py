"""Main CombatAppQt class."""

import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QApplication

import Definitions
from Combat.Definitions import BasicCombatantData, Condition, ExtendedCombatantData, Visibility
from Features.Equipment import Armor
from .damage_mixin import DamageMixin
from .conditions_mixin import ConditionsMixin
from .spells_mixin import SpellsMixin
from .turns_mixin import TurnsMixin
from .cards_mixin import CardsMixin
from .logging_mixin import LoggingMixin
from .dialogs_mixin import DialogsMixin
from .window_mixin import WindowMixin
from .styles import QSS
from .stats import _default_stats


class CombatAppQt(DamageMixin, ConditionsMixin, SpellsMixin, TurnsMixin, CardsMixin, LoggingMixin, DialogsMixin, WindowMixin):
    ACTION_ECONOMY_TYPES: list[str] = ["Action", "Bonus Action", "Reaction"]
    ACTION_ECONOMY_SHORTCUTS: dict[str, str] = {
        "A": "Action",
        "B": "Bonus Action",
        "R": "Reaction",
    }

    def __init__(
        self,
        combatants: list[BasicCombatantData],
        character_sheets: list,
        combatants_per_column: int = 4,
        resume_log_path: str | None = None,
    ):
        self.combatants_per_column = combatants_per_column
        self._resume_log_path = resume_log_path

        # ---- data ----
        self.characters: list[dict] = []
        for cs in character_sheets:
            self._add_from_character_sheet(cs)
        for c in combatants:
            self._add_basic_combatant(c)

        self.conditions = Condition.list_all()
        self.visibility_states = Visibility.list_all()
        self.selected_character: dict | None = None
        self.target_character: dict | None = None
        self.round_number = 1
        self.history: list[tuple] = []

        # --- Phase / initiative state ---
        self.phase: str = "INITIATIVE"
        self.initiative_order: list[dict] = []
        self.current_turn_idx: int = 0

        log_dir = Path("CombatLogs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = log_dir / f"combat_log_{timestamp}.json"
        self._write_log({})

        # card widget registry: maps id(char_dict) -> QFrame
        self._card_widgets: dict = {}

        # initiative input registry: maps id(char_dict) -> QLineEdit
        self._initiative_inputs: dict = {}

    def _add_from_character_sheet(self, character_sheet):
        from Spells.SpellFactory import SpellFactory

        character = character_sheet.setup_character_stat_block()
        ac = character.calculate_armor_class()
        if Armor.ShieldArmor in [type(a) for a in character_sheet.armors]:
            ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"
        else:
            ac = f"{ac} (no Shield)"
        try:
            spell_slots = character.get_spell_slots()
        except ValueError:
            spell_slots = {}
        hp = character.calculate_hit_points()

        # Apply weapon masteries to live weapon objects
        weapons = list(character_sheet.weapons)
        if character_sheet.weapon_masteries:
            mastery_types = {type(m) for m in character_sheet.weapon_masteries}
            for w in weapons:
                if type(w) in mastery_types:
                    w.player_has_mastery = True

        # Pre-compute spell levels (display_name, level, Ability enum)
        spells_with_level = []
        spell_objects: dict[str, object] = {}
        for spell_name, ability, ruling in character_sheet.spells:
            display_name = getattr(spell_name, "value", str(spell_name))
            try:
                spell_obj = SpellFactory.create(spell_name, ability, ruling)
                spells_with_level.append((display_name, spell_obj.level, ability))
                spell_objects[display_name] = spell_obj
            except Exception:
                spells_with_level.append((display_name, 0, ability))

        self.characters.append(
            {
                "name": character_sheet.character_name,
                "create_name": character_sheet.character_name,
                "hp": hp,
                "max_hp": hp,
                "ac": ac,
                "temp_hp": 0,
                "conditions": [],
                "visibility_states": [],
                "death_saves_fail": 0,
                "death_saves_success": 0,
                "stats": _default_stats(),
                "spell_slots": spell_slots,
                "Ability Scores": {
                    ability.short_name: character.get_ability_score(ability)
                    for ability in Definitions.Ability
                },
                "Saving Throws": {
                    ability.short_name: character.get_saving_throw_modifier(ability)
                    for ability in Definitions.Ability
                },
                "_is_player": True,
                "_stat_block": character,
                "_weapons_objects": weapons,
                "class_levels": {
                    cls.value: lvl
                    for cls, lvl in character_sheet.level_per_class.items()
                },
                "subclass": character_sheet.character_subclass or "",
                "proficiency_bonus": character.get_proficiency_bonus(),
                "speed": character_sheet.speed or "",
                "size": character_sheet.size.value if character_sheet.size else "",
                "spells_with_level": spells_with_level,
                "_spell_objects": spell_objects,
                "features": [
                    getattr(f, "name", type(f).__name__)
                    for f in character_sheet.features
                ],
                "_feature_objects": list(character_sheet.features),
                "invocations": list(character_sheet.invocations),
            }
        )

    def _add_basic_combatant(self, combatant: BasicCombatantData):
        char = {
            "name": combatant.combatant_type,
            "create_name": combatant.create_name if combatant.create_name is not None else combatant.combatant_type,
            "combatant_type": combatant.combatant_type,
            "hp": combatant.hp,
            "max_hp": combatant.max_hp,
            "ac": combatant.ac,
            "temp_hp": combatant.temp_hp,
            "conditions": [cond.value for cond in combatant.conditions],
            "visibility_states": [vis.value for vis in (combatant.visibility_states or [])],
            "death_saves_fail": 0,
            "death_saves_success": 0,
            "stats": _default_stats(),
            "spell_slots": combatant.spell_slots,
            "Ability Scores": combatant.ability_scores,
            "Saving Throws": combatant.saving_throws,
        }
        if isinstance(combatant, ExtendedCombatantData):
            char.update(
                {
                    "cr": combatant.cr,
                    "monster_type": combatant.monster_type,
                    "ac_note": combatant.ac_note,
                    "hp_formula": combatant.hp_formula,
                    "speed": combatant.speed,
                    "skills": combatant.skills,
                    "damage_vulnerabilities": combatant.damage_vulnerabilities,
                    "damage_resistances": combatant.damage_resistances,
                    "damage_immunities": combatant.damage_immunities,
                    "condition_immunities": combatant.condition_immunities,
                    "senses": combatant.senses,
                    "languages": combatant.languages,
                    "traits": combatant.traits,
                    "actions": combatant.actions,
                    "bonus_actions": combatant.bonus_actions,
                    "reactions": combatant.reactions,
                    "legendary_actions": combatant.legendary_actions,
                    "legendary_resistances": combatant.legendary_resistances,
                    "lair_actions": combatant.lair_actions,
                    "mythic_actions": combatant.mythic_actions,
                }
            )
        self.characters.append(char)

    def run(self):
        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyleSheet(QSS)

        self._build_window()

        if self._resume_log_path:
            self._load_log_from_path(self._resume_log_path)

        self._window.show()
        sys.exit(app.exec())
