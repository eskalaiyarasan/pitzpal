# Create your views here.
from django.shortcuts import render
from markupsafe import Markup

from .rules.docs import classic, kingz, one


def about_game(request, name, level):
    # You can pass data to the template via a dictionary (context)
    rules = ""
    sno = 1
    if "classic" in name:
        for rule in classic.get_rules(level):
            rules = rules + "<p>" + str(sno) + " " + rule + "</p>\n"
            sno = sno + 1
    if "kingz" in name:
        for rule in kingz.get_rules(level):
            rules = rules + "<p>" + str(sno) + " " + rule + "</p>\n"
            sno = sno + 1
    if "one" in name:
        for rule in one.get_rules(level):
            rules = rules + "<p>" + str(sno) + " " + rule + "</p>\n"
            sno = sno + 1
    html_rules = "".join(rule for rule in rules)
    name1 = str(name)
    name1 = name1.replace("one", "Standard")
    name1 = name1.replace("kingz", "Premium")
    print("name=", name)
    print("name1=", name1)
    content = {
        "page_title": f"About game {name1}",
        "welcome_message": f"Welcome to game : {name1} - {level} ",
        "rules_data": Markup(html_rules),
    }

    return render(request, "docs/about.html", content)
