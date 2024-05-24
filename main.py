from game_urls_scraper import scrape_games_ids_by_year
import os


def create_year_dir(year):
    if not os.path.exists(f"data/{year}"):
        os.makedirs(f"data/{year}")


def write_game_ids(game_ids, year):
    create_year_dir(year)
    with open(f'data/year/game_urls.txt', 'w+') as f:
        f.write("\n".join(game_ids))


def main():
    for year in range(2019, 2024):
        game_ids = scrape_games_ids_by_year(year)
        write_game_ids(game_ids, year)


if __name__ == '__main__':
    main()
