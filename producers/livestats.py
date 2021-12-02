import json
import asyncio
from loguru import logger
from janus import Queue
from first import first
from typing import Mapping

from producers.decorator import producer


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


async def compute_stats(q: Queue):
    computed["last_home_score"] = first(
        reversed(plays), key=lambda x: is_team(x, HOME) and is_scoring_play(x)
    )
    computed["last_away_score"] = first(
        reversed(plays), key=lambda x: is_team(x, AWAY) and is_scoring_play(x)
    )
    await q.async_q.put(computed)


async def updated_computed(action: Mapping, q: Queue):
    if is_scoring_play(action):
        side = "home" if action["teamNumber"] == HOME else "away"
        key = f"last_{side}_score"
        computed[key] = action
        await q.async_q.put({key: action})


@producer(debug_only=True)
async def listen_to_nls(q: Queue):
    return
    logger.info("Initializing LiveStats watcher.")
    global plays
    reader, writer = await asyncio.open_connection("192.168.1.161", 7677)
    logger.info("Connected to NCAA LiveStats.")

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
                await q.async_q.put(message_json)
                await q.async_q.put({"homeKey": HOME})
                await q.async_q.put({"awayKey": AWAY})
                logger.info(f"Home is {HOME} and away is {AWAY}")
            else:
                await q.async_q.put({"boxscore": message_json})
        elif message_type == "playbyplay":
            plays = message_json["actions"]
            await compute_stats(q)
        elif message_type == "action":
            plays.append(message_json)
            await updated_computed(message_json, q)


if __name__ == "__main__":
    asyncio.run(listen_to_nls())
