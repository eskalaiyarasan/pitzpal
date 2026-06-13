import json


def get_rules(level):
    data = {}
    json_file = "pitzpalgame/rules/json/pro.json"
    with open(json_file) as sf:
        data = json.load(sf)
    rule = []
    if level.strip() not in data:
        return rule
    # game setup
    # Special Capture Rule (Accumulation)
    rule.append(
        f" Accumulation Rule: If any pit accumulates exactly {data[level.strip()]['Early']['Value']} seeds, "
        f"those seeds are instantly captured and given to the owner of that pit."
    )

    return rule
