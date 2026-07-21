from Combat.Definitions import (
    Alignment,
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterAbility,
    Size,
    Skill,
)
from Definitions import Ability


class TheHeadlessDragon(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Headless Dragon",
            hp=218,
            ac=19,
            temp_hp=0,
            conditions=[],
            ability_scores={Ability.STRENGTH.short_name: 23, Ability.DEXTERITY.short_name: 14, Ability.CONSTITUTION.short_name: 21, Ability.INTELLIGENCE.short_name: 5, Ability.WISDOM.short_name: 13, Ability.CHARISMA.short_name: 17},
            saving_throws={},
            spell_slots={},
            cr="15",
            size=Size.HUGE, monster_type='Dragon', alignment=Alignment.NEUTRAL_EVIL,
            ac_note="natural armor",
            hp_formula="23d12+69",
            speed_ground_ft=40, speed_fly_ft=80, speed_climb_ft=40, speed_special_rules='',
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.ACID], note=''),
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=''),
                DamageTypeEntry(damage_types=[DamageType.POISON], note=''),
            ],
            condition_immunities=[Condition.BLINDED, Condition.CHARMED, Condition.FRIGHTENED, Condition.POISONED],
            senses="Blindsight 60 ft., Tremorsense 60 ft. (no eyes — senses only through the sigil), Passive Perception 11",
            languages="understands Draconic and Common but can't speak",
            traits=[
            MonsterAbility(name='Legendary Resistance (3/Day)', description='If the dragon fails a saving throw, it can choose to succeed instead.'),
            MonsterAbility(name='Sigil of Silence', description="The dragon can't be Blinded or Deafened by nonmagical means, and it can't be surprised."),
            MonsterAbility(name='Cursed Regeneration', description="The dragon regains 15 Hit Points at the start of its turn if it has at least 1 Hit Point and hasn't taken Radiant damage since the start of its last turn."),
        ],
            actions=[
            MonsterAbility(name='Multiattack', description='The dragon makes two Rend attacks and one Tail attack.'),
            MonsterAbility(name='Rend', description='Melee Attack Roll: +11, reach 10 ft. Hit: 17 (2d10 + 6) Slashing damage.'),
            MonsterAbility(name='Tail', description='Melee Attack Roll: +11, reach 15 ft. Hit: 15 (2d8 + 6) Bludgeoning damage.'),
            MonsterAbility(name='Sigil Breath (Recharge 5-6)', description="The metal sigil erupts with corrosive void-acid in a 60-foot line. Each creature in the line makes a DC 18 Dexterity saving throw, taking 54 (12d8) Acid damage on a failed save, or half as much on a success. A creature that fails the save also can't speak or make any sound (as the Silence spell centered on it) for 1 minute."),
            MonsterAbility(name='Frightful Presence', description="Each creature of the dragon's choice within 120 feet that can sense it must succeed on a DC 15 Wisdom saving throw or be frightened for 1 minute."),
        ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[
            MonsterAbility(name='Detect', description='The dragon makes a Wisdom (Perception) check.'),
            MonsterAbility(name='Tail Attack', description='The dragon makes one Tail attack.'),
            MonsterAbility(name='Wing Buffet (Costs 2 Actions)', description='The dragon beats its wings. Each creature within 15 feet must succeed on a DC 18 Dexterity saving throw or take 13 (2d6 + 6) Bludgeoning damage and be knocked prone. The dragon can then fly up to half its flying speed.'),
        ],
            legendary_resistances=3,
            lair_actions=[
            MonsterAbility(name='Grasping Hands', description='On initiative count 20 (losing initiative ties), accursed hands erupt from the ground in a 20-foot-radius sphere centered on a point the dragon can see within 120 feet. Each creature in that area must succeed on a DC 15 Strength saving throw or be Restrained until the dragon uses this lair action again or the dragon dies.'),
        ],
            mythic_actions=[],
        )
