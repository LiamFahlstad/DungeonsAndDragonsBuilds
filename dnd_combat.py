from enum import Enum
import tkinter as tk
import json
from pathlib import Path

import CharacterSheetCreator
import Definitions
from Features import Armor


class Action(str, Enum):
    HEAL = "heal"
    DAMAGE = "damage"
    ADD_CONDITION = "add_condition"
    REMOVE_CONDITION = "remove_condition"
    REMOVE_SPELL_SLOT = "remove_spell_slot"


class Condition(str, Enum):
    BLINDED = "Blinded"
    CHARMED = "Charmed"
    CONCENTRATING = "Concentrating"
    FRIGHTENED = "Frightened"
    GRAPPLED = "Grappled"
    PARALYZED = "Paralyzed"
    POISONED = "Poisoned"
    PRONE = "Prone"
    STUNNED = "Stunned"

    @staticmethod
    def list_all():
        return [cond.value for cond in Condition]


class CombatApp:
    def __init__(
        self, root, character_sheets: list[CharacterSheetCreator.CharacterSheetData]
    ):
        self.root = root
        self.root.title("DnD Combat Engine")

        # -------- DATA --------
        self.characters = [
            {"name": "Hero", "hp": 20, "ac": 15, "temp_hp": 0, "conditions": []},
            {"name": "Goblin", "hp": 7, "ac": 13, "temp_hp": 0, "conditions": []},
        ]
        for character_sheet in character_sheets:
            character = character_sheet.setup_character_stat_block()
            ac = character.calculate_armor_class()
            if Armor.ShieldArmor in [type(armor) for armor in character_sheet.armors]:
                ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"
            else:
                ac = f"{ac} (no Shield)"
            try:
                character_spell_slots = character.get_spell_slots()
            except ValueError:
                character_spell_slots = {}
            self.characters.append(
                {
                    "name": character_sheet.character_name,
                    "hp": character.calculate_hit_points(),  # Placeholder HP
                    "ac": ac,  # Placeholder AC
                    "temp_hp": 0,
                    "conditions": [],
                    "spell_slots": character_spell_slots,
                    "Ability Scores": {
                        ability.name: character.get_ability_score(ability)
                        for ability in Definitions.Ability
                    },
                    "Saving Throws": {
                        ability.name: character.get_saving_throw_modifier(ability)
                        for ability in Definitions.Ability
                    },
                }
            )

        self.conditions = Condition.list_all()

        self.selected_character = None
        self.round_number = 1
        self.history: list[tuple[Action, str | int]] = []
        self.log_file = Path("combat_log.json")
        self.log_file.write_text("{}")

        # -------- UI --------
        self.build_ui()
        self.refresh_ui()

    # -------- LOGGING --------
    def log_event(self, text):
        data = json.loads(self.log_file.read_text())
        key = f"round_{self.round_number}"
        data.setdefault(key, []).append(text)
        self.log_file.write_text(json.dumps(data, indent=2))

    # -------- ACTIONS --------
    def select_character(self, char):
        self.selected_character = char
        self.selected_label.config(text=f"Selected: {char['name']}")
        self.refresh_ui()

    def apply_damage(self):
        if not self.selected_character:
            return
        try:
            dmg = int(self.damage_var.get())
        except ValueError:
            return

        self.selected_character["hp"] -= dmg
        self.history.append((Action.DAMAGE, dmg))
        self.log_event(f"{self.selected_character['name']} takes {dmg} damage")
        self.refresh_ui()

    def apply_heal(self):
        if not self.selected_character:
            return
        try:
            heal = int(self.heal_var.get())
        except ValueError:
            return

        self.selected_character["hp"] += heal
        self.history.append((Action.HEAL, heal))
        self.log_event(f"{self.selected_character['name']} heals {heal} HP")
        self.refresh_ui()

    def apply_condition(self):
        if not self.selected_character:
            return

        cond = self.condition_var.get()
        if cond not in self.selected_character["conditions"]:
            self.selected_character["conditions"].append(cond)
            self.history.append((Action.ADD_CONDITION, cond))
            self.log_event(f"{self.selected_character['name']} gains {cond}")
            self.refresh_ui()

    def remove_condition(self):
        if not self.selected_character:
            return

        cond = self.condition_var.get()
        if cond in self.selected_character["conditions"]:
            self.selected_character["conditions"].remove(cond)
            self.history.append((Action.REMOVE_CONDITION, cond))
            self.log_event(f"{self.selected_character['name']} loses {cond}")
            self.refresh_ui()

    def remove_spell_slot(self):
        if not self.selected_character:
            return

        slot = self.spell_slot_var.get()
        level = int(slot.split()[1])
        if self.selected_character["spell_slots"].get(level, 0) <= 0:
            return

        old_value = self.selected_character["spell_slots"][level]
        self.selected_character["spell_slots"][level] = max(old_value - 1, 0)
        self.history.append((Action.REMOVE_SPELL_SLOT, level))
        self.log_event(f"{self.selected_character['name']} uses a {slot}")
        self.refresh_ui()

    def undo_last_action(self):
        if not self.selected_character:
            return

        data = json.loads(self.log_file.read_text())
        key = f"round_{self.round_number}"
        if key in data and data[key]:
            action, value = self.history.pop()

            if action == Action.DAMAGE:
                self.selected_character["hp"] += value
            elif action == Action.HEAL:
                self.selected_character["hp"] -= value
            elif action == Action.ADD_CONDITION:
                cond = value
                if cond in self.selected_character["conditions"]:
                    self.selected_character["conditions"].remove(value)
            elif action == Action.REMOVE_CONDITION:
                cond = value
                if cond not in self.selected_character["conditions"]:
                    self.selected_character["conditions"].append(value)
            elif action == Action.REMOVE_SPELL_SLOT:
                level = value
                self.selected_character["spell_slots"][level] += 1

            last_event = data[key].pop()
            self.log_file.write_text(json.dumps(data, indent=2))
            # Note: Actual state reversal logic would be needed here
            print(f"Undid action: {last_event}")
            self.refresh_ui()

    # -------- UI BUILD --------
    def build_ui(self):
        main = tk.Frame(self.root)
        main.pack(padx=10, pady=10)

        self.char_frame = tk.Frame(main)
        self.char_frame.grid(row=0, column=0, padx=10)

        control = tk.Frame(main)
        control.grid(row=0, column=1, padx=10, sticky="n")

        self.selected_label = tk.Label(
            control, text="Selected: None", font=("Arial", 10, "bold")
        )
        self.selected_label.pack(pady=(0, 10))

        self.damage_var = tk.StringVar()
        tk.Entry(control, textvariable=self.damage_var).pack(fill="x")
        tk.Button(control, text="Apply Damage", command=self.apply_damage).pack(
            fill="x"
        )

        self.heal_var = tk.StringVar()
        tk.Entry(control, textvariable=self.heal_var).pack(fill="x")
        tk.Button(control, text="Apply Heal", command=self.apply_heal).pack(fill="x")

        self.condition_var = tk.StringVar(value=self.conditions[0])
        tk.OptionMenu(control, self.condition_var, *self.conditions).pack(fill="x")
        tk.Button(control, text="Add Condition", command=self.apply_condition).pack(
            fill="x"
        )
        tk.Button(control, text="Remove Condition", command=self.remove_condition).pack(
            fill="x"
        )

        spell_slots = [f"Level {level} spell slot" for level in range(1, 10)]
        self.spell_slot_var = tk.StringVar(value=spell_slots[0])
        tk.OptionMenu(control, self.spell_slot_var, *spell_slots).pack(fill="x")
        tk.Button(control, text="Cast spell", command=self.remove_spell_slot).pack(
            fill="x"
        )
        tk.Button(control, text="Undo Last Action", command=self.undo_last_action).pack(
            fill="x"
        )

        self.char_widgets = []

    # -------- RENDER --------
    def refresh_ui(self):
        for w in self.char_widgets:
            w.destroy()
        self.char_widgets.clear()

        for index, char in enumerate(self.characters):
            row = index % 3
            column = index // 3

            frame = tk.Frame(self.char_frame, bd=2, relief="ridge", padx=6, pady=4)
            frame.grid(row=row, column=column, padx=6, pady=4, sticky="nw")

            if char is self.selected_character:
                frame.config(bg="#cce5ff")

            tk.Label(frame, text=char["name"], font=("Arial", 11, "bold")).pack(
                anchor="w"
            )
            tk.Label(frame, text=f"HP: {char['hp']}").pack(anchor="w")
            tk.Label(frame, text=f"AC: {char['ac']}").pack(anchor="w")

            tk.Label(
                frame,
                text=f"Conditions: {', '.join(char['conditions']) or 'None'}",
            ).pack(anchor="w")

            for level, slots in char.get("spell_slots", {}).items():
                tk.Label(frame, text=f"Level {level} Spell Slots: {slots}").pack(
                    anchor="w"
                )

            if "Ability Scores" in char:
                text = ", ".join(
                    f"{ability[:3]} {modifier:02}"
                    for ability, modifier in char["Ability Scores"].items()
                )
                tk.Label(frame, text="Ability Scores:").pack(anchor="w")
                tk.Label(frame, text=text).pack(anchor="w")

            if "Saving Throws" in char:
                text = ", ".join(
                    f"{ability[:3]} {modifier:02}"
                    for ability, modifier in char["Saving Throws"].items()
                )
                tk.Label(frame, text="Saving Throws:").pack(anchor="w")
                tk.Label(frame, text=text).pack(anchor="w")

            frame.bind("<Button-1>", lambda e, c=char: self.select_character(c))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, c=char: self.select_character(c))

            self.char_widgets.append(frame)


if __name__ == "__main__":
    import OptimizedRangerHunter
    import OptimizedBerserkerBarbarian

    character_sheets = [
        OptimizedRangerHunter.get_data(),
        OptimizedBerserkerBarbarian.get_data(),
    ]
    root = tk.Tk()
    app = CombatApp(root, character_sheets)
    root.mainloop()
