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


class TheChoirmasterOfHollowHymns(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Choirmaster of Hollow Hymns",
            hp=84,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 10,
                Ability.DEXTERITY.short_name: 16,
                Ability.CONSTITUTION.short_name: 14,
                Ability.INTELLIGENCE.short_name: 12,
                Ability.WISDOM.short_name: 16,
                Ability.CHARISMA.short_name: 16,
            },
            saving_throws={
                Ability.CONSTITUTION.short_name: 5,
                Ability.WISDOM.short_name: 6,
            },
            spell_slots={},
            cr="5",
            monster_type="Humanoid (Cultist)",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
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
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note="from the curse's lingering touch"),
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
                MonsterAbility(
                    name="Multiattack",
                    description="The Choirmaster makes two Hooked Bow attacks.",
                ),
                MonsterAbility(
                    name="Hooked Bow",
                    description="Melee Attack Roll: +6, reach 5 ft. Hit: 10 (1d8 + 3) Slashing damage plus 4 (1d8) Necrotic damage as the curse bleeds from his own throat into the wound.",
                ),
                MonsterAbility(
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
