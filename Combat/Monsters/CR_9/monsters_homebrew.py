from Combat.Definitions import (
    Alignment,
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    LegendaryResistance,
    MonsterAbility,
    MonsterType,
    Multiattack,
    NamedAttackAction,
    Size,
    Skill,
)
from Core.Definitions import Ability


class TheBellSaint(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Bell Saint",
            hp=161,
            ac=17,
            temp_hp=0,
            conditions=[],
            ability_scores={Ability.STRENGTH: 20, Ability.DEXTERITY: 8, Ability.CONSTITUTION: 18, Ability.INTELLIGENCE: 6, Ability.WISDOM: 15, Ability.CHARISMA: 16},
            saving_throws={},
            spell_slots={},
            cr="9",
            size=Size.HUGE, monster_type=MonsterType.UNDEAD, monster_type_note='', alignment=Alignment.UNALIGNED,
            ac_note="natural armor",
            hp_formula="17d12+51",
            speed_ground_ft=10, speed_fly_ft=None, speed_climb_ft=None, speed_special_rules='',
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
            LegendaryResistance(creature_name='Bell Saint', uses=1),
            MonsterAbility(name='Undying Vigil', description='The cleric entombed within refuses to release its grip on life. The Bell Saint has advantage on death saving throws, and reviving spells that would restore it to consciousness instead restore 2d10 Hit Points.'),
        ],
            actions=[
            Multiattack(creature_name='Bell Saint', attacks_text='two Chain Lash attacks'),
            MonsterAbility(name='Chain Lash', description="Melee Attack Roll: +8, reach 15 ft. Hit: 15 (2d10 + 4) Bludgeoning damage, and the target is grappled (escape DC 15) by one of the bell's dragging chains."),
            MonsterAbility(name='Toll of Rising (Recharge 5-6)', description="The bell tolls with unholy force. Each Undead creature within 30 feet of the Bell Saint that isn't already under another creature's control rises to fight for the Bell Saint, acting immediately after the Bell Saint's turn. Each living creature within 30 feet must succeed on a DC 15 Wisdom saving throw or take 10 (3d6) Psychic damage and have its speed halved until the end of its next turn, or take half as much damage on a success and suffer no speed reduction."),
        ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[
            MonsterAbility(name='Drag (Costs 1 Action)', description='The Bell Saint moves up to half its speed without provoking opportunity attacks.'),
            NamedAttackAction(name='Chain Lash (Costs 1 Action)', creature_name='Bell Saint', attack_name='Chain Lash'),
            MonsterAbility(name='Muffled Toll (Costs 2 Actions)', description='One creature the Bell Saint can see within 30 feet must succeed on a DC 15 Wisdom saving throw or be frightened until the end of its next turn.'),
        ],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )
