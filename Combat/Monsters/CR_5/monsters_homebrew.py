from Core.Definitions import Condition, CreatureSize, DamageType, Skill
from Model.Creatures.Combatants import (
    Alignment,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import (
    DcMonsterAbility,
    DiceType,
    MonsterAbility,
    Multiattack,
    RangedAttack,
    SavingThrowEffect,
)
from Core.Definitions import Ability


class TheChoirmasterOfHollowHymns(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Choirmaster of Hollow Hymns",
            hp=84,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 16,
                Ability.CONSTITUTION: 14,
                Ability.INTELLIGENCE: 12,
                Ability.WISDOM: 16,
                Ability.CHARISMA: 12,
            },
            saving_throws={
                Ability.CONSTITUTION: 5,
                Ability.WISDOM: 3,
            },
            spell_slots={},
            cr="5",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Cultist",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="ragged vestments and a bone gorget",
            hp_formula="13d8 + 26",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERFORMANCE: 6,
                Skill.RELIGION: 4,
                Skill.PERCEPTION: 6,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(
                    damage_types=[DamageType.NECROTIC],
                    note="from the curse's lingering touch",
                ),
            ],
            damage_immunities=[],
            condition_immunities=[Condition.FRIGHTENED],
            senses="darkvision 60 ft., Passive Perception 16",
            languages="Common, Deep Speech (cannot speak any language aloud)",
            traits=[
                MonsterAbility(
                    name="Legendary Resistance (1/Day)",
                    description="If the Choirmaster fails a saving throw, he can choose to succeed instead.",
                ),
                MonsterAbility(
                    name="Curse-Marked",
                    description="The Choirmaster's throat was carved open by his own hand the night he first mimicked Noc'tra and lived. He has Resistance to Necrotic damage and cannot be Frightened.",
                ),
                MonsterAbility(
                    name="Throat-Strain",
                    description="The Choirmaster's voice is an instrument played upon his own ruined throat, and every note costs him blood. Each time he uses Warding Rasp or Hollow Hymn, he gains one stack of Throat-Strain (maximum 5 stacks). At the start of each of his turns, he takes 1d6 Necrotic damage per stack of Throat-Strain he has, and while he has 3 or more stacks he has Disadvantage on Constitution saving throws as the wound threatens to tear open fully. If this damage would reduce the Choirmaster to 0 Hit Points, he instead drops to 1 Hit Point, loses all stacks of Throat-Strain, and can't use Warding Rasp or Hollow Hymn again until he finishes a Short or Long Rest, his instrument silenced along with his throat.",
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="Choirmaster",
                    attacks_text="two Hooked Bow attacks",
                ),
                MonsterAbility(
                    name="Hooked Bow",
                    description="Melee Attack Roll: +6, reach 5 ft. Hit: 10 (1d8 + 3) Slashing damage plus 4 (1d8) Necrotic damage as the curse bleeds from his own throat into the wound.",
                ),
                DcMonsterAbility(
                    name="Warding Rasp (Recharge 5-6)",
                    description="The Choirmaster drags the hooked bow across his throat, and a broken fragment of Noc'tra tears free in a 20-foot Cone. Each creature in the area must make a DC 14 Wisdom saving throw, taking 17 (5d6) Psychic damage and gaining the Frightened condition until the end of the Choirmaster's next turn on a failed save, or half as much damage only on a successful one. The Choirmaster then gains one stack of Throat-Strain (see Throat-Strain).",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Hollow Hymn",
                    description="The Choirmaster draws his hooked bow across his own ruined throat, producing a warped, layered tone woven from fragments of Noc'tra that carries far beyond any living voice. Every Accursed within 120 feet that can hear the tone joins the choir: the Choirmaster chooses any number of them, and for each he can either have it move up to its Speed to a point he designates and then make one melee attack, or simply reposition it up to its Speed toward a point he designates, reshaping the choir's formation exactly as he wills, per the Accursed's Directed by the Faithful trait. Until the start of the Choirmaster's next turn, every Accursed he directed this way has Advantage on attack rolls, their broken bodies moving in perfect, horrible unison to his voice. The Choirmaster then gains one stack of Throat-Strain (see Throat-Strain).",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )


class MiraPrincessOfTheLoop(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Mira, Princess of the Loop",
            description="A princess who dabbled in power and ancient magic beyond imagination, and the reason the kingdom is trapped in a time loop. She fights beside the Warrior (Mirelle's stat block): she marks a target for its greatsword, teleports it into reach, and rewinds the blows it takes, recharging its Golden Arc. A boss exception to the 4-ability house rule: Multiattack, Eldritch Blast and Stutter Time are separate actions so the combat UI rolls each.",
            hp=99,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 12,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 18,
                Ability.WISDOM: 14,
                Ability.CHARISMA: 14,
            },
            saving_throws={},
            spell_slots={},
            cr="5",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Wizard",
            alignment=Alignment.CHAOTIC_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="a gown of frozen moments",
            hp_formula="18d8 + 18",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.ARCANA: 10,
                Skill.INSIGHT: 5,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(
                    damage_types=[DamageType.PSYCHIC],
                    note="",
                ),
            ],
            damage_immunities=[],
            condition_immunities=[Condition.CHARMED],
            senses="Passive Perception 12",
            languages="Common and most other languages",
            traits=[
                MonsterAbility(
                    name="Fractured Timeline",
                    description="If Mira fails a saving throw, she rewinds to the moment before and succeeds instead (Legendary Resistance, 2/Day). The first time she is Bloodied, two illusory duplicates of her from other loops appear in unoccupied spaces she can see within 30 feet of her. Each has AC 15 and 1 Hit Point, and vanishes when it takes damage or when Mira dies. At the end of each of Mira's turns, each duplicate makes one Eldritch Blast attack.",
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="Mira",
                    attacks_text="two attacks, using Eldritch Blast or Stutter Time in any combination",
                    use_article=False,
                ),
                RangedAttack(
                    name="Eldritch Blast",
                    attack_bonus=7,
                    range_ft=120,
                    dice_count=2,
                    dice_type=DiceType.D6,
                    damage_bonus=4,
                    damage_type=DamageType.FORCE,
                ),
                SavingThrowEffect(
                    name="Stutter Time",
                    ability=Ability.WISDOM,
                    dc=15,
                    target="one creature Mira can see within 60 feet",
                    dice_count=2,
                    dice_type=DiceType.D8,
                    damage_type=DamageType.PSYCHIC,
                    failure_effect="and the target is slowed: its Speed is halved, it can't take Bonus Actions or Reactions, and it takes 3 (1d6) Psychic damage each time it takes an action",
                    success_effect="No effect.",
                    extra_ruling="A slowed target repeats the save at the end of each of its turns, ending the effect on a success, and another creature can end it early by touching it as an action.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Temporal Shift",
                    description="Mira marks one creature she can see within 120 feet until the start of her next turn; attack rolls against it have Advantage. She can then teleport herself, or one willing ally she can see within 60 feet of her, up to 30 feet to an unoccupied space she can see.",
                ),
            ],
            reactions=[
                MonsterAbility(
                    name="Rewind (2/Day)",
                    description="Trigger: Mira or an ally she can see within 60 feet of her takes damage. Response: Mira turns the moment back. The creature has Resistance to that damage and gains 10 Temporary Hit Points, and one of its abilities with a Recharge recharges.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=2,
            lair_actions=[],
            mythic_actions=[],
        )
