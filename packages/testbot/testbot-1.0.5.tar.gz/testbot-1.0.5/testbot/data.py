# -*- coding: utf-8 -*-
import asyncio
import aiohttp

from pprint import pprint
import motor.motor_asyncio

from testbot.settings import settings
from testbot.model import *

try:
    # Подключаемся к хранилищу
    DB_URL = settings["mongodb"]["test"][0]["url"]
    CLIENT = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)

    # Подключаемся к базе
    db = CLIENT.test
except:
    pass


async def add_new_user(user_id: int, name: str, surname: str, role="STUDENT"):
    """
    Добавляет нового пользователя в таблицу users.
    Операция выполняется в начале общения пользователя с ботом.
    :param user_id: id пользователя в Телеграме
    :param name: имя пользователя
    :param surname: фамилия пользователя
    :param role: роль пользователя (STUDENT, ADMIN, SUPPORT, CREATOR)
    """
    document = await db.users.find_one({"tg_id": user_id})
    if not document:
        user = {
            "tg_id": user_id,
            "role": role,
            "name": name,
            "surname": surname,
            "tests": [],
            "callback": None
        }
        result = await db.users.insert_one(user)
        print(result)
    else:
        print("user already exists")


async def add_question_result(user_id: int, test_index: int, question_index: int, result: int):
    """
    Добавляет результат решения вопроса пользователем
    :param user_id: id пользователя в Телеграм
    :param test_index: индекс теста
    :param question_index: индекс вопроса
    :param result: результат
    """
    res = await db.users.find_one({"tg_id": user_id}, projection=["tests.current_question"])
    current_question = res["tests"][test_index]["current_question"]
    current_question = current_question if current_question else 0
    current_question += 1
    key = {"tg_id": user_id}
    await db.users.update_one(key, {"$set": {f"tests.{test_index}.questions.{question_index}.result": result,
                                             f"tests.{test_index}.current_question": current_question}})


async def add_user_test(user_id: int, test_obj: dict):
    """
    Добавляет в список tests пользователя новый тест
    :param user_id: id пользователя в Телеграме
    :param test_obj: объект теста
    """
    key = {"tg_id": user_id}
    test = Test(test_obj)
    res = await db.users.update_one(key, {"$push": {"tests": dict(test)}})


async def get_all_user_tests(user_id: int):
    # FIXME
    res = await db.users.find_one({"tg_id": user_id}, projection=["tests.name"])
    all_tests = res["tests"]
    return all_tests


async def get_user_tests(user_id: int):
    """
    Получает все доступные тесты пользователя
    :param user_id: id пользователя в Телеграме
    :return: список имен и индексов тестов
    """
    res = await db.users.find_one({"tg_id": user_id},
                                  projection=["tests.is_available", "tests.name", "tests.current_question"])
    all_tests = res["tests"]
    # pprint(all_tests)
    if all_tests:
        tests = []
        for i in range(len(all_tests)):
            if all_tests[i]["is_available"]:
                tests.append({"name": all_tests[i]["name"], "index": i,
                              "current_question": all_tests[i]["current_question"]})
        return tests
    return None


async def get_user_test(user_id: int, test_index: int):
    """
    Получает тест пользователя по его индексу
    :param user_id: id пользователя в Телеграме
    :param test_index: индекс теста
    :return: список тестов
    """
    res = await db.users.find_one({"tg_id": user_id}, projection=["tests"])
    tests = res["tests"]
    if tests:
        return tests[test_index]
    else:
        return None


async def edit_test_status(user_id: int, test_index: int, status: bool):
    """
    Изменяет статус доступности теста пользователя
    :param user_id: id пользователя
    :param test_index: индекс теста
    :param status: статус доступности
    """
    key = {"tg_id": user_id}
    await db.users.update_one(key, {"$set": {f"tests.{test_index}.is_available": status}})


async def get_user_callback(user_id: int):
    """
    Возвращает значение поля waiting_for_function таблицы users
    :param user_id: id пользователя в Телеграме
    :return: функция, которая должна быть выполнена ботом или None, если такой нет
    """
    key = {"tg_id": user_id}
    user = await db.users.find_one(key)
    if user:
        return user["callback"]
    else:
        return None


async def set_user_callback(user_id: int, function_name, args: list=list(), kwargs: dict=dict()):
    """
    Устанавливает значение поля waiting_for_function таблицы users
    :param user_id: id пользователя в Телеграме
    :param function_name: имя функции, которую нужно будет
        вызвать при вводе сообщения пользователем
    :param args: аргументы функции
    :param kwargs: именованные агрументы функции
    """
    key = {"tg_id": user_id}
    if function_name == None:
        changing = {"callback": None}
    else:
        changing = {"callback": {
            "function": function_name,
            "args": args,
            "kwargs": kwargs
        }}
    result = await db.users.update_one(key, {"$set": changing})


async def get_bot_setting(setting_key: str, setting_field="text"):
    """
    Возвращает значение заданного поля заданной настройки бота
    :param setting_key: имя параметра настроек
    :param setting_field: поле настройки, которое нужно получить
    :return: значение заданного поля настройки или None,
        если такого поля или настройки не существует
    """
    setting = await db["settings"].find_one({"key": setting_key})
    if setting:
        if setting_field in setting:
            return setting[setting_field]
        else:
            return None
    else:
        return None


async def edit_bot_settings(setting_key: str, setting_body: dict):
    """
    Изменяет или добавляет новые внутренние переменные бота.
    Например, можно изменить значение настройки help:
        await edit_bot_settings("help", {
            "text": "test help message"
        })
    :param setting_key: имя параметра настроек
    :param setting_body: тело настройки (см. пример)
    """
    key = {"key": setting_key}
    setting = await db.settings.find_one(key)
    if setting:
        result = db.settings.update_one(key, {"$set": setting_body})
    else:
        document = setting_body
        document["key"] = setting_key
        result = await db.settings.insert_one(document)


async def get_tg_document(token: str, file_path: str):
    """
    Получает документ из чата в Телеграме
    :param token: токен бота
    :param file_path: отностиельный путь к файлу
    :return: текст из файла
    """
    # TO DO: Обрабатывать не только текстовые документы
    link = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_path)
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            print(resp.status)
            return await resp.text()


async def get_task_link(text: str):
    # FIXME
    link = f"https://yandex.ru/search/?text={text} iloveeconomics"
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            print(resp.status)
            page = await resp.text()
            try:
                part_index = page.index("<li class=serp-item")
                part = page[part_index: part_index + 600]
                href_index = part.index("href")
                href = part[href_index+6:].split()[0][:-1]
                return href
            except:
                return None

# === PACKAGES ================== =============================== === PACKAGES ================== ====================
# ===== PACKAGES ================ =============================== ===== PACKAGES ================ ====================
# ======= PACKAGES ============== =============================== ======= PACKAGES ============== ====================
# ===== PACKAGES ================ =============================== ===== PACKAGES ================ ====================
# === PACKAGES ================== =============================== === PACKAGES ================== ====================


async def get_bot_packages():
    """
    Получает список всех пакетов
    :return: список имен пакетов
    """
    cursor = db.packages.find({})
    packages = [package["name"] for package in await cursor.to_list(length=100)]
    return packages


async def get_bot_package(package_name: str):
    """
    Получает объект пакета по его имени
    :param package_name: имя пакета
    :return: объект пакета
    """
    package = await db.packages.find_one({"name": package_name})
    return package


async def add_bot_package(name: str):
    """

    :param name: имя пакета
    :return: статус операции (True/False)
    """
    package = await db.packages.find_one({"name": name})
    if not package:
        package = Package(name=name)
        result = await db.packages.insert_one(dict(package))
        return True
    else:
        return False


async def edit_bot_package(name: str, changing: dict):
    """
    Изменяет значение одного из полей пакета (или добавляет новое поле)
    :param name: имя пакета
    :param changing: изменение в формате {"ключ": значение}
    :return: статус операции (True/False)
    """
    # TODO: исправить ошибки при изменении имени
    key = {"name": name}
    package = await db.packages.find_one(key)
    if package:
        result = await db.packages.update_one(key, {"$set": changing})
        return True
    else:
        return False


async def delete_bot_package(package_name: str):
    """
    Удаляет пакет тестов с давнным именем
    :param package_name: имя пакета
    :return:
    """
    result = await db.tests.delete_many({"package": package_name})
    result = await db.packages.delete_one({"name": package_name})


async def get_package_tests(package_name: str):
    """
    Получает список тестов введенного пакета
    :param package_name: имя пакета
    :return: список имен тестов
    """
    cursor = db.tests.find({"package": package_name})
    tests = [package_test["name"] for package_test in await cursor.to_list(length=100)]
    return tests


async def get_package_test(package_name: str, test_name: str):
    """
    Получает объект теста конкретного пакета
    :param package_name: имя пакета
    :param test_name: имя теста
    :return: объект теста
    """
    key = {"name": test_name, "package": package_name}
    package_test = await db.tests.find_one(key)
    return package_test


async def add_package_test(package_name: str, test_name: str, price: float=0.0,
                           questions: list=[], description: str="", is_exam: bool=False):
    """
    Добавляет объект теста в таблицу тестов
    :param package_name: имя пакета, содержащего тест
    :param test_name: имя теста
    :param price: цена теста
    :param questions: список вопросов теста
    :param description: описание теста
    :param is_exam: является ли тест экзаменом
    :return: статус операции добавления (true/false)
    """
    package_test = await db.tests.find_one({"name": test_name, "package": package_name})
    if not package_test:
        package_test = {
            "name": test_name,
            "package": package_name,
            "price": price,
            "questions": questions,
            "description": description,
            "is_exam": is_exam
        }
        result = await db.tests.insert_one(package_test)
        result = await db.packages.update_one(
            {"name": package_name},
            {"$push": {"tests": test_name}}
        )
        return True
    else:
        return False


async def edit_package_test(package_name: str, test_name: str, changing: dict):
    """
    Изменяет значение одного из полей теста (или добавляет новое поле)
    :param package_name: имя пакета
    :param test_name: имя теста
    :param changing: изменения в формате {"ключ": значение}
    :return: статус операции (True/False)
    """
    key = {"name": test_name, "package": package_name}
    package_test = await db.tests.find_one(key)
    if package_test:
        if "name" in changing:
            result = await db.packages.update_one(
                {"name": package_name, "tests.$": test_name},
                {"$set": {"tests.$": changing["name"]}}
            )
        if "questions" in changing:
            return False
        result = await db.tests.update_one(key, {"$set": changing})
        return True
    else:
        return False


async def add_test_question(package_name: str, test_name: str, answer: str, points: int=1,
                            answer_type: str="text", body_text: str="",
                            yd_url: str="", answer_variants: list=[]):
    # TODO
    key = {"name": test_name, "package": package_name}
    question = {
        "points": points,
        "answer": answer,
        "answer_type": answer_type,
        "body": {
            "yd_url": yd_url,
            "text": body_text
        },
        "answer_variants": answer_variants
    }
    result = await db.tests.update_one(key, {"$push": {"questions": question}})


async def delete_package_test(package_name: str, test_name: str):
    """
    Удаляет один тест из пакета
    :param package_name: имя пакета
    :param test_name: имя теста
    """
    result = await db.tests.delete_one({"name": test_name, "package": package_name})
    result = await db.packages.delete_one({"tests.$": test_name})


async def edit_test_question(package_name: str, test_name: str, question_index: int,
                             question_key: str, updated_value: str):
    """
    Изменяет вопрос по индексу из списка вопросов теста
    :param package_name: имя пакета
    :param test_name: имя теста
    :param question_index: индекс вопроса
    :param question_key: поле, которое будет изменено/добавлено
    :param updated_value: новое значение изменяемого поля
    :return: статус операции (True/False)
    """
    key = {"name": test_name, "package": package_name}
    package_test = await get_package_test(package_name, test_name)
    questions = package_test["questions"]
    try:
        questions[question_index][question_key] = updated_value
    except IndexError as e:
        return False
    result = await db.tests.update_one(key, {"$set": {"questions": questions}})
    return True


async def delete_test_question(package_name: str, test_name: str, question_index: int):
    """
    Удаляет один вопрос из теста по индексу в списке tests.questions
    :param package_name: имя пакета
    :param test_name: имя теста
    :param question_index: индекс вопроса
    :return: статус операции удаления (True/False)
    """
    key = {"name": test_name, "package": package_name}
    package_test = await get_package_test(package_name, test_name)
    questions = package_test["questions"]
    try:
        questions.pop(question_index)
    except IndexError as e:
        return False
    result = await db.tests.update_one(key, {"$set": {"questions": questions}})
    return True

if __name__ == '__main__':
    async def test():
        # print(await get_user_callback(240014565))
        # print(await delete_bot_package("a"*97))
        # print(await add_package_test("first", "test1"))
        # print(await edit_package_test("first", "test1", {"name": "test0"}))

        # print(await add_bot_package("new_formatted_package"))
        # pprint(await get_user_test(240014565, 0))
        # await add_question_result(240014565, 0, 0, 0)
        # pprint(await add_user_test(240014565, {}))
        # await edit_test_status(240014565, 0, True)
        print(await get_task_link("Рассмотрите страну Z, производящую два товара – икс и игрек – с помощью двух факторов производства: капитала и труда. Для производства единицы икса необход"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
