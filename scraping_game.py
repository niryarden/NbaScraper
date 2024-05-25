import json
import urllib.request
from bs4 import BeautifulSoup


REQ_RETRIES = 3


def get_response(game_id):
    print(f"fetching {game_id=}")
    url = f"https://www.nba.com/game/{game_id}"
    for i in range(REQ_RETRIES):
        try:
            response = urllib.request.urlopen(url).read()
            print("Success")
            return response, True
        except Exception as e:
            print(f"caught error {e}, retrying...")

    print(f"failed fetching {game_id=}, moving on...")
    with open("data/unsuccessful_game_ids.txt", 'a') as f:
        f.write(game_id)
    return None, False


def convert_clock(raw):
    raw = raw.replace('PT', '')
    raw = raw.replace('M', ':')
    raw = raw.replace('S', '')
    return raw


def parse_play_by_play(actions):
    play_by_play = []
    score = "0:0"
    for action in actions:
        period = action["period"]
        clock = convert_clock(action["clock"])
        event = action["description"]
        if action["scoreHome"]:
            score = f"{action['scoreHome']}:{action['scoreAway']}"
        play_as_text = f"Period: {period}, Clock: {clock}, Score: {score}, Event: {event}"
        play_by_play.append(play_as_text)
    return "\n".join(play_by_play)


def parse_recap(recap_as_list):
    recap = "\n".join(recap_as_list)
    if " (AP) " in recap:
        _, _, recap = recap.partition(" (AP) ")
    if "\n--\n" in recap:
        recap, _, _ = recap.partition("\n--\n")
    if "\n---\n" in recap:
        recap, _, _ = recap.partition("\n---\n")
    if "\nUP NEXT\n" in recap:
        recap, _, _ = recap.partition("\nUP NEXT\n")
    recap = recap.strip()
    recap = recap.replace("  ", " ")
    return recap


def parse_metadata(data):
    metadata = {}
    home_team = data["props"]["pageProps"]["game"]["homeTeam"]
    metadata["homeTeam"] = f"{home_team['teamCity']} {home_team['teamName']}"
    away_team = data["props"]["pageProps"]["game"]["awayTeam"]
    metadata["awayTeam"] = f"{away_team['teamCity']} {away_team['teamName']}"
    metadata["time"] = data["props"]["pageProps"]["game"]["gameEt"]
    return metadata


def scrape_game(game_id):
    response, is_success = get_response(game_id)
    if not is_success:
        return
    soup = BeautifulSoup(response, "html.parser")
    data = json.loads(soup.find('script', type='application/json', id="__NEXT_DATA__").text)
    recap_as_list = data["props"]["pageProps"]["story"]["content"]
    recap = parse_recap(recap_as_list)
    actions = data["props"]["pageProps"]["playByPlay"]["actions"]
    play_by_play = parse_play_by_play(actions)
    metadata = parse_metadata(data)
    game = {
        "metadata": metadata,
        "input": play_by_play,
        "output": recap
    }
    with open(f"data/dataset/supervised.jsonl", "a") as f:
        f.write(json.dumps(game) + "\n")


def main():
    for year in range(2019, 2024):
        with open(f"data/game_ids/{year}.txt") as f:
            for game_id in f.read().splitlines():
                scrape_game(game_id)


if __name__ == '__main__':
    main()
