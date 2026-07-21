from Combat.Definitions import (
    Alignment,
    Condition,
    ExtendedCombatantData,
    MonsterAbility,
    Size,
    Skill,
)
from Definitions import Ability


class CommonCultist(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Common Cultist",
            hp=22,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 11,
                Ability.DEXTERITY.short_name: 14,
                Ability.CONSTITUTION.short_name: 12,
                Ability.INTELLIGENCE.short_name: 9,
                Ability.WISDOM.short_name: 10,
                Ability.CHARISMA.short_name: 12,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type="Humanoid (Cultist)",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="scavenged padding",
            hp_formula="4d8+4",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.RELIGION: 1,
                Skill.INTIMIDATION: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Passive Perception 10",
            languages="Common",
            traits=[
                MonsterAbility(
                    name="Zealous Communion",
                    description="While a Priest of the Black Tongues or a Cantor of the Black Choir is within 30 feet of the cultist, the cultist fights with the reckless fervor of the newly converted and has Advantage on attack rolls.",
                ),
                MonsterAbility(
                    name="Strength of the Faithful Mob",
                    description="The cultist has Advantage on an attack roll against a creature if at least one of the cultist's allies is within 5 feet of that creature and the ally doesn't have the Incapacitated condition.",
                ),
                MonsterAbility(
                    name="Marked for the Choir",
                    description="Ritual scarring rings the cultist's throat, and its vestments are stitched shut at the collar in imitation of the silence to come. The sight unsettles the faithless, and the cultist has Advantage on Charisma (Intimidation) checks against any creature that can see these markings.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Scavenged Sickle",
                    description="Melee Attack Roll: +4, reach 5 ft. Hit: 5 (1d6 + 2) Slashing damage.",
                ),
                MonsterAbility(
                    name="Scavenged Sling",
                    description="Ranged Attack Roll: +4, range 30/120 ft. Hit: 4 (1d4 + 2) Bludgeoning damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class SisterAshNumberSeven(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Sister Ash - Number Seven",
            hp=32,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 12,
                Ability.DEXTERITY.short_name: 16,
                Ability.CONSTITUTION.short_name: 14,
                Ability.INTELLIGENCE.short_name: 13,
                Ability.WISDOM.short_name: 15,
                Ability.CHARISMA.short_name: 16,
            },
            saving_throws={Ability.WISDOM.short_name: 4},
            spell_slots={},
            cr="1",
            monster_type="Humanoid (Cultist)",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="studded leather",
            hp_formula="5d8+10",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.ACROBATICS: 5,
                Skill.INSIGHT: 4,
                Skill.PERSUASION: 5,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[Condition.FRIGHTENED],
            senses="Passive Perception 12",
            languages="Common",
            traits=[
                MonsterAbility(
                    name="The Severing of Names",
                    description="Sister Ash burned every ledger, seal, and portrait bearing her birth name during her Severing rite, and answers now only to her number. Any divination or effect that seeks her out by her former name automatically fails to locate or identify her.",
                ),
                MonsterAbility(
                    name="Fear Unlearned",
                    description="Sister Ash's composure was forged in the dueling courts and council chambers of her old life, long before she ever heard Noc'tra whispered. She can't be Frightened, and unlike the curse-marked cultists above her, this fearlessness is entirely her own.",
                ),
                MonsterAbility(
                    name="The Curse Is Watching",
                    description="Those near Sister Ash sometimes swear the shadows linger on her a moment longer than the light allows, as if something patient were taking her measure. She has noticed nothing. Yet.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="Sister Ash makes two Rapier attacks.",
                ),
                MonsterAbility(
                    name="Rapier",
                    description="Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Piercing damage.",
                ),
                MonsterAbility(
                    name="Dagger",
                    description="Melee or Ranged Attack Roll: +5, reach 5 ft. or range 20/60 ft. Hit: 6 (1d4 + 3) Piercing damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[
                MonsterAbility(
                    name="Duelist's Guard",
                    description="In response to being hit by a melee attack, Sister Ash adds 2 to her AC against that attack, possibly causing it to miss.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class AccursedGroupSmall(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed Group (Small)",
            hp=32,
            ac=9,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 12,
                Ability.DEXTERITY.short_name: 8,
                Ability.CONSTITUTION.short_name: 12,
                Ability.INTELLIGENCE.short_name: 3,
                Ability.WISDOM.short_name: 6,
                Ability.CHARISMA.short_name: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type="Undead",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.LARGE,
            ac_note="",
            hp_formula="8d6+4",
            speed_ground_ft=20,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[Condition.EXHAUSTION, Condition.POISONED],
            senses="darkvision 60 ft., Passive Perception 8",
            languages="Understands the languages its bodies knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Thinning Ranks",
                    description="The Small Group represents a cluster of roughly 3 to 4 Accursed shambling and grasping as a single combatant. The number of Rotten Grasp attacks it can make with Multiattack falls as its bodies are destroyed: 4 attacks while it has 25 or more Hit Points, 3 attacks at 17-24 Hit Points, 2 attacks at 9-16 Hit Points, and 1 attack at 8 Hit Points or fewer.",
                ),
                MonsterAbility(
                    name="Noc'tra's Failed Bargain",
                    description="If damage reduces the Small Group to 0 Hit Points, it must make a Constitution saving throw (DC 5 plus the damage taken) unless the damage is Radiant or from a Critical Hit. On a successful save, its last husk still standing holds together and the Small Group drops to 1 Hit Point instead.",
                ),
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Small Group has Advantage on saving throws against being frightened and against effects that would move it against its will, as the press of its fellow husks holds the line.",
                ),
                MonsterAbility(
                    name="Directed by the Faithful",
                    description="A priest of Noc'tra within 30 feet of the Small Group can take a Bonus Action to command it, causing the Small Group to immediately take the Attack action or to move up to its Speed toward a point the priest designates. Without such direction, the Small Group can only shamble toward the nearest creature it can sense and attack that creature.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="The Small Group makes a number of Rotten Grasp attacks determined by its Thinning Ranks trait (up to 4).",
                ),
                MonsterAbility(
                    name="Rotten Grasp",
                    description="Melee Attack Roll: +2, reach 5 ft. Hit: 3 (1d6) Bludgeoning damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
