from Combat.Definitions import (
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterAbility,
    Skill,
)
from Definitions import Ability


class TheBellSaint(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Bell Saint",
            hp=161,
            ac=17,
            temp_hp=0,
            conditions=[],
            ability_scores={Ability.STRENGTH.short_name: 20, Ability.DEXTERITY.short_name: 8, Ability.CONSTITUTION.short_name: 18, Ability.INTELLIGENCE.short_name: 6, Ability.WISDOM.short_name: 15, Ability.CHARISMA.short_name: 16},
            saving_throws={},
            spell_slots={},
            cr="9",
            monster_type="Huge Undead, Unaligned",
            ac_note="natural armor",
            hp_formula="17d12+51",
            speed="10 ft.",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING], note='from Nonmagical Attacks'),
            ],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=''),
                DamageTypeEntry(damage_types=[DamageType.POISON], note=''),
            ],
            condition_immunities=[Condition.CHARMED, Condition.EXHAUSTION, Condition.FRIGHTENED, Condition.PARALYZED, Condition.POISONED],
            senses="Blindsight 60 ft. (blind beyond this radius), Passive Perception 12",
            languages="understands Common but can't speak, communicates only through tolling",
            traits=[
            MonsterAbility(name='Legendary Resistance (1/Day)', description='If the Bell Saint fails a saving throw, it can choose to succeed instead.'),
            MonsterAbility(name='Undying Vigil', description='The cleric entombed within refuses to release its grip on life. The Bell Saint has advantage on death saving throws, and reviving spells that would restore it to consciousness instead restore 2d10 Hit Points.'),
        ],
            actions=[
            MonsterAbility(name='Multiattack', description='The Bell Saint makes two Chain Lash attacks.'),
            MonsterAbility(name='Chain Lash', description="Melee Attack Roll: +8, reach 15 ft. Hit: 15 (2d10 + 4) Bludgeoning damage, and the target is grappled (escape DC 15) by one of the bell's dragging chains."),
            MonsterAbility(name='Toll of Rising (Recharge 5-6)', description="The bell tolls with unholy force. Each Undead creature within 30 feet of the Bell Saint that isn't already under another creature's control rises to fight for the Bell Saint, acting immediately after the Bell Saint's turn. Each living creature within 30 feet must succeed on a DC 15 Wisdom saving throw or take 10 (3d6) Psychic damage and have its speed halved until the end of its next turn, or take half as much damage on a success and suffer no speed reduction."),
        ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[
            MonsterAbility(name='Drag (Costs 1 Action)', description='The Bell Saint moves up to half its speed without provoking opportunity attacks.'),
            MonsterAbility(name='Chain Lash (Costs 1 Action)', description='The Bell Saint makes one Chain Lash attack.'),
            MonsterAbility(name='Muffled Toll (Costs 2 Actions)', description='One creature the Bell Saint can see within 30 feet must succeed on a DC 15 Wisdom saving throw or be frightened until the end of its next turn.'),
        ],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )
