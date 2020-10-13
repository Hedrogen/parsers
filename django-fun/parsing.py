"""

    Скрипт парсит информацию о разделах документации Django

"""


import requests
from bs4 import BeautifulSoup


LINK_RU = 'https://django.fun/docs/django/ru/3.1/'
LINK_ENG = 'https://django.fun/docs/django/en/3.1/'

def get_html(link):

    """ Получает html и возвращает из него content """

    request = requests.get(link)
    content = request.content

    return content


def get_soup(content):

    """ Переводит html.content в soup """

    soup = BeautifulSoup(content, 'lxml')
    return soup


def write_to_txt(arg):

    """ Записывает получаемый список/строку в формат txt """

    with open('result.txt', 'a') as file_:
        if isinstance(arg, list):
            for string in arg:
                file_.writelines(string)
            file_.writelines('\n\n')
        elif isinstance(arg, str):
            file_.writelines('\n' + arg + '\n')
        else:
            raise ValueError('Неверный формат: ', type(arg))


def parse(link=None):

    """ Парсит разделы документации """

    soup = get_soup(get_html(link))
    base = soup.find('div', {'id': 's-django-documentation'})
    section = base.find_all('div', {'class': 'section'})

    for num, sect in enumerate(section):
        head = str(num + 1) + '. ' + str(sect.find('h2').text[:-1]) + '\n\n'
        descrtiption = sect.find('p').text

        list_to_write = [head, descrtiption]
        write_to_txt(list_to_write)

        for tag_ul in sect.find_all('ul', {'class': 'simple'}):
            try:
                write_to_txt(tag_ul.find('strong').text + '\n')
            except AttributeError:
                write_to_txt('')
            for num2, tag_li in enumerate(tag_ul.find_all('li')):
                for num3, tag_a in enumerate(tag_li.find_all('a')):
                    try:
                        write_to_txt('\t' + f'{num+1}.{num2+1}.{num3+1} ' \
                                     + str(tag_a.find('span').text) + '\n')
                    except AttributeError:
                        write_to_txt('')
                    try:
                        write_to_txt('\t' + str(link + tag_a['href']) + '\n')
                    except AttributeError:
                        write_to_txt('')

if __name__ == '__main__':
    parse(LINK_RU)
