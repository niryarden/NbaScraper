import json
import urllib.request
from bs4 import BeautifulSoup


def convert_clock(raw):
    raw = raw.replace('PT', '')
    raw = raw.replace('M', ':')
    raw = raw.replace('S', '')
    return raw


def main():
    URL = "https://www.nba.com/game/mia-vs-bos-0042300105/play-by-play?period=All"
    oururl = urllib.request.urlopen(URL).read()
    soup = BeautifulSoup(oururl, "html.parser")
    data = json.loads(soup.find('script', type='application/json', id="__NEXT_DATA__").text)
    actions = data["props"]["pageProps"]["playByPlay"]["actions"]
    play_by_play = []
    score = "0:0"
    for action in actions:
        play = {
            "period": action["period"],
            "clock": convert_clock(action["clock"]),
            "description": action["description"]
        }
        if action["scoreHome"]:
            score = f"{action['scoreHome']}:{action['scoreAway']}"
        play["score"] = score
        play_by_play.append(play)

    with open('data/game_play_by_play.json', 'w+') as f:
        json.dump(play_by_play, f)


if __name__ == '__main__':
    main()
