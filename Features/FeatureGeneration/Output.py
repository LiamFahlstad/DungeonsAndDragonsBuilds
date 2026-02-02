class WildMagicSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Wild Magic Surge", origin="Wild Magic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your spellcasting can unleash surges of untamed magic. Once per turn, you can roll 1d20 immediately after you cast a Sorcerer spell with a spell slot. If you roll a 20, roll on the Wild Magic Surge table to create a magical effect.\n"
            "If the magical effect is a spell, it is too wild to be affected by your Metamagic."
        )
        return description


class TidesofChaos(TextFeature):
    def __init__(self):
        super().__init__(name="Tides of Chaos", origin="Wild Magic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can manipulate chaos itself to give yourself Advantage on one D20 Test before you roll the d20. Once you do so, you must cast a Sorcerer spell with a spell slot or finish a Long Rest before you can use this feature again.\n"
            "If you do cast a Sorcerer spell with a spell slot before you finish a Long Rest, you automatically roll on the Wild Magic Surge table."
        )
        return description


class BendLuck(TextFeature):
    def __init__(self):
        super().__init__(name="Bend Luck", origin="Wild Magic Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have the ability to twist fate using your wild magic. Immediately after another creature you can see rolls the d20 for a D20 Test, you can take a Reaction and spend 1 Sorcery Point to roll 1d4 and apply the number rolled as a bonus or penalty (your choice) to the d20 roll."
        return description


class ControlledChaos(TextFeature):
    def __init__(self):
        super().__init__(name="Controlled Chaos", origin="Wild Magic Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain a modicum of control over the surges of your wild magic. Whenever you roll on the Wild Magic Surge table, you can roll twice and use either number."
        return description


class TamedSurge(TextFeature):
    def __init__(self):
        super().__init__(name="Tamed Surge", origin="Wild Magic Sorcerer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Immediately after you cast a Sorcerer spell with a spell slot, you can create an effect of your choice from the Wild Magic Surge table instead of rolling on that table. You can choose any effect in the table except for the final row, and if the chosen effect involves a roll, you must make it.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest."
        )
        return description
