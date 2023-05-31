from functools import lru_cache

import json
import os

import requests
from bs4 import BeautifulSoup

period = ['week', 'month', '3month', '6month', 'year', 'patch_7.33']

all_hero_names = [
    "abaddon", "alchemist", "ancient-apparition", "anti-mage", "arc-warden", "axe", "bane", "batrider", "beastmaster",
    "bloodseeker", "bounty-hunter", "brewmaster", "bristleback", "broodmother", "centaur-warrunner",
    "chaos-knight", "chen", "clinkz", "clockwerk", "crystal-maiden", "dark-seer", "dark-willow", "dawnbreaker",
    "dazzle", "death-prophet", "disruptor", "doom", "dragon-knight", "drow-ranger", "earth-spirit", "earthshaker",
    "elder-titan", "ember-spirit", "enchantress", "enigma", "faceless-void", "grimstroke", "gyrocopter", "hoodwink",
    "huskar", "invoker", "io", "jakiro", "juggernaut", "keeper-of-the-light", "kunkka", "legion-commander", "leshrac",
    "lich", "lifestealer", "lina", "lion", "lone-druid", "luna", "lycan", "magnus", "marci", "mars", "medusa", "meepo",
    "mirana", "monkey-king", "morphling", "muerta", "naga-siren", "natures-prophet", "necrophos", "night-stalker",
    "nyx-assassin", "ogre-magi", "omniknight", "oracle", "outworld-destroyer", "pangolier", "phantom-assassin",
    "phantom-lancer", "phoenix", "primal-beast", "puck", "pudge", "pugna", "queen-of-pain", "razor", "riki",
    "rubick", "sand-king", "shadow-demon", "shadow-fiend", "shadow-shaman", "silencer", "skywrath-mage", "slardar",
    "slark", "snapfire", "sniper", "spectre", "spirit-breaker", "storm-spirit", "sven", "techies",
    "templar-assassin", "terrorblade", "tidehunter", "timbersaw", "tinker", "tiny", "treant-protector", "troll-warlord",
    "tusk", "underlord", "undying", "ursa", "vengeful-spirit", "venomancer", "viper", "visage", "void-spirit",
    "warlock", "weaver", "windranger", "winter-wyvern", "witch-doctor", "wraith-king", "zeus"
]


def normalize_hero_name(hero_name):
    return hero_name.lower().replace('-', ' ').replace("'", "").replace(".", "")


@lru_cache(maxsize=None)
def fetch_counters(hero_name, period):
    normalized_hero_name = normalize_hero_name(hero_name).replace(' ', '-')
    url = f"https://www.dotabuff.com/heroes/{normalized_hero_name}/counters?date={period}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.36",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", class_="sortable")

        counter_data = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            hero_name = cells[1].text.strip()
            disadvantage = cells[2].text.strip()
            win_rate = cells[3].text.strip()
            Matches_Played = cells[4].text.strip()

            counter_data.append({
                "hero_name": normalize_hero_name(hero_name),
                "disadvantage": disadvantage,
                "win_rate": win_rate,
                "Matches_Played": Matches_Played,
            })
        print(counter_data)
        return counter_data
    else:
        print(f"Ошибка при получении данных: {response.status_code}")
        return []


def save_economy_data_to_json(period):
    url_economy = f"https://www.dotabuff.com/heroes/economy?date={period}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.36",
    }

    response_economy = requests.get(url_economy, headers=headers)

    if response_economy.status_code == 200:
        soup_economy = BeautifulSoup(response_economy.content, "html.parser")

        # Parse economy data
        table_economy = soup_economy.find("table", class_="sortable")
        economy_data = []
        for row in table_economy.find_all("tr")[1:]:
            cells = row.find_all("td")
            hero_name = cells[1].text.strip()
            gold_per_minute = cells[2].text.strip()
            experience_per_minute = cells[3].text.strip()

            # Add economy data to your economy_data
            economy_data.append({
                "hero_name": normalize_hero_name(hero_name),
                "gold_per_minute": gold_per_minute,
                "experience_per_minute": experience_per_minute,
            })

        # Create directory if it doesn't exist
        if not os.path.exists('data_economy'):
            os.makedirs('data_economy')

        # Save data to json file
        with open(f'data_economy/economy_data_{period}.json', 'w') as f:
            json.dump(economy_data, f)
    else:
        print(f"Ошибка при получении данных: {response_economy.status_code}")


def load_or_fetch_economy_data(period):
    filename = f'data_economy/economy_data_{period}.json'

    # Check if file exists
    if not os.path.isfile(filename):
        # If file doesn't exist, fetch and save data
        save_economy_data_to_json(period)

    # Load data from json file
    with open(filename, 'r') as f:
        economy_data = json.load(f)
    return economy_data
