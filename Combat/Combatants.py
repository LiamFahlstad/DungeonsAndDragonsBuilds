from Combat.Definitions import BasicCombatantData


class Pirate(BasicCombatantData):
    def __init__(self):
        super().__init__(
            name="Pirate",
            hp=33,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 10,
                "Dex": 16,
                "Con": 12,
                "Int": 8,
                "Wis": 12,
                "Cha": 14,
            },
            spell_slots={},
        )


class Tiger(BasicCombatantData):
    def __init__(self):
        super().__init__(
            name="Tiger",
            hp=30,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 17,
                "Dex": 16,
                "Con": 14,
                "Int": 3,
                "Wis": 12,
                "Cha": 8,
            },
            spell_slots={},
        )


class BugbearWarrior(BasicCombatantData):
    # https://www.aidedd.org/monster/bugbear-warrior
    def __init__(self):
        super().__init__(
            name="Bugbear Warrior",
            hp=33,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 15,
                "Dex": 14,
                "Con": 13,
                "Int": 8,
                "Wis": 11,
                "Cha": 9,
            },
            spell_slots={},
        )


class Mage(BasicCombatantData):
    # https://www.aidedd.org/monster/mage
    def __init__(self):
        super().__init__(
            name="Mage",
            hp=81,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 9,
                "Dex": 14,
                "Con": 11,
                "Int": 17,
                "Wis": 12,
                "Cha": 11,
            },
        )


class Vrock(BasicCombatantData):
    # https://www.aidedd.org/monster/vrock
    def __init__(self):
        super().__init__(
            name="Vrock",
            hp=152,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 17,
                "Dex": 15,
                "Con": 18,
                "Int": 8,
                "Wis": 13,
                "Cha": 8,
            },
            saving_throws={
                "Str": 3,
                "Dex": 5,
                "Con": 4,
                "Int": -1,
                "Wis": 4,
                "Cha": 2,
            },
        )


class SaberToothedTiger(BasicCombatantData):
    # https://www.aidedd.org/monster/saber-toothed-tiger
    def __init__(self):
        super().__init__(
            name="Saber-Toothed Tiger",
            hp=52,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 18,
                "Dex": 17,
                "Con": 15,
                "Int": 3,
                "Wis": 12,
                "Cha": 8,
            },
            spell_slots={},
            saving_throws={
                "Str": 4,
                "Dex": 5,
                "Con": 2,
                "Int": -4,
                "Wis": 1,
                "Cha": -1,
            },
        )


class Priest(BasicCombatantData):
    # https://www.aidedd.org/monster/priest
    def __init__(self):
        super().__init__(
            name="Priest",
            hp=38,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 16,
                "Dex": 10,
                "Con": 12,
                "Int": 13,
                "Wis": 16,
                "Cha": 13,
            },
            spell_slots={1: 3, 2: 2},
        )


class Rhinoceros(BasicCombatantData):
    # https://www.aidedd.org/monster/rhinoceros

    def __init__(self):
        super().__init__(
            name="Rhinoceros",
            hp=45,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 21,
                "Dex": 8,
                "Con": 15,
                "Int": 2,
                "Wis": 12,
                "Cha": 6,
            },
            spell_slots={},
            saving_throws={
                "Str": 5,
                "Dex": -1,
                "Con": 2,
                "Int": -4,
                "Wis": 1,
                "Cha": -2,
            },
        )


class Player1(BasicCombatantData):

    def __init__(self):
        super().__init__(
            name="Player 1",
            hp=45,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 21,
                "Dex": 8,
                "Con": 15,
                "Int": 2,
                "Wis": 12,
                "Cha": 6,
            },
            spell_slots={},
            saving_throws={
                "Str": 5,
                "Dex": -1,
                "Con": 2,
                "Int": -4,
                "Wis": 1,
                "Cha": -2,
            },
        )


class Bull(BasicCombatantData):

    def __init__(self):
        super().__init__(
            name="Bull",
            hp=126,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 20,
                "Dex": 18,
                "Con": 20,
                "Int": 12,
                "Wis": 12,
                "Cha": 8,
            },
            spell_slots={},
            saving_throws={
                "Str": 5,
                "Dex": 5,
                "Con": 5,
                "Int": 1,
                "Wis": 3,
                "Cha": -1,
            },
        )
