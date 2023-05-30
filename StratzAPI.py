import json
import os

import requests

from ConfigStratzApi import *

graphql_url = stratz_graphql_url  # URL для GraphQL API Stratz
api_key = your_api_key

hero_id = hero_id


def hero_id_to_name(hero_id, hero_id_dict):
    for key, value in hero_id_dict.items():
        if value == hero_id:
            return key
    return None


def fetch_synergy_data(hero_name):
    # Преобразование имени героя к формату, используемому в словаре hero_id
    hero_name = hero_name.replace('-', ' ').title()

    hero_id_value = hero_id.get(hero_name)
    if not hero_id_value:
        print(f"Неизвестный герой: {hero_name}")
        return []

    query = f"""
    {{
      heroStats {{
        heroVsHeroMatchup(heroId: {hero_id_value}) {{
          disadvantage {{
            with {{
              heroId1
              heroId2
              synergy
              matchCount
            }}
          }}
        }}
        laneOutcomeIsWithTruePosition1: laneOutcome(heroId: {hero_id_value}, isWith: true, positionIds: POSITION_1) {{
          heroId1
          heroId2
          week
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithFalsePosition1: laneOutcome(heroId: {hero_id_value}, isWith: false, positionIds: POSITION_1) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithTruePosition2: laneOutcome(heroId: {hero_id_value}, isWith: true, positionIds: POSITION_2) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithFalsePosition2: laneOutcome(heroId: {hero_id_value}, isWith: false, positionIds: POSITION_2) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithTruePosition3: laneOutcome(heroId: {hero_id_value}, isWith: true, positionIds: POSITION_3) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithFalsePosition3: laneOutcome(heroId: {hero_id_value}, isWith: false, positionIds: POSITION_3) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithTruePosition4: laneOutcome(heroId: {hero_id_value}, isWith: true, positionIds: POSITION_4) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithFalsePosition4: laneOutcome(heroId: {hero_id_value}, isWith: false, positionIds: POSITION_4) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithTruePosition5: laneOutcome(heroId: {hero_id_value}, isWith: true, positionIds: POSITION_5) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithTruePosition5: laneOutcome(heroId: {hero_id_value}, isWith: true, positionIds: POSITION_5) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithTruePositionALL: laneOutcome(heroId: {hero_id_value}, isWith: true) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
        laneOutcomeIsWithFalsePositionALL: laneOutcome(heroId: {hero_id_value}, isWith: false) {{
          heroId1
          heroId2
          matchCount
          drawCount
          winCount
          lossCount
          stompWinCount
          stompLossCount
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {"query": query}

    # Создайте путь к файлу в папке data
    file_path = os.path.join("data", f"{hero_name}.json")

    if not os.path.exists(file_path):
        response = requests.post(graphql_url, headers=headers, json=data)
        result = response.json()
        hero_stats_data = result['data']['heroStats']

        # Если файл не существует, сохраните данные в новом файле JSON
        with open(file_path, 'w') as f:
            json.dump(hero_stats_data, f, ensure_ascii=False, indent=4)
    else:
        print(f"Файл {file_path} уже существует, пропускаем запрос к API")

    # Открываем файл для чтения
    with open(f'data/{hero_name}.json', 'r') as f:
        # Загружаем JSON-данные из файла
        data = json.load(f)

    return data
