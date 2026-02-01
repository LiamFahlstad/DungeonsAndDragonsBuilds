class Sentinel(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 4:
            raise ValueError("Sentinel requires character level 4 or higher.")
        super().__init__(
            name="Sentinel",
            origin="General Feat Level 4+",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+\n"
            "\n"
            "You gain the following benefits.\n"
            "\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "\n"
            "Concentration Breaker. When you damage a creature that is concentrating, it has Disadvantage on the saving throw it makes to maintain Concentration.\n"
            "\n"
            "Guarded Mind. If you fail an Intelligence, a Wisdom, or a Charisma saving throw, you can cause yourself to succeed instead. Once you use this benefit, you can't use it again until you finish a Short or Long Rest.\n"
        )
                return text
