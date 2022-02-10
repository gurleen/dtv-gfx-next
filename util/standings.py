import os
import time
from typing import Literal
import requests
import PySimpleGUI as sg
from pprint import pprint
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


STANDINGS_CODES = {
    "Men's Basketball": 176,
    "Women's Basketball": 177
}

BASE_URL = "https://caasports.com/standings.aspx?standings={key}&print=true"

FILENAMES = {
    "Charleston": "COFC",
    "James Madison": "JMU",
    "Northeastern": "NEastern",
    "Delaware": "UDel",
    "William & Mary": "WilliamAndMary"
}

SCORES_URL = "https://stats.statbroadcast.com/interface/scoreboard/page/?&confid=caa&schoolList=%27elon%27,%27tows%27,%27ncwi%27,%27ne%27,%27wima%27,%27dela%27,%27hofs%27,%27chac%27,%27drex%27,%27jame%27&sportfilter=bbgame;{sport}&_={ts}"


def write_standings_to_file(standings: list):
    path = os.path.join("/", "Users", "gurleen", "standings.txt")
    with open(path, "w+") as out:
        for idx, team in enumerate(standings):
            out.write(f"CAATeam{idx}Name = {team[0]}\n")
            out.write(f"CAATeam{idx}Conf = {team[1]}\n")
            out.write(f"CAATeam{idx}Record = {team[2]}\n")
            if team[0] in FILENAMES:
                out.write(f"CAATeam{idx}Img = {FILENAMES[team[0]]}.png\n")
            else:
                out.write(f"CAATeam{idx}Img = {team[0]}.png\n")


def get_standings(code: int):
    standings = []

    ua = UserAgent()
    url = BASE_URL.format(key=code)
    req = requests.get(url, headers={"User-Agent": ua.chrome})
    soup = BeautifulSoup(req.text, "html.parser")
    
    rows = soup.find_all("tr")
    for r in rows[1:]:
        name = r.find_next("td").contents[0].string
        cells = r.find_all("td")[2:]
        standings.append((name, cells[0].string, cells[2].string))

    pprint(standings)
    write_standings_to_file(standings)


def write_scores_to_file(games: list):
    path = os.path.join("/", "Users", "gurleen", "scores.txt")
    with open(path, "w+") as out:
        for idx, game in enumerate(games):
            out.write(f"OOTGame{idx}HomeName = {game['homename']}\n")
            out.write(f"OOTGame{idx}AwayName = {game['visname']}\n")
            out.write(f"OOTGame{idx}HomeScore = {game['homescore']}\n")
            out.write(f"OOTGame{idx}AwayScore = {game['visname']}\n")
            out.write(f"OOTGame{idx}HomeName = {game['homename']}\n")
            if game['homename'] in FILENAMES:
                out.write(f"OOTGame{idx}HomeImg = {FILENAMES[game['homename']]}.png\n")
            else:
                out.write(f"OOTGame{idx}HomeImg = {game['homename']}.png\n")
            if game['visname'] in FILENAMES:
                out.write(f"OOTGame{idx}AwayImg = {FILENAMES[game['visname']]}.png\n")
            else:
                out.write(f"OOTGame{idx}AwayImg = {game['visname']}.png\n")
            out.write(f"OOTGame{idx}Status = {game['status']}\n")


def get_scores(sport: Literal["M", "W"]):
    ua = UserAgent()
    url = SCORES_URL.format(sport=sport, ts=int(time.time()))
    req = requests.get(url, headers={"User-Agent": ua.chrome})
    data = req.json()
    data = [game for game in data["games"] if game["gamestatus"] in ["INPROGRESS", "COMPLETE"]]
    
    pprint(data)
    write_scores_to_file(data)



def main():
    layout = [
        [sg.Combo(list(STANDINGS_CODES.keys()), enable_events=True, key="sport")],
        [sg.Button("Get Standings")],
        [sg.Button("Get Scores")]
    ]

    window = sg.Window("CAA Standings", layout)

    while True:
        event, values = window.read()
        if event == "Get Standings":
            print(values["sport"])
            key = STANDINGS_CODES.get(values["sport"])
            get_standings(key)
        elif event == "Get Scores":
            sport = "M" if values["sport"] == "Men's Basketball" else "W"
            get_scores(sport)
        elif event == sg.WINDOW_CLOSED:
            window.close()
            quit()

if __name__ == "__main__":
    main()