from Definitions import DiceRollCondition, Die
from Utils.CharacterSheetUtils import write_table_with_title


def probability_of_success(
    difficulty_class: int, die: Die, condition: DiceRollCondition, bonus: int
):
    # assuming success if roll >= DC
    if difficulty_class - bonus <= 1:
        return 1.0

    if difficulty_class - bonus > die.value:
        return 0.0

    probability = (die.value + bonus - difficulty_class + 1) / die.value

    if condition == DiceRollCondition.NEUTRAL:
        return probability

    if condition == DiceRollCondition.ADVANTAGE:
        return 1 - (1 - probability) ** 2

    if condition == DiceRollCondition.DISADVANTAGE:
        return probability**2

    raise ValueError("Invalid DiceRollCondition")


def calculate_average_damage(
    armor_class: int,
    attack_roll_die: Die,
    attack_roll_condition: DiceRollCondition,
    attack_roll_bonus: int,
    damage_die: Die,
    number_of_damage_dice: int,
    damage_condition: DiceRollCondition,
    damage_bonus: int,
) -> float:
    p = probability_of_success(
        difficulty_class=armor_class,
        die=attack_roll_die,
        condition=attack_roll_condition,
        bonus=attack_roll_bonus,
    )
    if damage_condition == DiceRollCondition.NEUTRAL:
        average_damage = damage_die.average
    elif damage_condition == DiceRollCondition.ADVANTAGE:
        average_damage = damage_die.average_with_advantage()
    elif damage_condition == DiceRollCondition.DISADVANTAGE:
        average_damage = damage_die.average_with_disadvantage()

    average_damage += damage_bonus
    return p * average_damage * number_of_damage_dice


def damage_report(
    file_name: str,
    attack_roll_die: Die,
    attack_roll_condition: DiceRollCondition,
    attack_roll_bonus: int,
    damage_die: Die,
    number_of_damage_dice: int,
    damage_condition: DiceRollCondition,
    damage_bonus: int,
) -> None:

    with open(file_name, "w") as file:
        headers = [
            "Atk Die",
            "Atk Condition",
            "Atk Bonus",
            "Dmg Die",
            "Dmg Condition",
            "Dmg Bonus",
        ]
        rows = [
            [
                attack_roll_die,
                attack_roll_condition.value,
                attack_roll_bonus,
                damage_die,
                damage_condition.value,
                damage_bonus,
            ]
        ]

        write_table_with_title("Parameters", headers, rows, file)

        file.write("\n")
        headers = []
        row = []

        for ac in range(10, 21):
            avg_damage = calculate_average_damage(
                armor_class=ac,
                attack_roll_die=attack_roll_die,
                attack_roll_condition=attack_roll_condition,
                attack_roll_bonus=attack_roll_bonus,
                damage_die=damage_die,
                number_of_damage_dice=number_of_damage_dice,
                damage_condition=damage_condition,
                damage_bonus=damage_bonus,
            )
            headers.append(f"AC{ac}")
            row.append(f"{avg_damage:.2f}")

        write_table_with_title("Average Damage by AC", headers, [row], file)


if __name__ == "__main__":
    attack_roll_die = Die.D20
    attack_roll_condition = DiceRollCondition.NEUTRAL
    attack_roll_bonus = 5
    damage_die = Die.D10
    number_of_damage_dice = 2
    damage_condition = DiceRollCondition.NEUTRAL
    damage_bonus = 4

    file_name = "damage_report.txt"

    damage_report(
        file_name=file_name,
        attack_roll_die=attack_roll_die,
        attack_roll_condition=attack_roll_condition,
        attack_roll_bonus=attack_roll_bonus,
        damage_die=damage_die,
        number_of_damage_dice=number_of_damage_dice,
        damage_condition=damage_condition,
        damage_bonus=damage_bonus,
    )
