from Definitions import Ability, CreatureSize
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.SMALL  # Given by your species


class Darkvision(TextFeature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Gnome Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class GnomishCunning(CharacterFeature):
    def modify(self, character_stat_block: CharacterStatBlock) -> None:
        character_stat_block.add_advantage_in_saving_throw(Ability.INTELLIGENCE)
        character_stat_block.add_advantage_in_saving_throw(Ability.WISDOM)
        character_stat_block.add_advantage_in_saving_throw(Ability.CHARISMA)


class ForestGnomeSpeakWithAnimals(TextFeature):
    def __init__(self):
        super().__init__(
            name="Forest Gnome Speak with Animals",
            origin="Gnomish Lineage Forest Gnome Trait",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You also always have the Speak with Animals spell prepared. You can cast it without a spell slot a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest. You can also use any spell slots you have to cast the spell."


class RockGnomePrestidigitation(TextFeature):
    def __init__(self):
        super().__init__(
            name="Rock Gnome Prestidigitation",
            origin="Gnomish Lineage Rock Gnome Trait",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Prestidigitation to create a Tiny clockwork device (AC 5,1 HP), such as a toy, fire starter, or music box. When you create the device, you determine its function by choosing one effect from Prestidigitation; the device produces that effect whenever you or another creature takes a Bonus Action to activate it with a touch. If the chosen effect has options within it, you choose one of those options for the device when you create it. For example, if you choose the spell's ignite-extinguish effect, you determine whether the device ignites or extinguishes fire; the device doesn't do both. You can have three such devices in existence at a time, and each falls apart 8 hours after its creation or when you dismantle it with a touch as a Utilize action."
