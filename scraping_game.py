import json
import os
import urllib.request
from bs4 import BeautifulSoup


def convert_clock(raw):
    raw = raw.replace('PT', '')
    raw = raw.replace('M', ':')
    raw = raw.replace('S', '')
    return raw


def create_dir(game_id):
    if not os.path.exists(f"data/{game_id}"):
        os.makedirs(f"data/{game_id}")


def parse_play_by_play(actions):
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
    return play_by_play


def parse_recap(recap_as_list):
    recap = "\n".join(recap_as_list)
    if " (AP) " in recap:
        _, _, recap = recap.partition(" (AP) ")
    if "\n--\n" in recap:
        recap, _, _ = recap.partition("\n--\n")
    if "\n---\n" in recap:
        recap, _, _ = recap.partition("\n---\n")
    recap = recap.strip()
    recap = recap.replace("  ", " ")
    return recap


def scrape_game(game_id):
    url = f"https://www.nba.com/game/{game_id}"
    response = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(response, "html.parser")
    data = json.loads(soup.find('script', type='application/json', id="__NEXT_DATA__").text)
    recap_as_list = data["props"]["pageProps"]["story"]["content"]
    recap = parse_recap(recap_as_list)
    actions = data["props"]["pageProps"]["playByPlay"]["actions"]
    play_by_play = parse_play_by_play(actions)
    with open(f'data/{game_id}/recap.txt', 'w+') as f:
        f.write(recap)
    with open(f'data/{game_id}/play_by_play.json', 'w+') as f:
        json.dump(play_by_play, f)


def main(game_id):
    create_dir(game_id)
    scrape_game(game_id)


if __name__ == '__main__':
    main("mia-vs-bos-0042300105")
