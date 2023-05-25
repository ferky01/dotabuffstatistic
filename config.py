import requests
from bs4 import BeautifulSoup
from functools import lru_cache

period = ['week', 'month', '3month','6month', 'year' , 'patch_7.33']

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
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
            "Matches_Played" : Matches_Played,
            })
        print(counter_data)
        return counter_data
    else:
        print(f"Ошибка при получении данных: {response.status_code}")
        return []
