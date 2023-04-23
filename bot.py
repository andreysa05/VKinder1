from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from config import user_token, group_token
from random import randrange
from db import check, insert_data_seen_person


class Bot:
    def __init__(self):
        print("Bot creation completed")
        self.vk_user = vk_api.VkApi(token=user_token)
        self.vk_user_got_api = self.vk_user.get_api()
        self.vk_group = vk_api.VkApi(token=group_token)
        self.vk_group_got_api = self.vk_group.get_api()
        self.longpoll = VkLongPoll(self.vk_group)

    def sending_messages(self, user_id, message):
        self.vk_group_got_api.messages.send(
            user_id=user_id, message=message, random_id=randrange(10**7)
        )

    def title(self, user_id):
        try:
            import datetime
            user_info = self.vk_group_got_api.users.get(user_id=user_id)
            title = user_info[0]["first_title"]
            return title
        except (KeyError, Exception):
            self.sending_messages(user_id, "Ошибка")

    def naming_of_years(self, years, till=True):
        if till:
            title_years = [1, 21, 31, 41, 51, 61, 71, 81, 91, 101]
            if years in title_years:
                return f"{years} года"
            elif years % 10 in [2, 3, 4] and years not in [12, 13, 14]:
                return f"{years} года"
            else:
                return f"{years} лет"
        else:
            title_years = [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54, 62, 63, 64]
            if years == 1:
                return f"{years} год"
            elif years % 10 in [2, 3, 4] and years not in [12, 13, 14]:
                return f"{years} года"
            else:
                return f"{years} лет"

   def input_looking_age(self, user_id, age):
    a = age.split("-")
    try:
        age_from = int(a[0])
        age_to = int(a[1]) if len(a) > 1 else age_from
        if age_from == age_to:
            self.sending_messages(user_id, f" Ищем возраст {self.naming_of_years(age_to, False)}")
        else:
            self.sending_messages(user_id, f" Ищем возраст в пределах от {age_from} и до {self.naming_of_years(age_to, True)}")
    except (IndexError, ValueError):
        self.sending_messages(user_id, f"Ошибка! Введен неверный формат возраста.")

def get_years_of_person(bdate: str):
    bdate_splited = bdate.split(".")
    month = bdate_splited[1]
    birth_date = {
        "1": "января",
        "2": "февраля",
        "3": "марта",
        "4": "апреля",
        "5": "мая",
        "6": "июня",
        "7": "июля",
        "8": "августа",
        "9": "сентября",
        "10": "октября",
        "11": "ноября",
        "12": "декабря",
    }
    return f"{bdate_splited[0]} {birth_date[month]} {bdate_splited[2]}"

def get_age_of_user(self, user_id):
    global age_from, age_to
    try:
        info = self.vk_user_got_api.users.get(
            user_ids=user_id,
            fields="bdate",
        )[0]
        bdate = info.get("bdate")
        if not bdate:
            print("День рождения скрыт настройками приватности!")
            self.sending_messages(
                user_id,
                "Бот ищет людей вашего возраста, "
                'но в ваших в настройках профиля установлен пункт "Не показывать дату рождения". '
                "Введите возраст поиска, например от 21 года и до 35 лет, в формате: 21-35 (или 21 конкретный возраст 21 год).",
            )
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    return self.input_looking_age(user_id, age)

        bdate_splited = bdate.split(".")
        if len(bdate_splited) != 3:
            print(f"День рождения {bdate} не может быть обработан!")
            return

        reverse_bdate = datetime.date(
            int(bdate_splited[2]), int(bdate_splited[1]), int(bdate_splited[0])
        )
        today = datetime.date.today()
        years = today.year - reverse_bdate.year
        if (
            reverse_bdate.month >= today.month
            and reverse_bdate.day > today.day
            or reverse_bdate.month > today.month
        ):
            years -= 1
        age_from = age_to = years
        if years == 0:
            self.sending_messages(
                user_id,
                f"Ваш {self.naming_of_years(years, False)}",
            )
            return
        print(f"Ищем вашего возраста {self.naming_of_years(years)}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return

def get_target_city(self, user_id):
    global city_id, city_title
    self.sending_messages(
        user_id,
        f' Введите "Да" - поиск будет произведен в городе указанный в профиле.'
        f" Или введите название города, например: Москва",
    )
    while True:
        event = self.longpoll.check()
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            answer = event.text.lower()
            if answer == "да" or answer == "y":
                info = self.vk_user_got_api.users.get(
                    user_id=user_id, fields="city"
                )
                if info and info[0].get("city"):
                    city_id = info[0]["city"]["id"]
                    city_title = info[0]["city"]["title"]
                    return f" в городе {city_title}."
            else:
                cities = self.vk_user_got_api.database.getCities(
                    country_id=1, q=answer.capitalize(), need_all=1, count=1
                )["items"]
                if cities:
                    city_id = cities[0]["id"]
                    city_title = cities[0]["title"]
                    return f" в городе {city_title}"
    
def looking_for_gender(self, user_id):
    info = self.vk_user_got_api.users.get(user_id=user_id, fields="sex")
    if info and info[0].get("sex"):
        if info[0]["sex"] == 1:
            print(f"Ваш пол женский, ищем мужчину.")
            return 2
        elif info[0]["sex"] == 2:
            print(f"Ваш пол мужской, ищем женщину.")
            return 1
    print("ERROR!!!")

def looking_for_persons(self, user_id, city_id, city_title, age_from, age_to, gender):
    list_found_persons = []
    res = self.vk_user_got_api.users.search(
        sort=0,
        city=city_id,
        hometown=city_title,
        sex=gender,
        status=1,
        age_from=age_from,
        age_to=age_to,
        has_photo=1,
        count=1000,
        fields="can_write_private_message,city,domain,home_town",
    )
    for index, person in enumerate(res["items"], start=1):
        if "city" in person and person["city"]["id"] == city_id and person["city"]["title"] == city_title:
            id_vk = person["id"]
            list_found_persons.append(id_vk)
    print(f'Bot found {len(list_found_persons)} opened profiles for viewing from {res["count"]}')
    return list_found_persons

def photo_of_found_person(self, user_id):
    res = self.vk_user_got_api.photos.get(
        owner_id=user_id, album_id="profile", extended=1, count=30
    )
    dict_photos = {}
    for i in res["items"]:
        photo_id = str(i["id"])
        i_likes = i["likes"]
        if i_likes["count"]:
            likes = i_likes["count"]
            dict_photos[likes] = photo_id
    list_of_ids = sorted(dict_photos.items(), reverse=True)
    photo_ids = ["photo{}_{}".format(user_id, i[1]) for i in list_of_ids]
    if photo_ids:
        return photo_ids[:3]
    else:
        print("Нет фото")
        return []

def get_found_person_id(self):
    seen_person = [int(i[0]) for i in check()]
    if not seen_person:
        try:
            unique_person_id = list_found_persons[0]
            return unique_person_id
        except IndexError:
            return 0
    else:
        for ifp in list_found_persons:
            if ifp not in seen_person:
                return ifp
        return 0

def found_person_info(self, show_person_id):
    res = self.vk_user_got_api.users.get(
        user_ids=show_person_id,
        fields="about,activities,bdate,status,can_write_private_message,city,common_count,contacts,domain,home_town,interests,movies,music,occupation",
    )
    person = res[0]
    first_name = person.get("first_name", "")
    last_name = person.get("last_name", "")
    bdate = person.get("bdate", "")
    age = self.get_years_of_person(bdate) if bdate else ""
    domain = person.get("domain", "")
    city = person.get("city", {}).get("title", "") or person.get("home_town", "")
    if city:
        city = f"Город {city}"
    vk_link = f"vk.com/{domain}" if domain else ""
    print(f"{first_name} {last_name}, {age}, {city}. {vk_link}")
    return f"{first_name} {last_name}, {age}, {city}. {vk_link}"

def send_photo(self, user_id, message, attachments):
    self.vk_group_got_api.messages.send(
        user_id=user_id,
        message=message,
        random_id=randrange(10**7),
        attachment=",".join(attachments),
    )

def show_found_person(self, user_id):
    found_person_id = self.get_found_person_id()
    if found_person_id is None:
        self.sending_messages(
            user_id,
            "Все анекты ранее были просмотрены. Будет выполнен новый поиск. "
            "Измените критерии поиска (возраст, город). "
            "Введите возраст поиска, на пример от 21 года и до 35 лет, "
            "в формате : 21-35 (или 21 конкретный возраст 21 год). ",
        )
        while True:
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    self.input_looking_age(user_id, age)
                    self.get_target_city(user_id)
                    self.looking_for_persons(user_id)
                    break
            found_person_id = self.get_found_person_id()
            if found_person_id is not None:
                break
    self.sending_messages(user_id, self.found_person_info(found_person_id))
    self.send_photo(user_id, "Фото с максимальными лайками",
                    self.photo_of_found_person(found_person_id))
    insert_data_seen_person(found_person_id)


bot = Bot()
