import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class MagicAwareness(Feature):
    def __init__(self):
        super().__init__(name="Magic Awareness", origin="Path Of Wild Magic Barbarian Level 3", action_type="action", duration="Until the End of Your Next Turn", range="60 Feet", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "When you choose this path at 3rd level, as an action, you can open your awareness to the presence of concentrated magic. Until the end of your next turn, you know the location of any spell or magic item within 60 feet of you that isn't behind total cover. When you sense a spell, you learn which school of magic it belongs to.\n"
            "\n"
            "You can use this feature a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest", max_box_count=6, current_formula="Current amount: equal to your proficiency bonus.")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return [
            ("Action", "Action"),
            ("Range", "60 feet (not through total cover)"),
            ("Duration", "Until end of your next turn"),
            ("Detects", "Spells (learn school of magic) and magic items"),
            ("Uses", f"Proficiency bonus ({proficiency_bonus}) per long rest"),
        ]


class WildSurge(Feature):
    def __init__(self):
        super().__init__(name="Wild Surge", origin="Path Of Wild Magic Barbarian Level 3", duration="Until Your Rage Ends", usage_tags=["damage", "heal", "buff", "control", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        con_mod = character_stat_block.get_ability_modifier(Definitions.Ability.CONSTITUTION)
        dc = 8 + proficiency_bonus + con_mod
        description = (
            "Also at 3rd level, the magical energy roiling inside you sometimes erupts from you. When you enter your rage, roll on the Wild Magic table to determine the magical effect produced.\n"
            "\n"
            f"If the effect requires a saving throw, the DC equals 8 + your proficiency bonus + your Constitution modifier ({dc}).\n"
            "\n"
            "Wild Magic\n"
            "d8\tEffect\n"
            "1\tEach creature of your choice that you can see within 30 feet of you must succeed on a Constitution saving throw or take 1d12 necrotic damage. You also gain 1d12 temporary hit points.\n"
            "2\tYou teleport up to 30 feet to an unoccupied space you can see. Until your rage ends, you can use this effect again on each of your turns as a bonus action.\n"
            "3\tAn intangible spirit, which looks like a flumph or a pixie (your choice), appears within 5 feet of one creature of your choice that you can see within 30 feet of you. At the end of the current turn, the spirit explodes, and each creature within 5 feet of it must succeed on a Dexterity saving throw or take 1d6 force damage. Until your rage ends, you can use this effect again, summoning another spirit, on each of your turns as a bonus action.\n"
            "4\tMagic infuses one weapon of your choice that you are holding. Until your rage ends, the weapon's damage type changes to force, and it gains the light and thrown properties, with a normal range of 20 feet and a long range of 60 feet. If the weapon leaves your hand, the weapon reappears in your hand at the end of the current turn.\n"
            "5\tWhenever a creature hits you with an attack roll before your rage ends, that creature takes 1d6 force damage, as magic lashes out in retribution.\n"
            "6\tUntil your rage ends, you are surrounded by multicolored, protective lights; you gain a +1 bonus to AC, and while within 10 feet of you, your allies gain the same bonus.\n"
            "7\tFlowers and vines temporarily grow around you; until your rage ends, the ground within 15 feet of you is difficult terrain for your enemies.\n"
            "8\tA bolt of light shoots from your chest. Another creature of your choice that you can see within 30 feet of you must succeed on a Constitution saving throw or take 1d6 radiant damage and be blinded until the start of your next turn. Until your rage ends, you can use this effect again on each of your turns as a bonus action."
        )
        return description


class BolsteringMagic(Feature):
    def __init__(self):
        super().__init__(name="Bolstering Magic", origin="Path Of Wild Magic Barbarian Level 6", action_type="action", duration="For 10 Minutes", range="Touch", usage_tags=["buff", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "Beginning at 6th level, you can harness your wild magic to bolster yourself or a companion. As an action, you can touch one creature (which can be yourself) and confer one of the following benefits of your choice to that creature:\n"
            "\n"
            "For 10 minutes, the creature can roll a d3 whenever making an attack roll or an ability check and add the number rolled to the d20 roll.\n"
            "\n"
            "Roll a d3. The creature regains one expended spell slot, the level of which equals the number rolled or lower (the creature's choice). Once a creature receives this benefit, that creature can't receive it again until after a long rest.\n"
            "\n"
            "You can take this action a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest", max_box_count=6, current_formula="Current amount: equal to your proficiency bonus.")


class UnstableBacklash(Feature):
    def __init__(self):
        super().__init__(name="Unstable Backlash", origin="Path Of Wild Magic Barbarian Level 10", action_type="reaction", usage_tags=["damage", "heal", "buff", "control", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 10th level, when you are imperiled during your rage, the magic within you can lash out; immediately after you take damage or fail a saving throw while raging, you can use your reaction to roll on the Wild Magic table and immediately produce the effect rolled. This effect replaces your current Wild Magic effect."
        )
        return description

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "When you take damage or fail a save while raging, use a Reaction to roll on the Wild Magic table and produce that effect (replaces your current effect)."
        )


class ControlledSurge(Feature):
    def __init__(self):
        super().__init__(name="Controlled Surge", origin="Path Of Wild Magic Barbarian Level 14", usage_tags=["damage", "heal", "buff", "control", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 14th level, whenever you roll on the Wild Magic table, you can roll the die twice and choose which of the two effects to unleash. If you roll the same number on both dice, you can ignore the number and choose any effect on the table."
        )
        return description
