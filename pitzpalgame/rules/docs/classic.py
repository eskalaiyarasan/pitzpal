import json

from . import pro


def get_rules(level):
    data = {}
    json_file = "pitzpalgame/rules/json/classic.json"
    with open(json_file) as sf:
        data = json.load(sf)
    rule = []
    if level.strip() not in data:
        return rule
    # game setup
    rule.append(f" This is a {data[level.strip()]['Nside']}-player game.")
    rule.append(f" The board consists of {data[level.strip()]['Nside']} rows/sides.")
    rule.append(f" A coin toss is used to determine who chooses their side.")
    rule.append(f" The toss winner gets Side 0 and makes the opening move.")

    # move
    rule.append(
        " Sowing Ends: When you drop your last seed, check the immediate next pit."
    )
    rule.append(
        " - If the next pit contains seeds: Scoop them up and continue sowing in the same direction."
    )
    rule.append(
        " - If the next pit is empty: Your turn ends. You capture all the seeds in the next pit "
        "immediately following that empty pit."
    )
    rule = rule + pro.get_rules(level)
    return rule
