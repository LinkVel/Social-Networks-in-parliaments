import random
import time


import requests
from bs4 import BeautifulSoup
import lxml
import json



# СОЗДАНИЕ СПИСКА ССЫЛОК ДЛЯ ПОСЛЕДУЮЩЕЙ РАБОТЫ С НИМИ

persons_url_list = []

for i in range(0, 740, 20):
    url = f'https://www.bundestag.de/ajax/filterlist/en/members/863330-863330?limit=20&noFilterSet=true&offset={i}'

    q = requests.get(url)
    result = q.content

    soup = BeautifulSoup(result, 'lxml')
    persons = soup.find_all('a')


    for person in persons:
        person_page_url = person.get('href')
        persons_url_list.append(person_page_url)


with open('persons_url_list_V2.txt', 'a') as file:
    for line in persons_url_list:
        file.write(f'{line}\n')


# СБОР ИНФОРМАЦИИ И ЗАПИСЬ В ФАЙЛ

with open('persons_url_list_V2.txt') as file:

    lines = [line.strip() for line in file.readlines()]

    data_dict = []
    count = 0
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
              'Accept': '*/*'}

    for line in lines:
        q = requests.get(line, headers=header)
        result = q.content

# ПОЛУЧАЕМ ОСНОВНЫЕ ДАННЫЕ (ФАМИЛИЯ, ИМЯ, ОТЧЕСТВО; НАЗВАНИЕ ПАРТИИ; ПРОФЕССИИ; РЕГИОНА ОТ КОТОРОГО ИЗБРАН)

        soup = BeautifulSoup(result, 'lxml')
        person = soup.find(class_='col-xs-8 col-md-9 bt-biografie-name').find('h3').text
        person_name_company = person.strip().split(',')
        person_name = person_name_company[0]
        person_company = person_name_company[1].strip()
        person_profession = soup.find(class_='bt-biografie-beruf').find('p').text.strip()
        region_of_election = soup.find(class_='col-xs-12 col-sm-6 bt-standard-content').find('h5').text.strip()

# ПОЛУЧАЕМ ДАННЫЕ О СОЦ СЕТЯХ

        social_networks = soup.find_all(class_='bt-link-extern')

        social_networks_urls = {}

        for item in social_networks:
            social_networks_name = item.get('title').strip()
            social_networks_link = item.get('href').strip()
            social_networks_urls[social_networks_name] = social_networks_link

# МЕНЯЕМ ССЫЛКИ НА СОЦ СЕТИ НА ЗНАЧЕНИЕ 1

        for link in social_networks_urls:
            social_networks_urls[link] = 1

# ПОЛУЧАЕМ ДАТУ РОЖДЕНИЯ

        biography_information = soup.find(class_='bt-collapse-padding-bottom').find('p').text.strip()


        date_index = []
        for i, val in enumerate(biography_information):
          if val.isdigit():
              date_index.append(i)

        birthday = biography_information[date_index[0]:date_index[-1]+1].replace('.','')

# СОБИРАЕМ ВСЕ ДАННЫЕ В СЛОВАРЬ

        data = {
            'person_name': person_name,
            'birthday_date': birthday,
            'company_name': person_company,
            'profession': person_profession,
            'election_region': region_of_election,
            'social_networks': social_networks_urls
        }
        # ИСПОЛЬЗУЕТСЯ ДЛЯ ОТОБРАЖЕНИЯ ПРОГРЕССА ПРИ ПАРСИНГЕ
        count += 1
        print(f'#{count}: {line} is done!')

        data_dict.append(data)

        pause = random.randint(0, 5)
        time.sleep(pause)

# ЗАПИСЬ В ФАЙЛ JSON
        with open('result_V2.json', 'w', encoding='utf8') as json_file:
            json.dump(data_dict, json_file, indent=4, ensure_ascii=False)




