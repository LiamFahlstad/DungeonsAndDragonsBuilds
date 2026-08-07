from Core.Definitions import BARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class DazzlingFootwork(Feature):
    def __init__(self):
        super().__init__(
            name="Dazzling Footwork", origin="College of Dance Bard Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "While you aren't wearing armor or wielding a Shield, you gain the following benefits.\n"
            "Dance Virtuoso. You have Advantage on any Charisma (Performance) check you make that involves you dancing.\n"
            "Unarmored Defense. Your base Armor Class equals 10 plus your Dexterity and Charisma modifiers.\n"
            "Agile Strikes. When you expend a use of your Bardic Inspiration as part of an action, a Bonus Action, or a Reaction, you can make one Unarmed Strike as part of that action, Bonus Action, or Reaction.\n"
            "Bardic Damage. You can use Dexterity instead of Strength for the attack rolls of your Unarmed Strikes. When you deal damage with an Unarmed Strike, you can deal Bludgeoning damage equal to a roll of your Bardic Inspiration die plus your Dexterity modifier, instead of the strike's normal damage. This roll doesn't expend the die."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Dance Virtuoso", "Advantage on Charisma (Performance) checks involving dancing"),
            ("Unarmored Defense", "AC = 10 + Dex modifier + Cha modifier"),
            ("Agile Strikes", "When expending Bardic Inspiration, make one Unarmed Strike as part of that action"),
            ("Bardic Damage", "Unarmed Strikes use Dexterity; deal Bludgeoning damage = Bardic Inspiration die roll + Dex modifier (no cost)"),
        ]


class InspiringMovement(Feature):
    def __init__(self):
        super().__init__(
            name="Inspiring Movement", origin="College of Dance Bard Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When an enemy you can see ends its turn within 5 feet of you, you can take a Reaction and expend one use of your Bardic Inspiration to move up to half your Speed. Then one ally of your choice within 30 feet of you can also move up to half their Speed using their Reaction.\n"
            "None of this feature's movement provokes Opportunity Attacks."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Enemy you can see ends its turn within 5 feet of you"),
            ("Action", "Reaction"),
            ("Cost", "1 use of Bardic Inspiration"),
            ("Effect", "You move up to half your Speed; one ally within 30 feet moves up to half its Speed using its Reaction"),
            ("Movement", "Does not provoke Opportunity Attacks"),
        ]


class TandemFootwork(Feature):
    def __init__(self):
        super().__init__(name="Tandem Footwork", origin="College of Dance Bard Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you roll Initiative, you can expend one use of your Bardic Inspiration if you don't have the Incapacitated condition. When you do so, roll your Bardic Inspiration die; you and each ally within 30 feet of you who can see or hear you gains a bonus to Initiative equal to the number rolled."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Roll Initiative"),
            ("Condition", "You cannot have the Incapacitated condition"),
            ("Cost", "1 use of Bardic Inspiration"),
            ("Effect", "Roll Bardic Inspiration die; you and each ally within 30 feet who can see/hear you gain that bonus to Initiative"),
        ]


class LeadingEvasion(Feature):
    def __init__(self):
        super().__init__(
            name="Leading Evasion", origin="College of Dance Bard Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you are subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you instead take no damage if you succeed on the saving throw and only half damage if you fail. If any creatures within 5 feet of you are making the same Dexterity saving throw, you can share this benefit with them for that save.\n"
            "You can't use this feature if you have the Incapacitated condition."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Dexterity save to take only half damage"),
            ("Benefit", "Success: take no damage; Failure: take only half damage"),
            ("Share", "Creatures within 5 feet can use this benefit for the same save"),
            ("Condition", "Cannot use if you have the Incapacitated condition"),
        ]
