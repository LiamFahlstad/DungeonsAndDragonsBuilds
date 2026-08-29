from Core import Definitions
from Core.Definitions import Ability, WIZARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ConjurationSavant(Feature):
    def __init__(self):
        super().__init__(name="Conjuration Savant", origin="Conjuration Wizard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The gold and time you must spend to copy a Conjuration spell into your spellbook is halved."
        return description


class MinorConjuration(Feature):
    def __init__(self):
        super().__init__(name="Minor Conjuration", origin="Conjuration Wizard Level 3", activation=FeatureActivation(action_type="action", duration="1 Hour", range="10 Feet"), usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your action to conjure up an inanimate object in your hand or on the ground in an unoccupied space that you can see within 10 feet of you. This object can be no larger than 3 feet on a side and weigh no more than 10 pounds, and its form must be that of a nonmagical object that you have seen. The object is visibly magical, radiating dim light out to 5 feet.\n"
            "The object disappears after 1 hour, when you use this feature again, or if it takes or deals any damage."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Location", "Your hand or unoccupied space within 10 feet"),
            ("Object Type", "Nonmagical inanimate object you have seen"),
            ("Size", "No larger than 3 feet on a side"),
            ("Weight", "No more than 10 pounds"),
            ("Appearance", "Visibly magical, dim light 5 feet"),
            ("Duration", "1 hour, until you use feature again, or until takes/deals damage"),
        ]


class BenignTransportation(Feature):
    def __init__(self):
        super().__init__(name="Benign Transportation", origin="Conjuration Wizard Level 6", activation=FeatureActivation(action_type="action", range="30 Feet"), usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your action to teleport up to 30 feet to an unoccupied space that you can see. Alternatively, you can choose a space within range that is occupied by a Small or Medium creature. If that creature is willing, you both teleport, swapping places.\n"
            "Once you use this feature, you can't use it again until you finish a long rest or you cast a conjuration spell of 1st level or higher."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Option 1", "Teleport up to 30 feet to unoccupied space you can see"),
            ("Option 2", "Swap with willing Small or Medium creature within range"),
            ("Recharge", "Long rest or cast conjuration spell of 1st level or higher"),
        ]


class FocusedConjuration(Feature):
    def __init__(self):
        super().__init__(name="Focused Conjuration", origin="Conjuration Wizard Level 10", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While you are concentrating on a conjuration spell, your concentration can't be broken as a result of taking damage."
        return description


class DurableSummons(Feature):
    def __init__(self):
        super().__init__(name="Durable Summons", origin="Conjuration Wizard Level 14", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Any creature that you summon or create with a conjuration spell has 30 temporary hit points."
        return description
