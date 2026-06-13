import json


def get_rules(level):
    data = {}
    json_file = "pitzpalgame/rules/json/kingz.json"
    with open(json_file) as sf:
        data = json.load(sf)
    rule = []
    if level.strip() not in data:
        return rule
    # game setup
    level = level.strip()
    # Board Setup
    # King's Pit Rules
    rule.append(
        f" Each side of the board consists of {data[level]['PitsPerSide']} pits."
    )
    rule.append(
        f" Each pit is pre-filled with {data[level]['Nseeds']} seeds at the start of the game. except king's pits"
    )
    rule.append(
        f" King's Pits: There are {data[level]['Kingzpits']['Value']} neutral King's Pits on the board that are not owned by any player."
    )

    rule.append(" - Exemption: The Accumulation Rule does not apply to King's Pits.")

    rule.append(
        " - Sowing Limit: You can sow seeds into a King's Pit, but you cannot scoop seeds out of it. "
        "If your last seed lands in the pit just before a King's Pit, your turn ends immediately without any capture."
    )

    rule.append(
        " - Fractional Capture: Seeds in a King's Pit cannot be captured entirely like normal pits. Instead, "
        "the game tracks how many times each player triggers a capture on it, and the seeds are distributed "
        "proportionally based on those capture counts."
    )

    rule.append(
        " - Round Reset: Captured shares do not carry over to the next round. "
        "Players must successfully trigger a capture in the current round to qualify for a share."
    )

    rule.append(
        " - Rollover: If no player triggers a capture on a King's Pit, its seeds remain in the pit "
        "and roll over to the next round or the end of the game."
    )
    rule.append(
        " - Initial Setup: King's Pits are pre-filled with 0 seeds at the start of the game."
    )
    return rule
