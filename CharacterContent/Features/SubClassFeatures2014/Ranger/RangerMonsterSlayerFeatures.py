from CharacterContent.Features.Core.BaseFeatures import Feature
from Core.Definitions import Ability
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class MonsterSlayerMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Monster Slayer Magic", origin="Monster Slayer Ranger Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 3rd level, you learn an additional spell when you reach certain levels in this class, as shown in the Monster Slayer Spells table. The spell counts as a ranger spell for you, but it doesn't count against the number of ranger spells you know.\n"
            "Monster Slayer Spells\n"
            "Ranger Level	Spells\n"
            "3	Protection from Evil and Good\n"
            "5	Zone of Truth\n"
            "9	Magic Circle\n"
            "13	Banishment\n"
            "17	Hold Monster"
        )
        return description


class HuntersSense(Feature):
    def __init__(self):
        super().__init__(
            name="Hunter's Sense",
            origin="Monster Slayer Ranger Level 3",
            action_type="action",
            range="60 Feet",
            usage_tags=["utility"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, you gain the ability to peer at a creature and magically discern how best to hurt it. As an action, choose one creature you can see within 60 feet of you. You immediately learn whether the creature has any damage immunities, resistances, or vulnerabilities and what they are. If the creature is hidden from divination magic, you sense that it has no damage immunities, resistances, or vulnerabilities.\n"
            "\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses of it when you finish a long rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wisdom_modifier)
        return [
            ("What", "Discern damage immunities/resistances/vulnerabilities"),
            ("Action", "Action"),
            ("Range", "60 feet"),
            ("Effect", "Learn creature's damage properties"),
            ("Uses", f"{uses}"),
            ("Recharge", "Long rest"),
        ]


class SlayersPrey(Feature):
    def __init__(self):
        super().__init__(
            name="Slayer's Prey",
            origin="Monster Slayer Ranger Level 3",
            action_type="bonus_action",
            duration="Until Short or Long Rest",
            range="60 Feet",
            usage_tags=["damage"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 3rd level, you can focus your ire on one foe, increasing the harm you inflict on it. As a bonus action, you designate one creature you can see within 60 feet of you as the target of this feature. The first time each turn that you hit that target with a weapon attack, it takes an extra 1d6 damage from the weapon.\n"
            "\n"
            "This benefit lasts until you finish a short or long rest. It ends early if you designate a different creature."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("What", "Designate one creature as prey"),
            ("Action", "Bonus action"),
            ("Range", "60 feet"),
            ("Effect", "Extra 1d6 damage on first hit per turn"),
            ("Duration", "Until short or long rest (ends early if redesignate)"),
        ]


class SupernaturalDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Supernatural Defense",
            origin="Monster Slayer Ranger Level 7",
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 7th level, you gain extra resilience against your prey's assaults on your mind and body. Whenever the target of your Slayer's Prey forces you to make a saving throw and whenever you make an ability check to escape that target's grapple, add 1d6 to your roll."
        return description


class MagicUsersNemesis(Feature):
    def __init__(self):
        super().__init__(
            name="Magic-User's Nemesis",
            origin="Monster Slayer Ranger Level 11",
            action_type="reaction",
            range="60 Feet",
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 11th level, you gain the ability to thwart someone else's magic. When you see a creature casting a spell or teleporting within 60 feet of you, you can use your reaction to try to magically foil it. The creature must succeed on a Wisdom saving throw against your spell save DC, or its spell or teleport fails and is wasted.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        spell_save_dc = 8 + proficiency_bonus + wisdom_modifier
        return [
            ("What", "Foil spell or teleport"),
            ("Action", "Reaction"),
            ("Range", "60 feet"),
            ("Save", f"Wisdom save vs. spell save DC {spell_save_dc}"),
            ("Effect", "Spell or teleport fails"),
            ("Recharge", "Short or long rest"),
        ]


class SlayersCounter(Feature):
    def __init__(self):
        super().__init__(
            name="Slayer's Counter",
            origin="Monster Slayer Ranger Level 15",
            action_type="reaction",
            usage_tags=["damage"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 15th level, you gain the ability to counterattack when your prey tries to sabotage you. If the target of your Slayer's Prey forces you to make a saving throw, you can use your reaction to make one weapon attack against the quarry. You make this attack immediately before making the saving throw. If the attack hits, your save automatically succeeds, in addition to the attack's normal effects."
        return description
