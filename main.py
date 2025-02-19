import gspread
import telebot
#import datetime
import time
#import threading
import random2
import io
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


bot = telebot.TeleBot('7946315844:AAHQAQ5TEDaCemBJIeYCx0frMH5vqdD5ejs')
@bot.message_handler(commands=['start'])
def start_message(message):
        bot.reply_to(message, 'Привет! Я чат бот, который будет строить графики и мониторить здоровье Лаймика')
#        reminder_thread = threading.Thread(target=send_reminders, args=(message.chat.id,))
#       reminder_thread.start()

@bot.message_handler(commands=['help'])
def help_message(message):
        bot.reply_to(message, f'Возможны команды /start - начало общения, /fact - факты о диабете, /graph - построить общий график, /gdose - набор графиков по дозам!')

@bot.message_handler(commands=['fact'])
def fact_message(message):
        list = [
            "**Вероятность заболеть есть в любом возрасте**: Исследования показывают, что сахарный диабет может возникнуть в любом возрасте. Однако в популяции домашних кошек он чаще регистрируется у животных 10–15 лет, а у собак — 5–15 лет.",
            "**У котов и собак это бывает по разному**: В популяции кошек наиболее распространена форма диабета, напоминающая сахарный диабет второго типа человека. У собак же преобладает сахарный диабет первого типа.",
            "**Как кормить?**: Для правильного лечения очень важно давать Вашему питомцу подходящий корм. Питание собак и кошек, больных сахарным диабетом, несколько отличается. Для собак необходима диета с умеренным содержанием сложных углеводов и клетчатки и низким уровнем жира. Собак необходимо кормить 2 раза в день, непосредственно перед введением инсулина. Корм для кошек должен содержать большое количество белка и малое количество углеводов. Обычно кошки едят небольшими порциями несколько раз в день, однако очень важно, чтобы кошка не переедала.",
            "**Позитивный прогноз реален**: При своевременном назначении инсулина у 80% кошек наступает ремиссия, то есть их поджелудочная железа восстанавливает способность к выработке достаточного количества инсулина."]
        random2.fact = random2.choice(list)
        bot.reply_to(message, f'Лови факт о диабете у котов и кошек {random2.fact}')

    # Путь к файлу ключа JSON
json_file_path = r'C:\Json_dir\catstracker-449519-fd725f5dd83f.json'

    # Определение области видимости
scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

# Создание учетных данных
creds = Credentials.from_service_account_file(json_file_path, scopes=scope)

# Авторизация и открытие Google Таблицы
gc = gspread.authorize(creds)
    # Откройте Google Таблицу по её URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1ZZIPE6JrIzLQskv37z_UXg0YW7NxmrfeyUuaDyNGL6I/edit?gid=0#gid=0"
sh = gc.open_by_url(spreadsheet_url)

# Выберите первый лист таблицы
wks = sh.sheet1

# Преобразование данных в DataFrame
data = wks.get_all_records()
df = pd.DataFrame(data)

    # Вывод последних 10 строк
    #print(df.tail(10))
    #print(df.head(10))

    # Преобразование столбцов в нужные типы данных
df['дата'] = pd.to_datetime(df['дата'], format='%d.%m.%Y', errors='coerce').dt.strftime('%d.%m.%Y')
df['время'] = pd.to_datetime(df['время'], format='%H:%M', errors='coerce').dt.time
df['глюкоза'] = pd.to_numeric(df['глюкоза'], errors='coerce')/100
df['доза'] = pd.to_numeric(df['доза'], errors='coerce') / 100
df['укол время'] = pd.to_datetime(df['укол время'], format='%H:%M', errors='coerce').dt.time
df['Стул'] = df['Стул'].apply(lambda x: 1 if x == 'был' else 0)

    # Добавление признака "часть дня"
def determine_part_of_day(row):
        # Проверка, что время не является NaT (Not a Time)
    if pd.notna(row['время']):
            # Если время меньше 14:00, считаем это утро
        return 'утро' if row['время'] < pd.to_datetime('14:00').time() else 'вечер'
    elif pd.notna(row['укол время']):
            # Аналогично для времени укола
        return 'утро' if row['укол время'] < pd.to_datetime('14:00').time() else 'вечер'
    else:
        return None

    # Применение функции фильтрации
df['часть дня'] = df.apply(determine_part_of_day, axis=1)

    # Разделение данных на утренние и вечерние

morning_data = df[df['часть дня'] == 'утро']
evening_data = df[df['часть дня'] == 'вечер']

    # Вывод данных, на основе которых построены графики
    #print("Данные для утренних часов:")
    #print(morning_data[['дата', 'глюкоза', 'доза']])

    #print("\nДанные для вечерних часов:")
    #print(evening_data[['дата', 'глюкоза', 'доза']])

    # Проверка что все данные включены, на основе которых построены графики
    #print(f"Количество утренних записей: {len(morning_data)}")
    #print(f"Количество вечерних записей: {len(evening_data)}")

@bot.message_handler(commands=['graph'])
def graph_command(message):
        # Построение графиков
    fig, axs = plt.subplots(2, 1, figsize=(14, 10))

    # График для утренних часов
    ax1 = axs[0]
    ax1.plot(morning_data['дата'], morning_data['глюкоза'], label='Глюкоза', marker='o', color='b')
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Глюкоза', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.xaxis.set_tick_params(rotation=45)  # Поворот меток на оси X

    # Добавление тренда для глюкозы
    z1 = np.polyfit(morning_data.index, morning_data['глюкоза'], 1)
    p1 = np.poly1d(z1)
    ax1.plot(morning_data['дата'], p1(morning_data.index), "b--", label='Тренд глюкозы')

    ax2 = ax1.twinx()
    ax2.plot(morning_data['дата'], morning_data['доза'], label='Доза', marker='x', color='r')
    ax2.set_ylabel('Доза', color='r')
    ax2.tick_params(axis='y', labelcolor='r')


    ax1.set_title('Утро: Глюкоза и Доза по Датам')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid(True)

        # График для вечерних часов
    ax3 = axs[1]
    ax3.plot(evening_data['дата'], evening_data['глюкоза'], label='Глюкоза', marker='o', color='b')
    ax3.set_xlabel('Дата')
    ax3.set_ylabel('Глюкоза', color='b')
    ax3.tick_params(axis='y', labelcolor='b')
    ax3.xaxis.set_tick_params(rotation=45)  # Поворот меток на оси X

    # Добавление тренда для глюкозы
    z3 = np.polyfit(evening_data.index, evening_data['глюкоза'], 1)
    p3 = np.poly1d(z3)
    ax3.plot(evening_data['дата'], p3(evening_data.index), "b--", label='Тренд глюкозы')

    ax4 = ax3.twinx()
    ax4.plot(evening_data['дата'], evening_data['доза'], label='Доза', marker='x', color='r')
    ax4.set_ylabel('Доза', color='r')
    ax4.tick_params(axis='y', labelcolor='r')

    ax3.set_title('Вечер: Глюкоза и Доза по Датам')
    ax3.legend(loc='upper left')
    ax4.legend(loc='upper right')
    ax3.grid(True)

    plt.tight_layout()
    # Сохранение графика в файл
    plt.savefig('glucose_levels.png')
    with io.BytesIO() as image_binary:
        plt.savefig(image_binary, format='png')
        image_binary.seek(0)
        bot.send_photo(message.chat.id, image_binary)
    # Отображение графика
    #plt.show()

    # Закрытие фигуры
#    plt.close()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(15)  # Wait before restarting polling

    # Группировка данных по периодам с одинаковой дозой
#    morning_groups = df[df['часть дня'] == 'утро'].groupby('доза')
#    evening_groups = df[df['часть дня'] == 'вечер'].groupby('доза')


#    a = int(input("Строить графики по дозам? 1 - да 0 - нет: "))
#    if a == 1:
        # Построение графиков для утренних часов
#        for dose, group in morning_groups:
#            fig, ax1 = plt.subplots(figsize=(14, 7))
#             ax1.plot(group['дата'], group['глюкоза'], label='Глюкоза', marker='o', color='b')
#             ax1.set_xlabel('Дата')
#             ax1.set_ylabel('Глюкоза', color='b')
#             ax1.tick_params(axis='y', labelcolor='b')

    #         ax2 = ax1.twinx()
    #         ax2.plot(group['дата'], group['доза'], label='Доза', marker='x', color='r')
    #         ax2.set_ylabel('Доза', color='r')
    #         ax2.tick_params(axis='y', labelcolor='r')
    #
    #         ax1.set_title(f'Утро: Глюкоза и Доза по Датам (Доза: {dose})')
    #         ax1.legend(loc='upper left')
    #         ax2.legend(loc='upper right')
    #         ax1.grid(True)
    #
    #         plt.savefig(f'glucose_Morning_{dose}.png')
    #         plt.tight_layout()
    #         #plt.show()
    #         plt.close()
    #         # Вывод данных, на основе которых построен график
    #         print(f"Данные для утренних часов (Доза: {dose}):")
    #         print(group[['дата', 'глюкоза', 'доза']])
    #         print("\n")
    #
    #
    # # Построение графиков для вечерних часов
    #     for dose, group in evening_groups:
    #         fig, ax1 = plt.subplots(figsize=(14, 7))
    #         ax1.plot(group['дата'], group['глюкоза'], label='Глюкоза', marker='o', color='b')
    #         ax1.set_xlabel('Дата')
    #         ax1.set_ylabel('Глюкоза', color='b')
    #         ax1.tick_params(axis='y', labelcolor='b')
    #
    #         ax2 = ax1.twinx()
    #         ax2.plot(group['дата'], group['доза'], label='Доза', marker='x', color='r')
    #         ax2.set_ylabel('Доза', color='r')
    #         ax2.tick_params(axis='y', labelcolor='r')
    #
    #         ax1.set_title(f'Вечер: Глюкоза и Доза по Датам (Доза: {dose})')
    #         ax1.legend(loc='upper left')
    #         ax2.legend(loc='upper right')
    #         ax1.grid(True)
    #
    #         plt.tight_layout()
    #         plt.savefig(f'glucose_Evening_{dose}.png')
    #         #plt.show()
    #         plt.close()
    #     # Вывод данных, на основе которых построен график
    #         print(f"Данные для вечерних часов (Доза: {dose}):")
    #         print(group[['дата', 'глюкоза', 'доза']])
    #         print("\n")
