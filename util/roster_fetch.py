import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


def get(url) -> BeautifulSoup:
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def get_players(url):
    soup: BeautifulSoup = get(url)
    hostname = urlparse(url).netloc
    players = soup.find_all("li", {"class": "sidearm-roster-player"})
    for p in players:
        ident = p.find("div", {"class": "sidearm-roster-player-name"})
        name = ident.find("a").text.strip()
        num = ident.find("span", {"class": "sidearm-roster-player-jersey-number"}).text.strip()
        pos = p.find("span", {"class": "sidearm-roster-player-position-long-short"})
        if pos is None:
            pos = p.find("div", {"class": "sidearm-roster-player-position"}).find("span", {"class": "text-bold"})
        pos = pos.text.strip()
        img = p.find("img")["data-src"]
        img_url = urljoin(f"https://{hostname}", urlparse(img).path)
        print(name, num, pos, img_url)


get_players("https://drexeldragons.com/sports/womens-soccer/roster")