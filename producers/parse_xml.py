import xmltodict
from pprint import pprint
from collections import namedtuple
from datetime import timedelta
import xml.etree.ElementTree as ET

from pytimeparse import parse as tparse


Play = namedtuple(
    "Play",
    (
        "number",
        "actionId",
        "sequence",
        "vh",
        "team",
        "clock",
        "action",
        "text",
        "vscore",
        "hscore",
    ),
    defaults=[None] * 10,
)

def next_with(iterator, key, value):
    for i, x in enumerate(iterator):
        if getattr(x, key) == value:
            return x, iterator[i + 1 :]
    return None, []


def parse_old(raw_xml: str):
    if not raw_xml:
        return []
    xml = xmltodict.parse(raw_xml, attr_prefix="")

    raw_plays = xml["sogame"]["plays"]["period"]["play"]
    plays = [Play(**x) for x in raw_plays]
    plays.reverse()
    return plays

    last_goal, rest = next_with(plays, "action", "GOAL")
    prev_goal, rest = next_with(rest, "action", "GOAL")

    last_goal_time, prev_goal_time = tparse(last_goal.clock), tparse(prev_goal.clock)
    delta = last_goal_time - prev_goal_time
    print(str(timedelta(seconds=delta)))

    return plays

def parse(raw_xml: str):
    root = ET.fromstring(raw_xml)
    officals = [x.attrib["text"].replace(", ", ",").split(",") for x in root.iter("officials")]
    plays = [x.attrib for x in root.iter("play")]
    box = {}
    teams = {}
    for team in root.iter("team"):
        team_side = team.attrib["vh"]
        teams[team_side] = [
            {**x.attrib, **x.find("stats").attrib} for x in team.iter("player")
        ]
        box[team_side] = team.find("totals").find("stats").attrib
    return {"officials": officals, "plays": plays, "teams": teams, "box": box}
