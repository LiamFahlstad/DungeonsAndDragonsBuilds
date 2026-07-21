from Combat.Definitions import ExtendedCombatantData


class TheHeadlessDragon(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Headless Dragon",
            hp=218,
            ac=19,
            temp_hp=0,
            conditions=[],
            ability_scores={
                "Str": 23,
                "Dex": 14,
                "Con": 21,
                "Int": 5,
                "Wis": 13,
                "Cha": 17,
            },
            saving_throws={},
            spell_slots={},
            cr="15",
            monster_type="Huge Dragon, Neutral Evil",
            ac_note="natural armor",
            hp_formula="23d12+69",
            speed="40 ft., climb 40 ft., fly 80 ft.",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=["Acid", "Necrotic", "Poison"],
            condition_immunities=["Blinded", "Charmed", "Frightened", "Poisoned"],
            senses="Blindsight 60 ft., Tremorsense 60 ft. (no eyes — senses only through the sigil), Passive Perception 11",
            languages="understands Draconic and Common but can't speak",
            traits=[
                {
                    "name": "Legendary Resistance (3/Day)",
                    "description": "If the dragon fails a saving throw, it can choose to succeed instead.",
                },
                {
                    "name": "Sigil of Silence",
                    "description": "The dragon can't be Blinded or Deafened by nonmagical means, and it can't be surprised.",
                },
                {
                    "name": "Cursed Regeneration",
                    "description": "The dragon regains 15 Hit Points at the start of its turn if it has at least 1 Hit Point and hasn't taken Radiant damage since the start of its last turn.",
                },
            ],
            actions=[
                {
                    "name": "Multiattack",
                    "description": "The dragon makes two Rend attacks and one Tail attack.",
                },
                {
                    "name": "Rend",
                    "description": "Melee Attack Roll: +11, reach 10 ft. Hit: 17 (2d10 + 6) Slashing damage.",
                },
                {
                    "name": "Tail",
                    "description": "Melee Attack Roll: +11, reach 15 ft. Hit: 15 (2d8 + 6) Bludgeoning damage.",
                },
                {
                    "name": "Sigil Breath (Recharge 5-6)",
                    "description": "The metal sigil erupts with corrosive void-acid in a 60-foot line. Each creature in the line makes a DC 18 Dexterity saving throw, taking 54 (12d8) Acid damage on a failed save, or half as much on a success. A creature that fails the save also can't speak or make any sound (as the Silence spell centered on it) for 1 minute.",
                },
                {
                    "name": "Frightful Presence",
                    "description": "Each creature of the dragon's choice within 120 feet that can sense it must succeed on a DC 15 Wisdom saving throw or be frightened for 1 minute.",
                },
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[
                {
                    "name": "Detect",
                    "description": "The dragon makes a Wisdom (Perception) check.",
                },
                {
                    "name": "Tail Attack",
                    "description": "The dragon makes one Tail attack.",
                },
                {
                    "name": "Wing Buffet (Costs 2 Actions)",
                    "description": "The dragon beats its wings. Each creature within 15 feet must succeed on a DC 18 Dexterity saving throw or take 13 (2d6 + 6) Bludgeoning damage and be knocked prone. The dragon can then fly up to half its flying speed.",
                },
            ],
            legendary_resistances=3,
            lair_actions=[
                {
                    "name": "Grasping Hands",
                    "description": "On initiative count 20 (losing initiative ties), accursed hands erupt from the ground in a 20-foot-radius sphere centered on a point the dragon can see within 120 feet. Each creature in that area must succeed on a DC 15 Strength saving throw or be Restrained until the dragon uses this lair action again or the dragon dies.",
                },
            ],
            mythic_actions=[],
        )
