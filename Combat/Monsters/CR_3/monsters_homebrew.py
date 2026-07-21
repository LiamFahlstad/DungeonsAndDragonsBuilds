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


class CantorOfTheBlackChoir(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Cantor of the Black Choir",
            hp=90,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 10,
                Ability.DEXTERITY.short_name: 14,
                Ability.CONSTITUTION.short_name: 16,
                Ability.INTELLIGENCE.short_name: 12,
                Ability.WISDOM.short_name: 14,
                Ability.CHARISMA.short_name: 17,
            },
            saving_throws={
                Ability.CONSTITUTION.short_name: 5,
                Ability.WISDOM.short_name: 4,
            },
            spell_slots={},
            cr="3",
            monster_type="Humanoid (Curse-Touched)",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="voice-amplifying horn and ritual wrappings",
            hp_formula="12d8 + 36",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERCEPTION: 4,
                Skill.RELIGION: 3,
                Skill.DECEPTION: 5,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
            ],
            damage_immunities=[],
            condition_immunities=[Condition.FRIGHTENED],
            senses="darkvision 60 ft., Passive Perception 14",
            languages="Common, Undercommon (speaks only in broken, layered echoes)",
            traits=[
                MonsterAbility(
                    name="Blackened Choir",
                    description="Veins of curse-blackened blood lace the Cantor's throat and chest, drawing necrotic energy inward: the Cantor has Resistance to Necrotic damage and is immune to being Frightened, having spoken past death often enough that it no longer holds any terror for it.",
                ),
                MonsterAbility(
                    name="Brink of the Accursed",
                    description="While Bloodied, the curse strains against the Cantor's failing throat: at the start of each of its turns, the Cantor takes 3 (1d6) Necrotic damage as Noc'tra claws its way outward, but until the start of its next turn, its Curseward Lash and Speak Noc'tra deal an extra 3 (1d6) Necrotic damage and the save DC of Speak Noc'tra increases by 1. If this damage would reduce the Cantor to 0 Hit Points, it instead drops to 1 Hit Point as its ruined throat finally gives out: for the rest of the encounter it can no longer speak, and it loses access to Speak Noc'tra and Conduct the Choir, the last of its will consumed by the curse it served.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="The Cantor makes two Curseward Lash attacks.",
                ),
                MonsterAbility(
                    name="Curseward Lash",
                    description="Melee or Ranged Attack Roll: +5, reach 5 ft. or range 30 ft. Hit: 11 (2d8 + 2) Necrotic damage, and the target has Disadvantage on the next saving throw it makes against a Wisdom- or Charisma-based effect before the start of the Cantor's next turn, its will already fraying at the edge of the Cantor's voice.",
                ),
                MonsterAbility(
                    name="Speak Noc'tra (Recharge 5-6)",
                    description="The Cantor tears a fragment of the black word from its ruined throat in a 30-foot Cone. Each creature in the area makes a DC 13 Wisdom saving throw. Failure: 14 (4d6) Psychic damage, and the target has the Frightened condition until the end of the Cantor's next turn. Success: Half damage only. A half-second later, the word catches up to itself: at the start of the Cantor's next turn, each creature that failed the save must succeed on a DC 13 Wisdom saving throw or take 7 (2d6) Necrotic damage as the echo arrives. Whether or not the word strikes any target, the toll is real: the Cantor takes 3 (1d6) Necrotic damage as it passes through, one utterance closer to its own undoing.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Conduct the Choir",
                    description="The Cantor lets out a wordless, layered command audible to every Accursed creature within 40 feet that can hear it. Each commanded Accursed can immediately move up to its Speed and make one attack, their bodies moving in eerie unison to the Cantor's voice.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class GarronTheKindly(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Garron the Kindly",
            hp=97,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 20,
                Ability.DEXTERITY.short_name: 12,
                Ability.CONSTITUTION.short_name: 18,
                Ability.INTELLIGENCE.short_name: 10,
                Ability.WISDOM.short_name: 14,
                Ability.CHARISMA.short_name: 12,
            },
            saving_throws={
                Ability.CONSTITUTION.short_name: 6,
                Ability.WISDOM.short_name: 4,
            },
            spell_slots={},
            cr="3",
            monster_type="Humanoid (Goliath)",
            alignment=Alignment.LAWFUL_NEUTRAL,
            size=Size.LARGE,
            ac_note="hide armor, natural bulk",
            hp_formula="13d10 + 26",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.MEDICINE: 6,
                Skill.INTIMIDATION: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[Condition.FRIGHTENED],
            senses="Passive Perception 12",
            languages="understands Common and Goliath but can't speak; communicates by hand signs and a chalkboard he carries strapped to his back",
            traits=[
                MonsterAbility(
                    name="Field Surgeon",
                    description="Garron carries a satchel of anesthetics, clean tools, and stitched bandages, and is proficient with healer's kits. He has Advantage on Wisdom (Medicine) checks, and any creature he tends for at least 1 minute outside combat regains all of its missing Hit Points, so long as it permits the treatment.",
                ),
                MonsterAbility(
                    name="Unshaken Conviction",
                    description="Garron's certainty that he is saving the world is absolute and untouched by doubt: he can't be Frightened, and no plea, scream, or accusation slows his steady hands.",
                ),
                MonsterAbility(
                    name="The Reliquary of Voices",
                    description="Strung along Garron's belt are dozens of small glass jars, each labeled in careful handwriting with a name and a date, every one a tongue he has removed. He keeps them not as trophies but as a record of everyone he believes he has saved. Should a creature realize what the jars hold, Garron has Advantage on the Intimidation check that follows, though he intends it as reassurance, never as a threat.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="Garron makes two Surgeon's Maul attacks.",
                ),
                MonsterAbility(
                    name="Surgeon's Maul",
                    description="Melee Attack Roll: +7, reach 10 ft. Hit: 14 (2d10 + 5) Bludgeoning damage.",
                ),
                MonsterAbility(
                    name="Precise Incision",
                    description="Melee Attack Roll: +7, reach 10 ft. Hit: 9 (2d6 + 2) Slashing damage, and the target must succeed on a DC 13 Constitution saving throw or Garron's blade finds the throat with surgical precision: until the end of the target's next turn, it can't speak and can't cast spells that require a Verbal component.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Field Dressing (Recharge 5-6)",
                    description="Garron tends to his own wounds or those of one creature within 5 feet of him. The chosen creature regains 13 (2d8 + 4) Hit Points.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class SerCaldusTheVowOfSilence(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Ser Caldus, the Vow of Silence",
            hp=67,
            ac=18,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 18,
                Ability.DEXTERITY.short_name: 10,
                Ability.CONSTITUTION.short_name: 16,
                Ability.INTELLIGENCE.short_name: 10,
                Ability.WISDOM.short_name: 14,
                Ability.CHARISMA.short_name: 15,
            },
            saving_throws={
                Ability.WISDOM.short_name: 4,
                Ability.CHARISMA.short_name: 4,
            },
            spell_slots={},
            cr="3",
            monster_type="Humanoid (Orc)",
            alignment=Alignment.LAWFUL_NEUTRAL,
            size=Size.MEDIUM,
            ac_note="plate armor, shield",
            hp_formula="9d8 + 27",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.INSIGHT: 4,
                Skill.RELIGION: 2,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Passive Perception 12",
            languages="understands Common and Orc but speaks only in hand signs, honoring his order's vow",
            traits=[
                MonsterAbility(
                    name="Vow of Silence",
                    description="A hush clings to Ser Caldus and carries to his allies: each creature of his choice within 10 feet of him has Advantage on saving throws against being Frightened or Charmed by an effect that requires the source to speak or make sound.",
                ),
                MonsterAbility(
                    name="Names Unspoken",
                    description="Every tongue Ser Caldus has taken is recorded as a tattooed name on his forearm, so that someone still remembers what its owner can no longer say. He has Advantage on any Wisdom (Insight) or Intelligence (History) check made to recall the identity or history of a creature he has silenced.",
                ),
                MonsterAbility(
                    name="Undying Vow (1/Day)",
                    description="If damage would reduce Ser Caldus to 0 Hit Points, he instead drops to 1 Hit Point, his vow unwilling to let him fall before a rite is complete.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="Ser Caldus makes two Silencing Blade attacks.",
                ),
                MonsterAbility(
                    name="Silencing Blade",
                    description="Melee Attack Roll: +6, reach 5 ft. Hit: 11 (2d6 + 4) Slashing damage.",
                ),
                MonsterAbility(
                    name="Rite of Silence (3/Day)",
                    description="Immediately after hitting a creature with Silencing Blade, Ser Caldus kneels into the strike and calls the rite complete: the target takes an extra 9 (2d8) Psychic damage. If this damage reduces the target to 0 Hit Points, it dies without a sound, and each other creature within 10 feet that witnessed the kill must succeed on a DC 13 Wisdom saving throw or have the Frightened condition until the end of Ser Caldus's next turn.",
                ),
            ],
            bonus_actions=[],
            reactions=[
                MonsterAbility(
                    name="Silent Guard",
                    description="Trigger: An allied creature within 10 feet of Ser Caldus is about to make a saving throw against an effect with a Verbal component or one that relies on sound, such as a scream or a shouted command. Response: That ally has Advantage on the saving throw, Ser Caldus's vow standing between his allies and the voice of the curse.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
