# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('agg')

import matplotlib.pyplot as plt
import PIL
import numpy as np
import testbot.data


async def get_test_results(user_id: int, test_index: int):
    """
    Получает результаты теста и преобразует в проценты
    :param user_id: id пользователя в Телеграм
    :param test_index: индекс теста пользователя
    :return: объект результата теста
    """
    test = await testbot.data.get_user_test(user_id, test_index)
    questions = test["questions"]
    s = 0
    r = 0
    for question in questions:
        s += question["points"]
        if question["result"] is None:
            r += 0
        else:
            r += question["result"]
    if s == 0:
        result = 0
    else:
        result = (r / s) * 100
    return {"name": test["name"], "result": result}


async def get_user_results(user_id: int):
    """
    Строит столбчатую диаграмму по всем тестам
    пользователя и процентам выполнения каждого теста
    :param user_id: id пользователя в Телеграм
    :return: картинка диаграммы в байтовом формате
    """
    tests = await testbot.data.get_all_user_tests(user_id)
    if not tests:
        return None
    x = []
    repeated_names = {}
    y = []
    for test_index in range(len(tests)):
        res = await get_test_results(user_id, test_index)
        name = res["name"]
        if name in repeated_names:
            repeated_names[name] += 1
            name += f" ({repeated_names[name]})"
        else:
            repeated_names[name] = 0
        x.append(name)
        y.append(res["result"])

    fig, ax = plt.subplots(figsize=(10/6.4*len(tests)+0.8, 3))
    # строим диаграмму
    ax.bar(range(len(x)), y)
    # подписи под графиком
    ax.stackplot(x, [0 for _ in x])
    ax.set_ylim(ymin=0, ymax=100)

    fig.canvas.draw()
    # Получаем RGB список
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close()

    # Конвертируем в PNG
    img = PIL.Image.fromarray(data)
    bytes_png = img._repr_png_()
    return bytes_png
