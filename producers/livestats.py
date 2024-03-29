import json
import asyncio
from pprint import pprint
from loguru import logger
from janus import Queue
from first import first
from typing import Mapping
import socket
from boltons.socketutils import BufferedSocket

# from producers.decorator import producer
# from util.store import store


READ_LIMIT = 2097152


CONN_PARAMS = {
    "type": "parameters",
    "types": "se,ac,mi,te,box,pbp",
    "playbyplayOnConnect": 1,
}

SCORING_PLAYS = ("2pt", "3pt", "freethrow")

HOME, AWAY = -1, -1
store = dict()
plays = list()
computed = dict()
numbers = dict(home={}, away={})    # shirt number => player index
starters = dict(home=[], away=[])


def is_scoring_play(action: Mapping) -> bool:
    return action["actionType"] in SCORING_PLAYS and action["success"] == 1


def is_team(action: Mapping, team: int) -> bool:
    return action.get("teamNumber") == team


def determine_sides(message: Mapping) -> None:
    global HOME, AWAY
    for team in message["teams"]:
        if team["detail"]["isHomeCompetitor"] == 1:
            HOME = team["teamNumber"]
        else:
            AWAY = team["teamNumber"]


def process_teams(message: dict, q: Queue):
    global numbers, starters
    for team in message["teams"]:
        team_starters = []
        side = "home" if team["teamNumber"] == HOME else "away"
        for player in team["players"]:
            print(player)
            numbers[side][player["shirtNumber"]] = player["pno"]
            if player["starter"] == 1:
                team_starters.append(player)
        starters[side] = team_starters
    
    q.sync_q.put({
        "numbers": numbers,
        "starters": starters
    })



def compute_stats(q: Queue):
    computed["last_home_score"] = first(
        reversed(plays), key=lambda x: is_team(x, HOME) and is_scoring_play(x)
    )
    computed["last_away_score"] = first(
        reversed(plays), key=lambda x: is_team(x, AWAY) and is_scoring_play(x)
    )
    q.sync_q.put(computed)


def updated_computed(action: Mapping, q: Queue):
    if is_scoring_play(action):
        side = "home" if action["teamNumber"] == HOME else "away"
        key = f"last_{side}_score"
        computed[key] = action
        q.sync_q.put({key: action})


def process_action(action: Mapping, q: Queue):
    pprint(action)
    if action["actionType"] == "timeout" and action["subType"] == "commercial":
        logger.info("***MEDIA TIMEOUT***")
        q.sync_q.put({"mediaTimeout": True})
    elif action["actionType"] == "clock" and action["subType"] == "start":
        logger.info("MEDIA TIMEOUT OVER.")
        q.sync_q.put({"mediaTimeout": False})


def process_boxscore(box: dict, q: Queue):
    pass


def listen_to_nls_sync(q: Queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # addr = ("10.250.42.142", 7677)
    addr = ("192.168.1.161", 7677)
    sock.connect(addr)
    bufsock = BufferedSocket(sock, maxsize=READ_LIMIT, timeout=None)

    sock.send(json.dumps(CONN_PARAMS).encode())
    while True:
        message = bufsock.recv_until(b"\r\n")
        message_json = json.loads(message.decode("utf-8"))
        message_type = message_json["type"]

        if message_type in ["teams", "boxscore"]:
            store[message_type] = message_json
            if message_type == "teams":
                determine_sides(message_json)
                process_teams(message_json, q)
                q.sync_q.put(message_json)
                q.sync_q.put({"homeKey": HOME})
                q.sync_q.put({"awayKey": AWAY})
                logger.info(f"Home is {HOME} and away is {AWAY}")
            else:
                q.sync_q.put({"boxscore": message_json})
        elif message_type == "playbyplay":
            plays = message_json["actions"]
            compute_stats(q)
        elif message_type == "action":
            plays.append(message_json)
            process_action(message_json, q)
            updated_computed(message_json, q)
        if message_type != "boxscore":
            pprint(message_json)
            pass




async def create_queue() -> Queue:
    q = Queue()
    return q


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    q = loop.run_until_complete(create_queue())
    listen_to_nls_sync(q)
