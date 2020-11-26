"""

    Утилиты - получение html, soup

"""

import logging
import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


logger = logging.getLogger('UtilsLogger')
logger.setLevel(logging.WARNING)

file_handler = logging.FileHandler('logs.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def get_html(link):

    """ Возвращает html """

    response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
    if response.status_code == 200:
        logger.info('Получение html')
        content = response.text
        return content
    logger.error('Ошибка подключегия, код: %s', response.status_code)
    return None # # # # Временно # # # #

def get_soup(html):

    """ Получает html и возвращает soup """

    soup = BeautifulSoup(html, 'lxml')
    logger.info('Перевод html в soup')

    return soup


def get_full_soup(link):

    """ Получение soup по ссылке """
    
    return get_soup(get_html(link))
