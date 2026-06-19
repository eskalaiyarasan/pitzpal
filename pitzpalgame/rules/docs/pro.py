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
    # Special Last-Seed Accumulation Override
    rule.append(
        " Accumulation Bonus: If your last seed lands in a pit and brings its total "
        f"to exactly {data[level.strip()]['Early']['Value']} seeds, you are guaranteed to capture at least that one seed. "
        "You instantly claim all the seeds in that pit, regardless of who owns it. "
        "Note: This override is only valid for the final pit where your last seed lands. "
        "Any previous pits passed during the sowing sequence that happen to hit the threshold are not captured via this bonus."
    )
    rule.append(
        " - Dual Capture Rule: This Accumulation Bonus: works in addition to the standard capture process rather than replacing it. "
        "If the immediate next pit is empty and the following pit contains seeds, you perform your standard capture "
        "AND also collect the accumulated seeds from your last-drop pit."
    )
    rule.append(
        " - Restriction: If the pit where your last seed lands does not reach the exact threshold required "
        "for accumulation, you cannot claim its seeds, and only the standard empty-pit capture applies."
    )
    return rule
