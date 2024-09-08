import json
import urllib.request
from bs4 import BeautifulSoup
import threading
import os


REQ_RETRIES = 5


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_response(game_id, year):
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
    with open(f"data/dataset/{year}/unsuccessful_game_ids.txt", 'a') as f:
        f.write(game_id + "\n")
        f.flush()
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
            if int(action["scoreHome"]) or int(action["scoreAway"]):
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


def scrape_game(game_id, year, get_recaps):
    response, is_success = get_response(game_id, year)
    if not is_success:
        return
    soup = BeautifulSoup(response, "html.parser")
    data = json.loads(soup.find('script', type='application/json', id="__NEXT_DATA__").text)
    page_props = data["props"]["pageProps"]
    actions = page_props["playByPlay"]["actions"]
    home_team_players = page_props["game"]["homeTeamPlayers"]
    home_team_player_names = ",".join([player['name'] for player in home_team_players])
    home_team_names_I = ",".join([player['nameI'] for player in home_team_players])

    away_team_players = page_props["game"]["awayTeamPlayers"]
    away_team_player_names = ",".join([player['name'] for player in away_team_players])
    away_team_names_I = ",".join([player['nameI'] for player in away_team_players])

    play_by_play = parse_play_by_play(actions)
    metadata = parse_metadata(data)
    game = {
        "game_id": game_id,
        "metadata": metadata,
        "input": play_by_play,
        "home_team_player_names": home_team_player_names,
        "home_team_names_I": home_team_names_I,
        "away_team_player_names": away_team_player_names,
        "away_team_names_I": away_team_names_I
    }
    if get_recaps:
        if story := page_props["story"]:
            recap_as_list = story["content"]
            recap = parse_recap(recap_as_list)
            game["output"] = recap

    with open(f"data/dataset/{year}/{year}_samples.jsonl", "a") as f:
        f.write(json.dumps(game) + "\n")
        f.flush()


def scrape_unsuccessful_games(year, get_recaps):
    with open(f"data/dataset/{year}/unsuccessful_game_ids.txt", 'r') as f:
        game_ids = f.read().splitlines()
    with open(f"data/dataset/{year}/unsuccessful_game_ids.txt", 'w') as f:
        pass
    for game_id in game_ids:
        scrape_game(game_id, year, get_recaps)


def scrape_year(year, get_recaps):
    create_dir(f"data/dataset/{year}")
    with open(f"data/game_ids/{year}.txt") as f:
        game_ids = f.read().splitlines()
    for game_id in game_ids:
        scrape_game(game_id, year, get_recaps)

    if os.path.isfile(f"data/dataset/{year}/unsuccessful_game_ids.txt"):
        should_stop = False
        while not should_stop:
            scrape_unsuccessful_games(year, get_recaps)
            with open(f"data/dataset/{year}/unsuccessful_game_ids.txt", 'r') as f:
                if len(f.read()) == 0:
                    should_stop = True


def main(year_start, year_end, get_recaps=True):
    threads = []
    for year in range(year_start, year_end):
        thread = threading.Thread(target=scrape_year, args=(year, get_recaps,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main(2019, 2024, True)
    main(1996, 2019, False)
