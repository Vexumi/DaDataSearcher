import sqlite3
import requests


def app_get_coords():
    main_cycle = True

    while main_cycle:
        resp = menu_main()  # запускаем главное меню и получаем запрос пользователя
        if resp == "EXIT":  # если запрос == EXIT завершаем работу
            print("Завершение работы программы")
            main_cycle = False
            continue

        settings = get_settings_from_sql()  # получаем последние настройки из БД
        sd = get_sample_data(resp, settings)  # получаем данные с сервера
        if not sd: continue  # если есть ошибка то выходим в меню

        # выводим полученные данные
        print("Найденные варианты:")
        for n, i in enumerate(sd["suggestions"]):
            print(str(n + 1) + ")", i['value'])

        while True:
            print("Для получения инфомации о координатах введите номер искомого обьекта")
            try:
                # получаем от пользователя номер обьекта для получения его координат
                number = int(input())
                object_data = sd["suggestions"][number - 1]["data"]
                print("Координаты " + sd["suggestions"][number - 1]['value'] + ": " + object_data["geo_lat"],
                      object_data["geo_lon"] + "\n")  # выводим координаты
                break  # выходим из цикла
            except (IndexError, ValueError) as e:  # если ловим ошибку то получаем номер обьекта заново
                print("Неверно указан номер, повторите попытку")


def get_sample_data(req, settings):
    """
    Функция обращается к серверу с запросом req и параметрами settings. Возвращает ответ сервера в формате json
    :param req: Запрос пользователя
    :param settings: [URl, API_KEY, Language("ru"/"en")]
    :return: Ответ сервера в формате json
    """
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {settings[1]}",
    }  # формируем заголовки
    params = dict(query=req, language=settings[2])  # формируем параметры

    try:
        res = requests.get(settings[0], headers=headers, params=params)  # отправляем запрос на сервер
    except requests.exceptions.ConnectionError as e:  # если ловим ошибку подключения то ничего не возвращаем
        print("Ошибка! Проверьте подключение к сети, а так же правильность указанного адреса")
    except Exception as e:
        print("Непредвиденная ошибка!", str(e))
    else:
        if res:  # если ответ получен без ошибок...
            return res.json()  # ... то возвращаем ответ в формате json
        else:  # иначе...
            print("Ошибка!", res.status_code)  # ...выводим код ошибки


def menu_main():
    """
    Главное меню программы
    :param settings: [URl, API_KEY, Language("ru"/"en")]
    :return: "EXIT" если пользователь хочет выйти из программы,
            "Continue" если пользователь изменил данные в настройках,
            иначе возвращает текст для поиска координат.
    """
    while True:
        print("//Меню//")
        print("1) Выход\n"
              "2) Настройки\n"
              "Для получения координат введите адрес в свободной форме")

        response = input()
        if (response == "2"):  # если пользователь ввел 2 запускаем меню настроек
            menu_settings()
            continue
        elif (response == "1"):  # если пользователь ввел 1 возвращаем EXIT
            return "EXIT"
        return response  # иначе возвращаем запрос


def get_settings_from_sql(sql_file="settings.db"):
    """

    :param sql_file: Файл БД
    :return: [URl, API_KEY, Language("ru"/"en")]
    """
    cur = sqlite3.connect(sql_file).cursor()
    response = cur.execute("""SELECT * FROM settings""").fetchone()  # из таблицы settings получаем 1 строку
    cur.connection.close()
    return response


def save_settings_to_sql(settings, sql_file="settings.db"):
    """
    Функция сохраняет настройки БД
    :param settings: [URl, API_KEY, Language("ru"/"en")]
    :param sql_file: файл БД
    :return: None
    """
    cur = sqlite3.connect(sql_file).cursor()
    cur.execute("""UPDATE settings
                    SET URL=?,
                        API_KEY=?,
                        Language=?""", settings)  # обновляем данные в БД
    cur.connection.commit()  # подтверждаем изменение
    cur.connection.close()  # отключаемся


def menu_settings():
    """
    Функция запускает меню настроек программы
    :return: None
    """
    while True:
        settings = get_settings_from_sql()
        print("//Настройки//")
        print(f"1) URL адрес: {settings[0]}\n"
              f"2) API ключ: {settings[1]}\n"
              f"3) Язык: {settings[2]}")
        print('Для изменения введите данные в формате "<номер_поля> <новое_значение>"\n'
              'Для выхода из настроек нажмите ENTER')

        response = input().split()
        if len(response) == 2:
            settings = list(settings)  # tuple -> list
            settings[int(response[0]) - 1] = response[1]  # settings[<номер_поля> - 1] = <новое_значение>
            try:
                save_settings_to_sql(settings)
                print("Данные успешно изменены!")
            except sqlite3.IntegrityError as e:  # в бд стоит CHECK на поле Language, принимает только "ru" или "en"
                print('Ошибка! Поле "Язык" может содержать в себе значение "ru" или "en". Попробуйте снова')
                continue
        break


if __name__ == '__main__':
    app_get_coords()
