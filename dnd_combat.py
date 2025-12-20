import tkinter as tk
import json
from pathlib import Path

# ------------------ DATA ------------------

characters = [
    {"name": "Hero", "hp": 20, "ac": 15, "temp_hp": 0, "conditions": []},
    {"name": "Goblin", "hp": 7, "ac": 13, "temp_hp": 0, "conditions": []},
]

CONDITIONS = [
    "Blinded",
    "Charmed",
    "Concentrating",
    "Frightened",
    "Grappled",
    "Paralyzed",
    "Poisoned",
    "Prone",
    "Stunned",
]

SELECTED_CHARACTER = None
round_number = 1
log_file = Path("combat_log.json")

if not log_file.exists():
    log_file.write_text(json.dumps({}, indent=2))


# ------------------ LOGGING ------------------


def log_event(text):
    data = json.loads(log_file.read_text())
    round_key = f"round_{round_number}"
    data.setdefault(round_key, []).append(text)
    log_file.write_text(json.dumps(data, indent=2))


# ------------------ UI ACTIONS ------------------


def select_character(char):
    global SELECTED_CHARACTER
    SELECTED_CHARACTER = char
    selected_label.config(text=f"Selected: {char['name']}")
    refresh_ui()


def apply_damage(damage_var, selected_character):
    if not selected_character:
        return
    try:
        dmg = int(damage_var.get())
    except ValueError:
        return

    selected_character["hp"] -= dmg
    log_event(f"{selected_character['name']} takes {dmg} damage")
    refresh_ui()


def apply_heal(heal_var, selected_character):
    if not selected_character:
        return
    try:
        heal = int(heal_var.get())
    except ValueError:
        return

    selected_character["hp"] += heal
    log_event(f"{selected_character['name']} heals {heal} HP")
    refresh_ui()


def apply_condition(selected_character):
    if not selected_character:
        return

    cond = condition_var.get()
    if cond and cond not in selected_character["conditions"]:
        selected_character["conditions"].append(cond)
        log_event(f"{selected_character['name']} gains {cond}")
        refresh_ui()


# ------------------ UI ------------------

root = tk.Tk()
root.title("DnD Combat Engine")

main = tk.Frame(root)
main.pack(padx=10, pady=10)

# Character list (left)
char_frame = tk.Frame(main)
char_frame.grid(row=0, column=0, padx=10)

# Control panel (right)
control = tk.Frame(main)
control.grid(row=0, column=1, padx=10, sticky="n")

selected_label = tk.Label(control, text="Selected: None", font=("Arial", 10, "bold"))
selected_label.pack(pady=(0, 10))

# ----- Damage -----
tk.Label(control, text="Deal Damage").pack(anchor="w")
damage_var = tk.StringVar()
tk.Entry(control, textvariable=damage_var).pack(fill="x")
tk.Button(
    control,
    text="Apply Damage",
    command=lambda: apply_damage(damage_var, SELECTED_CHARACTER),
).pack(fill="x", pady=2)

# ----- Heal -----
tk.Label(control, text="Heal HP").pack(anchor="w", pady=(10, 0))
heal_var = tk.StringVar()
tk.Entry(control, textvariable=heal_var).pack(fill="x")
tk.Button(
    control, text="Apply Heal", command=lambda: apply_heal(heal_var, SELECTED_CHARACTER)
).pack(fill="x", pady=2)

# ----- Conditions -----
tk.Label(control, text="Apply Condition").pack(anchor="w", pady=(10, 0))
condition_var = tk.StringVar(value=CONDITIONS[0])
tk.OptionMenu(control, condition_var, *CONDITIONS).pack(fill="x")
tk.Button(
    control, text="Add Condition", command=lambda: apply_condition(SELECTED_CHARACTER)
).pack(fill="x", pady=2)

# ------------------ CHARACTER RENDER ------------------

char_widgets = []


def refresh_ui():
    for w in char_widgets:
        w.destroy()
    char_widgets.clear()

    for char in characters:
        frame = tk.Frame(char_frame, bd=2, relief="ridge", padx=6, pady=4)
        frame.pack(fill="x", pady=4)

        if char == SELECTED_CHARACTER:
            frame.config(bg="#cce5ff")

        tk.Label(frame, text=char["name"], font=("Arial", 11, "bold")).pack(anchor="w")
        tk.Label(
            frame,
            text=f"HP: {char['hp']} | AC: {char['ac']} | Temp HP: {char['temp_hp']}",
        ).pack(anchor="w")
        tk.Label(
            frame, text=f"Conditions: {', '.join(char['conditions']) or 'None'}"
        ).pack(anchor="w")

        frame.bind("<Button-1>", lambda e, c=char: select_character(c))
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e, c=char: select_character(c))

        char_widgets.append(frame)


refresh_ui()
root.mainloop()
