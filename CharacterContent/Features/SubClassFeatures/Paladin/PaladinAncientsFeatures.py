from Core.Definitions import PALADIN_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class NaturesWrath(Feature):
    def __init__(self):
        super().__init__(
            name="Nature's Wrath", origin="Oath of the Ancients Paladin Level 3", activation=FeatureActivation(action_type="action", duration="1 Minute", range="15 Feet"), usage_tags=["control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to conjure spectral vines around nearby creatures. Each creature of your choice that you can see within 15 feet of yourself must succeed on a Strength saving throw or have the Restrained condition for 1 minute. A Restrained creature repeats the save at the end of each of its turns, ending the effect on a success."
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Magic action"),
            ("Cost", "1 Channel Divinity use"),
            ("Range", "15 feet"),
            ("Save", "Strength"),
            ("Effect", "Restrained condition for 1 minute (repeats save at end of turn)"),
        ]


class OathOfTheAncientsSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Oath of the Ancients Spells",
            origin="Oath of the Ancients Paladin Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The magic of your oath ensures you always have certain spells ready; when you reach a Paladin level specified in the Oath of the Ancients Spells table, you thereafter always have the listed spells prepared.\n"
            "Oath of the Ancients Spells\n"
            "Paladin Level	Spells\n"
            "3	Ensnaring Strike, Speak with Animals\n"
            "5	Misty Step, Moonbeam\n"
            "9	Plant Growth, Protection from Energy\n"
            "13	Ice Storm, Stoneskin\n"
            "17	Commune with Nature, Tree Stride"
        )
        return description


class AuraOfWarding(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Warding", origin="Oath of the Ancients Paladin Level 7", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Ancient magic lies so heavily upon you that it forms an eldritch ward, blunting energy from beyond the Material Plane; you and your allies have Resistance to Necrotic, Psychic, and Radiant damage while in your Aura of Protection."
        return description


class UndyingSentinel(Feature):
    def __init__(self):
        super().__init__(
            name="Undying Sentinel", origin="Oath of the Ancients Paladin Level 15", usage_tags=["heal"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you are reduced to 0 Hit Points and not killed outright, you can drop to 1 Hit Point instead, and you regain a number of Hit Points equal to three times your Paladin level. Once you use this feature, you can't do so again until you finish a Long Rest.\n"
            "Additionally, you can't be aged magically, and you cease visibly aging."
        )
        return description

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "When reduced to 0 HP and not killed, drop to 1 HP instead and regain 3× your Paladin level HP (1/Long Rest). "
            "Additionally, you can't be aged magically and stop visibly aging."
        )


class ElderChampion(Feature):
    def __init__(self):
        super().__init__(
            name="Elder Champion", origin="Oath of the Ancients Paladin Level 20", activation=FeatureActivation(action_type="bonus_action", duration="1 Minute or Until Ended"), usage_tags=["heal", "control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can imbue your Aura of Protection with primal power, granting the following benefits for 1 minute or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Diminish Defiance. Enemies in the aura have Disadvantage on saving throws against your spells and Channel Divinity options.\n"
            "Regeneration. At the start of each of your turns, you regain 10 Hit Points.\n"
            "Swift Spells. Whenever you cast a spell that has a casting time of an action, you can cast it using a Bonus Action instead."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action"),
            ("Duration", "1 minute (or until ended)"),
            ("Recharge", "Once per Long Rest (or spend level 5 spell slot)"),
            ("Diminish Defiance", "Enemies in aura have Disadvantage on saves against your spells and Channel Divinity"),
            ("Regeneration", "Regain 10 HP at start of each turn"),
            ("Swift Spells", "Cast spells with action casting time as Bonus Action instead"),
        ]
