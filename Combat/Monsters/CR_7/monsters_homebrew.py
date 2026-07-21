from Combat.Definitions import ExtendedCombatantData


class TheCrownWithoutAKing(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Crown Without a King",
            hp=90,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 4,
                "Dex": 18,
                "Con": 14,
                "Int": 14,
                "Wis": 12,
                "Cha": 20,
            },
            saving_throws={},
            spell_slots={},
            cr="7",
            monster_type="Tiny Undead, Lawful Evil",
            ac_note="natural armor",
            hp_formula="20d4+40",
            speed="0 ft., fly 30 ft. (hover)",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=["Necrotic", "Psychic"],
            damage_immunities=["Poison"],
            condition_immunities=["Charmed", "Frightened", "Paralyzed", "Petrified", "Poisoned", "Prone", "Restrained"],
            senses="Truesight 30 ft., Passive Perception 11",
            languages="telepathy 60 ft., understands all languages known by its current or most recent host",
            traits=[
                {
                    "name": "Legendary Resistance (1/Day)",
                    "description": "If the crown fails a saving throw, it can choose to succeed instead.",
                },
                {
                    "name": "Discorporate",
                    "description": "If the crown is reduced to 0 Hit Points while worn, it is instead knocked from its host's head and rendered inert for 1 minute, reverting to its dormant floating form when that time expires with all Hit Points restored.",
                },
            ],
            actions=[
                {
                    "name": "Crown Spike",
                    "description": "Melee Attack Roll: +7, reach 5 ft. Hit: 9 (2d6 + 2) Piercing damage.",
                },
                {
                    "name": "Coronation (Recharge 5-6)",
                    "description": "The crown flings itself at a creature it can see within 5 feet, attempting to seize their head. The target must succeed on a DC 16 Charisma saving throw or become the crown's Host: for the next 24 hours, the target is Charmed by the crown and treats the crown's telepathic commands as though they came from a trusted ally, and the crown can take control of the Host's actions on the crown's turn. If the saving throw fails by 5 or more, the Host's own personality is suppressed entirely and it becomes a loyal servant of the Cult of the Curse until the crown is forcibly removed (requires a successful DC 16 Strength check as an action, dealing 10 Force damage to the crown to knock it free).",
                },
                {
                    "name": "Command the Accursed",
                    "description": "The crown issues a telepathic command to all Undead creatures within 120 feet that are loyal to the Cult of the Curse, granting them advantage on their next attack roll before the end of their next turn.",
                },
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )
