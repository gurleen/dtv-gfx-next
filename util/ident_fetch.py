import requests
import wikipedia
from bs4 import BeautifulSoup


CONF_ROOT = "https://teamcolorcodes.com/ncaa-color-codes/"


def get(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def get_selection(items):
    for i, item in enumerate([x[0] for x in items]):
        print(i, item)
    selected = int(input("> "))
    return items[selected][1]


def get_items(url):
    soup = get(url)
    confs = soup.find_all("a", {"class": "team-button"})
    return [(c.text, c["href"]) for c in confs]


def get_ident(url):
    rv = list()
    soup = get(url)
    color = soup.find("div", {"class": "colorblock"})
    hexc = color.decode_contents().split("<br/>")[2]
    name = soup.title.string.split(" Color Codes")[0].split(" Colors")[0]
    wiki = wikipedia.page(name)
    image = wiki.images[-2]
    return (hexc[11:-1], image)


def main():
    conf = get_items(CONF_ROOT)
    teams = get_items(get_selection(conf))
    print(get_ident(get_selection(teams)))


if __name__ == "__main__":
    main()