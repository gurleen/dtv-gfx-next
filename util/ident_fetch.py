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
    try:
        soup = get(url)
    except requests.exceptions.MissingSchema:
        soup = get(CONF_ROOT + url.lstrip("/"))
    color = soup.find("div", {"class": "colorblock"})
    hexc = color.decode_contents().split("<br/>")[2]
    name = soup.title.string.split(" Color Codes")[0].split(" Colors")[0]
    wiki = wikipedia.page(name)
    image = [x for x in wiki.images if "icon_edit" not in x and "logo" in x][-1]
    return (hexc[11:-1].lstrip(), image, name)


def main():
    conf = get_items(CONF_ROOT)
    teams = get_items(get_selection(conf))
    print(get_ident(get_selection(teams)))


if __name__ == "__main__":
    main()
