import json
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

REQ_RETRIES = 3


def parse_game_urls(games):
    game_urls = []
    for game in games:
        card_data = game["cardData"]
        if card_data["seasonType"] != "Playoffs":
            game_urls.append(game["cardData"]["shareUrl"].split("/")[-1])
        else:
            print("Playoffs, stopping")
            return game_urls, True
    return game_urls, False


def scrape_games_by_day(day):
    url = f"https://www.nba.com/games?date={day}"
    response = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(response, "html.parser")
    data = json.loads(soup.find('script', type='application/json', id="__NEXT_DATA__").text)
    games_as_list = data["props"]["pageProps"]["gameCardFeed"]["modules"]
    if not games_as_list:
        print("No games this day - skipping")
        return [], False
    game_cards_list = games_as_list[0]["cards"]
    return parse_game_urls(game_cards_list)


def write_games(game_urls):
    with open(f'data/game_urls.txt', 'w+') as f:
        for game in game_urls:
            f.write(f"{game}\n")


def generate_dates_for_year(year):
    start_date = datetime(year, 10, 1)
    end_date = datetime(year + 1, 6, 1)

    all_days = []

    current_date = start_date
    while current_date < end_date:
        all_days.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    return all_days


def main():
    game_urls = []
    year = 2023  # TODO: change to run on multiple years
    days_of_year = generate_dates_for_year(year)
    should_stop = False

    for day in days_of_year:
        print(f"fetching games for {day=}")
        for i in range(REQ_RETRIES):
            try:
                game_urls_for_day, should_stop = scrape_games_by_day(day)
                game_urls.extend(game_urls_for_day)
                print("Done")
                break
            except Exception as e:
                print(f"caught error {e}, retrying...")

            print(f"failed fetching games for {day=}, moving on...")

        if should_stop:
            break

    write_games(game_urls)


if __name__ == '__main__':
    main()
