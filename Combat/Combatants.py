from Model.Creatures.Combatants import BasicCombatantData
from Core.Definitions import Ability


class Pirate(BasicCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Pirate",
            hp=33,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 16,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 14,
            },
            spell_slots={},
        )


class Tiger(BasicCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Tiger",
            hp=30,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 17,
                Ability.DEXTERITY: 16,
                Ability.CONSTITUTION: 14,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 8,
            },
            spell_slots={},
        )


class BugbearWarrior(BasicCombatantData):
    # https://www.aidedd.org/monster/bugbear-warrior
    def __init__(self):
        super().__init__(
            combatant_type="Bugbear Warrior",
            hp=33,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 15,
                Ability.DEXTERITY: 14,
                Ability.CONSTITUTION: 13,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 11,
                Ability.CHARISMA: 9,
            },
            spell_slots={},
        )


class Mage(BasicCombatantData):
    # https://www.aidedd.org/monster/mage
    def __init__(self):
        super().__init__(
            combatant_type="Mage",
            hp=81,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 9,
                Ability.DEXTERITY: 14,
                Ability.CONSTITUTION: 11,
                Ability.INTELLIGENCE: 17,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 11,
            },
        )


class Vrock(BasicCombatantData):
    # https://www.aidedd.org/monster/vrock
    def __init__(self):
        super().__init__(
            combatant_type="Vrock",
            hp=152,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 17,
                Ability.DEXTERITY: 15,
                Ability.CONSTITUTION: 18,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 13,
                Ability.CHARISMA: 8,
            },
            saving_throws={
                Ability.STRENGTH: 3,
                Ability.DEXTERITY: 5,
                Ability.CONSTITUTION: 4,
                Ability.INTELLIGENCE: -1,
                Ability.WISDOM: 4,
                Ability.CHARISMA: 2,
            },
        )


class SaberToothedTiger(BasicCombatantData):
    # https://www.aidedd.org/monster/saber-toothed-tiger
    def __init__(self):
        super().__init__(
            combatant_type="Saber-Toothed Tiger",
            hp=52,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 18,
                Ability.DEXTERITY: 17,
                Ability.CONSTITUTION: 15,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 8,
            },
            spell_slots={},
            saving_throws={
                Ability.STRENGTH: 4,
                Ability.DEXTERITY: 5,
                Ability.CONSTITUTION: 2,
                Ability.INTELLIGENCE: -4,
                Ability.WISDOM: 1,
                Ability.CHARISMA: -1,
            },
        )


class Priest(BasicCombatantData):
    # https://www.aidedd.org/monster/priest
    def __init__(self):
        super().__init__(
            combatant_type="Priest",
            hp=38,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 16,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 13,
                Ability.WISDOM: 16,
                Ability.CHARISMA: 13,
            },
            spell_slots={1: 3, 2: 2},
        )


class Rhinoceros(BasicCombatantData):
    # https://www.aidedd.org/monster/rhinoceros

    def __init__(self):
        super().__init__(
            combatant_type="Rhinoceros",
            hp=45,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 21,
                Ability.DEXTERITY: 8,
                Ability.CONSTITUTION: 15,
                Ability.INTELLIGENCE: 2,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 6,
            },
            spell_slots={},
            saving_throws={
                Ability.STRENGTH: 5,
                Ability.DEXTERITY: -1,
                Ability.CONSTITUTION: 2,
                Ability.INTELLIGENCE: -4,
                Ability.WISDOM: 1,
                Ability.CHARISMA: -2,
            },
        )


class Player1(BasicCombatantData):

    def __init__(self):
        super().__init__(
            combatant_type="Player 1",
            hp=45,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 21,
                Ability.DEXTERITY: 8,
                Ability.CONSTITUTION: 15,
                Ability.INTELLIGENCE: 2,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 6,
            },
            spell_slots={},
            saving_throws={
                Ability.STRENGTH: 5,
                Ability.DEXTERITY: -1,
                Ability.CONSTITUTION: 2,
                Ability.INTELLIGENCE: -4,
                Ability.WISDOM: 1,
                Ability.CHARISMA: -2,
            },
        )


class Bull(BasicCombatantData):

    def __init__(self):
        super().__init__(
            combatant_type="Bull",
            hp=126,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 20,
                Ability.DEXTERITY: 18,
                Ability.CONSTITUTION: 20,
                Ability.INTELLIGENCE: 12,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 8,
            },
            spell_slots={},
            saving_throws={
                Ability.STRENGTH: 5,
                Ability.DEXTERITY: 5,
                Ability.CONSTITUTION: 5,
                Ability.INTELLIGENCE: 1,
                Ability.WISDOM: 3,
                Ability.CHARISMA: -1,
            },
        )
