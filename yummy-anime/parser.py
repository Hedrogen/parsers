"""

    Парсер

    Что парсить:
    0. Рейтинг
    1. Количетсво просмотров
    2. Возрастной рейтинг
    3. Тэги
    4. Студия
    5. Тип - сериал/фильм
    6. Доступная озвучка

"""

import logging
import re

from datetime import datetime


import csv

from multiprocessing import Pool
from parsing_utils import get_full_soup
from settings import HOME_LINK, GLOBAL_LINK, MULTI_VALUE


logger = logging.getLogger('ParserLogger')
logger.setLevel(logging.WARNING)

file_handler = logging.FileHandler('logs.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Parser:

    """ Класс парсера """

    def __init__(self, link, multi_value, home_link):

        """ Инициализация данных """

        logger.info('Инициализация данных')

        start = datetime.now()

        self.link = link
        self.home_link = home_link
        self.multi_value = multi_value

        self.pages_links = self.get_pages_links()  # ссылки на страницы со списками аниме
        self.logic()
        self.inner_links = self.read_csv(number=0) # ссылки на конктретные аниме

        end = datetime.now()
        logger.info('Время выполнения: %s', end-start)
        print(f'Количество ссылок на страницы со списками аниме: {len(self.pages_links)}')
        print(f'Количество ссылок на внутренние страницы аниме: {len(self.inner_links)}')
        print(f'Время выполнения: {end-start}')


    def parse_outer(self, local_link):

        """ Парсит списки аниме """

        logger.info('Парсит списки аниме')
        soup = get_full_soup(local_link)
        base = soup.find_all('div', {'class': 'anime-column'})

        list_to_save = []
        for data in base:
            inner = self.home_link + data.find('a', class_='anime-title')['href']
            list_to_save.append(inner)
        self.write_to_csv(list_to_save, 1)

    @staticmethod
    def write_to_csv(value, position):

        """ Функция записывает получаемые значения в формат csv """

        name = 'data.csv' if position == 1 else 'detail_data.csv'

        logger.info('Записывает значение в формат csv, тип: %s', value)

        with open(name, 'a') as file_:
            writer = csv.writer(file_)
            writer.writerow(value)


    @staticmethod
    def read_csv(number):

        """
        Если number == 0, то считывает ссылки на аниме.
        Если number =! 0, то считывает детальную иноформацию об аниме.
        """

        value = 'data.csv' if number == 0 else 'detail_data.csv'

        logger.info('Считывает данные из формата csv, тип: %s', value)

        with open(value, newline='') as file_:
            reader = csv.reader(file_)
            list_to_return = []
            for row in reader:
                list_to_return.extend(row if isinstance(row, list) else [row])
        return list_to_return


    def get_pages_links(self):

        """ Генерирует страницы для парсинга """

        soup = get_full_soup(self.link)
        pages = int(soup.find('ul', {'class': 'pagination'}).find_all('li')[-2].text)
        print(pages)
        pages_list = [self.link.format(i) for i in range(1, pages)]
        return pages_list


    def parse_inner(self, link):

        """ Парсит по ссылке детальную информацию об аниме """

        # try:
        soup = get_full_soup(link)
        info = soup.find('div', {'class': 'content-page anime-page'})

        name = soup.find('h1').text.strip()
        try:
            rating = soup.find('span', {'class': 'main-rating'}).text
        except AttributeError as atbe:
            rating = 'Нет информации'
            logger.error('Информация не найдена %s', atbe)
        try:
            description = soup.find('div', {'id': 'content-desc-text'}).text.strip()
        except AttributeError:
            description = 'Нет данных'
        try:
            votes_count = soup.find('span',
                                    {'class': 'main-rating-info'}).text.split('г')[0][1:]
        except AttributeError:
            votes_count = 'Нет информации'
        try:
            year = self.conv(info, 'Год').strip()
        except AttributeError:
            year = 'Нет информации'
        try:
            views = self.conv(info, 'Просмотров').strip()
        except AttributeError:
            views = 'Нет информации'
        try:
            make_studio = self.conv(info, 'Студия').strip()
        except AttributeError:
            make_studio = 'Нет информации'
        try:
            anime_type = self.conv(info, 'Тип').strip()
        except AttributeError:
            anime_type = 'Нет информации'
        try:
            tags = self.conv(info, 'Жанр').strip().split('\n\n') # список
        except AttributeError:
            tags = 'Нет информации'
        try:
            translate = info.find_all('a', class_='studio-name')
            translate = [item.text for item in translate]
        except AttributeError:
            translate = self.conv(info, 'Перевод')
        try:
            if not translate:
                translate = [self.conv(info, 'Озвучка').strip()]
        except Exception:
            translate = 'Нет информации'
        try:
            episodes_count = self.conv(info, 'Серии').strip()
        except AttributeError:
            episodes_count = 1

        write_list = [name, description, year, rating, make_studio, anime_type,
                      episodes_count, votes_count, views, tags, translate, link]
        self.write_to_csv(write_list, 0)
        # except Exception as excpetion:
        #     print(f'Ошибка {link}')

    @staticmethod
    def conv(soup, name):

        """ Метод для сокращения шаблонного кода """

        return soup.find(text=re.compile(name)).findParents(limit=2)[1].text.split(':')[1]


    def logic(self):

        """ Логика парсера """

        with Pool(self.multi_value) as poll:
            poll.map(self.parse_outer, self.pages_links)
        print('Сбор ссылок закончен')
        self.inner_links = self.read_csv(number=0)

        header = ['name', 'description', 'year', 'rating', 'make_studio', 'anime_type',
                  'episodes_count', 'votes_count', 'views', 'tags', 'translate', 'url']
        self.write_to_csv(header, 0)

        with Pool(self.multi_value) as poll:
            poll.map(self.parse_inner, self.inner_links)


Parser(GLOBAL_LINK, MULTI_VALUE, HOME_LINK)
