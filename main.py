import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Путь к файлу ключа JSON
json_file_path = 'C:\Json_dir\catstracker-449519-fd725f5dd83f.json'

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
# Вывод первых последних строк
df.tail()

# Вывод первых 10 строк
print(df.head(10))

# Преобразование столбцов в нужные типы данных
df['дата'] = pd.to_datetime(df['дата'], format='%d.%m.%Y', errors='coerce').dt.strftime('%d.%m.%Y')
df['время'] = pd.to_datetime(df['время'], format='%H:%M', errors='coerce').dt.time
df['глюкоза'] = pd.to_numeric(df['глюкоза'], errors='coerce')/100
df['доза'] = pd.to_numeric(df['доза'], errors='coerce') / 100
df['укол время'] = pd.to_datetime(df['укол время'], format='%H:%M', errors='coerce').dt.time
df['Стул'] = df['Стул'].apply(lambda x: 1 if x == 'был' else 0)

# Добавление признака "часть дня"
def determine_part_of_day(row):
    if pd.notna(row['время']):
        return 'утро' if row['время'] < pd.to_datetime('14:00').time() else 'вечер'
    elif pd.notna(row['укол время']):
        return 'утро' if row['укол время'] < pd.to_datetime('14:00').time() else 'вечер'
    else:
        return None

df['часть дня'] = df.apply(determine_part_of_day, axis=1)
# Разделение данных на утренние и вечерние

morning_data = df[df['часть дня'] == 'утро']
evening_data = df[df['часть дня'] == 'вечер']

# Вывод данных, на основе которых построены графики
print("Данные для утренних часов:")
print(morning_data[['дата', 'глюкоза', 'доза']])

print("\nДанные для вечерних часов:")
print(evening_data[['дата', 'глюкоза', 'доза']])

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

# Добавление тренда для дозы
z2 = np.polyfit(morning_data.index, morning_data['доза'], 1)
p2 = np.poly1d(z2)
ax2.plot(morning_data['дата'], p2(morning_data.index), "r--", label='Тренд дозы')

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

# Добавление тренда для дозы
z4 = np.polyfit(evening_data.index, evening_data['доза'], 1)
p4 = np.poly1d(z4)
ax4.plot(evening_data['дата'], p4(evening_data.index), "r--", label='Тренд дозы')

ax3.set_title('Вечер: Глюкоза и Доза по Датам')
ax3.legend(loc='upper left')
ax4.legend(loc='upper right')
ax3.grid(True)


plt.tight_layout()
plt.show()
# Группировка данных по периодам с одинаковой дозой
morning_groups = df[df['часть дня'] == 'утро'].groupby('доза')
evening_groups = df[df['часть дня'] == 'вечер'].groupby('доза')

# Построение графиков для утренних часов
for dose, group in morning_groups:
    fig, ax1 = plt.subplots(figsize=(14, 7))
    ax1.plot(group['дата'], group['глюкоза'], label='Глюкоза', marker='o', color='b')
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Глюкоза', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    ax2 = ax1.twinx()
    ax2.plot(group['дата'], group['доза'], label='Доза', marker='x', color='r')
    ax2.set_ylabel('Доза', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    ax1.set_title(f'Утро: Глюкоза и Доза по Датам (Доза: {dose})')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid(True)

    # Форматирование дат на оси X
   # ax1.xaxis.set_major_formatter(plt.DateFormatter('%d.%m.%Y'))
   # plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    plt.show()

    # Вывод данных, на основе которых построен график
    print(f"Данные для утренних часов (Доза: {dose}):")
    print(group[['дата', 'глюкоза', 'доза']])
    print("\n")

# Построение графиков для вечерних часов
for dose, group in evening_groups:
    fig, ax1 = plt.subplots(figsize=(14, 7))
    ax1.plot(group['дата'], group['глюкоза'], label='Глюкоза', marker='o', color='b')
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Глюкоза', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    ax2 = ax1.twinx()
    ax2.plot(group['дата'], group['доза'], label='Доза', marker='x', color='r')
    ax2.set_ylabel('Доза', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    ax1.set_title(f'Вечер: Глюкоза и Доза по Датам (Доза: {dose})')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax1.grid(True)

    # Форматирование дат на оси X
  #  ax1.xaxis.set_major_formatter(plt.DateFormatter('%d.%m.%Y'))
 #   plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    plt.show()

    # Вывод данных, на основе которых построен график
    print(f"Данные для вечерних часов (Доза: {dose}):")
    print(group[['дата', 'глюкоза', 'доза']])
    print("\n")
