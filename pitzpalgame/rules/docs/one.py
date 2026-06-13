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

    return rule
