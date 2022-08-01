import sqlite3
import requests


def get_address():
    while True:
        settings = get_settings_from_sql()
        print("//Меню//")
        print("1) Выход\n"
              "2) Настройки\n"
              "Для получения координат введите адрес в свободной форме")

        response = input()
        if (response == "2"):
            change_settings(settings)
            settings = get_settings_from_sql()
            continue
        elif (response == "1"):
            return


def get_settings_from_sql(sql_file="settings.db"):
    cur = sqlite3.connect(sql_file).cursor()
    response = cur.execute("""SELECT * FROM settings""").fetchone()
    cur.connection.close()
    return response


def save_settings_to_sql(settings, sql_file="settings.db"):
    cur = sqlite3.connect(sql_file).cursor()
    cur.execute("""UPDATE settings
                    SET URL=?,
                        API_KEY=?,
                        Language=?""", settings)
    cur.connection.commit()
    cur.connection.close()


def change_settings(settings):
    print("//Настройки//")
    print(f"1) URL адрес: {settings[0]}\n"
          f"2) API ключ: {settings[1]}\n"
          f"3) Язык: {settings[2]}")
    print('Для изменения введите данные в формате "<номер_поля> <новое_значение>"\n'
          'Для выхода из настроек нажмите ENTER')

    response = input().split()
    if len(response) == 2:
        settings = list(settings)
        settings[int(response[0]) - 1] = response[1]
        try:
            save_settings_to_sql(settings)
            print("Данные успешно изменены!")
        except sqlite3.IntegrityError as e:
            print('Ошибка! Поле "Язык" может содержать в себе значение "ru" или "en". Попробуйте снова')


if __name__ == '__main__':
    get_address()
