from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

SPEED = 35  # Given by your species


class Darkvision(TextFeature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Dhampir Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class SpiderClimb(TextFeature):
    def __init__(self, character_level: int):
        self.character_level = character_level
        super().__init__(name="Spider Climb", origin="Dhampir Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if self.character_level >= 3:
            return (
                "You have a Climb Speed equal to your Speed. "
                "You can move up, down, and across vertical surfaces and along ceilings while leaving your hands free."
            )
        return (
            "You have a Climb Speed equal to your Speed. "
            "When you reach character level 3, you can move up, down, and across vertical surfaces and along ceilings while leaving your hands free."
        )


class TraceOfUndeath(TextFeature):
    def __init__(self):
        super().__init__(name="Trace of Undeath", origin="Dhampir Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Necrotic damage."


class VampiricBite(TextFeature):
    def __init__(self):
        super().__init__(name="Vampiric Bite", origin="Dhampir Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "When you use your Unarmed Strike and deal damage, you can choose to bite with your fangs. "
            "You deal Piercing damage equal to 1d4 plus your Constitution modifier instead of the normal damage of an Unarmed Strike.\n"
            "In addition, when you deal this damage to a creature that isn't a Construct or an Undead, you can empower yourself in one of the following ways:\n"
            "Drain. You regain Hit Points equal to the Piercing damage dealt.\n"
            "Strengthen. You gain a bonus to the next ability check or attack roll you make within the next minute; the bonus is equal to the Piercing damage dealt.\n"
            f"You can empower yourself with this trait a number of times equal to your Proficiency Bonus ({proficiency_bonus}), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)
