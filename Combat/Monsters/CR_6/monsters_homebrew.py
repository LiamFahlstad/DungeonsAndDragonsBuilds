from Combat.Definitions import (
    Alignment,
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterAbility,
    Size,
)
from Definitions import Ability


class TheMouthThatWalks(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Mouth That Walks",
            hp=124,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 19,
                Ability.DEXTERITY.short_name: 6,
                Ability.CONSTITUTION.short_name: 18,
                Ability.INTELLIGENCE.short_name: 3,
                Ability.WISDOM.short_name: 11,
                Ability.CHARISMA.short_name: 18,
            },
            saving_throws={
                Ability.CONSTITUTION.short_name: 7,
            },
            spell_slots={},
            cr="6",
            monster_type="Aberration",
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
                MonsterAbility(
                    name="Legendary Resistance (1/Day)",
                    description="If the Mouth fails a saving throw, it can choose to succeed instead, its ruined mind refusing the concept of a true, final death.",
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
