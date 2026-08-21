from Core.Definitions import BARD_HIT_DIE, Language, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import GrantLanguage, SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class MoonsInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Moon's Inspiration", origin="College of the Moon Bard Level 3", duration="Until Start of Your Next Turn"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The primal and ever-changing power of the moon flows through you, granting you the following benefits.\n"
            "Inspired Eclipse. When you take a Bonus Action to give a creature a Bardic Inspiration die, you can have the Invisible condition and teleport up to 30 feet to an unoccupied space you can see as part of that Bonus Action. This invisibility lasts until the start of your next turn and ends early immediately after you make an attack roll, deal damage, or cast a spell.\n"
            "Lunar Vitality. Once per turn when you restore Hit Points to a creature with a spell, you can expend a Bardic Inspiration die and increase the amount of Hit Points restored by a number equal to a roll of the Bardic Inspiration die. The creature's Speed also increases by 10 feet until the end of its next turn."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Inspired Eclipse", "When giving Bardic Inspiration, gain Invisible condition and teleport up to 30 feet; invisibility ends at start of next turn or after you attack/deal damage/cast spell"),
            ("Lunar Vitality", "Once per turn when restoring HP with a spell, expend Bardic Inspiration die to increase HP restored by that die roll; target gains 10 feet Speed until end of its next turn"),
        ]


class PrimalLore(Feature):
    def __init__(self, skill: Skill):
        super().__init__(name="Primal Lore", origin="College of the Moon Bard Level 3")
        self._skill = skill
        allowed_skills = [
            Skill.ANIMAL_HANDLING,
            Skill.INSIGHT,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.SURVIVAL,
        ]
        self._proficiency_choice = SkillProficiencyChoice(
            [skill],
            allowed_skills,
            count=1,
            error_prefix="Primal Lore",
        )
        self._language = GrantLanguage(Language.DRUIDIC, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._proficiency_choice.apply(character_stat_block)
        self._language.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn Druidic and one cantrip from the Druid spell list. It counts as a Bard spell for you but doesn't count against the number of cantrips you know. Whenever you gain a Bard level, you can replace this cantrip with another cantrip of your choice from the Druid spell list.\n"
            f"Additionally, you have proficiency in {self._skill.value}."
        )
        return description


class BlessingOfMoonlight(Feature):
    def __init__(self):
        super().__init__(
            name="Blessing of Moonlight", origin="College of the Moon Bard Level 6", range="60 Feet"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the Moonbeam spell prepared.\n"
            "When you cast Moonbeam, you can modify the spell so that you glow faintly while the spell is active. While glowing, you shed Dim Light out to 5 feet, and whenever a creature fails its saving throw against the effects of this Moonbeam, another creature of your choice that you can see within 60 feet of yourself regains 2d4 Hit Points.\n"
            "Once you use this feature to modify a casting of Moonbeam, you can't use it again until you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Always Prepared", "Moonbeam"),
            ("Trigger", "Cast Moonbeam"),
            ("Effect", "You glow faintly, shed Dim Light 5 feet; when creature fails save against Moonbeam, another creature within 60 feet regains 2d4 HP"),
            ("Recharge", "Long Rest"),
        ]


class EventidesSplendor(Feature):
    def __init__(self):
        super().__init__(
            name="Eventide's Splendor", origin="College of the Moon Bard Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You become suffused with the might of the moon, improving your Moon's Inspiration in the following ways.\n"
            "Shadow of the New Moon. When you use Inspired Eclipse, the creature who received the Bardic Inspiration die can also have the Invisible condition and immediately take a Reaction to teleport up to 30 feet to an unoccupied space it can see. The creature remains Invisible until the start of its next turn.\n"
            "Vibrance of the Full Moon. When you use Lunar Vitality, you can roll 1d6 and use the number rolled in place of expending a Bardic Inspiration die."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Shadow of the New Moon", "When using Inspired Eclipse, recipient gains Invisible condition and Reaction to teleport up to 30 feet; stays Invisible until start of next turn"),
            ("Vibrance of the Full Moon", "When using Lunar Vitality, roll 1d6 and use in place of expending Bardic Inspiration die"),
        ]
