from tkinter import *
from tkinter import ttk

from ConfigStratzApi import hero_id
from StratzAPI import fetch_synergy_data
from config import all_hero_names, fetch_counters, period, normalize_hero_name, load_or_fetch_economy_data

hero_names = all_hero_names
period = period


def on_period_change(selected_period):
    global period
    period = selected_period
    # print(f"Выбранный период: {selected_period}")


def calculate_average_values(heroes_list):
    all_counters = []
    for hero in heroes_list:
        hero_counters = fetch_counters(hero, period)
        all_counters.extend(hero_counters)

    sums = {}
    for counter in all_counters:
        hero_name = counter["hero_name"]
        disadvantage = float(counter["disadvantage"].strip('%'))
        win_rate = float(counter["win_rate"].strip('%'))
        matches_played = int(counter["Matches_Played"].replace(',', ''))

        if hero_name in sums:
            sums[hero_name]['disadvantage'] += disadvantage
            sums[hero_name]['win_rate'] += win_rate
            sums[hero_name]['matches_played'] += matches_played
        else:
            sums[hero_name] = {
                'disadvantage': disadvantage,
                'win_rate': win_rate,
                'matches_played': matches_played
            }

    averages = {}
    for hero, values in sums.items():
        averages[hero] = {
            'disadvantage': values['disadvantage'],
            'win_rate': values['win_rate'] / len(heroes_list),
            'matches_played': values['matches_played']
        }

    sorted_averages = sorted(averages.items(), key=lambda x: x[1]['disadvantage'], reverse=True)
    sorted_averages = [(hero, values) for hero, values in sorted_averages if
                       hero.lower().replace(' ', '-') not in heroes_list]

    return sorted_averages


def on_entry_hero_changed(event, hero_entry, autocomplete_listbox):
    typed_text = hero_entry.get().strip().lower()
    if typed_text:
        matching_heroes = [hero.replace('-', ' ').title() for hero in hero_names if
                           hero.replace('-', ' ').title().lower().startswith(typed_text)]

        autocomplete_listbox.delete(0, 'end')
        for hero in matching_heroes:
            autocomplete_listbox.insert('end', hero)

        # Определите, должен ли выпадающий список отображаться вверх или вниз от поля ввода
        if hero_entry.winfo_y() > root.winfo_height() // 2:
            y_position = hero_entry.winfo_y() - autocomplete_listbox.winfo_height()
        else:
            y_position = hero_entry.winfo_y() + hero_entry.winfo_height()

        autocomplete_listbox.place(x=hero_entry.winfo_x(), y=y_position, width=hero_entry.winfo_width(), height=100)
        autocomplete_listbox.lift()
    else:
        autocomplete_listbox.place_forget()


def on_autocomplete_listbox_select(event, hero_entry, autocomplete_listbox):
    selected_hero = autocomplete_listbox.get('active')
    hero_entry.delete(0, 'end')
    hero_entry.insert(0, selected_hero)
    autocomplete_listbox.place_forget()


def create_hero_entry_row(row, column):
    hero_entry = Entry(root)
    hero_entry.grid(row=row, column=column, padx=10, pady=10)

    autocomplete_listbox = Listbox(root)
    autocomplete_listbox.bind('<<ListboxSelect>>',
                              lambda event: on_autocomplete_listbox_select(event, hero_entry, autocomplete_listbox))

    hero_entry.bind('<KeyRelease>', lambda event: on_entry_hero_changed(event, hero_entry, autocomplete_listbox))

    return hero_entry


def sort(tree, col, reverse):
    l = [(float(tree.set(k, col).replace('%', '')) if col != 'Hero' else tree.set(k, col), k) for k in
         tree.get_children("")]
    l.sort(reverse=reverse)

    for index, (_, k) in enumerate(l):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort(tree, col, not reverse))


def show_counters(hero_entries):
    input_heroes = [entry.get().lower().replace(' ', '-') for entry in hero_entries if entry.get().strip()]

    sorted_average_values = calculate_average_values(input_heroes)

    # Создание таблицы
    table = ttk.Treeview(root, columns=('Hero', 'Disadvantage', 'Win Rate', 'Matches Played'), show='headings')
    table.heading('Hero', text='Hero', command=lambda: sort(table, 'Hero', False))
    table.heading('Disadvantage', text='Disadvantage', command=lambda: sort(table, 'Disadvantage', False))
    table.heading('Win Rate', text='Win Rate', command=lambda: sort(table, 'Win Rate', False))
    table.heading('Matches Played', text='Matches Played', command=lambda: sort(table, 'Matches Played', False))

    for hero_name, values in sorted_average_values:
        table.insert('', 'end', values=(
            hero_name.replace('-', ' ').title(), f"{values['disadvantage']:.2f}%", f"{values['win_rate']:.2f}%",
            values['matches_played']))

    table.grid(row=3, column=0, columnspan=5)


def create_synergy_table(team_heroes):
    synergy_table = []

    for i in range(len(team_heroes)):
        hero1 = team_heroes[i]
        hero1_synergy_data = fetch_synergy_data(hero1)
        hero1_name = normalize_hero_name(hero1)

        total_synergy = 0
        count = 0

        for j in range(len(team_heroes)):
            if i != j:
                hero2 = team_heroes[j]
                hero2_name = normalize_hero_name(hero2)
                hero2_id = hero_id[hero2]

                for disadvantage_info in hero1_synergy_data['heroVsHeroMatchup']['disadvantage']:
                    for synergy_info in disadvantage_info['with']:
                        if synergy_info['heroId2'] == hero2_id:
                            hero1_synergy = float(synergy_info['synergy'])
                            total_synergy += hero1_synergy
                            count += 1
                            break

        average_synergy = round(total_synergy, 2) if count > 0 else 0
        synergy_table.append([hero1_name, average_synergy])

    # Считаем общую синергию
    total_synergy = sum([row[1] for row in synergy_table])
    synergy_table.append(["Total synergy", total_synergy])

    return synergy_table


def show_synergy_table():
    team1_heroes = [entry.get().replace('-', ' ') for entry in team1_hero_entries if entry.get().strip()]
    team2_heroes = [entry.get().replace('-', ' ') for entry in team2_hero_entries if entry.get().strip()]

    synergy_table_team1 = create_synergy_table(team1_heroes)
    synergy_table_team2 = create_synergy_table(team2_heroes)

    # Создание таблицы для команды 1
    table1 = ttk.Treeview(root, columns=('Hero', 'Average Synergy'), show='headings')
    table1.heading('Hero', text='Hero')
    table1.heading('Average Synergy', text='Average Synergy')

    for row in synergy_table_team1:
        table1.insert('', 'end', values=row)

    # Создание таблицы для команды 2
    table2 = ttk.Treeview(root, columns=('Hero', 'Average Synergy'), show='headings')
    table2.heading('Hero', text='Hero')
    table2.heading('Average Synergy', text='Average Synergy')

    for row in synergy_table_team2:
        table2.insert('', 'end', values=row)

    # Отображение таблиц
    table1.grid(row=7, column=0, padx=10, pady=10)  # Измените номера строк и столбцов
    # в соответствии с вашим макетом
    table2.grid(row=7, column=4, padx=10, pady=10)  # Измените номера строк и столбцов в соответствии с вашим макетом


def create_comparison_table(team1_heroes, team2_heroes):
    comparison_table = []

    for hero1 in team1_heroes:
        hero_row = [hero1.replace('-', ' ').title()]  # Add hero1 name as the first cell in the row
        row_sum = 0  # Initialize the sum for the row
        for hero2 in team2_heroes:
            hero1_counters = fetch_counters(hero1, period)
            hero2_counters = fetch_counters(hero2, period)

            hero1_name = normalize_hero_name(hero1)
            hero2_name = normalize_hero_name(hero2)

            hero1_disadvantage = next((float(counter['disadvantage'].strip('%')) for counter in hero1_counters if
                                       normalize_hero_name(counter['hero_name']) == hero2_name), 0)
            hero2_disadvantage = next((float(counter['disadvantage'].strip('%')) for counter in hero2_counters if
                                       normalize_hero_name(counter['hero_name']) == hero1_name), 0)

            comparison_value = round(((hero1_disadvantage - hero2_disadvantage) / 2), 2)
            row_sum += comparison_value  # Add comparison value to the row sum
            hero_row.append(comparison_value)  # Add comparison value to the row

        hero_row.append(round(row_sum, 2))  # Add the rounded row sum to the end of the row
        comparison_table.append(hero_row)

    return comparison_table


def show_comparison_table():
    team1_heroes = [entry.get().lower().replace(' ', '-') for entry in team1_hero_entries if entry.get().strip()]
    team2_heroes = [entry.get().lower().replace(' ', '-') for entry in team2_hero_entries if entry.get().strip()]

    comparison_table = create_comparison_table(team1_heroes, team2_heroes)

    # Create a Treeview widget with an extra column for "Team 1" and "Total Team 1"
    tree = ttk.Treeview(root, columns=["Team 1"] + team2_heroes + ["Total Team 1"], show="headings")

    # Set column headers and center the column values
    tree.heading("Team 1", text="Team 1")
    for hero in team2_heroes:
        tree.heading(hero, text=hero.replace('-', ' ').title())
        tree.column(hero, anchor="center")
    tree.heading("Total Team 1", text="Total team 1")
    tree.column("Total Team 1", anchor="center")

    # Insert rows into the Treeview and calculate the sum of the "Total Team 1" column
    total_sum = 0
    for row in comparison_table:
        total_sum += row[-1]  # Add the last element of the row (the row sum) to the total sum
        tree.insert("", END, values=row)

    # Calculate the sum for each column corresponding to a hero from team 2 and round it to two decimal places
    column_sums = [round(sum(row[i] for row in comparison_table), 2) for i in range(1, len(team2_heroes) + 1)]

    # Insert the rounded total sum as the last entry in the "Total Team 1" column and the rounded column sums for
    total_row = ["Total team 2"] + [str(column_sum) for column_sum in column_sums] + [str(round(total_sum, 2))]
    tree.insert("", END, values=total_row)

    # Use grid to add the Treeview to the parent widget
    tree.grid(row=3, column=0, columnspan=5, sticky='nsew')


def calculate_team_economy(team_hero_entries, period, team_number):
    economy_data = load_or_fetch_economy_data(period)

    team_heroes = [entry.get().lower() for entry in team_hero_entries if entry.get().strip()]

    total_gold_per_minute = 0
    total_experience_per_minute = 0
    for hero in team_heroes:
        for data in economy_data:
            if data['hero_name'] == hero:
                total_gold_per_minute += float(data['gold_per_minute'])
                total_experience_per_minute += float(data['experience_per_minute'])
                break

    # Calculate average
    average_gold_per_minute = total_gold_per_minute / len(team_heroes)
    average_experience_per_minute = total_experience_per_minute / len(team_heroes)

    # Display the results in a table
    display_results(average_gold_per_minute, average_experience_per_minute, team_number)


table = None


def display_results(avg_gpm, avg_xpm, team_number):
    global table

    # Если таблица еще не создана, создайте ее и добавьте строки
    if table is None:
        table = ttk.Treeview(root, columns=('Team', 'Avg GPM', 'Avg XPM'), show='headings', height=3)
        table.heading('Team', text='Team')
        table.heading('Avg GPM', text='Avg GPM')
        table.heading('Avg XPM', text='Avg XPM')

        table.insert('', 'end', values=('Team 1', 0, 0))
        table.insert('', 'end', values=('Team 2', 0, 0))

        table.grid(row=4, column=0, padx=10, pady=10, columnspan=5)

    # Обновление результатов в таблице
    if team_number == 1:
        table.set(table.get_children()[0], 'Avg GPM', avg_gpm)
        table.set(table.get_children()[0], 'Avg XPM', avg_xpm)
    else:
        table.set(table.get_children()[1], 'Avg GPM', avg_gpm)
        table.set(table.get_children()[1], 'Avg XPM', avg_xpm)


def calculate_matchup(team1, team2):
    matchup_table = []
    position_data_map = {
        0: 'laneOutcomeIsWithFalsePosition1',
        1: 'laneOutcomeIsWithFalsePosition2',
        2: 'laneOutcomeIsWithFalsePosition3',
        3: 'laneOutcomeIsWithFalsePosition4',
        4: 'laneOutcomeIsWithFalsePosition5'
    }

    # Сопоставление позиций героев в командах
    matchup_positions = [
        ([0, 4], [2, 3]),
        ([1], [1]),
        ([2, 3], [0, 4])
    ]

    # Названия дорог
    lanes = ["Bot lane", "Mid lane", "Top lane"]

    for idx, positions_set in enumerate(matchup_positions):
        total_match_count = 0
        total_draw_count = 0
        total_win_count = 0
        total_loss_count = 0
        total_stomp_win_count = 0
        total_stomp_loss_count = 0
        heroes_pairs = [(team1[i], team2[j]) for i in positions_set[0] for j in positions_set[1]]

        team1_heroes = ", ".join(team1[i] for i in positions_set[0])
        team2_heroes = ", ".join(team2[i] for i in positions_set[1])

        lane_msg = "{}: {} vs {}".format(lanes[idx], team1_heroes, team2_heroes)

        for hero1, hero2 in heroes_pairs:
            hero1_data = fetch_synergy_data(hero1)
            hero1_name = normalize_hero_name(hero1)
            hero2_id = hero_id[hero2]

            if position_data_map[team1.index(hero1)] in hero1_data:
                for outcome_info in hero1_data[position_data_map[team1.index(hero1)]]:
                    if outcome_info['heroId2'] == hero2_id:
                        total_match_count += outcome_info['matchCount']
                        total_draw_count += outcome_info['drawCount']
                        total_win_count += outcome_info['winCount']
                        total_loss_count += outcome_info['lossCount']
                        total_stomp_win_count += outcome_info['stompWinCount']
                        total_stomp_loss_count += outcome_info['stompLossCount']

        win_probability = (total_win_count / total_match_count) * 100
        loss_probability = (total_loss_count / total_match_count) * 100
        draw_probability = (total_draw_count / total_match_count) * 100
        stomp_win_probability = (total_stomp_win_count / total_match_count) * 100
        stomp_loss_probability = (total_stomp_loss_count / total_match_count) * 100

        matchup_table.append(
            [lane_msg, total_match_count, win_probability, loss_probability, draw_probability, stomp_win_probability,
             stomp_loss_probability])
    return matchup_table


root = Tk()
root.title("Dota 2 Counter Picker")
root.resizable(width=False, height=False)
s = ttk.Style()
s.theme_use('clam')

hero_label = Label(root, text="Выберите героев команды 1: -")
hero_label.grid(row=0, column=0, padx=10, pady=10)

team1_hero_entries = []
for k in range(5):
    hero_entry = create_hero_entry_row(1, k)
    team1_hero_entries.append(hero_entry)

team2_hero_label = Label(root, text="Выберите героев команды 2: +")
team2_hero_label.grid(row=4, column=0, padx=10, pady=10)

team2_hero_entries = []
for i in range(5):
    hero_entry = create_hero_entry_row(5, i)
    team2_hero_entries.append(hero_entry)


def get_team_from_entries(entries):
    return [entry.get() for entry in entries]


def print_matchup_table(event, team1_entries, team2_entries):
    team1 = get_team_from_entries(team1_entries)
    team2 = get_team_from_entries(team2_entries)
    matchup_table = calculate_matchup(team1, team2)
    for row in matchup_table:
        print(row)


# Добавьте эту строку в вашу функцию setup GUI, после создания всех виджетов ввода.
matchup_button = ttk.Button(root, text="Calculate Matchup")
matchup_button.grid(row=9, column=0, padx=10, pady=10, columnspan=10)
matchup_button.bind('<Button-1>', lambda event: print_matchup_table(event, team1_hero_entries, team2_hero_entries))

calculate_button = ttk.Button(root, text="Показать синергию", command=show_synergy_table)
calculate_button.grid(row=6, column=0, padx=10, pady=10, columnspan=5)

compare_button = ttk.Button(root, text="Сравнить героев", command=show_comparison_table)
compare_button.grid(row=7, column=0, padx=10, pady=10, columnspan=5)

calculate_button = ttk.Button(root, text="calculate_economy")
calculate_button.grid(row=8, column=0, padx=10, pady=10, columnspan=10)
calculate_button.bind('<Button-1>',
                      lambda event: [calculate_team_economy(team_hero_entries, period, team_number)
                                     for team_hero_entries, team_number in
                                     [(team1_hero_entries, 1), (team2_hero_entries, 2)]])

# Изменить номер строки для кнопки "Показать контрпики"
calculate_button = ttk.Button(root, text="Показать контрпики команды 1",
                              command=lambda: show_counters(team1_hero_entries))
calculate_button.grid(row=0, column=0, padx=10, pady=10, columnspan=4)

calculate_button = ttk.Button(root, text="Показать контрпики команды 2",
                              command=lambda: show_counters(team2_hero_entries))
calculate_button.grid(row=0, column=2, padx=10, pady=10, columnspan=5)

period_options = [' ', 'week', 'month', '3month', '6month', 'year', 'patch_7.33']
period_var = StringVar(root)
period_var.set(period_options[0])  # установите значение по умолчанию
period_dropdown = ttk.OptionMenu(root, period_var, *period_options, command=on_period_change)
period_dropdown.grid(row=6, column=0, padx=10, pady=10)

root.mainloop()
