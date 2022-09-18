from sys import platform
import sqlite3
import requests
from werkzeug.exceptions import abort
import feedparser
import csv
import pandas as pd
import re


class News:
    our_feeds = {}  # пример словаря RSS-лент
    f_all_news = ''
    f_certain_news = ''  # пример пути файла
    vector1 = ''  # пример таргетов
    vector2 = ''
    allheadlines = []
    alldescriptions = []
    alllinks = []
    alldates = []
    allImg = []

    def __init__(self, our_feeds, f_all_news, f_certain_news, vector1, vector2):
        self.our_feeds = our_feeds
        self.f_all_news = f_all_news
        self.f_certain_news = f_certain_news
        self.vector1 = vector1
        self.vector2 = vector2

    def __check_url__(self, url_feed):
        return feedparser.parse(url_feed)

    def __getHeadlines__(self, url_feed):  # функция для получения заголовков новости
        headlines = []
        lenta = self.__check_url__(url_feed).entries
        for item_of_news in lenta:
            headlines.append(item_of_news.title)
        return headlines

    # функция для получения описания новости
    def __getDescriptions__(self, url_feed):
        descriptions = []
        lenta = self.__check_url__(url_feed).entries
        for item_of_news in lenta:
            descriptions.append(item_of_news.description)
        return descriptions

    def __getLinks__(self, url_feed):  # функция для получения ссылки на источник новости
        links = []
        lenta = self.__check_url__(url_feed)
        for item_of_news in lenta.entries:
            links.append(item_of_news.link)
        return links

    def __getDates__(self, url_feed):  # функция для получения даты публикации новости
        dates = []
        lenta = self.__check_url__(url_feed).entries
        for item_of_news in lenta:
            dates.append(item_of_news.published)
        return dates

    def __getImg__(self, url_feed):  # функция для получения даты публикации новости
        img = []
        lenta = self.__check_url__(url_feed).entries
        for link in lenta:
            img.append(link.links[1].href)
        return img

    def addNews(self):  # заполнение масивы новостями
        # Прогоняем наши URL и добавляем их в наши пустые списки
        for key, url in self.our_feeds.items():
            self.allheadlines.extend(self.__getHeadlines__(url))

        for key, url in self.our_feeds.items():
            self.alldescriptions.extend(self.__getDescriptions__(url))

        for key, url in self.our_feeds.items():
            self.alllinks.extend(self.__getLinks__(url))

        for key, url in self.our_feeds.items():
            self.alldates.extend(self.__getDates__(url))

        for key, url in self.our_feeds.items():
            self.allImg.extend(self.__getImg__(url))

    # функция для записи всех новостей в .csv,
    def write_all_news(self, all_news_filepath):
        # возвращает нам этот датасет
        header = ['Title', 'Description', 'Links', 'Publication Date', 'Img']

        with open(all_news_filepath, 'w', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')

            writer.writerow(i for i in header)

            for a, b, c, d, e in zip(self.allheadlines, self.alldescriptions,
                                     self.alllinks, self.alldates, self.allImg):
                writer.writerow((a, b, c, d, e))

            df = pd.read_csv(all_news_filepath)

        return df

    # функция для поиска, а затем записи
    def looking_for_certain_news(self, all_news_filepath, certain_news_filepath, target1, target2):
        # определенных новостей по таргета,
        # затем возвращает этот датасет
        df = pd.read_csv(all_news_filepath)

        result = df.apply(lambda x: x.str.contains(target1, na=False,
                                                   flags=re.IGNORECASE, regex=True)).any(axis=1)
        result2 = df.apply(lambda x: x.str.contains(target2, na=False,
                                                    flags=re.IGNORECASE, regex=True)).any(axis=1)
        new_df = df[result & result2]

        new_df.to_csv(certain_news_filepath, sep='\t', encoding='utf-8-sig')

        return new_df


def get_db_connection():
    if platform == "linux" or platform == "linux2":
        DATABASE = '/var/www/ITnews/IT_news/database.db'
    elif platform == "win32":
        DATABASE = 'database.db'
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


def temperature():
    API_KEY = '01711b167ecd7d1e5977867e1453a795'  # initialize your key here
    # city = request.args.get('moscow')  # city name passed as argument
    city = ('kaluga')

    # call API and convert response into Python dictionary
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&APPID={API_KEY}'
    response = requests.get(url).json()

    # error like unknown city name, inavalid api key
    if response.get('cod') != 200:
        message = response.get('message', '')
        return f'Error getting temperature for {city.title()}. Error message = {message}'

    # get current temperature and convert it into Celsius
    current_temperature = response.get('main', {}).get('temp')
    if current_temperature:
        current_temperature_celsius = round(current_temperature - 273.15, 2)
        return f'Current temperature of {city.title()} is {current_temperature_celsius}'
    else:
        return f'Error getting temperature for {city.title()}'
