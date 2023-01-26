from random import randrange
from pprint import pprint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from datetime import datetime

from Table import create_tables, session, Course

with open("access_token.txt", "r") as file_object:  # access_token
    token_vk = file_object.read().strip()

with open("token_community.txt", "r") as file:  # ключ сообщества
    token_community = file.read().strip()


with open("password_base.txt", "r") as file_object:  # access_token
    password = file_object.read().strip()

list_base = password.split(",")

login= list_base[0]
password = list_base[1]
database = list_base[2]

create_tables(login,password,database)


class VKApi():

    def __init__(self, base_url: str = "https://api.vk.com/"):
        self.token_vk = token_vk
        self.base_url = base_url
        self.params = {'access_token': self.token_vk, 'v': '5.131'}

    def users_get_name(self, user_id):
        params = {"user_ids": user_id, "fields": "sex, city, bdate,is_closed"}
        response = requests.get(f"{self.base_url}/method/users.get",
                                params={
                                    **self.params,
                                    **params
                                })
        user_json = response.json()
        return (user_json)

    def users_search(self, age_go, age_from, s_1, city, count, offset):
        params = {
            "count": count,
            "offset": count * offset,
            "fields": "city,sex",
            "sex": s_1,
            "age_from": age_from,
            "age_go": age_go,
            "has_photo": 1,
            "status": 1
        }
        response = requests.get(f"{self.base_url}/method/users.search",
                                params={
                                    **self.params,
                                    **params
                                })

        user_search = response.json()
        flag = error_checking(user_search)
        list_id = []
        black_list_id = []
        list_name = []
        for user in user_search['response']['items']:
            id = user['id']
            for key, value in user.items():
                if user['is_closed'] == True:
                    black_list_id.append(id)
                if user['is_closed'] == False:
                    if key == 'city':
                        for key, value in value.items():
                            if key == 'title' and value == city:
                                list_id.append(id)
                                first_name = user['first_name']
                                last_name = user['last_name']
                                full_name = f'{first_name} {last_name}'
                                list_name.append(full_name)
        dict_name_id = {list_id[i]: list_name[i] for i in range(len(list_id))}
        return (dict_name_id, flag)

    def photos_get(self, id):
        params = {"owner_id": id, "album_id": "profile", "extended": "1"}
        response = requests.get(f"{self.base_url}/method/photos.get",
                                params={
                                    **self.params,
                                    **params
                                })
        photo_json = response.json()
        return (photo_json)


def get_age(response_user):
    currentYear = int(datetime.now().year)
    date = 20
    for r in response_user['response']:
        if 'bdate' in r:
            date_date = r['bdate']
            year = int(date_date[-4:])
            date = currentYear - year
        if 'bdate' not in r:
            write_msg(event.user_id, "Введите ваш возраст")
            date = listen_user()
    return (date)


def get_city(response_user):
    for r in response_user['response']:
        city = "Теткино"
        if 'city' in r:
            city = r['city']['title']
        if 'city' not in r:
            write_msg(event.user_id, "Введите ваш город")
            city = listen_user()
    return (city)


def get_sex(response_user):
    for r in response_user['response']:
        sex_faind = 0
        sex = r['sex']
        if sex == 1:
            sex_faind = 2
        if sex == 2:
            sex_faind = 1
    return (sex_faind)


def photo_send(id_people_search):
    for key, value in id_people_search.items():
        response_photo = user_vk_name.photos_get(key)
        flag = error_checking(response_photo)
        id = key
        name = value
        id_profile_link = f'https://vk.com/id{id}'
        id_photo = []
        likes = []
        owner_id = 0

        for photo in response_photo['response']['items']:
            owner_id = photo['owner_id']
            id_photo.append(photo['id'])
            for key, value in photo['likes'].items():
                if key == 'count':
                    likes.append(value)
        print(owner_id)
        dict_photo_link = {id_photo[i]: likes[i] for i in range(len(id_photo))}
        print(dict_photo_link)
        photos_best = sorted(dict_photo_link, key=dict_photo_link.get, reverse=True)[:3]
        print(photos_best)
        write_msg(event.user_id, f'{name} {id_profile_link}')
        for photo in photos_best:
            send_photo(event.user_id, f'photo{owner_id}_{photo}')
        return (flag)


def write_msg(user_id, message):
    vk.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7)
    })


def send_photo(user_id, attachment):
    vk.method('messages.send', {
        'user_id': user_id,
        'attachment': attachment,
        'random_id': randrange(10 ** 7)
    })


def listen_user():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            age = event.text
            break
    return (age)


def error_checking(error_checking):
    try:
        error_checking = error_checking['response']
        flag = 'OK'
    except:
        write_msg(event.user_id, " Извините, ошибка сервера((")
        flag = "Error"
    return (flag)


vk = vk_api.VkApi(token=token_community)
longpoll = VkLongPoll(vk)

offset = 1

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_vk_name = VKApi()
        name_user = user_vk_name.users_get_name(event.user_id)
        error_respons = error_checking(name_user)
        if error_respons == "Error":
            continue
        else:
            for r in name_user['response']:
                name = r['first_name']
            write_msg(event.user_id,
                      f"Привет, {name} ! Я могу найти вам пару.Хотите начать  поиск?")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    response_1 = event.text
                    if response_1.lower() == "да":
                        user_id = event.user_id
                        currentYear = int(datetime.now().year)
                        date = get_age(name_user)
                        age_go = str(date)
                        age_from = str(date)
                        city = get_city(name_user)
                        sex = get_sex(name_user)
                        count = 6
                        people_search = user_vk_name.users_search(age_go, age_from, sex, city, count, offset)
                        offset = offset + 1
                        people_search_out = people_search[0]
                        print(people_search_out)
                        people_search_error = people_search[1]
                        if people_search_error == "Error":
                            continue
                        else:

                            session(user_id, people_search_out, login, password, database)
                            photo_send(people_search_out)
                            write_msg(event.user_id, "Хотите продолжить поиск?")
                            for event in longpoll.listen():
                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    response_2 = event.text
                                    if response_2.lower() == "да":
                                        offset = offset + 1
                                        people_search_new = user_vk_name.users_search(age_go, age_from, sex, city,
                                                                                      count, offset)
                                        people_search_out = people_search_new[0]
                                        people_search_error = people_search_new[1]
                                        if people_search_error == "Error":
                                            continue
                                        else:
                                            photo_send(people_search_out)
                                            write_msg(event.user_id, "Хотите продолжить поиск?")
                                            session(user_id, people_search_out, login, password, database)
                                            continue
                                    if response_2.lower() == "нет":
                                        write_msg(event.user_id, "Пока((")
                                        break
                                    else:
                                        write_msg(event.user_id, "Не понял вашего ответа...Вы хотите продолжить поиск?")
                                        continue
                        if response_1.lower() == "нет":
                            write_msg(event.user_id, "Пока((")
                        break



