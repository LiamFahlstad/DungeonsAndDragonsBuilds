from Core.Definitions import CharacterClass, ROGUE_HIT_DIE
import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class PsionicPower(Feature):
    def __init__(self):
        super().__init__(name="Psionic Power", origin="Soulknife Rogue Level 3", activation=FeatureActivation(action_type=ActionType.ACTION, duration="Hours Based on Energy Die Roll", range="1 Mile"), usage_tags=["utility"], uses=FeatureUses(max_uses=12, regain_all_on="long rest", regain_x_on=(1, "short rest")))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You harbor a wellspring of psionic energy within yourself. It is represented by your Psionic Energy Dice, which fuel certain powers you have from this subclass. The Soulknife Energy Dice table shows the number of these dice you have when you reach certain Rogue levels, and the table shows the die size.\n"
            "Soulknife Energy Dice\n"
            "Rogue Level	Die Size	Number\n"
            "3	D6	4\n"
            "5	D8	6\n"
            "9	D8	8\n"
            "11	D10	8\n"
            "13	D10	10\n"
            "17	D12	12\n"
            "Any features in this subclass that use a Psionic Energy Die use only the dice from this subclass. Some of your powers expend a Psionic Energy Die, as specified in the power's description, and you can't use the power if it requires you to use a die when your Psionic Energy Dice are all expended.\n"
            "You regain one of your expended Psionic Energy Dice when you finish a Short Rest, and you regain all of them when you finish a Long Rest.\n"
            "Psi-Bolstered Knack. If you fail an ability check using a skill or tool with which you have proficiency, you can roll one Psionic Energy Die and add the number rolled to the check, potentially turning failure into success. The die is expended only if the roll then succeeds.\n"
            "Psychic Whispers. You can establish telepathic communication between yourself and others. As a Magic action, choose one or more creatures you can see, up to a number of creatures equal to your Proficiency Bonus, and then roll one Psionic Energy Die. For a number of hours equal to the number rolled, the chosen creatures can speak telepathically to you, and you can speak telepathically with them. To send or receive a message (no action required), you and the other creature must be within 1 mile of each other. A creature can end the telepathic connection at any time (no action required)."
        )
        return description



    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST
class PsychicBlades(Feature):
    def __init__(self):
        super().__init__(name="Psychic Blades", origin="Soulknife Rogue Level 3", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can manifest shimmering blades of psychic energy. Whenever you take the Attack action or make an Opportunity Attack, you can manifest a Psychic Blade in your free hand and make the attack with that blade. The magic blade has the following traits:\n"
            "Weapon Category: Simple Melee\n"
            "Damage on a Hit: 1d6 Psychic plus the ability modifier used for the attack roll\n"
            "Properties: Finesse, Thrown (range 60/120 feet)\n"
            "Mastery: Vex (you can use this property, and it doesn't count against the number of properties you can use with Weapon Mastery)\n"
            "The blade vanishes immediately after it hits or misses its target, and it leaves no mark if it deals damage.\n"
            "After you attack with the blade on your turn, you can make a melee or ranged attack with a second psychic blade as a Bonus Action on the same turn if your other hand is free to create it. The damage die of this bonus attack is 1d4 instead of 1d6."
        )
        return description


class SoulBlades(Feature):
    def __init__(self):
        super().__init__(name="Soul Blades", origin="Soulknife Rogue Level 9", activation=FeatureActivation(range="Up to 120 Feet"), usage_tags=["buff", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can now use the following powers with your Psychic Blades.\n"
            "Homing Strikes. If you make an attack roll with your Psychic Blade and miss the target, you can roll one Psionic Energy Die and add the number rolled to the attack roll. If this causes the attack to hit, the die is expended.\n"
            "Psychic Teleportation. As a Bonus Action, you manifest a Psychic Blade, expend one Psionic Energy Die and roll it, and throw the blade at an unoccupied space you can see up to a number of feet away equal to 10 times the number rolled. You then teleport to that space, and the blade vanishes."
        )
        return description


class PsychicVeil(Feature):
    def __init__(self):
        super().__init__(name="Psychic Veil", origin="Soulknife Rogue Level 13", activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Hour or Until Dismissed"), usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can weave a veil of psychic static to mask yourself. As a Magic action, you gain the Invisible condition for 1 hour or until you dismiss the effect (no action required). This invisibility ends early immediately after you deal damage to a creature or you force a creature to make a saving throw.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Magic action"),
            ("Effect", "Gain Invisible condition"),
            ("Duration", "1 hour or until you dismiss"),
            ("Ends Early", "When you deal damage or force a save"),
            ("Recharge", "Long Rest (or expend 1 Psionic Energy Die)"),
        ]


class RendMind(Feature):
    def __init__(self):
        super().__init__(name="Rend Mind", origin="Soulknife Rogue Level 17", activation=FeatureActivation(duration="1 Minute"), usage_tags=["control"])

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        dexterity_modifier = character_stat_block.get_dexterity_modifier()
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return 8 + dexterity_modifier + proficiency_bonus

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can sweep your Psychic Blades through a creature's mind. When you use you Psychic Blades to deal Sneak Attack damage to a creature, you can force that target to make a Wisdom saving throw (DC 8 plus your Dexterity modifier and Proficiency Bonus). If the save fails, the target has the Stunned condition for 1 minute. The Stunned target repeats the save at the end of each of its turns, ending the effect on itself with a success.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest unless you expend three Psionic Energy Dice (no action required) to restore your use of it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        dc = self.calculate_dc(character_stat_block)
        return [
            ("Trigger", "Use Psychic Blades to deal Sneak Attack damage"),
            ("Save", f"Wisdom (DC {dc})"),
            ("Effect", "Stunned for 1 minute on failed save"),
            ("Repeat Save", "End of target's turn (success ends effect)"),
            ("Recharge", "Long Rest (or expend 3 Psionic Energy Dice)"),
        ]
