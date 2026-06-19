import json


def get_rules(level):
    data = {}
    json_file = "pitzpalgame/rules/json/one.json"
    with open(json_file) as sf:
        data = json.load(sf)
    rule = []
    if level.strip() not in data:
        return rule
    # game setup
    level = level.strip()
    # Board Setup
    rule.append(
        f" Each side of the board consists of {data[level]['PitsPerSide']} pits."
    )
    rule.append(
        f" Each pit is pre-filled with {data[level]['Nseeds']} seeds at the start of the game."
    )
    # Round Transition Conditions
    rule.append(
        " Round Transition: If it is your turn to move but all of your pits are empty, "
        "the current round ends and the game transitions to the next round, provided you have seeds in your store."
    )

    # Board Reset Logic
    rule.append(
        " Board Reset: During a round transition, all remaining seeds on the board are returned "
        "to their respective owners' stores. Both players then refill their pits using seeds from their stores."
    )

    # Disabled Pits (Rubbish Pits)
    rule.append(
        f" Disabled Pits: If you do not have enough seeds to completely fill a pit (requires {data[level]['Nseeds']} seeds), "
        "that pit becomes disabled for the upcoming round. You can re-enable it in a future round if you accumulate enough seeds."
    )

    # End Game Conditions
    rule.append(
        " Game Over: If, during a round transition, any player does not have enough seeds to fill "
        "at least one single pit, the game ends immediately. The player with the most seeds is declared the winner, "
        "and the player with fewer seeds is the loser."
    )

    return rule
