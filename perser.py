"""
Парсер данных
Этот модуль предназначен для сбора и обработки информации с веб-сайтов или API.
📘 Возможности:
- Получение HTML-страниц с помощью requests
- Извлечение нужных данных (через BeautifulSoup)
- Сохранение результатов в CSV или JSON
"""
# Импорт библиотек
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# Пример шаблона функции парсера
def parse_example():
    """Пример функции парсера."""
    url = "https://example.com"  # сюда вставь нужный сайт
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # пример: найти все заголовки h2
        titles = [t.text for t in soup.find_all("h2")]

        # вывести результаты
        print("Найдено заголовков:", len(titles))
        for t in titles:
            print("-", t)

        # сохранить в JSON
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(titles, f, ensure_ascii=False, indent=4)
    else:
        print("Ошибка при запросе:", response.status_code)


if name == "__main__":

    parse_example()
