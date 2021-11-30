import sys
import json
import asyncio
from loguru import logger
from first import first
from pprint import pprint


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


def is_scoring_play(action):
    return action["actionType"] in SCORING_PLAYS and action["success"] == 1


def is_team(action, team):
    return action.get("teamNumber") == team


def determine_sides(message):
    global HOME, AWAY
    for team in message["teams"]:
        if team["detail"]["isHomeCompetitor"] == 1:
            HOME = team["teamNumber"]
        else:
            AWAY = team["teamNumber"]


async def compute_stats():
    computed["last_home_score"] = first(
        reversed(plays), key=lambda x: is_team(x, HOME) and is_scoring_play(x)
    )
    computed["last_away_score"] = first(
        reversed(plays), key=lambda x: is_team(x, AWAY) and is_scoring_play(x)
    )


async def updated_computed(action):
    if is_scoring_play(action):
        side = "home" if action["teamNumber"] == HOME else "away"
        computed[f"last_{side}_score"] = action


async def listen_to_nls(q):
    global plays
    loop = asyncio.get_event_loop()
    reader, writer = await asyncio.open_connection("localhost", 7677)

    writer.write(json.dumps(CONN_PARAMS).encode())
    await writer.drain()

    while True:
        message = await reader.readuntil(b"\r\n")
        message_json = json.loads(message.decode("utf-8"))
        message_type = message_json["type"]

        if message_type in ["teams", "boxscore"]:
            store[message_type] = message_json
            if message_type == "teams":
                determine_sides(message_json)
                await q.put(message_json)
                logger.info(f"Home is {HOME} and away is {AWAY}")
        elif message_type == "playbyplay":
            plays = message_json["actions"]
            await compute_stats()
            pprint(computed)
        elif message_type == "action":
            plays.append(message_json)
            await updated_computed(message_json)
            pprint(plays[-1])

        if message_type != "ping":
            logger.debug(f"Recieved a {message_type} message.")


if __name__ == "__main__":
    asyncio.run(listen_to_nls())
