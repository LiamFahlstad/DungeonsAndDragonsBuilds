from Core.Definitions import Ability, RANGER_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class GatheredSwarm(Feature):
    def __init__(self):
        super().__init__(name="Gathered Swarm", origin="Swarmkeeper Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, a swarm of intangible nature spirits has bonded itself to you and can assist you in battle. While you're alive, the swarm remains in your space, crawling on you or flying and skittering around you within your space. You determine its appearance, or you generate its appearance by rolling on the Swarm Appearance table.\n"
            "Swarm Appearance\n"
            "d4\tAppearance\n"
            "1\tSwarming insects\n"
            "2\tMiniature twig blights\n"
            "3\tFluttering birds\n"
            "4\tPlayful pixies\n"
            "Once on each of your turns, you can cause the swarm to assist you in one of the following ways, immediately after you hit a creature with an attack:\n"
            "    * The attack's target takes 1d6 piercing damage from the swarm.\n"
            "    * The attack's target must succeed on a Strength saving throw against your spell save DC or be moved by the swarm up to 15 feet horizontally in a direction of your choice.\n"
            "    * You are moved by the swarm 5 feet horizontally in a direction of your choice."
        )
        return description


class SwarmkeeperMagic(Feature):
    def __init__(self):
        super().__init__(name="Swarmkeeper Magic", origin="Swarmkeeper Ranger Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Also at 3rd level, you learn the Mage Hand cantrip if you don't already know it. When you cast it, the hand takes the form of your swarming nature spirits.\n"
            "\n"
            "You also learn an additional spell of 1st level or higher when you reach certain levels in this class, as shown in the Swarmkeeper Spells table. Each spell counts as a ranger spell for you, but it doesn't count against the number of ranger spells you know.\n"
            "Swarmkeeper Spells\n"
            "Ranger Level\tSpell\n"
            "3rd\tFaerie Fire, Mage Hand\n"
            "5th\tWeb\n"
            "9th\tGaseous Form\n"
            "13th\tArcane Eye\n"
            "17th\tInsect Plague"
        )
        return description


class WrithingTide(Feature):
    def __init__(self):
        super().__init__(name="Writhing Tide", origin="Swarmkeeper Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "Beginning at 7th level, you can condense part of your swarm into a focused mass that lifts you up. As a bonus action, you gain a flying speed of 10 feet and can hover. This effect lasts for 1 minute or until you are incapacitated.\n"
            "\n"
            f"You can use this feature a number of times equal to your proficiency bonus ({proficiency_bonus}), and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest", max_box_count=6, current_formula="Current amount: equal to your proficiency bonus.")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return [
            ("What", "Gain flying speed from swarm"),
            ("Action", "Bonus action"),
            ("Effect", "Flying speed 10 ft, can hover"),
            ("Duration", "1 minute or until incapacitated"),
            ("Uses", f"{proficiency_bonus}"),
            ("Recharge", "Long rest"),
        ]


class MightySwarm(Feature):
    def __init__(self):
        super().__init__(name="Mighty Swarm", origin="Swarmkeeper Ranger Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 11th level, your Gathered Swarm grows mightier in the following ways:\n"
            "    * The damage of Gathered Swarm increases to 1d8.\n"
            "    * If a creature fails its saving throw against being moved by the Gathered Swarm, you can also cause the swarm to knock the creature prone.\n"
            "    * When you are moved by Gathered Swarm, it gives you half cover until the start of your next turn."
        )
        return description


class SwarmingDispersal(Feature):
    def __init__(self):
        super().__init__(name="Swarming Dispersal", origin="Swarmkeeper Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "When you reach 15th level, you can discorporate into your swarm, avoiding danger. When you take damage, you can use your reaction to give yourself resistance to that damage. You vanish into your swarm and then teleport to an unoccupied space that you can see within 30 feet of you, where you reappear with the swarm.\n"
            "\n"
            f"You can use this feature a number of times equal to your proficiency bonus ({proficiency_bonus}), and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest", max_box_count=6, current_formula="Current amount: equal to your proficiency bonus.")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return [
            ("What", "Discorporate into swarm"),
            ("Action", "Reaction"),
            ("Condition", "When you take damage"),
            ("Effect", "Resistance to that damage, teleport to unoccupied space within 30 ft"),
            ("Uses", f"{proficiency_bonus}"),
            ("Recharge", "Long rest"),
        ]
