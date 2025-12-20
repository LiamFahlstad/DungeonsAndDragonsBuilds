from enum import Enum
import tkinter as tk
import json
from pathlib import Path


class Action(str, Enum):
    HEAL = "heal"
    DAMAGE = "damage"
    ADD_CONDITION = "add_condition"
    REMOVE_CONDITION = "remove_condition"


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
    def __init__(self, root):
        self.root = root
        self.root.title("DnD Combat Engine")

        # -------- DATA --------
        self.characters = [
            {"name": "Hero", "hp": 20, "ac": 15, "temp_hp": 0, "conditions": []},
            {"name": "Goblin", "hp": 7, "ac": 13, "temp_hp": 0, "conditions": []},
        ]

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

        tk.Button(control, text="Undo Last Action", command=self.undo_last_action).pack(
            fill="x"
        )

        self.char_widgets = []

    # -------- RENDER --------
    def refresh_ui(self):
        for w in self.char_widgets:
            w.destroy()
        self.char_widgets.clear()
        for char in self.characters:
            frame = tk.Frame(self.char_frame, bd=2, relief="ridge", padx=6, pady=4)
            frame.pack(fill="x", pady=4)

            if char is self.selected_character:
                frame.config(bg="#cce5ff")

            tk.Label(frame, text=char["name"], font=("Arial", 11, "bold")).pack(
                anchor="w"
            )
            tk.Label(frame, text=f"HP: {char['hp']} | AC: {char['ac']}").pack(
                anchor="w"
            )
            tk.Label(
                frame, text=f"Conditions: {', '.join(char['conditions']) or 'None'}"
            ).pack(anchor="w")

            frame.bind("<Button-1>", lambda e, c=char: self.select_character(c))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, c=char: self.select_character(c))

            self.char_widgets.append(frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = CombatApp(root)
    root.mainloop()
