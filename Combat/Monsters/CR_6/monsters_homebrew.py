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
    Size,
    Skill,
)
from Core.Definitions import Ability


class TheMouthThatWalks(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Mouth That Walks",
            hp=124,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 19,
                Ability.DEXTERITY: 6,
                Ability.CONSTITUTION: 18,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 11,
                Ability.CHARISMA: 18,
            },
            saving_throws={
                Ability.CONSTITUTION: 7,
            },
            spell_slots={},
            cr="6",
            monster_type=MonsterType.ABERRATION, monster_type_note='',
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.LARGE,
            ac_note="scarred, wound-thick flesh and rusted ritual chains",
            hp_formula="13d10 + 52",
            speed_ground_ft=5,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="The Mouth is bound in ancient chains anchored to the sanctum floor and cannot move more than 10 feet from its anchor point unless the chains are destroyed (AC 20, 30 Hit Points, Immune to Poison and Psychic damage).",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
                DamageTypeEntry(damage_types=[DamageType.PSYCHIC], note=""),
            ],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[
                Condition.CHARMED,
                Condition.EXHAUSTION,
                Condition.FRIGHTENED,
                Condition.POISONED,
            ],
            senses="blindsight 60 ft. (blind beyond this radius), Passive Perception 10",
            languages="understands Common and Undercommon but can speak only in broken, overlapping fragments of Noc'tra",
            traits=[
                LegendaryResistance(
                    creature_name="Mouth",
                    uses=1,
                    flavor_note="its ruined mind refusing the concept of a true, final death",
                ),
                MonsterAbility(
                    name="The Ceaseless Litany",
                    description="The wound that was once the Mouth's face and chest never stops speaking splintered fragments of Noc'tra, filling a 20-foot Emanation with a droning, layered horror. A creature that ends its turn within the Emanation begins accumulating the toll of Noc'tra: at the start of each of its turns thereafter, it takes 1d6 Psychic damage for every consecutive round it has ended its turn within the Emanation (maximum 6d6), as the broken litany claws deeper into its mind with every passing moment of exposure. A creature that ends its turn outside the Emanation loses all accumulated rounds, the grip fading once it is out of earshot. A creature that is Deafened is immune to this damage.",
                ),
                MonsterAbility(
                    name="Verge of Unmaking",
                    description="While Bloodied, the wound the Curse tore into the Mouth strains to finish what it started: the Emanation of the Ceaseless Litany increases to 30 feet, and the Mouth's Devouring Maw attack deals an extra 7 (2d6) Necrotic damage.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Devouring Maw",
                    description="Melee Attack Roll: +7, reach 10 ft. Hit: 26 (4d10 + 4) Piercing damage plus 7 (2d6) Necrotic damage. If the target is Medium or smaller and isn't already grappled by the Mouth, the target is also grappled (escape DC 15) and drawn into the wound: while grappled this way, the target is Restrained, and at the start of each of its turns it takes 7 (2d6) Necrotic damage as the wound convulses around it.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )


class TheHunter(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Hunter",
            hp=110,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 16,
                Ability.DEXTERITY: 18,
                Ability.CONSTITUTION: 16,
                Ability.INTELLIGENCE: 12,
                Ability.WISDOM: 15,
                Ability.CHARISMA: 14,
            },
            saving_throws={
                Ability.CONSTITUTION: 6,
                Ability.WISDOM: 5,
            },
            spell_slots={},
            cr="6",
            monster_type=MonsterType.HUMANOID, monster_type_note='Cursebound',
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="worn leathers and curse-hardened grey skin",
            hp_formula="13d10 + 39",
            speed_ground_ft=35,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERCEPTION: 5,
                Skill.STEALTH: 7,
                Skill.INTIMIDATION: 5,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            damage_immunities=[],
            condition_immunities=[
                Condition.FRIGHTENED,
            ],
            senses="darkvision 60 ft., Passive Perception 15",
            languages="Common, plus a fragment of the old tongue the Curse left behind, which it rarely speaks",
            traits=[
                MonsterAbility(
                    name="Cursebound",
                    description="The Hunter has absorbed the essence of an Accursed creature into its own flesh, marking it with grey skin, blackened teeth, and eyes like dying embers. It has Resistance to Necrotic and Poison damage, and it is immune to being Frightened.",
                ),
                MonsterAbility(
                    name="Unnerving Calm",
                    description="The Hunter never raises its voice or its guard. It has Advantage on Charisma (Intimidation) checks. In addition, at the start of each of its turns, the Hunter can choose one creature within 10 feet of it that can see it; that creature must succeed on a DC 15 Wisdom saving throw or have Disadvantage on attack rolls against the Hunter until the start of the Hunter's next turn, unnerved by its stillness.",
                ),
                MonsterAbility(
                    name="Curse Sense",
                    description="The Hunter always knows the direction and distance to any Accursed or cursed creature within 60 feet of it, even if that creature is hidden, invisible, or behind total cover, and the Hunter has Advantage on attack rolls against such creatures.",
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="Hunter",
                    attacks_text="two Cursed Kris attacks",
                ),
                MonsterAbility(
                    name="Cursed Kris",
                    description="Melee Attack Roll: +7, reach 5 ft. Hit: 11 (2d6 + 4) Piercing damage plus 7 (2d6) Necrotic damage as the bound curse feeds through the blade.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Marked for the Hunt (Recharge 5-6)",
                    description="The Hunter fixes its gaze on one creature it can see within 30 feet. Constitution Saving Throw: DC 15, the target. Failure: The target is Marked until the start of the Hunter's next turn. While a creature is Marked this way, the Hunter's attack rolls against it score a Critical Hit on a roll of 19 or 20, and the Marked creature can't benefit from Invisible or Heavily Obscured against the Hunter.",
                ),
            ],
            reactions=[
                MonsterAbility(
                    name="Predator's Reflexes",
                    description="Trigger: A creature the Hunter can see moves within 5 feet of the Hunter. Response: The Hunter makes one Cursed Kris attack against that creature.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
