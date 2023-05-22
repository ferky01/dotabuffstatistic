from tkinter import *
from tkinter import ttk

from config import all_hero_names, fetch_counters, period

hero_names = all_hero_names


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


def show_counters_team_1():
    input_heroes = [entry.get().lower().replace(' ', '-') for entry in team1_hero_entries if entry.get().strip()]

    if not input_heroes:
        result_text.delete(1.0, "end")
        result_text.insert("end", "Нет выбранных героев.")
        return

    sorted_average_values = calculate_average_values(input_heroes)

    # Создание таблицы
    table = ttk.Treeview(root, columns=('Hero', 'Disadvantage', 'Win Rate', 'Matches Played'), show='headings')
    table.heading('Hero', text='Hero')
    table.heading('Disadvantage', text='Disadvantage')
    table.heading('Win Rate', text='Win Rate')
    table.heading('Matches Played', text='Matches Played')

    for hero_name, values in sorted_average_values:
        table.insert('', 'end', values=(hero_name.replace('-', ' ').title(), f"{values['disadvantage']:.2f}%", f"{values['win_rate']:.2f}%", values['matches_played']))

    # Размещение таблицы в интерфейсе
    table.grid(row=10, column=0, columnspan=4)  # Измените параметры row и column в соответствии с вашим интерфейсом


def show_counters_team_2():
    input_heroes = [entry.get().lower().replace(' ', '-') for entry in team2_hero_entries if entry.get().strip()]

    if not input_heroes:
        result_text.delete(1.0, "end")
        result_text.insert("end", "Нет выбранных героев.")
        return

    sorted_average_values = calculate_average_values(input_heroes)

    # Создание таблицы
    table = ttk.Treeview(root, columns=('Hero', 'Disadvantage', 'Win Rate', 'Matches Played'), show='headings')
    table.heading('Hero', text='Hero')
    table.heading('Disadvantage', text='Disadvantage')
    table.heading('Win Rate', text='Win Rate')
    table.heading('Matches Played', text='Matches Played')

    for hero_name, values in sorted_average_values:
        table.insert('', 'end', values=(hero_name.replace('-', ' ').title(), f"{values['disadvantage']:.2f}%", f"{values['win_rate']:.2f}%", values['matches_played']))

    # Размещение таблицы в интерфейсе
    table.grid(row=10, column=0, columnspan=4)  # Измените параметры row и column в соответствии с вашим интерфейсом

def normalize_hero_name(hero_name):
    return hero_name.lower().replace('-', ' ').replace("'", "").replace(".", "")


def create_comparison_table(team1_heroes, team2_heroes):
    comparison_table = []

    for hero1 in team1_heroes:
        hero_row = []
        for hero2 in team2_heroes:
            hero1_counters = fetch_counters(hero1, period)
            hero2_counters = fetch_counters(hero2, period)

            hero1_name = normalize_hero_name(hero1)
            hero2_name = normalize_hero_name(hero2)

            hero1_disadvantage = next((float(counter['disadvantage'].strip('%')) for counter in hero1_counters if
                                       normalize_hero_name(counter['hero_name']) == hero2_name), 0)
            hero2_disadvantage = next((float(counter['disadvantage'].strip('%')) for counter in hero2_counters if
                                       normalize_hero_name(counter['hero_name']) == hero1_name), 0)

            comparison_value = (hero1_disadvantage - hero2_disadvantage) / 2
            hero_row.append(comparison_value)

        comparison_table.append(hero_row)

    return comparison_table


def show_comparison_table():
    team1_heroes = [entry.get().lower().replace(' ', '-') for entry in team1_hero_entries if entry.get().strip()]
    team2_heroes = [entry.get().lower().replace(' ', '-') for entry in team2_hero_entries if entry.get().strip()]

    if not team1_heroes or not team2_heroes:
        result_text.delete(1.0, "end")
        result_text.insert("end", "Выберите героев для обеих команд.")
        return

    # Увеличьте ширину колонки с названиями героев до 25 символов
    column_width = 20

    comparison_table = create_comparison_table(team1_heroes, team2_heroes)

    result_text.delete(1.0, "end")

    # Добавьте строку с именами героев команды 2
    team2_hero_names = ' '.join([f"{hero.replace('-', ' ').title():<{column_width}}" for hero in team2_heroes])
    result_text.insert("end", f"{' ' * column_width}  {team2_hero_names}\n")

    for hero1, row in zip(team1_heroes, comparison_table):
        row_text = '  '.join([f"{value:+.2f}".ljust(column_width) for value in row])
        row_average = sum(row)
        # Вставьте название героя команды 1 перед значениями сравнения с учетом новой ширины колонки
        result_text.insert("end",
                           f"{hero1.replace('-', ' ').title():<{column_width}}  {row_text}  {row_average:+.2f}\n")

    # Расчет суммы для каждого столбца
    column_sums = [sum(column) for column in zip(*comparison_table)]
    column_averages_text = '  '.join([f"{value:+.2f}".ljust(column_width) for value in column_sums])
    # Расчет суммы для нижней строки
    bottom_row_sum = sum(column_sums)
    # Добавьте сумму нижней строки в вывод
    result_text.insert("end", f"{' ' * column_width}  {column_averages_text}  {bottom_row_sum:+.2f}\n")


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

compare_button = ttk.Button(root, text="Сравнить команды", command=show_comparison_table)
compare_button.grid(row=4, column=0, padx=10, pady=10, columnspan=5)

# Изменить номер строки для кнопки "Показать контрпики"
calculate_button = ttk.Button(root, text="Показать контрпики команды 1", command=show_counters_team_1)
calculate_button.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

calculate_button = ttk.Button(root, text="Показать контрпики команды 2", command=show_counters_team_2)
calculate_button.grid(row=0, column=2, padx=10, pady=10, columnspan=5)

result_text = Text(root, wrap="word", width=140, height=20)
result_text.grid(row=3, column=0, padx=10, pady=10, columnspan=4)

result_scrollbar = Scrollbar(root, command=result_text.yview)
result_scrollbar.grid(row=3, column=4, sticky="nsew")
result_text["yscrollcommand"] = result_scrollbar.set

period_options = [' ', 'week', 'month', '3month','6month', 'year' , 'patch_7.33']
period_var = StringVar(root)
period_var.set(period_options[0])  # установите значение по умолчанию
period_dropdown = ttk.OptionMenu(root, period_var, *period_options, command=on_period_change)
period_dropdown.grid(row=6, column=0, padx=10, pady=10)

root.mainloop()
